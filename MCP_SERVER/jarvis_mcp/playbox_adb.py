from __future__ import annotations

import inspect
import ipaddress
import re
import shlex
import subprocess
from datetime import datetime
from pathlib import Path, PurePosixPath
from types import SimpleNamespace
from typing import Any, Callable, Literal

from jarvis_mcp.tv_control import DSLOADER_PACKAGE, find_adb_binary

PlayboxAction = Literal[
    "connect",
    "disconnect",
    "device_info",
    "get_prop",
    "get_setting",
    "list_packages",
    "check_app",
    "check_webview",
    "check_location",
    "logcat_tail",
    "screenshot",
    "set_setting",
    "set_prop",
    "set_timezone",
    "grant_permission",
    "start_app",
    "stop_app",
    "restart_app",
    "clear_app_data",
    "open_url",
    "keyevent",
    "install_apk",
    "reboot",
    "shell",
]

VALID_NAMESPACES = {"system", "secure", "global"}
ALLOWED_KEYEVENTS = {
    "HOME",
    "BACK",
    "WAKEUP",
    "SLEEP",
    "DPAD_UP",
    "DPAD_DOWN",
    "DPAD_LEFT",
    "DPAD_RIGHT",
    "DPAD_CENTER",
    "ENTER",
    "VOLUME_UP",
    "VOLUME_DOWN",
    "VOLUME_MUTE",
    "MENU",
    "SETTINGS",
}

FORBIDDEN_SHELL_COMMANDS = {
    "rm",
    "dd",
    "mkfs",
    "format",
    "wipe",
    "fastboot",
    "su",
    "sh",
    "bash",
    "chmod",
    "chown",
    "mount",
    "reboot",
    "recovery",
}

READONLY_SIMPLE_COMMANDS = {
    "getprop",
    "dumpsys",
    "df",
    "free",
    "uptime",
    "date",
    "uname",
    "id",
    "whoami",
    "ip",
    "ifconfig",
    "ping",
    "pidof",
    "ps",
    "ls",
    "cat",
    "logcat",
}

WRITE_SIMPLE_COMMANDS = {"setprop", "input", "monkey", "svc", "cmd"}

UNSAFE_SHELL_CHARS = (";", "&", "|", "`", "$", ">", "<", "\n", "\r")
_KEY_RE = re.compile(r"^[A-Za-z0-9._-]+$")
_PKG_RE = re.compile(r"^[A-Za-z0-9._]+$")
_HOSTNAME_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9.\-]{0,251}[A-Za-z0-9])?$")
_TIMEZONE_RE = re.compile(r"^[A-Za-z_]+(?:/[A-Za-z0-9_+\-]+)+$")
_PROP_LINE_RE = re.compile(r"^\[([^\]]+)\]: \[(.*)\]$")

MAX_OUTPUT_CHARS = 8000
MAX_PACKAGES_RETURNED = 100
DEFAULT_SANDBOX_DIR = Path(__file__).resolve().parents[2] / "SANDBOX"

UNREACHABLE_MARKERS = (
    "cannot connect",
    "unable to connect",
    "failed to connect",
    "connection refused",
    "no route to host",
    "offline",
    "host is down",
    "timed out",
    "no devices/emulators found",
    "not found",
)

UNAUTHORIZED_HINT = (
    "กรุณาดูที่หน้าจอกล่อง Playbox แล้วติ๊ก 'Always allow from this computer' "
    "และกด 'Allow / อนุญาต' (ครั้งแรกของการเชื่อมต่อ) จากนั้นแจ้ง AI ให้ลองใหม่อีกครั้ง"
)
UNREACHABLE_HINT = (
    "ไม่สามารถเชื่อมต่อกล่อง Playbox ได้ กรุณาตรวจสอบว่า: "
    "(1) กล่องอยู่ Wi-Fi/LAN วงเดียวกับคอมพิวเตอร์, "
    "(2) เลข IP ถูกต้อง, "
    "(3) เปิด ADB debugging / USB debugging + Internet ADB (ถ้ามี) "
    "และตั้งการกำหนดค่า USB เป็น MTP แล้ว"
)


def parse_playbox_target(ip: str, port: int = 5555) -> str:
    """Validate and normalize target IP/host and ADB TCP port into '<host>:<port>'."""
    raw = (ip or "").strip()
    if not raw:
        raise ValueError("INVALID_INPUT: กรุณาระบุเลข IP ของกล่อง Playbox")
    if any(ch.isspace() or ch in UNSAFE_SHELL_CHARS for ch in raw):
        raise ValueError("INVALID_INPUT: IP หรือ hostname มีอักขระต้องห้าม")

    host_part = raw
    resolved_port = port

    if raw.startswith("["):
        match = re.fullmatch(r"\[([^\]]+)\](?::(\d+))?", raw)
        if not match:
            raise ValueError(f"INVALID_INPUT: รูปแบบ IPv6 '{ip}' ไม่ถูกต้อง")
        host_part = match.group(1)
        if match.group(2) is not None:
            resolved_port = int(match.group(2))
    else:
        try:
            ip_obj = ipaddress.ip_address(raw)
            if isinstance(ip_obj, ipaddress.IPv6Address):
                host_part = f"[{raw}]"
        except ValueError:
            if raw.count(":") == 1:
                candidate_host, _, port_str = raw.partition(":")
                if not port_str.isdigit():
                    raise ValueError(f"INVALID_INPUT: port ใน '{ip}' ต้องเป็นตัวเลข 1-65535")
                host_part = candidate_host
                resolved_port = int(port_str)
            elif ":" in raw:
                raise ValueError(f"INVALID_INPUT: รูปแบบ IP/host '{ip}' ไม่ถูกต้อง")

    if not (1 <= int(resolved_port) <= 65535):
        raise ValueError("INVALID_INPUT: port ต้องอยู่ระหว่าง 1 ถึง 65535")

    bare_host = host_part.strip("[]")
    try:
        ip_obj = ipaddress.ip_address(bare_host)
        if isinstance(ip_obj, ipaddress.IPv6Address):
            return f"[{bare_host}]:{int(resolved_port)}"
        return f"{bare_host}:{int(resolved_port)}"
    except ValueError:
        if not _HOSTNAME_RE.fullmatch(bare_host):
            raise ValueError(f"INVALID_INPUT: IP หรือ hostname '{ip}' ไม่ถูกต้อง")
        return f"{bare_host}:{int(resolved_port)}"


def _validate_identifier(value: str | None, field_name: str, pattern: re.Pattern[str]) -> str:
    clean = (value or "").strip()
    if not clean or not pattern.fullmatch(clean):
        raise ValueError(f"INVALID_INPUT: '{field_name}' ไม่ถูกต้อง ({value!r})")
    return clean


def _validate_safe_value(value: Any, field_name: str, *, allow_empty: bool = False) -> str:
    if value is None:
        raise ValueError(f"INVALID_INPUT: กรุณาระบุ '{field_name}'")
    text = str(value).strip()
    if not allow_empty and not text:
        raise ValueError(f"INVALID_INPUT: '{field_name}' ต้องไม่เป็นค่าว่าง")
    if any(ch in text for ch in UNSAFE_SHELL_CHARS):
        raise ValueError(f"INVALID_INPUT: '{field_name}' มีอักขระต้องห้าม")
    return text


def _validate_url(url: str | None) -> str:
    clean = (url or "").strip()
    if not clean or not (clean.startswith("http://") or clean.startswith("https://")):
        raise ValueError("INVALID_INPUT: action 'open_url' ต้องระบุ URL ที่ขึ้นต้นด้วย http:// หรือ https://")
    if any(ch.isspace() or ch in UNSAFE_SHELL_CHARS for ch in clean):
        raise ValueError("INVALID_INPUT: URL มีช่องว่างหรืออักขระต้องห้าม")
    return clean


def validate_safe_shell_command(command: str | None) -> tuple[list[str], bool]:
    """Validate an ADB shell command against forbidden blocklist and read/write allowlists.

    Returns (tokens, is_write). Raises ValueError for unsafe or unsupported commands.
    """
    raw = (command or "").strip()
    if not raw:
        raise ValueError("INVALID_INPUT: action 'shell' ต้องระบุคำสั่งใน 'command'")
    if any(ch in raw for ch in UNSAFE_SHELL_CHARS):
        raise ValueError("FORBIDDEN_COMMAND: ไม่อนุญาตให้ใช้เครื่องหมาย shell chaining หรือ redirection")

    try:
        tokens = shlex.split(raw)
    except ValueError as exc:
        raise ValueError(f"INVALID_INPUT: ไม่สามารถแยกคำสั่งได้ ({exc})") from exc

    if not tokens:
        raise ValueError("INVALID_INPUT: action 'shell' ต้องระบุคำสั่งใน 'command'")

    base_cmd = PurePosixPath(tokens[0]).name.lower()

    if base_cmd in FORBIDDEN_SHELL_COMMANDS:
        raise ValueError(f"FORBIDDEN_COMMAND: ไม่อนุญาตให้รันคำสั่ง '{base_cmd}'")

    # Reject dangerous subcommands inside cmd/pm/am
    if base_cmd == "pm" and len(tokens) >= 2 and tokens[1].lower() in {"clear", "uninstall", "install"}:
        raise ValueError(
            f"FORBIDDEN_COMMAND: กรุณาใช้ action เฉพาะทางแทน 'pm {tokens[1]}' เพื่อความปลอดภัย"
        )

    if base_cmd in READONLY_SIMPLE_COMMANDS:
        return tokens, False

    if base_cmd in WRITE_SIMPLE_COMMANDS:
        return tokens, True

    sub = tokens[1].lower() if len(tokens) >= 2 else ""

    if base_cmd == "pm":
        if sub in {"list", "path", "dump"}:
            return tokens, False
        if sub in {"grant", "revoke", "enable", "disable-user"}:
            return tokens, True
    elif base_cmd == "settings":
        if sub in {"get", "list"}:
            return tokens, False
        if sub in {"put", "delete"}:
            return tokens, True
    elif base_cmd == "appops":
        if sub == "get":
            return tokens, False
        if sub == "set":
            return tokens, True
    elif base_cmd == "am":
        if sub in {"start", "force-stop", "broadcast"}:
            return tokens, True
    elif base_cmd == "wm":
        if sub in {"size", "density"}:
            if len(tokens) == 2:
                return tokens, False
            return tokens, True

    raise ValueError(f"UNSUPPORTED_COMMAND: คำสั่ง '{raw}' ไม่อยู่ในรายการที่อนุญาต")


def _default_adb_runner(cmd: list[str], timeout: int = 15) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
        encoding="utf-8",
        errors="replace",
    )


def _invoke_runner(
    runner: Callable[..., Any],
    cmd: list[str],
    timeout: int = 15,
) -> tuple[Any, bool]:
    """Call an adb runner safely, supporting injected 1-arg or 2-arg mocks and catching timeouts."""
    try:
        params = inspect.signature(runner).parameters
        accepts_timeout = (
            "timeout" in params
            or len(params) >= 2
            or any(
                p.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
                for p in params.values()
            )
        )
    except (TypeError, ValueError):
        accepts_timeout = False

    try:
        proc = runner(cmd, timeout=timeout) if accepts_timeout else runner(cmd)
        return proc, False
    except subprocess.TimeoutExpired as exc:
        out_text = ((exc.stdout or "") if isinstance(exc.stdout, str) else "") + "\n"
        err_text = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
        return (
            SimpleNamespace(
                returncode=124,
                stdout=out_text.strip(),
                stderr=(err_text or f"Command timed out after {timeout}s").strip(),
            ),
            True,
        )


def _combine_output(proc: Any) -> str:
    stdout = getattr(proc, "stdout", "") or ""
    stderr = getattr(proc, "stderr", "") or ""
    return "\n".join(part for part in (stdout.strip(), stderr.strip()) if part).strip()


def _truncate_text(text: str, limit: int = MAX_OUTPUT_CHARS) -> tuple[str, bool]:
    if len(text) <= limit:
        return text, False
    return text[:limit] + "\n... [truncated]", True


def _parse_props(raw_getprop: str) -> dict[str, str]:
    props: dict[str, str] = {}
    for line in raw_getprop.splitlines():
        match = _PROP_LINE_RE.match(line.strip())
        if match:
            props[match.group(1)] = match.group(2)
    return props


def _parse_real_hardware_rom(raw_parts: str, chip_name: str = "", manfid: str = "") -> dict[str, Any] | None:
    main_blocks = 0
    dev_name = ""
    for line in raw_parts.splitlines():
        parts = line.strip().split()
        if len(parts) >= 4 and parts[3].startswith("mmcblk") and not re.search(r"p\d+$|boot\d+$", parts[3]):
            try:
                blocks = int(parts[2])
                if blocks > main_blocks:
                    main_blocks = blocks
                    dev_name = parts[3]
            except ValueError:
                pass
    if main_blocks > 0:
        total_bytes = main_blocks * 1024
        total_gib = round(total_bytes / (1024**3), 2)
        total_gb = round(total_bytes / 1e9, 2)
        if 45 <= total_gb <= 75:
            nominal_gb = 64
        elif 90 <= total_gb <= 140:
            nominal_gb = 128
        elif 180 <= total_gb <= 280:
            nominal_gb = 256
        elif 24 <= total_gb <= 38:
            nominal_gb = 32
        elif 12 <= total_gb <= 19:
            nominal_gb = 16
        elif 6 <= total_gb <= 10:
            nominal_gb = 8
        else:
            nominal_gb = round(total_gb)
        mfg_map = {
            "0x000015": "Samsung",
            "0x000090": "SK Hynix",
            "0x000045": "SanDisk",
            "0x000011": "Toshiba/Kioxia",
            "0x0000fe": "Micron",
        }
        clean_manfid = manfid.strip().lower()
        clean_name = chip_name.strip()
        if "no such" in clean_name.lower():
            clean_name = ""
        return {
            "device": dev_name,
            "real_capacity_bytes": total_bytes,
            "real_capacity_gib": total_gib,
            "real_capacity_gb": total_gb,
            "market_spec": f"{nominal_gb} GB",
            "chip_name": clean_name or None,
            "manufacturer": mfg_map.get(clean_manfid, manfid.strip() if ("no such" not in clean_manfid and clean_manfid) else None),
        }
    return None


def _parse_meminfo(raw_meminfo: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in raw_meminfo.splitlines():
        for key in ("MemTotal", "MemFree", "MemAvailable", "SwapTotal", "SwapFree"):
            if line.startswith(f"{key}:"):
                result[key] = line.split(":", 1)[1].strip()
    return result


def _parse_package_dump(raw_dump: str) -> dict[str, Any]:
    version_name = None
    version_code = None
    permissions: list[str] = []
    for line in raw_dump.splitlines():
        stripped = line.strip()
        if version_name is None and stripped.startswith("versionName="):
            version_name = stripped.split("=", 1)[1].strip()
        elif version_code is None and "versionCode=" in stripped:
            m = re.search(r"versionCode=(\S+)", stripped)
            if m:
                version_code = m.group(1)
        elif "granted=" in stripped and (
            "LOCATION" in stripped or "CAMERA" in stripped or "STORAGE" in stripped or "SYSTEM_ALERT_WINDOW" in stripped
        ):
            permissions.append(stripped)
    return {
        "version_name": version_name,
        "version_code": version_code,
        "key_permissions": permissions[:20],
    }


def _parse_webview_dump(raw_dump: str) -> dict[str, Any]:
    current_pkg = None
    fallback = None
    for line in raw_dump.splitlines():
        stripped = line.strip()
        if "Current WebView package" in stripped:
            m = re.search(r":\s*\(([^,]+),\s*([^)]+)\)", stripped)
            if not m:
                m = re.search(r"\(([^,]+),\s*([^)]+)\)", stripped)
            if m:
                current_pkg = {"package": m.group(1).strip(), "version": m.group(2).strip()}
            else:
                current_pkg = {"raw": stripped}
        elif "Fallback logic enabled:" in stripped:
            fallback = stripped.split(":", 1)[1].strip()
    lines = [line for line in raw_dump.splitlines() if line.strip()]
    snippet, truncated = _truncate_text("\n".join(lines[:20]), 2000)
    return {
        "current_webview": current_pkg,
        "fallback_logic_enabled": fallback,
        "summary": snippet,
        "truncated": truncated,
    }


def _extract_location_providers(raw_dump: str) -> list[str]:
    lines = raw_dump.splitlines()
    captured: list[str] = []
    collect_remaining = 0
    for line in lines:
        lower = line.lower()
        if re.match(r"^\s*(gps|network|fused)\s+provider:", lower) or "last known locations" in lower:
            collect_remaining = 5
        if collect_remaining > 0:
            if line.strip():
                captured.append(line.rstrip())
            collect_remaining -= 1
            if len(captured) >= 60:
                break
    return captured


def _confirmation_response(target_serial: str, action: str, detail: str) -> dict[str, Any]:
    return {
        "status": "confirmation_required",
        "target": target_serial,
        "action": action,
        "message": f"คำสั่ง '{action}' ({detail}) มีผลต่อการทำงานของกล่อง Playbox กรุณายืนยันกับผู้ใช้ก่อนส่ง confirm=True",
    }


def _connect_and_check_state(
    adb_bin: str,
    target_serial: str,
    action: str,
    runner: Callable[..., Any],
) -> tuple[dict[str, Any] | None, str, str]:
    """Connect to device via ADB over TCP/IP and verify it is reachable and authorized."""
    conn_proc, timed_out = _invoke_runner(runner, [adb_bin, "connect", target_serial], timeout=15)
    conn_out = _combine_output(conn_proc)
    if timed_out:
        return (
            {
                "status": "timeout",
                "target": target_serial,
                "action": action,
                "output": conn_out,
                "hint": UNREACHABLE_HINT,
            },
            conn_out,
            "timeout",
        )

    conn_lower = conn_out.casefold()
    if "unauthorized" in conn_lower:
        return (
            {
                "status": "unauthorized",
                "target": target_serial,
                "action": action,
                "output": conn_out,
                "hint": UNAUTHORIZED_HINT,
            },
            conn_out,
            "unauthorized",
        )

    if any(marker in conn_lower for marker in UNREACHABLE_MARKERS) or getattr(conn_proc, "returncode", 0) != 0:
        return (
            {
                "status": "unreachable",
                "target": target_serial,
                "action": action,
                "output": conn_out,
                "hint": UNREACHABLE_HINT,
            },
            conn_out,
            "unreachable",
        )

    # adb connect can return exit code 0 even while device state is unauthorized or offline
    state_proc, state_timed_out = _invoke_runner(runner, [adb_bin, "-s", target_serial, "get-state"], timeout=10)
    if state_timed_out:
        return (
            {
                "status": "timeout",
                "target": target_serial,
                "action": action,
                "connect_output": conn_out,
                "output": _combine_output(state_proc),
                "hint": UNREACHABLE_HINT,
            },
            conn_out,
            "timeout",
        )

    state_out = _combine_output(state_proc)
    state_lower = state_out.casefold()
    if "unauthorized" in state_lower:
        return (
            {
                "status": "unauthorized",
                "target": target_serial,
                "action": action,
                "connect_output": conn_out,
                "output": state_out,
                "hint": UNAUTHORIZED_HINT,
            },
            conn_out,
            "unauthorized",
        )

    if any(marker in state_lower for marker in UNREACHABLE_MARKERS) or (
        getattr(state_proc, "returncode", 0) != 0 and state_out
    ):
        return (
            {
                "status": "unreachable",
                "target": target_serial,
                "action": action,
                "connect_output": conn_out,
                "output": state_out,
                "hint": UNREACHABLE_HINT,
            },
            conn_out,
            "unreachable",
        )

    device_state = state_out.splitlines()[-1].strip() if state_out else "device"
    return None, conn_out, device_state


def _validate_and_gate_action(
    target_serial: str,
    action: PlayboxAction,
    *,
    namespace: str | None,
    key: str | None,
    value: str | None,
    package: str | None,
    permission: str | None,
    url: str | None,
    apk_path: str | None,
    command: str | None,
    lines: int,
    confirm: bool,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """Validate inputs upfront and enforce confirmation gates before touching ADB."""
    parsed: dict[str, Any] = {}

    if action == "get_prop":
        if key is not None and str(key).strip():
            parsed["key"] = _validate_identifier(key, "key", _KEY_RE)
    elif action == "set_prop":
        parsed["key"] = _validate_identifier(key, "key", _KEY_RE)
        parsed["value"] = _validate_safe_value(value, "value")
    elif action in {"get_setting", "set_setting"}:
        ns = (namespace or "").strip().lower()
        if ns not in VALID_NAMESPACES:
            raise ValueError("INVALID_INPUT: namespace ต้องเป็น 'system', 'secure', หรือ 'global'")
        parsed["namespace"] = ns
        parsed["key"] = _validate_identifier(key, "key", _KEY_RE)
        if action == "set_setting":
            parsed["value"] = _validate_safe_value(value, "value")
    elif action == "set_timezone":
        parsed["timezone"] = _validate_identifier(value, "value (timezone)", _TIMEZONE_RE)
    elif action in {"check_app", "start_app", "stop_app", "restart_app"}:
        parsed["package"] = _validate_identifier(package or DSLOADER_PACKAGE, "package", _PKG_RE)
    elif action == "clear_app_data":
        parsed["package"] = _validate_identifier(package, "package", _PKG_RE)
        if not confirm:
            return _confirmation_response(target_serial, action, f"ล้างข้อมูลแอป {parsed['package']}"), parsed
    elif action == "grant_permission":
        parsed["package"] = _validate_identifier(package, "package", _PKG_RE)
        parsed["permission"] = _validate_identifier(permission, "permission", _PKG_RE)
    elif action == "open_url":
        parsed["url"] = _validate_url(url)
    elif action == "keyevent":
        raw_key = (value or "").strip().upper()
        if raw_key.startswith("KEYCODE_"):
            raw_key = raw_key[len("KEYCODE_") :]
        if raw_key not in ALLOWED_KEYEVENTS:
            raise ValueError(f"INVALID_INPUT: keyevent '{value}' ไม่อยู่ในรายการที่รองรับ ({sorted(ALLOWED_KEYEVENTS)})")
        parsed["keycode"] = f"KEYCODE_{raw_key}"
    elif action == "logcat_tail":
        if not (1 <= int(lines) <= 200):
            raise ValueError("INVALID_INPUT: 'lines' ต้องอยู่ระหว่าง 1 ถึง 200")
        parsed["lines"] = int(lines)
    elif action == "install_apk":
        clean_apk = (apk_path or "").strip()
        if not clean_apk:
            raise ValueError("INVALID_INPUT: action 'install_apk' ต้องระบุ 'apk_path'")
        apk_file = Path(clean_apk)
        if apk_file.suffix.lower() != ".apk" or not apk_file.is_file():
            raise ValueError(f"INVALID_INPUT: ไม่พบไฟล์ APK หรือนามสกุลไม่ใช่ .apk ({clean_apk})")
        parsed["apk_path"] = str(apk_file)
        if not confirm:
            return _confirmation_response(target_serial, action, f"ติดตั้ง APK {apk_file.name}"), parsed
    elif action == "reboot":
        if not confirm:
            return _confirmation_response(target_serial, action, "รีบูตกล่อง Playbox"), parsed
    elif action == "shell":
        tokens, is_write = validate_safe_shell_command(command)
        parsed["tokens"] = tokens
        parsed["is_write"] = is_write
        if is_write and not confirm:
            return _confirmation_response(target_serial, action, f"คำสั่ง shell ที่มีผลเปลี่ยนแปลงค่า: {command}"), parsed
    elif action not in {
        "connect",
        "disconnect",
        "device_info",
        "list_packages",
        "check_webview",
        "check_location",
        "screenshot",
    }:
        raise ValueError(f"INVALID_INPUT: ไม่รองรับ action '{action}'")

    return None, parsed


def playbox_adb(
    ip: str,
    action: PlayboxAction = "connect",
    port: int = 5555,
    namespace: str | None = None,
    key: str | None = None,
    value: str | None = None,
    package: str | None = None,
    permission: str | None = None,
    url: str | None = None,
    apk_path: str | None = None,
    command: str | None = None,
    filter_text: str | None = None,
    lines: int = 50,
    confirm: bool = False,
    adb_runner: Callable[..., Any] | None = None,
    adb_path: str | None = None,
    sandbox_dir: Path | None = None,
) -> dict[str, Any]:
    """เชื่อมต่อและจัดการกล่อง Playbox / Android TV Box ผ่าน ADB over LAN/Wi-Fi."""
    target_serial = parse_playbox_target(ip, port)

    early_result, parsed = _validate_and_gate_action(
        target_serial,
        action,
        namespace=namespace,
        key=key,
        value=value,
        package=package,
        permission=permission,
        url=url,
        apk_path=apk_path,
        command=command,
        lines=lines,
        confirm=confirm,
    )
    if early_result is not None:
        return early_result

    adb_bin = adb_path or find_adb_binary()
    runner = adb_runner or _default_adb_runner

    def run_cmd(args: list[str], timeout: int = 15) -> tuple[Any, str, bool]:
        proc, timed_out = _invoke_runner(runner, args, timeout=timeout)
        return proc, _combine_output(proc), timed_out

    def run_shell(shell_args: list[str], timeout: int = 15) -> tuple[Any, str, bool]:
        return run_cmd([adb_bin, "-s", target_serial, "shell", *shell_args], timeout=timeout)

    if action == "disconnect":
        proc, out, timed_out = run_cmd([adb_bin, "disconnect", target_serial], timeout=10)
        return {
            "status": "timeout" if timed_out else ("success" if getattr(proc, "returncode", 0) == 0 else "error"),
            "target": target_serial,
            "action": action,
            "output": out,
        }

    conn_error, conn_out, device_state = _connect_and_check_state(adb_bin, target_serial, action, runner)
    if conn_error is not None:
        return conn_error

    if action == "connect":
        return {
            "status": "connected",
            "target": target_serial,
            "action": action,
            "device_state": device_state,
            "connect_output": conn_out,
        }

    if action == "device_info":
        _, raw_props, _ = run_shell(["getprop"])
        props = _parse_props(raw_props)
        _, raw_date, _ = run_shell(["date"])
        _, raw_size, _ = run_shell(["wm", "size"])
        _, raw_density, _ = run_shell(["wm", "density"])
        _, raw_mem, _ = run_shell(["cat", "/proc/meminfo"])
        _, raw_df, _ = run_shell(["df", "-h", "/data"])
        _, raw_wv, _ = run_shell(["dumpsys", "webviewupdate"])
        _, raw_pid, _ = run_shell(["pidof", DSLOADER_PACKAGE])
        _, raw_pkg, _ = run_shell(["dumpsys", "package", DSLOADER_PACKAGE])
        _, raw_parts, _ = run_shell(["cat", "/proc/partitions"])
        _, chip_name, _ = run_shell(["cat", "/sys/class/block/mmcblk1/device/name"])
        if not chip_name.strip() or "no such" in chip_name.lower():
            _, chip_name, _ = run_shell(["cat", "/sys/class/block/mmcblk0/device/name"])
        _, manfid, _ = run_shell(["cat", "/sys/class/block/mmcblk1/device/manfid"])
        if not manfid.strip() or "no such" in manfid.lower():
            _, manfid, _ = run_shell(["cat", "/sys/class/block/mmcblk0/device/manfid"])
        pkg_info = _parse_package_dump(raw_pkg)
        wv_info = _parse_webview_dump(raw_wv)
        real_rom = _parse_real_hardware_rom(raw_parts, chip_name, manfid)
        return {
            "status": "success",
            "target": target_serial,
            "action": action,
            "device_info": {
                "model": props.get("ro.product.model"),
                "manufacturer": props.get("ro.product.manufacturer"),
                "brand": props.get("ro.product.brand"),
                "board_platform": props.get("ro.board.platform"),
                "android_version": props.get("ro.build.version.release"),
                "sdk_version": props.get("ro.build.version.sdk"),
                "build_id": props.get("ro.build.display.id"),
                "timezone": props.get("persist.sys.timezone"),
                "device_time": raw_date.strip(),
                "display_size": raw_size.strip(),
                "display_density": raw_density.strip(),
                "memory": _parse_meminfo(raw_mem),
                "real_hardware_rom": real_rom,
                "storage_data": raw_df.strip(),
                "webview": wv_info.get("current_webview"),
                "dsloader": {
                    "package": DSLOADER_PACKAGE,
                    "running": bool(raw_pid.strip()),
                    "pids": raw_pid.strip().split() if raw_pid.strip() else [],
                    "version_name": pkg_info.get("version_name"),
                    "version_code": pkg_info.get("version_code"),
                },
            },
        }

    if action == "get_prop":
        if "key" in parsed:
            proc, out, timed_out = run_shell(["getprop", parsed["key"]])
            return {
                "status": "timeout" if timed_out else ("success" if getattr(proc, "returncode", 0) == 0 else "error"),
                "target": target_serial,
                "action": action,
                "key": parsed["key"],
                "value": out.strip(),
            }
        proc, out, timed_out = run_shell(["getprop"])
        props = _parse_props(out)
        common_keys = (
            "ro.product.model",
            "ro.product.manufacturer",
            "ro.product.brand",
            "ro.board.platform",
            "ro.build.version.release",
            "ro.build.version.sdk",
            "ro.build.display.id",
            "persist.sys.timezone",
            "service.adb.tcp.port",
            "persist.adb.tcp.port",
            "ro.serialno",
        )
        return {
            "status": "timeout" if timed_out else ("success" if getattr(proc, "returncode", 0) == 0 else "error"),
            "target": target_serial,
            "action": action,
            "properties": {k: props.get(k) for k in common_keys if k in props},
        }

    if action == "set_prop":
        prop_key = parsed["key"]
        prop_val = parsed["value"]
        _, prev_val, _ = run_shell(["getprop", prop_key])
        proc, out, timed_out = run_shell(["setprop", prop_key, prop_val])
        _, new_val, _ = run_shell(["getprop", prop_key])
        res: dict[str, Any] = {
            "status": "timeout" if timed_out else ("success" if getattr(proc, "returncode", 0) == 0 else "error"),
            "target": target_serial,
            "action": action,
            "key": prop_key,
            "previous_value": prev_val.strip(),
            "requested_value": prop_val,
            "new_value": new_val.strip(),
            "output": out,
        }
        if prop_key.startswith("persist.") and new_val.strip() != prop_val:
            res["note"] = "ค่า persist.* หรือ system property บางตัวอาจต้องใช้สิทธิ์ root จึงจะเปลี่ยนได้"
        return res

    if action == "get_setting":
        proc, out, timed_out = run_shell(["settings", "get", parsed["namespace"], parsed["key"]])
        return {
            "status": "timeout" if timed_out else ("success" if getattr(proc, "returncode", 0) == 0 else "error"),
            "target": target_serial,
            "action": action,
            "namespace": parsed["namespace"],
            "key": parsed["key"],
            "value": out.strip(),
        }

    if action == "set_setting":
        ns = parsed["namespace"]
        s_key = parsed["key"]
        s_val = parsed["value"]
        _, prev_val, _ = run_shell(["settings", "get", ns, s_key])
        proc, out, timed_out = run_shell(["settings", "put", ns, s_key, s_val])
        _, new_val, _ = run_shell(["settings", "get", ns, s_key])
        return {
            "status": "timeout" if timed_out else ("success" if getattr(proc, "returncode", 0) == 0 else "error"),
            "target": target_serial,
            "action": action,
            "namespace": ns,
            "key": s_key,
            "previous_value": prev_val.strip(),
            "new_value": new_val.strip(),
            "changed": prev_val.strip() != new_val.strip(),
            "output": out,
        }

    if action == "set_timezone":
        tz = parsed["timezone"]
        _, prev_tz, _ = run_shell(["getprop", "persist.sys.timezone"])
        proc, out, timed_out = run_shell(["setprop", "persist.sys.timezone", tz])
        _, new_tz, _ = run_shell(["getprop", "persist.sys.timezone"])
        _, cur_date, _ = run_shell(["date"])
        return {
            "status": "timeout" if timed_out else ("success" if getattr(proc, "returncode", 0) == 0 else "error"),
            "target": target_serial,
            "action": action,
            "previous_timezone": prev_tz.strip(),
            "new_timezone": new_tz.strip(),
            "device_time": cur_date.strip(),
            "output": out,
        }

    if action == "list_packages":
        cmd = ["pm", "list", "packages", "-3"] if (value or "").strip().lower() in {"third_party", "3"} else ["pm", "list", "packages"]
        proc, out, timed_out = run_shell(cmd)
        packages = []
        for line in out.splitlines():
            clean = line.strip()
            if clean.startswith("package:"):
                packages.append(clean[len("package:") :])
        if filter_text and filter_text.strip():
            needle = filter_text.strip().casefold()
            packages = [p for p in packages if needle in p.casefold()]
        packages.sort()
        total_matched = len(packages)
        return {
            "status": "timeout" if timed_out else ("success" if getattr(proc, "returncode", 0) == 0 else "error"),
            "target": target_serial,
            "action": action,
            "total_matched": total_matched,
            "returned": min(total_matched, MAX_PACKAGES_RETURNED),
            "truncated": total_matched > MAX_PACKAGES_RETURNED,
            "packages": packages[:MAX_PACKAGES_RETURNED],
        }

    if action == "check_app":
        pkg = parsed["package"]
        _, path_out, timed_out_1 = run_shell(["pm", "path", pkg])
        _, pid_out, timed_out_2 = run_shell(["pidof", pkg])
        _, dump_out, timed_out_3 = run_shell(["dumpsys", "package", pkg])
        parsed_dump = _parse_package_dump(dump_out)
        installed = "package:" in path_out or f"Package [{pkg}]" in dump_out
        return {
            "status": "timeout" if (timed_out_1 or timed_out_2 or timed_out_3) else "success",
            "target": target_serial,
            "action": action,
            "package": pkg,
            "installed": installed,
            "apk_path": path_out.strip() or None,
            "running": bool(pid_out.strip()),
            "pids": pid_out.strip().split() if pid_out.strip() else [],
            **parsed_dump,
        }

    if action == "check_webview":
        proc, out, timed_out = run_shell(["dumpsys", "webviewupdate"])
        return {
            "status": "timeout" if timed_out else ("success" if getattr(proc, "returncode", 0) == 0 else "error"),
            "target": target_serial,
            "action": action,
            **_parse_webview_dump(out),
        }

    if action == "check_location":
        _, loc_mode, _ = run_shell(["settings", "get", "secure", "location_mode"])
        _, wifi_scan, _ = run_shell(["settings", "get", "global", "wifi_scan_always_enabled"])
        _, gms_pid, _ = run_shell(["pidof", "com.google.android.gms.persistent"])
        proc, dump_out, timed_out = run_shell(["dumpsys", "location"])
        return {
            "status": "timeout" if timed_out else ("success" if getattr(proc, "returncode", 0) == 0 else "error"),
            "target": target_serial,
            "action": action,
            "location_mode": loc_mode.strip(),
            "wifi_scan_always_enabled": wifi_scan.strip(),
            "gms_persistent_running": bool(gms_pid.strip()),
            "gms_persistent_pids": gms_pid.strip().split() if gms_pid.strip() else [],
            "providers_summary": _extract_location_providers(dump_out),
        }

    if action == "logcat_tail":
        proc, out, timed_out = run_shell(["logcat", "-d", "-t", str(parsed["lines"])])
        lines_list = out.splitlines()
        if filter_text and filter_text.strip():
            needle = filter_text.strip().casefold()
            lines_list = [ln for ln in lines_list if needle in ln.casefold()]
        joined, truncated = _truncate_text("\n".join(lines_list), MAX_OUTPUT_CHARS)
        return {
            "status": "timeout" if timed_out else ("success" if getattr(proc, "returncode", 0) == 0 else "error"),
            "target": target_serial,
            "action": action,
            "lines_returned": len(lines_list),
            "truncated": truncated,
            "output": joined,
        }

    if action == "screenshot":
        out_dir = sandbox_dir or DEFAULT_SANDBOX_DIR
        out_dir.mkdir(parents=True, exist_ok=True)
        ip_safe = re.sub(r"[^A-Za-z0-9_]", "_", target_serial)
        local_path = out_dir / f"playbox_{ip_safe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        remote_tmp = "/data/local/tmp/jarvis_playbox_cap.png"

        cap_proc, cap_out, cap_to = run_shell(["screencap", "-p", remote_tmp], timeout=20)
        if cap_to or getattr(cap_proc, "returncode", 0) != 0:
            return {
                "status": "timeout" if cap_to else "error",
                "target": target_serial,
                "action": action,
                "output": cap_out,
            }

        pull_proc, pull_out, pull_to = run_cmd([adb_bin, "-s", target_serial, "pull", remote_tmp, str(local_path)], timeout=30)
        run_shell(["rm", "-f", remote_tmp], timeout=10)
        return {
            "status": "timeout" if pull_to else ("success" if getattr(pull_proc, "returncode", 0) == 0 else "error"),
            "target": target_serial,
            "action": action,
            "file_path": str(local_path),
            "output": pull_out,
        }

    if action == "start_app":
        pkg = parsed["package"]
        proc, out, timed_out = run_shell(["monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1"])
        return {
            "status": "timeout" if timed_out else ("success" if getattr(proc, "returncode", 0) == 0 else "error"),
            "target": target_serial,
            "action": action,
            "package": pkg,
            "output": out,
        }

    if action == "stop_app":
        pkg = parsed["package"]
        proc, out, timed_out = run_shell(["am", "force-stop", pkg])
        return {
            "status": "timeout" if timed_out else ("success" if getattr(proc, "returncode", 0) == 0 else "error"),
            "target": target_serial,
            "action": action,
            "package": pkg,
            "output": out,
        }

    if action == "restart_app":
        pkg = parsed["package"]
        stop_proc, stop_out, stop_to = run_shell(["am", "force-stop", pkg])
        start_proc, start_out, start_to = run_shell(["monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1"])
        ok = getattr(stop_proc, "returncode", 0) == 0 and getattr(start_proc, "returncode", 0) == 0
        return {
            "status": "timeout" if (stop_to or start_to) else ("success" if ok else "error"),
            "target": target_serial,
            "action": action,
            "package": pkg,
            "output": "\n".join(p for p in (stop_out, start_out) if p),
        }

    if action == "clear_app_data":
        pkg = parsed["package"]
        proc, out, timed_out = run_shell(["pm", "clear", pkg])
        return {
            "status": "timeout" if timed_out else ("success" if getattr(proc, "returncode", 0) == 0 else "error"),
            "target": target_serial,
            "action": action,
            "package": pkg,
            "output": out,
        }

    if action == "grant_permission":
        pkg = parsed["package"]
        perm = parsed["permission"]
        proc, out, timed_out = run_shell(["pm", "grant", pkg, perm])
        return {
            "status": "timeout" if timed_out else ("success" if getattr(proc, "returncode", 0) == 0 else "error"),
            "target": target_serial,
            "action": action,
            "package": pkg,
            "permission": perm,
            "output": out,
        }

    if action == "open_url":
        proc, out, timed_out = run_shell(["am", "start", "-a", "android.intent.action.VIEW", "-d", parsed["url"]])
        return {
            "status": "timeout" if timed_out else ("success" if getattr(proc, "returncode", 0) == 0 else "error"),
            "target": target_serial,
            "action": action,
            "url": parsed["url"],
            "output": out,
        }

    if action == "keyevent":
        proc, out, timed_out = run_shell(["input", "keyevent", parsed["keycode"]])
        return {
            "status": "timeout" if timed_out else ("success" if getattr(proc, "returncode", 0) == 0 else "error"),
            "target": target_serial,
            "action": action,
            "keycode": parsed["keycode"],
            "output": out,
        }

    if action == "install_apk":
        proc, out, timed_out = run_cmd([adb_bin, "-s", target_serial, "install", "-r", parsed["apk_path"]], timeout=120)
        return {
            "status": "timeout" if timed_out else ("success" if getattr(proc, "returncode", 0) == 0 else "error"),
            "target": target_serial,
            "action": action,
            "apk_path": parsed["apk_path"],
            "output": out,
        }

    if action == "reboot":
        proc, out, timed_out = run_cmd([adb_bin, "-s", target_serial, "reboot"], timeout=15)
        return {
            "status": "timeout" if timed_out else ("success" if getattr(proc, "returncode", 0) == 0 else "error"),
            "target": target_serial,
            "action": action,
            "output": out or "ส่งคำสั่งรีบูตแล้ว",
        }

    # action == "shell"
    proc, out, timed_out = run_shell(parsed["tokens"], timeout=20)
    capped_out, truncated = _truncate_text(out, MAX_OUTPUT_CHARS)
    return {
        "status": "timeout" if timed_out else ("success" if getattr(proc, "returncode", 0) == 0 else "error"),
        "target": target_serial,
        "action": action,
        "command": command,
        "is_write": parsed["is_write"],
        "truncated": truncated,
        "output": capped_out,
    }
