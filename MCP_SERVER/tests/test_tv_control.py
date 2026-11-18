from types import SimpleNamespace

import pytest

from jarvis_mcp.tv_control import resolve_tv_target, tv_control


def test_resolve_tv_target_left_aliases():
    for alias in ("sharp_left", "sharp-left", "left", "ซ้าย", "จอซ้าย", "จอ2", "จอ 2", "A4AE125D42DE", "android-tv"):
        info = resolve_tv_target(alias)
        assert info["mac_address"] == "A4AE125D42DE"
        assert info["tailscale_ip"] == "100.120.41.101"
        assert info["adb_port"] == 5555


def test_resolve_tv_target_right_defaults_and_override(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("TV_SHARP_RIGHT_IP", raising=False)
    for alias in ("sharp_right", "sharp-right", "right", "ขวา", "จอขวา", "จอ3", "จอ 3", "A4AE125D4ACC"):
        info = resolve_tv_target(alias)
        assert info["mac_address"] == "A4AE125D4ACC"
        assert info["tailscale_ip"] == "100.75.151.107"

    monkeypatch.setenv("TV_SHARP_RIGHT_IP", "100.120.41.102")
    info_override = resolve_tv_target("ขวา")
    assert info_override["tailscale_ip"] == "100.120.41.102"


def test_tv_control_open_url_and_dsloader():
    recorded_cmds: list[list[str]] = []

    def fake_runner(cmd: list[str]):
        recorded_cmds.append(cmd)
        if cmd[1] == "connect":
            return SimpleNamespace(returncode=0, stdout="connected to 100.120.41.101:5555", stderr="")
        return SimpleNamespace(returncode=0, stdout="Starting: Intent { ... }", stderr="")

    res = tv_control(
        tv="sharp_left",
        action="open_url",
        url="https://tops.actx.digital/screen-monitor",
        adb_runner=fake_runner,
        adb_path="adb",
    )
    assert res["status"] == "success"
    assert res["target"] == "100.120.41.101:5555"
    assert recorded_cmds[0] == ["adb", "connect", "100.120.41.101:5555"]
    assert "force-stop" in recorded_cmds[1]
    assert "https://tops.actx.digital/screen-monitor" in recorded_cmds[2]

    recorded_cmds.clear()
    res_stop = tv_control(
        tv="sharp_left",
        action="stop_dsloader",
        adb_runner=fake_runner,
        adb_path="adb",
    )
    assert res_stop["status"] == "success"
    assert len(recorded_cmds) == 2  # connect + force-stop
    assert "force-stop" in recorded_cmds[1]

    recorded_cmds.clear()
    res_fs = tv_control(
        tv="sharp_right",
        action="fullscreen",
        adb_runner=fake_runner,
        adb_path="adb",
    )
    assert res_fs["status"] == "success"
    assert any("immersive.full" in " ".join(cmd) for cmd in recorded_cmds)

    recorded_cmds.clear()
    res_ds = tv_control(
        tv="ซ้าย",
        action="restart_dsloader",
        adb_runner=fake_runner,
        adb_path="adb",
    )
    assert res_ds["status"] == "success"
    assert len(recorded_cmds) == 3  # connect + force-stop + monkey launch


def test_tv_control_validation_and_unauthorized():
    with pytest.raises(ValueError, match="INVALID_INPUT"):
        tv_control(tv="sharp_left", action="open_url", url="ftp://invalid", adb_path="adb")

    def unauth_runner(cmd: list[str]):
        return SimpleNamespace(returncode=0, stdout="failed to authenticate to 100.120.41.101:5555 (unauthorized)", stderr="")

    res = tv_control(tv="sharp_left", action="status", adb_runner=unauth_runner, adb_path="adb")
    assert res["status"] == "unauthorized"
