import pytest
from jarvis_mcp.router_control import (
    router_control,
    scan_devices_lan,
    get_connected_clients,
    get_router_status,
    hex_hmac_md5,
)

class FakeDLinkClient:
    def __init__(self, ip="192.168.0.1", username="admin", password="password"):
        self.ip = ip
        self.username = username
        self.password = password
        self.logged_in = False

    def login(self):
        if self.password != "valid_pass":
            raise RuntimeError("AUTH_FAILED: รหัสผ่านเราเตอร์ไม่ถูกต้อง")
        self.logged_in = True
        return True

    def fetch(self, path: str) -> str:
        if path == "dhcptbl.htm":
            return (
                "<table>"
                "<tr><td>Add</td><td>192.168.0.100</td><td>10:D0:7A:E0:78:76</td><td>75000</td><td>host1</td></tr>"
                "<tr><td>Add</td><td>192.168.0.112</td><td>68:8F:C9:26:57:09</td><td>75000</td><td>hk1-box</td></tr>"
                "</table>"
            )
        if path == "wlstatbl.htm":
            return (
                "<table>"
                "<tr><td>Add</td><td>68:8f:c9:26:57:09</td><td>11n</td><td>100</td><td>200</td><td>108</td><td>no</td><td>300</td><td>Strong(80%)</td></tr>"
                "</table>"
            )
        if path == "status.htm":
            return (
                '<script>'
                'var productModel = "DWR-M930";\n'
                'var moduleName = "EC200A";\n'
                'var rsrp = "-82";\n'
                'var rsrq = "-6";\n'
                'var sinr = "11";\n'
                'var band = "40";\n'
                'var cellid = "78729829";\n'
                'var Imsi = "520050320341594";\n'
                'var lteinfo = "usb0,10.215.75.119,255.255.255.0,10.215.75.136,124.40.228.1,124.40.229.1,28947,dtac.Better Together";\n'
                '</script>'
                '<td>SIM Status</td><td>SIM READY</td>'
            )
        return ""

def test_hex_hmac_md5():
    res = hex_hmac_md5("key", "data")
    assert isinstance(res, str)
    assert len(res) == 32

def test_scan_devices_lan_mocked():
    def fake_ping(ip: str):
        return ip, (ip in ["192.168.0.1", "192.168.0.112"])

    def fake_arp():
        return {
            "192.168.0.1": "40:86:CB:40:C2:0E",
            "192.168.0.112": "68:8F:C9:26:57:09",
        }

    res = scan_devices_lan(
        router_ip="192.168.0.1",
        ping_func=fake_ping,
        arp_func=fake_arp,
    )
    assert res["status"] == "success"
    assert res["total_active_devices"] == 2
    ips = [d["ip"] for d in res["devices"]]
    assert "192.168.0.1" in ips
    assert "192.168.0.112" in ips

def test_get_connected_clients_mocked():
    fake_client = FakeDLinkClient(password="valid_pass")
    res = get_connected_clients(client=fake_client)
    assert res["status"] == "success"
    assert res["total_connected_clients"] == 2
    assert res["wifi_clients_count"] == 1
    assert res["lan_clients_count"] == 1
    
    wifi_device = next(c for c in res["clients"] if c["ip"] == "192.168.0.112")
    assert wifi_device["connection"] == "Wi-Fi"
    assert "Strong(80%)" in wifi_device["signal_quality"]

def test_get_router_status_and_cgnat():
    fake_client = FakeDLinkClient(password="valid_pass")
    res = get_router_status(client=fake_client, public_ip_func=lambda: "1.46.15.72")
    assert res["status"] == "success"
    assert res["router_model"] == "DWR-M930"
    assert res["cellular_module"] == "EC200A"
    assert res["provider"] == "dtac.Better Together"
    assert res["lte_metrics"]["band"] == "Band 40"
    assert res["network"]["lte_wan_ip"] == "10.215.75.119"
    assert res["network"]["public_ip_external"] == "1.46.15.72"
    assert res["network"]["is_cgnat"] is True
    assert res["network"]["port_forwarding_feasible_externally"] is False
    assert "Tailscale" in res["network"]["remote_inbound_recommendation"]

def test_router_control_wrapper():
    fake_client = FakeDLinkClient(password="valid_pass")
    with pytest.raises(ValueError, match="INVALID_INPUT"):
        router_control(action="invalid_action")
