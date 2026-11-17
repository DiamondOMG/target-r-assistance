from __future__ import annotations

import csv
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlparse

import httpx

BKK_TZ = timezone(timedelta(hours=7))


def _default_sandbox_dir() -> Path:
    project_root = Path(__file__).resolve().parents[2]
    sandbox_dir = project_root / "SANDBOX"
    sandbox_dir.mkdir(parents=True, exist_ok=True)
    return sandbox_dir


def _to_int(value: Any) -> int:
    if value is None or value == "":
        return 0
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _format_bkk_time(epoch_ms: int) -> str:
    if epoch_ms <= 0:
        return "-"
    return datetime.fromtimestamp(epoch_ms / 1000.0, tz=BKK_TZ).strftime("%Y-%m-%d %H:%M:%S")


def _format_stuck_duration(stuck_minutes: int) -> str:
    if stuck_minutes < 0:
        return "0 นาที"
    days, rem_minutes = divmod(stuck_minutes, 24 * 60)
    hours, minutes = divmod(rem_minutes, 60)
    parts: list[str] = []
    if days > 0:
        parts.append(f"{days} วัน")
    if hours > 0:
        parts.append(f"{hours} ชม.")
    if minutes > 0 or not parts:
        parts.append(f"{minutes} นาที")
    return " ".join(parts)


def _format_mem_mb(mem_bytes: Any) -> float | None:
    raw = _to_int(mem_bytes)
    if raw <= 0:
        return None
    return round(raw / (1024 * 1024), 2)


def _extract_inner_data(row: dict[str, Any]) -> dict[str, Any]:
    outer_data = row.get("data")
    if isinstance(outer_data, dict):
        inner = outer_data.get("data")
        if isinstance(inner, dict):
            return inner
        return outer_data
    return {}


async def _fetch_screen_rows(
    freshness: Literal["cached", "refresh"],
    timeout_seconds: float = 60.0,
) -> list[dict[str, Any]]:
    function_url = os.getenv("NEON_FUNCTION_URL", "").strip()
    token = os.getenv("NEON_MANUAL_SYNC_TOKEN", "").strip()
    if not function_url or not token:
        raise RuntimeError("NEON_FUNCTION_URL and NEON_MANUAL_SYNC_TOKEN must be configured")

    parsed = urlparse(function_url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise RuntimeError("NEON_FUNCTION_URL must be an HTTPS URL")

    base_url = function_url.rstrip("/")
    headers = {"Authorization": f"Bearer {token}"}

    try:
        async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=False) as client:
            if freshness == "refresh":
                sync_resp = await client.post(f"{base_url}/sync", headers=headers)
                if sync_resp.status_code != 200:
                    raise RuntimeError(f"SOURCE_UNAVAILABLE: Target-R refresh failed (HTTP {sync_resp.status_code})")

            async with client.stream("GET", f"{base_url}/tables/screen", headers=headers) as response:
                if response.status_code != 200:
                    raise RuntimeError(f"SOURCE_UNAVAILABLE: Neon table read failed (HTTP {response.status_code})")
                chunks = [chunk async for chunk in response.aiter_bytes()]
            payload = httpx.Response(200, content=b"".join(chunks)).json()
    except (httpx.HTTPError, ValueError) as exc:
        raise RuntimeError("SOURCE_RESPONSE_INVALID: Neon returned invalid or unavailable JSON") from exc

    if not isinstance(payload, dict) or not isinstance(payload.get("rows"), list):
        raise RuntimeError("SOURCE_RESPONSE_INVALID: Neon table response is missing rows")
    return payload["rows"]


def analyze_stuck_screens(
    rows: list[dict[str, Any]],
    min_stuck_minutes: int = 60,
    loader_online_window_minutes: int = 10,
    retailer: str | None = None,
    store_query: str | None = None,
    limit: int = 50,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    """วิเคราะห์รายการจอที่ Loader ออนไลน์แต่ Player ค้าง (ติดใบ้ / Player comms problem) และบันทึก CSV"""
    if min_stuck_minutes < 0 or loader_online_window_minutes < 1 or limit < 1:
        raise ValueError("INVALID_INPUT: min_stuck_minutes >= 0, loader_online_window_minutes >= 1, and limit >= 1 are required")

    reference_ms = max(
        (_to_int(_extract_inner_data(r).get("lastLoaderCommsMillis")) for r in rows if isinstance(r, dict)),
        default=0,
    )

    loader_window_ms = loader_online_window_minutes * 60_000
    min_stuck_ms = min_stuck_minutes * 60_000
    retailer_filter = retailer.strip().casefold() if retailer else None
    store_filter = store_query.strip().casefold() if store_query else None

    stuck_list: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        inner = _extract_inner_data(row)
        last_loader_ms = _to_int(inner.get("lastLoaderCommsMillis"))
        last_player_ms = _to_int(inner.get("lastPlayerCommsMillis") or row.get("lastPlayerCommsMillis"))

        if last_loader_ms <= 0:
            continue
        if (reference_ms - last_loader_ms) > loader_window_ms:
            continue

        if last_player_ms > 0 and (last_loader_ms - last_player_ms) < min_stuck_ms:
            continue

        screen_retailer = str(inner.get("retailer") or row.get("retailer") or "").strip()
        if retailer_filter and screen_retailer.casefold() != retailer_filter:
            continue

        store_location = str(inner.get("storeLocation") or row.get("storeLocation") or "").strip()
        label = str(inner.get("label") or row.get("label") or "").strip()
        if store_filter and store_filter not in store_location.casefold() and store_filter not in label.casefold():
            continue

        screen_id = str(
            inner.get("screenId")
            or row.get("screenId")
            or (row.get("data", {}).get("id") if isinstance(row.get("data"), dict) else "")
            or ""
        ).strip()

        stuck_minutes = (
            max(0, (last_loader_ms - last_player_ms) // 60_000)
            if last_player_ms > 0
            else (last_loader_ms // 60_000)
        )

        stuck_list.append(
            {
                "screenId": screen_id,
                "label": label,
                "retailer": screen_retailer,
                "storeLocation": store_location,
                "STC": str(inner.get("STC") or row.get("STC") or "").strip(),
                "hardwareModel": str(inner.get("hardwareModel") or row.get("hardwareModel") or "").strip(),
                "activePlayer": str(inner.get("activePlayer") or "").strip(),
                "lastLoaderCommsBkk": _format_bkk_time(last_loader_ms),
                "lastPlayerCommsBkk": _format_bkk_time(last_player_ms) if last_player_ms > 0 else "never",
                "stuck_minutes": stuck_minutes,
                "stuck_duration": _format_stuck_duration(stuck_minutes) if last_player_ms > 0 else "ไม่มีข้อมูล Player",
                "recentStartCount": _to_int(inner.get("recentStartCount")),
                "memFreeMB": _format_mem_mb(inner.get("memFree")),
                "anydesk": str(inner.get("ACT_AnyDesk") or "").strip(),
            }
        )

    stuck_list.sort(key=lambda item: (-item["stuck_minutes"], item["screenId"]))

    sandbox_path = Path(output_dir) if output_dir else _default_sandbox_dir()
    sandbox_path.mkdir(parents=True, exist_ok=True)
    csv_file = sandbox_path / "stuck_screens_report.csv"

    fieldnames = [
        "screenId",
        "label",
        "retailer",
        "storeLocation",
        "STC",
        "hardwareModel",
        "activePlayer",
        "lastLoaderCommsBkk",
        "lastPlayerCommsBkk",
        "stuck_minutes",
        "stuck_duration",
        "recentStartCount",
        "memFreeMB",
        "anydesk",
    ]
    with csv_file.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(stuck_list)

    returned_screens = stuck_list[:limit]
    return {
        "source": "targetr_neon_stuck_screens",
        "as_of_bkk": _format_bkk_time(reference_ms) if reference_ms > 0 else _format_bkk_time(int(datetime.now(timezone.utc).timestamp() * 1000)),
        "min_stuck_minutes": min_stuck_minutes,
        "loader_online_window_minutes": loader_online_window_minutes,
        "total_stuck": len(stuck_list),
        "returned": len(returned_screens),
        "csv_path": str(csv_file),
        "screens": returned_screens,
    }


async def find_stuck_screens(
    min_stuck_minutes: int = 60,
    loader_online_window_minutes: int = 10,
    retailer: str | None = None,
    store_query: str | None = None,
    limit: int = 50,
    freshness: Literal["cached", "refresh"] = "refresh",
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    """ดึงข้อมูลจอจาก Neon (พร้อม sync เมื่อ freshness='refresh') และคัดกรองจอติดใบ้ (Player comms problem)"""
    rows = await _fetch_screen_rows(freshness=freshness)
    return analyze_stuck_screens(
        rows=rows,
        min_stuck_minutes=min_stuck_minutes,
        loader_online_window_minutes=loader_online_window_minutes,
        retailer=retailer,
        store_query=store_query,
        limit=limit,
        output_dir=output_dir,
    )
