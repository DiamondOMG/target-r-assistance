from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable, Literal

TVAction = Literal[
    "status",
    "open_url",
    "open_dsloader",
    "restart_dsloader",
    "stop_dsloader",
    "hdmi1",
    "hdmi2",
    "home",
    "back",
    "wake",
    "lock_adb_port",
]

DSLOADER_PACKAGE = "net.targetr.stacks.central"


def _get_tv_registry() -> dict[str, dict[str, Any]]:
    return {
        "sharp_left": {
            "id": "sharp_left",
            "name": "Sharp Smart TV (ตัวซ้าย / จอ 2)",
            "mac_address": "A4AE125D42DE",
            "tailscale_ip": os.getenv("TV_SHARP_LEFT_IP", "100.120.41.101").strip(),
            "tailscale_domain": "sharp-left.tail6bc567.ts.net",
            "adb_port": 5555,
            "aliases": {
                "sharp_left", "sharp-left", "left", "ซ้าย", "จอซ้าย",
                "จอ2", "จอ 2", "tv2", "display2", "sharp2", "sharp_2",
                "a4ae125d42de", "android-tv",
            },
        },
        "sharp_right": {
            "id": "sharp_right",
            "name": "Sharp Smart TV (ตัวขวา / จอ 3)",
            "mac_address": os.getenv("TV_SHARP_RIGHT_MAC", "A4AE125D4ACC").strip(),
            "tailscale_ip": os.getenv("TV_SHARP_RIGHT_IP", "100.75.151.107").strip(),
            "tailscale_domain": "sharp-right.tail6bc567.ts.net",
            "adb_port": 5555,
            "aliases": {
                "sharp_right", "sharp-right", "right", "ขวา", "จอขวา",
                "จอ3", "จอ 3", "tv3", "display3", "sharp3", "sharp_3",
                "a4ae125d4acc",
            },
        },
    }


def resolve_tv_target(tv: str) -> dict[str, Any]:
    key = (tv or "").strip().casefold()
    registry = _get_tv_registry()
    for info in registry.values():
        if key in info["aliases"]:
            if not info["tailscale_ip"]:
                raise ValueError(
                    f"TV_NOT_CONFIGURED: '{info['name']}' ยังไม่ได้ตั้งค่า Tailscale IP "
                    f"(กรุณาลง Tailscale บนทีวีหรือตั้งค่า TV_SHARP_RIGHT_IP ใน .env)"
                )
            return info

    # Allow direct IP or host:port input
    if re.fullmatch(r"[A-Za-z0-9.\-]+(:\d+)?", (tv or "").strip()):
        raw = tv.strip()
        ip_part, _, port_part = raw.partition(":")
        return {
            "id": raw,
            "name": f"Custom TV ({ip_part})",
            "mac_address": "",
            "tailscale_ip": ip_part,
            "tailscale_domain": "",
            "adb_port": int(port_part) if port_part else 5555,
        }

    raise ValueError(
        f"INVALID_INPUT: ไม่รู้จักทีวี '{tv}' (ใช้ 'sharp_left', 'sharp_right', หรือ Tailscale IP)"
    )


def find_adb_binary() -> str:
    env_adb = os.getenv("ADB_PATH", "").strip()
    if env_adb and Path(env_adb).is_file():
        return env_adb

    found = shutil.which("adb")
    if found:
        return found

    local_appdata = os.getenv("LOCALAPPDATA", "")
    if local_appdata:
        sdk_adb = Path(local_appdata) / "Android" / "Sdk" / "platform-tools" / "adb.exe"
        if sdk_adb.is_file():
            return str(sdk_adb)

    raise RuntimeError(
        "ADB_NOT_FOUND: ไม่พบคำสั่ง adb ในเครื่อง กรุณาติดตั้ง Android Platform Tools หรือกำหนด ADB_PATH"
    )


def _default_adb_runner(cmd: list[str], timeout: int = 15) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)


def _validate_url(url: str | None) -> str:
    clean = (url or "").strip()
    if not clean or not (clean.startswith("http://") or clean.startswith("https://")):
        raise ValueError("INVALID_INPUT: action 'open_url' requires a valid http:// or https:// URL")
    if any(ch in clean for ch in (" ", "\n", "\r", ";", "&", "|", "`", "$")):
        raise ValueError("INVALID_INPUT: URL contains invalid whitespace or shell characters")
    return clean


def tv_control(
    tv: str = "sharp_left",
    action: TVAction = "status",
    url: str | None = None,
    adb_runner: Callable[[list[str]], Any] | None = None,
    adb_path: str | None = None,
) -> dict[str, Any]:
    """ควบคุมจอ Sharp Smart TV ผ่าน ADB over Tailscale VPN"""
    target_info = resolve_tv_target(tv)
    adb_bin = adb_path or find_adb_binary()
    runner = adb_runner or _default_adb_runner

    ip = target_info["tailscale_ip"]
    port = target_info["adb_port"]
    target_serial = f"{ip}:{port}"

    # Validate URL early if open_url
    validated_url = _validate_url(url) if action == "open_url" else None

    # 1. Connect via ADB over Tailscale
    conn_proc = runner([adb_bin, "connect", target_serial])
    conn_out = ((conn_proc.stdout or "") + "\n" + (conn_proc.stderr or "")).strip()

    if "unauthorized" in conn_out.casefold():
        return {
            "status": "unauthorized",
            "tv": target_info["name"],
            "target": target_serial,
            "action": action,
            "output": conn_out,
            "hint": "ทีวีกำลังรอการกด Allow USB/Network Debugging บนหน้าจอ (หรือต้องใช้ไฟล์ adbkey ของทีม)",
        }

    # Build ADB command(s) for requested action
    commands: list[list[str]] = []
    if action == "status":
        commands.append([adb_bin, "devices"])
    elif action == "open_url":
        # Force-stop DS Loader first so its auto-start does not steal focus back from the browser
        commands.append([adb_bin, "-s", target_serial, "shell", "am", "force-stop", DSLOADER_PACKAGE])
        commands.append(
            [adb_bin, "-s", target_serial, "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", validated_url]
        )
    elif action == "open_dsloader":
        commands.append(
            [adb_bin, "-s", target_serial, "shell", "monkey", "-p", DSLOADER_PACKAGE, "-c", "android.intent.category.LAUNCHER", "1"]
        )
    elif action == "restart_dsloader":
        commands.append([adb_bin, "-s", target_serial, "shell", "am", "force-stop", DSLOADER_PACKAGE])
        commands.append(
            [adb_bin, "-s", target_serial, "shell", "monkey", "-p", DSLOADER_PACKAGE, "-c", "android.intent.category.LAUNCHER", "1"]
        )
    elif action == "stop_dsloader":
        commands.append([adb_bin, "-s", target_serial, "shell", "am", "force-stop", DSLOADER_PACKAGE])
    elif action == "hdmi1":
        commands.append(
            [adb_bin, "-s", target_serial, "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", "content://android.media.tv/passthrough/passthrough_hdmi1"]
        )
    elif action == "hdmi2":
        commands.append(
            [adb_bin, "-s", target_serial, "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", "content://android.media.tv/passthrough/passthrough_hdmi2"]
        )
    elif action == "home":
        commands.append([adb_bin, "-s", target_serial, "shell", "input", "keyevent", "KEYCODE_HOME"])
    elif action == "back":
        commands.append([adb_bin, "-s", target_serial, "shell", "input", "keyevent", "KEYCODE_BACK"])
    elif action == "wake":
        commands.append([adb_bin, "-s", target_serial, "shell", "input", "keyevent", "KEYCODE_WAKEUP"])
    elif action == "lock_adb_port":
        commands.append(
            [adb_bin, "-s", target_serial, "shell", "setprop persist.adb.tcp.port 5555; setprop service.adb.tcp.port 5555"]
        )
    else:
        raise ValueError(f"INVALID_INPUT: unsupported action '{action}'")

    outputs: list[str] = []
    success = True
    for cmd in commands:
        proc = runner(cmd)
        out_text = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
        if out_text:
            outputs.append(out_text)
        if getattr(proc, "returncode", 0) != 0:
            success = False

    combined_out = "\n".join(outputs)
    if "unauthorized" in combined_out.casefold():
        status_str = "unauthorized"
    elif "offline" in combined_out.casefold() or "not found" in combined_out.casefold() or not success:
        status_str = "error"
    else:
        status_str = "success"

    return {
        "status": status_str,
        "tv": target_info["name"],
        "mac_address": target_info["mac_address"],
        "target": target_serial,
        "action": action,
        "url": validated_url,
        "connect_output": conn_out,
        "output": combined_out,
    }
