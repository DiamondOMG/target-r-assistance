from pathlib import Path

import pytest

from jarvis_mcp.stuck_screens import analyze_stuck_screens


def _make_screen_row(
    screen_id: str,
    retailer: str,
    store_location: str,
    loader_ms: int,
    player_ms: int,
    label: str = "",
    stc: str = "TM001",
    recent_start_count: int = 1,
    mem_free: int = 5 * 1024 * 1024,
) -> dict:
    return {
        "screenId": screen_id,
        "retailer": retailer,
        "storeLocation": store_location,
        "label": label or f"{retailer}-{store_location}",
        "data": {
            "id": screen_id,
            "data": {
                "screenId": screen_id,
                "retailer": retailer,
                "storeLocation": store_location,
                "label": label or f"{retailer}-{store_location}",
                "STC": stc,
                "hardwareModel": "HK1 RBOX K8-V",
                "activePlayer": "android-player-2023-06-02.apk",
                "lastLoaderCommsMillis": str(loader_ms),
                "lastPlayerCommsMillis": str(player_ms) if player_ms > 0 else "",
                "recentStartCount": str(recent_start_count),
                "memFree": str(mem_free),
                "ACT_AnyDesk": "123 456 789",
            },
        },
    }


def test_analyze_stuck_screens_filters_and_sorts(tmp_path: Path):
    now_ms = 1_794_900_000_000
    minute_ms = 60_000

    rows = [
        # Stuck 2 hours (Loader online)
        _make_screen_row("SCR_STUCK_2H", "Tops", "TopsDigital-Chidlom", now_ms, now_ms - 120 * minute_ms, recent_start_count=4),
        # Stuck 5 hours (Loader online 2m ago -> should sort first)
        _make_screen_row("SCR_STUCK_5H", "Big C", "Bangphlee", now_ms - 2 * minute_ms, now_ms - 302 * minute_ms, recent_start_count=10),
        # Healthy (Loader & Player 1m diff)
        _make_screen_row("SCR_OK", "Tops", "TopsDigital-Ladprao", now_ms, now_ms - 1 * minute_ms),
        # Completely offline (Loader 30m ago > 10m window)
        _make_screen_row("SCR_OFFLINE", "Tops", "TopsDigital-Offline", now_ms - 30 * minute_ms, now_ms - 180 * minute_ms),
    ]

    res = analyze_stuck_screens(
        rows=rows,
        min_stuck_minutes=60,
        loader_online_window_minutes=10,
        output_dir=tmp_path,
    )

    assert res["total_stuck"] == 2
    assert res["returned"] == 2
    assert [s["screenId"] for s in res["screens"]] == ["SCR_STUCK_5H", "SCR_STUCK_2H"]
    assert res["screens"][0]["stuck_minutes"] == 300
    assert res["screens"][0]["memFreeMB"] == 5.0
    assert Path(res["csv_path"]).exists()


def test_analyze_stuck_screens_retailer_and_store_query(tmp_path: Path):
    now_ms = 1_794_900_000_000
    minute_ms = 60_000

    rows = [
        _make_screen_row("SCR_1", "Tops", "TopsDigital-PWBChiangmai", now_ms, now_ms - 120 * minute_ms),
        _make_screen_row("SCR_2", "Big C", "Bangphlee", now_ms, now_ms - 180 * minute_ms),
    ]

    res_tops = analyze_stuck_screens(rows=rows, retailer="tops", output_dir=tmp_path)
    assert res_tops["total_stuck"] == 1
    assert res_tops["screens"][0]["screenId"] == "SCR_1"

    res_store = analyze_stuck_screens(rows=rows, store_query="chiangmai", output_dir=tmp_path)
    assert res_store["total_stuck"] == 1
    assert res_store["screens"][0]["screenId"] == "SCR_1"


def test_analyze_stuck_screens_invalid_input(tmp_path: Path):
    with pytest.raises(ValueError, match="INVALID_INPUT"):
        analyze_stuck_screens(rows=[], min_stuck_minutes=-1, output_dir=tmp_path)

    with pytest.raises(ValueError, match="INVALID_INPUT"):
        analyze_stuck_screens(rows=[], loader_online_window_minutes=0, output_dir=tmp_path)
