from __future__ import annotations

import concurrent.futures
import hashlib
import hmac
import http.cookiejar
import ipaddress
import json
import os
import re
import socket
import ssl
import subprocess
import urllib.parse
import urllib.request
from typing import Any, Callable, Literal

RouterAction = Literal[
    "scan_devices",
    "get_connected_clients",
    "get_router_status",
]

DEFAULT_ROUTER_IP = os.getenv("ROUTER_IP", "192.168.0.1").strip()
DEFAULT_ROUTER_USER = os.getenv("ROUTER_USER", "admin").strip()
DEFAULT_ROUTER_PASS = os.getenv("ROUTER_PASSWORD", "BC202$1$9@").strip()

def _create_ssl_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    try:
        ctx.set_ciphers("DEFAULT:@SECLEVEL=1")
    except Exception:
        pass
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def hex_hmac_md5(k: str, d: str) -> str:
    return hmac.new(k.encode("utf-8"), d.encode("utf-8"), hashlib.md5).hexdigest()

def _ping_host(ip: str) -> tuple[str, bool]:
    try:
        res = subprocess.run(
            ["ping", "-n", "1", "-w", "250", ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return ip, (res.returncode == 0)
    except Exception:
        return ip, False

def _get_local_ip_and_prefix(router_ip: str) -> tuple[str, str]:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((router_ip, 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "192.168.0.100"
    finally:
        s.close()
    prefix = ".".join(local_ip.split(".")[:3])
    return local_ip, prefix

def _get_arp_table() -> dict[str, str]:
    proc = subprocess.run(["arp", "-a"], capture_output=True, text=True, check=False)
    arp_entries: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        match = re.search(r"(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F-]+)\s+(\w+)", line)
        if match:
            ip, mac, arp_type = match.groups()
            mac_formatted = mac.replace("-", ":").upper()
            if arp_type.lower() == "dynamic" and not mac_formatted.startswith("FF:FF:FF"):
                arp_entries[ip] = mac_formatted
    return arp_entries

def scan_devices_lan(
    router_ip: str = DEFAULT_ROUTER_IP,
    timeout_ms: int = 250,
    max_workers: int = 60,
    ping_func: Callable[[str], tuple[str, bool]] | None = None,
    arp_func: Callable[[], dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Scan local subnet via Ping/ARP sweep to detect active online devices."""
    local_ip, prefix = _get_local_ip_and_prefix(router_ip)
    ips_to_scan = [f"{prefix}.{i}" for i in range(1, 255)]
    
    pinger = ping_func or _ping_host
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        _ = list(executor.map(pinger, ips_to_scan))

    arp_getter = arp_func or _get_arp_table
    arp_map = arp_getter()

    devices = []
    for ip, mac in sorted(arp_map.items(), key=lambda x: [int(p) for p in x[0].split(".")]):
        if ip.startswith(prefix):
            hostname = None
            try:
                host, _, _ = socket.gethostbyaddr(ip)
                hostname = host
            except Exception:
                pass
            devices.append({
                "ip": ip,
                "mac": mac,
                "hostname": hostname or "-",
            })

    return {
        "status": "success",
        "method": "lan_arp_sweep",
        "subnet": f"{prefix}.0/24",
        "local_ip": local_ip,
        "total_active_devices": len(devices),
        "devices": devices,
    }

class DLinkDWRM930Client:
    def __init__(self, ip: str = DEFAULT_ROUTER_IP, username: str = DEFAULT_ROUTER_USER, password: str = DEFAULT_ROUTER_PASS) -> None:
        self.ip = ip
        self.username = username
        self.password = password
        self.ctx = _create_ssl_context()
        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=self.ctx),
            urllib.request.HTTPCookieProcessor(self.cj),
        )

    def login(self) -> bool:
        # Step 1: get formLoginKey
        req_key = urllib.request.Request(
            f"https://{self.ip}/boafrm/formLoginKey",
            data=urllib.parse.urlencode({"username": self.username}).encode("utf-8"),
            headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/x-www-form-urlencoded"},
        )
        try:
            with self.opener.open(req_key, timeout=5) as resp:
                key_obj = json.loads(resp.read().decode("utf-8", errors="ignore"))
        except Exception as e:
            raise RuntimeError(f"ROUTER_UNREACHABLE: ไม่สามารถเชื่อมต่อไปยังเราเตอร์ {self.ip} ({e})") from e

        public_key = key_obj.get("PublicKey", "")
        challenge = key_obj.get("Challenge", "")
        if not public_key or not challenge:
            raise RuntimeError(f"AUTH_ERROR: ไม่ได้รับค่า Challenge จากเราเตอร์ ({key_obj})")

        # Step 2: compute HMAC
        private_key = hex_hmac_md5(public_key + self.password, challenge).upper()
        login_passwd = hex_hmac_md5(private_key, challenge).upper()

        # Step 3: post login
        req_setup = urllib.request.Request(
            f"https://{self.ip}/boafrm/formLoginSetup",
            data=urllib.parse.urlencode({
                "username": self.username,
                "password": login_passwd,
                "action": "0",
            }).encode("utf-8"),
            headers={
                "User-Agent": "Mozilla/5.0",
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": f"https://{self.ip}/login.htm",
            },
        )
        with self.opener.open(req_setup, timeout=5) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
            if "main.html" not in body and resp.status == 200 and "webuicookie" not in str(resp.headers):
                raise RuntimeError("AUTH_FAILED: รหัสผ่านเราเตอร์ไม่ถูกต้อง")

        return True

    def fetch(self, path: str) -> str:
        url = f"https://{self.ip}/{path.lstrip('/')}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0", "Referer": f"https://{self.ip}/main.html"},
        )
        with self.opener.open(req, timeout=5) as resp:
            return resp.read().decode("utf-8", errors="ignore")

def get_connected_clients(
    router_ip: str = DEFAULT_ROUTER_IP,
    username: str = DEFAULT_ROUTER_USER,
    password: str = DEFAULT_ROUTER_PASS,
    client: Any = None,
) -> dict[str, Any]:
    """Fetch DHCP and Wireless client tables directly from D-Link router web interface."""
    r_client = client or DLinkDWRM930Client(ip=router_ip, username=username, password=password)
    if hasattr(r_client, "login"):
        r_client.login()

    dhcp_html = r_client.fetch("dhcptbl.htm")
    wl_html = r_client.fetch("wlstatbl.htm")

    # Parse Wireless clients: MAC -> info
    wl_clients: dict[str, dict[str, Any]] = {}
    for tr in re.findall(r"<tr>(.*?)</tr>", wl_html, re.DOTALL):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.DOTALL)
        if len(tds) >= 8:
            clean_tds = [re.sub(r"<[^>]+>", "", t).strip() for t in tds]
            mac = None
            signal = None
            mode = None
            for idx, val in enumerate(clean_tds):
                if re.match(r"^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$", val):
                    mac = val.upper()
                    if idx + 1 < len(clean_tds):
                        mode = clean_tds[idx + 1]
                    for s_val in clean_tds:
                        if any(k in s_val for k in ["Strong", "Middle", "Weak", "%"]):
                            signal = s_val
                    break
            if mac:
                wl_clients[mac] = {
                    "connection": "Wi-Fi",
                    "wifi_mode": mode or "11n",
                    "signal_quality": signal or "Unknown",
                }

    # Parse DHCP clients
    dhcp_clients = []
    for tr in re.findall(r"<tr>(.*?)</tr>", dhcp_html, re.DOTALL):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.DOTALL)
        if len(tds) >= 5:
            clean_tds = [re.sub(r"<[^>]+>", "", t).strip() for t in tds]
            ip = None
            mac = None
            hostname = None
            lease_sec = None
            for val in clean_tds:
                if re.match(r"^\d+\.\d+\.\d+\.\d+$", val):
                    ip = val
                elif re.match(r"^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$", val):
                    mac = val.upper()
                elif val.isdigit() and int(val) > 1000:
                    lease_sec = int(val)
            if ip and mac:
                for val in clean_tds:
                    if val and val != ip and val != mac.lower() and val != str(lease_sec) and "add" not in val.lower():
                        hostname = val
                        break

                wl_info = wl_clients.get(mac, {"connection": "LAN (สายแลน)", "wifi_mode": "-", "signal_quality": "-"})
                dhcp_clients.append({
                    "ip": ip,
                    "mac": mac,
                    "hostname": hostname or "-",
                    "connection": wl_info["connection"],
                    "wifi_mode": wl_info.get("wifi_mode", "-"),
                    "signal_quality": wl_info.get("signal_quality", "-"),
                    "lease_remaining_sec": lease_sec,
                })

    dhcp_clients.sort(key=lambda x: [int(p) for p in x["ip"].split(".")])
    wifi_count = sum(1 for c in dhcp_clients if c["connection"] == "Wi-Fi")
    lan_count = sum(1 for c in dhcp_clients if c["connection"] != "Wi-Fi")

    return {
        "status": "success",
        "router_ip": router_ip,
        "total_connected_clients": len(dhcp_clients),
        "wifi_clients_count": wifi_count,
        "lan_clients_count": lan_count,
        "clients": dhcp_clients,
    }

def get_router_status(
    router_ip: str = DEFAULT_ROUTER_IP,
    username: str = DEFAULT_ROUTER_USER,
    password: str = DEFAULT_ROUTER_PASS,
    client: Any = None,
    public_ip_func: Callable[[], str] | None = None,
) -> dict[str, Any]:
    """Fetch deep router status including 4G LTE, SIM status, CGNAT detection, and cellular metrics."""
    r_client = client or DLinkDWRM930Client(ip=router_ip, username=username, password=password)
    if hasattr(r_client, "login"):
        r_client.login()

    status_html = r_client.fetch("status.htm")

    # Extract JS variables
    product_model = "DWR-M930"
    m_model = re.search(r'var productModel = "([^"]+)";', status_html)
    if m_model:
        product_model = m_model.group(1)

    module_name = None
    m_mod = re.search(r'var moduleName = "([^"]+)";', status_html)
    if m_mod:
        module_name = m_mod.group(1)

    rsrp = None
    m_rsrp = re.search(r'var rsrp = "([^"]+)";', status_html)
    if m_rsrp:
        rsrp = f"{m_rsrp.group(1)} dBm"

    rsrq = None
    m_rsrq = re.search(r'var rsrq = "([^"]+)";', status_html)
    if m_rsrq:
        rsrq = f"{m_rsrq.group(1)} dB"

    sinr = None
    m_sinr = re.search(r'var sinr = "([^"]+)";', status_html)
    if m_sinr:
        sinr = f"{m_sinr.group(1)} dB"

    band = None
    m_band = re.search(r'var band = "([^"]+)";', status_html)
    if m_band:
        band = f"Band {m_band.group(1)}"

    cellid = None
    m_cell = re.search(r'var cellid = "([^"]+)";', status_html)
    if m_cell:
        cellid = m_cell.group(1)

    imsi = None
    m_imsi = re.search(r'var Imsi = "([^"]+)";', status_html)
    if m_imsi:
        imsi = m_imsi.group(1)

    # Extract lteinfo line: "usb0,10.215.75.119,255.255.255.0,10.215.75.136,124.40.228.1,124.40.229.1,28947,dtac.Better Together"
    m_lte = re.search(r'var lteinfo = "([^"]+)";', status_html)
    lte_wan_ip = None
    lte_gateway = None
    lte_dns1 = None
    lte_dns2 = None
    uptime_sec = None
    provider = None

    if m_lte:
        parts = m_lte.group(1).split(",")
        if len(parts) >= 8:
            lte_wan_ip = parts[1]
            lte_gateway = parts[3]
            lte_dns1 = parts[4]
            lte_dns2 = parts[5]
            try:
                uptime_sec = int(parts[6])
            except ValueError:
                uptime_sec = None
            provider = parts[7]

    # Check Public IP
    if public_ip_func:
        public_ip = public_ip_func()
    else:
        try:
            req = urllib.request.Request("https://api.ipify.org", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as r:
                public_ip = r.read().decode("utf-8").strip()
        except Exception:
            public_ip = "unknown"

    # CGNAT Detection
    is_cgnat = False
    cgnat_reason = "Public IP matches WAN IP"
    if lte_wan_ip:
        try:
            ip_obj = ipaddress.ip_address(lte_wan_ip)
            if ip_obj.is_private:
                is_cgnat = True
                cgnat_reason = f"LTE WAN IP เป็น Private IP ({lte_wan_ip}) ซึ่งต่างจาก Public IP ({public_ip})"
            elif lte_wan_ip != public_ip and public_ip != "unknown":
                is_cgnat = True
                cgnat_reason = f"LTE WAN IP ({lte_wan_ip}) ไม่ตรงกับ Public IP จากภายนอก ({public_ip})"
        except ValueError:
            pass

    return {
        "status": "success",
        "router_ip": router_ip,
        "router_model": product_model,
        "cellular_module": module_name,
        "sim_status": "SIM READY" if "SIM READY" in status_html else "UNKNOWN",
        "provider": provider or "dtac / True",
        "imsi": imsi,
        "lte_metrics": {
            "band": band,
            "cell_id": cellid,
            "rsrp": rsrp,
            "rsrq": rsrq,
            "sinr": sinr,
            "signal_status": "Excellent" if rsrp and int(re.sub(r"[^\d-]", "", rsrp) or 0) > -90 else "Good",
        },
        "network": {
            "lte_wan_ip": lte_wan_ip,
            "gateway": lte_gateway,
            "dns": [lte_dns1, lte_dns2],
            "uptime_seconds": uptime_sec,
            "public_ip_external": public_ip,
            "is_cgnat": is_cgnat,
            "cgnat_details": cgnat_reason,
            "port_forwarding_feasible_externally": not is_cgnat,
            "remote_inbound_recommendation": (
                "เนื่องจากติด CGNAT การทำ Port Forwarding ตรงจะไม่ทำงานจากเน็ตภายนอก "
                "แนะนำให้ใช้ Tailscale Subnet Router บนกล่อง Android Box ในวง (tailscale up --advertise-routes=192.168.0.0/24) "
                "เพื่อปิงหรือเปิดหน้าเว็บเราเตอร์ 192.168.0.1 จากนอกวงแลนได้โดยตรง 100%"
            ),
        },
    }

def router_control(
    action: RouterAction = "scan_devices",
    router_ip: str = DEFAULT_ROUTER_IP,
    username: str = DEFAULT_ROUTER_USER,
    password: str = DEFAULT_ROUTER_PASS,
) -> dict[str, Any]:
    """Execute router discovery, connected clients audit, or router cellular health check."""
    if action == "scan_devices":
        return scan_devices_lan(router_ip=router_ip)
    if action == "get_connected_clients":
        return get_connected_clients(router_ip=router_ip, username=username, password=password)
    if action == "get_router_status":
        return get_router_status(router_ip=router_ip, username=username, password=password)
    raise ValueError(f"INVALID_INPUT: unsupported action '{action}'")
