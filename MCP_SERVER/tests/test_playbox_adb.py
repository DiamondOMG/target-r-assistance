import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from jarvis_mcp.playbox_adb import (
    parse_playbox_target,
    playbox_adb,
    validate_safe_shell_command,
)


def _ok(stdout: str = "", stderr: str = "") -> SimpleNamespace:
    return SimpleNamespace(returncode=0, stdout=stdout, stderr=stderr)


def test_parse_playbox_target_variants():
    assert parse_playbox_target("192.168.1.105") == "192.168.1.105:5555"
    assert parse_playbox_target("192.168.1.105", port=5556) == "192.168.1.105:5556"
    assert parse_playbox_target("192.168.1.105:5558") == "192.168.1.105:5558"
    assert parse_playbox_target("playbox-box1.local") == "playbox-box1.local:5555"
    assert parse_playbox_target("::1") == "[::1]:5555"
    assert parse_playbox_target("[::1]:5560") == "[::1]:5560"

    for bad in ("", "192.168.1.1; rm -rf", "192.168.1.1 && whoami", "192.168.1.1:abc", "999.999.999.999:5555:1"):
        with pytest.raises(ValueError, match="INVALID_INPUT"):
            parse_playbox_target(bad)

    with pytest.raises(ValueError, match="INVALID_INPUT"):
        parse_playbox_target("192.168.1.105", port=70000)


def test_connect_states_and_disconnect():
    cmds: list[list[str]] = []

    def connected_runner(cmd: list[str]):
        cmds.append(cmd)
        if cmd[1] == "connect":
            return _ok("connected to 192.168.1.105:5555")
        if "get-state" in cmd:
            return _ok("device\n")
        return _ok()

    res = playbox_adb("192.168.1.105", action="connect", adb_runner=connected_runner, adb_path="adb")
    assert res["status"] == "connected"
    assert res["target"] == "192.168.1.105:5555"
    assert res["device_state"] == "device"
    assert cmds[0] == ["adb", "connect", "192.168.1.105:5555"]
    assert cmds[1] == ["adb", "-s", "192.168.1.105:5555", "get-state"]

    # Unauthorized returned from connect directly
    def unauth_connect_runner(cmd: list[str]):
        return _ok("failed to authenticate to 192.168.1.105:5555 (unauthorized)")

    res_u1 = playbox_adb("192.168.1.105", action="connect", adb_runner=unauth_connect_runner, adb_path="adb")
    assert res_u1["status"] == "unauthorized"
    assert "Allow" in res_u1["hint"]

    # Unauthorized caught by get-state even when adb connect exits 0 with "connected"
    def unauth_state_runner(cmd: list[str]):
        if cmd[1] == "connect":
            return _ok("connected to 192.168.1.105:5555")
        return SimpleNamespace(returncode=1, stdout="", stderr="error: device unauthorized.")

    res_u2 = playbox_adb("192.168.1.105", action="device_info", adb_runner=unauth_state_runner, adb_path="adb")
    assert res_u2["status"] == "unauthorized"
    assert "Allow" in res_u2["hint"]

    # Unreachable
    def unreachable_runner(cmd: list[str]):
        return SimpleNamespace(returncode=1, stdout="cannot connect to 192.168.1.105:5555: Connection refused", stderr="")

    res_unreach = playbox_adb("192.168.1.105", action="connect", adb_runner=unreachable_runner, adb_path="adb")
    assert res_unreach["status"] == "unreachable"
    assert "MTP" in res_unreach["hint"]

    # Timeout
    def timeout_runner(cmd: list[str], timeout: int = 15):
        raise subprocess.TimeoutExpired(cmd=cmd, timeout=timeout)

    res_to = playbox_adb("192.168.1.105", action="connect", adb_runner=timeout_runner, adb_path="adb")
    assert res_to["status"] == "timeout"

    # Disconnect
    disc_cmds: list[list[str]] = []

    def disc_runner(cmd: list[str]):
        disc_cmds.append(cmd)
        return _ok("disconnected 192.168.1.105:5555")

    res_disc = playbox_adb("192.168.1.105", action="disconnect", adb_runner=disc_runner, adb_path="adb")
    assert res_disc["status"] == "success"
    assert disc_cmds == [["adb", "disconnect", "192.168.1.105:5555"]]


def _make_playbox_mock(responses: dict[tuple[str, ...], SimpleNamespace] | None = None):
    recorded: list[list[str]] = []
    mapping = responses or {}

    def runner(cmd: list[str]):
        recorded.append(cmd)
        if cmd[1] == "connect":
            return _ok("connected to 192.168.1.105:5555")
        if "get-state" in cmd:
            return _ok("device")
        shell_idx = cmd.index("shell") + 1 if "shell" in cmd else 3
        tail = tuple(cmd[shell_idx:])
        for key, resp in mapping.items():
            if tail == key:
                return resp
        return _ok("")

    return runner, recorded


def test_diagnostics_actions():
    mapping = {
        ("getprop",): _ok(
            "[ro.product.model]: [HK1 RBOX K8]\n"
            "[ro.product.manufacturer]: [Rockchip]\n"
            "[ro.build.version.release]: [13]\n"
            "[ro.build.version.sdk]: [33]\n"
            "[persist.sys.timezone]: [Asia/Bangkok]\n"
        ),
        ("date",): _ok("Thu Nov 19 11:15:00 +07 2026"),
        ("wm", "size"): _ok("Physical size: 1920x1080"),
        ("wm", "density"): _ok("Physical density: 320"),
        ("cat", "/proc/meminfo"): _ok("MemTotal:        3910000 kB\nMemAvailable:    1200000 kB\n"),
        ("df", "-h", "/data"): _ok("Filesystem Size Used Avail Use% Mounted on\n/dev/block 23G 3G 20G 13% /data"),
        ("dumpsys", "webviewupdate"): _ok("Current WebView package (com.android.webview, 109.0.5414.123)\nFallback logic enabled: false"),
        ("pidof", "net.targetr.stacks.central"): _ok("4210"),
        ("dumpsys", "package", "net.targetr.stacks.central"): _ok(
            "Package [net.targetr.stacks.central]\n"
            "  versionCode=20230602 minSdk=21 targetSdk=33\n"
            "  versionName=2023-06-02\n"
            "  android.permission.ACCESS_FINE_LOCATION: granted=true\n"
        ),
        ("pm", "path", "net.targetr.stacks.central"): _ok("package:/data/app/net.targetr.stacks.central/base.apk"),
        ("getprop", "ro.product.model"): _ok("HK1 RBOX K8"),
        ("settings", "get", "secure", "location_mode"): _ok("3"),
        ("settings", "get", "global", "wifi_scan_always_enabled"): _ok("1"),
        ("pidof", "com.google.android.gms.persistent"): _ok("1842"),
        ("dumpsys", "location"): _ok(
            "    gps provider:\n      enabled=true\n"
            "    network provider:\n      enabled=true\n"
        ),
        ("pm", "list", "packages"): _ok("\n".join(f"package:com.example.app{i:03d}" for i in range(120))),
        ("pm", "list", "packages", "-3"): _ok("package:net.targetr.stacks.central\npackage:com.example.gpsbridge"),
        ("logcat", "-d", "-t", "20"): _ok("line1 normal\nline2 TargetR error\nline3 TargetR ok"),
    }
    runner, _ = _make_playbox_mock(mapping)

    info = playbox_adb("192.168.1.105", action="device_info", adb_runner=runner, adb_path="adb")
    assert info["status"] == "success"
    assert info["device_info"]["model"] == "HK1 RBOX K8"
    assert info["device_info"]["dsloader"]["running"] is True
    assert info["device_info"]["webview"]["package"] == "com.android.webview"

    prop1 = playbox_adb("192.168.1.105", action="get_prop", key="ro.product.model", adb_runner=runner, adb_path="adb")
    assert prop1["value"] == "HK1 RBOX K8"

    prop_all = playbox_adb("192.168.1.105", action="get_prop", adb_runner=runner, adb_path="adb")
    assert prop_all["properties"]["ro.build.version.release"] == "13"

    setting = playbox_adb("192.168.1.105", action="get_setting", namespace="secure", key="location_mode", adb_runner=runner, adb_path="adb")
    assert setting["value"] == "3"

    wv = playbox_adb("192.168.1.105", action="check_webview", adb_runner=runner, adb_path="adb")
    assert wv["current_webview"]["version"] == "109.0.5414.123"

    loc = playbox_adb("192.168.1.105", action="check_location", adb_runner=runner, adb_path="adb")
    assert loc["location_mode"] == "3"
    assert loc["gms_persistent_running"] is True
    assert any("gps provider:" in line for line in loc["providers_summary"])

    app = playbox_adb("192.168.1.105", action="check_app", adb_runner=runner, adb_path="adb")
    assert app["installed"] is True
    assert app["running"] is True
    assert app["version_name"] == "2023-06-02"

    pkgs_all = playbox_adb("192.168.1.105", action="list_packages", adb_runner=runner, adb_path="adb")
    assert pkgs_all["total_matched"] == 120
    assert pkgs_all["returned"] == 100
    assert pkgs_all["truncated"] is True

    pkgs_filtered = playbox_adb("192.168.1.105", action="list_packages", value="third_party", filter_text="targetr", adb_runner=runner, adb_path="adb")
    assert pkgs_filtered["packages"] == ["net.targetr.stacks.central"]

    logs = playbox_adb("192.168.1.105", action="logcat_tail", lines=20, filter_text="targetr", adb_runner=runner, adb_path="adb")
    assert logs["lines_returned"] == 2
    assert "line1" not in logs["output"]

    with pytest.raises(ValueError, match="INVALID_INPUT"):
        playbox_adb("192.168.1.105", action="logcat_tail", lines=500, adb_runner=runner, adb_path="adb")


def test_configuration_and_app_actions():
    state = {
        "setting_val": "0",
        "prop_val": "0",
        "tz": "UTC",
    }
    recorded: list[list[str]] = []

    def runner(cmd: list[str]):
        recorded.append(cmd)
        if cmd[1] == "connect":
            return _ok("connected to 192.168.1.105:5555")
        if "get-state" in cmd:
            return _ok("device")
        args = cmd[4:]
        if args == ["settings", "get", "global", "wifi_scan_always_enabled"]:
            return _ok(state["setting_val"])
        if args[:4] == ["settings", "put", "global", "wifi_scan_always_enabled"]:
            state["setting_val"] = args[4]
            return _ok()
        if args == ["getprop", "persist.adb.tcp.port"]:
            return _ok(state["prop_val"])
        if args[:2] == ["setprop", "persist.adb.tcp.port"]:
            # Simulate non-root failing to persist
            return _ok()
        if args == ["getprop", "persist.sys.timezone"]:
            return _ok(state["tz"])
        if args[:2] == ["setprop", "persist.sys.timezone"]:
            state["tz"] = args[2]
            return _ok()
        if args == ["date"]:
            return _ok("Thu Nov 19 11:20:00 +07 2026")
        return _ok("Success")

    res_set = playbox_adb(
        "192.168.1.105",
        action="set_setting",
        namespace="global",
        key="wifi_scan_always_enabled",
        value="1",
        adb_runner=runner,
        adb_path="adb",
    )
    assert res_set["previous_value"] == "0"
    assert res_set["new_value"] == "1"
    assert res_set["changed"] is True

    res_prop = playbox_adb(
        "192.168.1.105",
        action="set_prop",
        key="persist.adb.tcp.port",
        value="5555",
        adb_runner=runner,
        adb_path="adb",
    )
    assert "root" in res_prop["note"]

    res_tz = playbox_adb(
        "192.168.1.105",
        action="set_timezone",
        value="Asia/Bangkok",
        adb_runner=runner,
        adb_path="adb",
    )
    assert res_tz["previous_timezone"] == "UTC"
    assert res_tz["new_timezone"] == "Asia/Bangkok"

    with pytest.raises(ValueError, match="INVALID_INPUT"):
        playbox_adb("192.168.1.105", action="set_timezone", value="BadTimezone", adb_runner=runner, adb_path="adb")

    res_perm = playbox_adb(
        "192.168.1.105",
        action="grant_permission",
        package="net.targetr.stacks.central",
        permission="android.permission.ACCESS_FINE_LOCATION",
        adb_runner=runner,
        adb_path="adb",
    )
    assert res_perm["status"] == "success"

    for act in ("start_app", "stop_app", "restart_app"):
        r = playbox_adb("192.168.1.105", action=act, adb_runner=runner, adb_path="adb")
        assert r["status"] == "success"

    r_url = playbox_adb("192.168.1.105", action="open_url", url="https://tops.actx.digital", adb_runner=runner, adb_path="adb")
    assert r_url["status"] == "success"

    r_key = playbox_adb("192.168.1.105", action="keyevent", value="home", adb_runner=runner, adb_path="adb")
    assert r_key["keycode"] == "KEYCODE_HOME"


def test_screenshot_saves_to_sandbox_without_exec_out(tmp_path: Path):
    recorded: list[list[str]] = []

    def runner(cmd: list[str], timeout: int = 15):
        recorded.append(cmd)
        if cmd[1] == "connect":
            return _ok("connected to 192.168.1.105:5555")
        if "get-state" in cmd:
            return _ok("device")
        if "pull" in cmd:
            Path(cmd[5]).write_bytes(b"\x89PNG\r\n\x1a\n")
            return _ok("1 file pulled.")
        return _ok()

    res = playbox_adb(
        "192.168.1.105",
        action="screenshot",
        adb_runner=runner,
        adb_path="adb",
        sandbox_dir=tmp_path,
    )
    assert res["status"] == "success"
    saved = Path(res["file_path"])
    assert saved.parent == tmp_path
    assert saved.exists()
    assert not any("exec-out" in c for c in recorded)
    assert any("screencap" in c for c in recorded)
    assert any("pull" in c for c in recorded)
    assert any("rm" in c and "/data/local/tmp/jarvis_playbox_cap.png" in c for c in recorded)


def test_confirmation_gates(tmp_path: Path):
    runner, recorded = _make_playbox_mock()

    # reboot
    r_rb1 = playbox_adb("192.168.1.105", action="reboot", confirm=False, adb_runner=runner, adb_path="adb")
    assert r_rb1["status"] == "confirmation_required"
    assert recorded == []

    r_rb2 = playbox_adb("192.168.1.105", action="reboot", confirm=True, adb_runner=runner, adb_path="adb")
    assert r_rb2["status"] == "success"
    assert any("reboot" in c for c in recorded)

    # clear_app_data requires explicit package and confirm=True
    with pytest.raises(ValueError, match="INVALID_INPUT"):
        playbox_adb("192.168.1.105", action="clear_app_data", confirm=True, adb_runner=runner, adb_path="adb")

    r_clr1 = playbox_adb("192.168.1.105", action="clear_app_data", package="com.example.app", confirm=False, adb_runner=runner, adb_path="adb")
    assert r_clr1["status"] == "confirmation_required"

    r_clr2 = playbox_adb("192.168.1.105", action="clear_app_data", package="com.example.app", confirm=True, adb_runner=runner, adb_path="adb")
    assert r_clr2["status"] == "success"

    # install_apk
    fake_apk = tmp_path / "app-debug.apk"
    fake_apk.write_bytes(b"PK")
    r_apk1 = playbox_adb("192.168.1.105", action="install_apk", apk_path=str(fake_apk), confirm=False, adb_runner=runner, adb_path="adb")
    assert r_apk1["status"] == "confirmation_required"

    r_apk2 = playbox_adb("192.168.1.105", action="install_apk", apk_path=str(fake_apk), confirm=True, adb_runner=runner, adb_path="adb")
    assert r_apk2["status"] == "success"
    assert any("install" in c for c in recorded)


def test_shell_security_allowlist_and_blocklist():
    tokens, is_write = validate_safe_shell_command("getprop ro.product.model")
    assert tokens == ["getprop", "ro.product.model"]
    assert is_write is False

    tokens, is_write = validate_safe_shell_command("wm size")
    assert is_write is False

    tokens, is_write = validate_safe_shell_command("wm size 1920x1080")
    assert is_write is True

    for forbidden in (
        "rm -rf /data/local/tmp/*",
        "/system/bin/rm /data/file",
        "dd if=/dev/zero of=/dev/block/sda",
        "su -c id",
        "reboot",
        "getprop ro.product.model; whoami",
        "getprop ro.product.model && id",
        "dumpsys location | grep gps",
        "pm clear com.example.app",
    ):
        with pytest.raises(ValueError, match="FORBIDDEN_COMMAND"):
            validate_safe_shell_command(forbidden)

    with pytest.raises(ValueError, match="UNSUPPORTED_COMMAND"):
        validate_safe_shell_command("unknownbinary --flag")

    runner, recorded = _make_playbox_mock({("df", "-h"): _ok("/data 20G")})
    res_ro = playbox_adb("192.168.1.105", action="shell", command="df -h", adb_runner=runner, adb_path="adb")
    assert res_ro["status"] == "success"
    assert res_ro["is_write"] is False

    res_wr1 = playbox_adb("192.168.1.105", action="shell", command="input keyevent KEYCODE_HOME", confirm=False, adb_runner=runner, adb_path="adb")
    assert res_wr1["status"] == "confirmation_required"

    res_wr2 = playbox_adb("192.168.1.105", action="shell", command="input keyevent KEYCODE_HOME", confirm=True, adb_runner=runner, adb_path="adb")
    assert res_wr2["status"] == "success"
    assert res_wr2["is_write"] is True
