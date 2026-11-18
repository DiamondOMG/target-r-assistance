from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Annotated, Any, Literal

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

from jarvis_mcp.email_sender import send_email as run_send_email
from jarvis_mcp.fuzzy_search import targetr_fuzzy_search as run_fuzzy_search
from jarvis_mcp.geo_distance import geo_distance as run_geo_distance
from jarvis_mcp.programmatic_helper import (
    UpdateMode,
    prepare_targetr_update as run_prepare_targetr_update,
)
from jarvis_mcp.stuck_screens import find_stuck_screens as run_find_stuck_screens
from jarvis_mcp.targetr_function import TargetRFunction
from jarvis_mcp.targetr_query import TargetRQuery
from jarvis_mcp.team_knowledge import (
    team_knowledge_save as run_team_knowledge_save,
    team_knowledge_search as run_team_knowledge_search,
)
from jarvis_mcp.tv_control import (
    TVAction,
    tv_control as run_tv_control,
)

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
load_dotenv()

_query_client: TargetRQuery | None = None
_function_client: TargetRFunction | None = None


def get_query_client() -> TargetRQuery:
    global _query_client
    if _query_client is None:
        _query_client = TargetRQuery.from_env()
    return _query_client


def get_function_client() -> TargetRFunction:
    global _function_client
    if _function_client is None:
        _function_client = TargetRFunction.from_env()
    return _function_client


class OriginInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    latitude: float = Field(description="Latitude in degrees (-90.0 to 90.0)")
    longitude: float = Field(description="Longitude in degrees (-180.0 to 180.0)")


class DestinationInput(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str = Field(default="", description="Identifier of the screen or location")
    label: str | None = Field(default=None, description="Display label")
    storeLocation: str | None = Field(default=None, description="Store location name")
    latitude: float = Field(description="Latitude coordinate")
    longitude: float = Field(description="Longitude coordinate")


class FunctionFilterInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str
    operator: Literal["eq", "ne", "contains", "in", "exists", "gt", "gte", "lt", "lte"]
    value: str | int | float | bool | list[str] | None = None


class SortInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str
    direction: Literal["asc", "desc"] = "asc"


class AggregateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation: Literal["count", "sum", "avg", "min", "max", "group_count"]
    field: str | None = None
    group_by: str | None = None


class FilterInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str = Field(description="Canonical field name allowed for the selected entity")
    operator: Literal["eq", "in", "contains", "exists", "gt", "lt"] = Field(
        description="Comparison operator; in requires an array value, exists checks for a non-null value; gt/lt are numeric and only allowed for lastPlayerCommsMillis"
    )
    value: str | int | float | bool | list[str] | None = Field(
        default=None,
        description="Comparison value; use a string for store codes to preserve leading zeroes; in requires a list of strings",
    )


mcp = FastMCP(
    "Jarvis Target-R",
    instructions=(
        "Query tools for Target-R digital signage data. Queries do not edit source records; explicit refresh triggers the configured sync/upsert. "
        "DS Loader is a user term for Target-R in this integration. "
        "Use freshness='refresh' only when the user asks for current/latest/time-sensitive data; "
        "otherwise use cached data. Never request raw JSON or expose device identifiers unnecessarily."
    ),
)


@mcp.tool(
    name="targetr_query",
    description=(
        "Query Target-R Screen, Sequence, or Library item data. DS Loader refers to Target-R in this integration. Query operations do not edit source records; explicit refresh triggers the configured sync/upsert. "
        "Supports count, select, and group_count with allowlisted fields and filters. "
        "Use freshness='refresh' only when the user asks for current/latest/time-sensitive data; "
        "this triggers a Target-R-to-Neon sync for the selected entity before reading it. "
        "Never returns raw JSONB data. Screen IDs are sensitive; select them only when necessary."
    ),
)
async def targetr_query(
    entity: Literal["screen", "sequence", "libraryitem"],
    operation: Literal["count", "select", "group_count"],
    filters: Annotated[list[FilterInput] | None, Field(description="All filters are combined with AND; field names are allowlisted for the selected entity")]=None,
    fields: Annotated[list[str] | None, Field(description="Required for select. Allowed names: screen [screenId, sequenceId, lastPlayerCommsMillis, label, AssetName, AssetTypeId, ProjectName, ProjectStart, ProjectEnd, retailer, RetailerType, STC, storeCode, signageType, storeSectionZone, hardwareDevice, hardwareId, hardwareManufacturer, hardwareModel, hardwareProduct, hardwareVersionCodename, orientation, platform, playerInstallation, playerRam, playerShape, playerType, restartTime, storeLocation, storeSection, timeZoneOverride, version, volume, webviewReuse, wifiSsid, blackCondition, hardware, hardwareBoard, hardwareBrand]; sequence [sequenceId, label, createdMillis, report, vastAddress, customType, usedBy]; libraryitem [id, sequenceId_0, createdMillis, label, image, blob-s, blob-l]. Never request raw data")]=None,
    group_by: Annotated[list[str] | None, Field(description="Required for group_count; use field names from the selected entity allowlist")]=None,
    limit: int = 20,
    offset: int = 0,
    freshness: Literal["cached", "refresh"] = "cached",
) -> dict[str, Any]:
    """Query allowlisted fields. `select` requires `fields`; `group_count` requires `group_by`.

    Filters are AND-combined objects. gt/lt are numeric comparisons allowed only for lastPlayerCommsMillis. Keep store codes as strings to preserve leading zeroes.
    """
    client = get_query_client()
    filter_values = [item.model_dump(exclude_none=True) for item in filters] if filters else None
    return await client.query(
        entity=entity,
        operation=operation,
        filters=filter_values,
        fields=fields,
        group_by=group_by,
        limit=limit,
        offset=offset,
        freshness=freshness,
    )


@mcp.tool(
    name="targetr_function",
    description=(
        "Filter, project, sort, aggregate or page through raw Target-R JSON rows fetched from Neon. "
        "By default exports every matching row and all source fields to a CSV file on the MCP host; returns the file path, not the dataset. "
        "Set limit only when a partial result is wanted. Raw JSON cells are serialized into CSV. Does not execute arbitrary code."
    ),
)
async def targetr_function(
    table: Literal["screen", "sequence", "libraryitem"],
    filters: Annotated[list[FunctionFilterInput] | None, Field(description="AND-combined field-path filters")]=None,
    fields: Annotated[list[str] | None, Field(description="Optional dot-path projection; omit to export every top-level source field")]=None,
    sort: Annotated[list[SortInput] | None, Field(description="Optional ordered sort keys")]=None,
    aggregate: Annotated[AggregateInput | None, Field(description="Optional aggregation; when set, rows are not returned")]=None,
    limit: int | None = None,
    offset: int = 0,
) -> dict[str, Any]:
    """Process Neon raw JSON internally and export the complete matched dataset as CSV by default."""
    return await get_function_client().run(
        table=table,
        filters=[item.model_dump(exclude_unset=True) for item in filters] if filters else None,
        fields=fields,
        sort=[item.model_dump() for item in sort] if sort else None,
        aggregate=aggregate.model_dump(exclude_none=True) if aggregate else None,
        limit=limit,
        offset=offset,
    )


@mcp.tool(
    name="geo_distance",
    description=(
        "Calculate geographic distance (Haversine formula) from an origin coordinate to multiple target destinations. "
        "Filters by maximum distance (radius) and returns the closest locations sorted from nearest to furthest. "
        "Never returns raw coordinates unnecessarily."
    ),
)
async def geo_distance_tool(
    origin: OriginInput,
    destinations: Annotated[list[DestinationInput], Field(description="List of target destinations with coordinates")],
    max_distance_km: Annotated[float | None, Field(description="Max search radius in km")]=None,
    limit: Annotated[int, Field(description="Max results to return (default 5, max 20)")]=5,
    unit: Literal["km", "m"] = "km",
) -> dict[str, Any]:
    """Calculate distance and rank nearby locations."""
    origin_dict = origin.model_dump()
    dest_dicts = [d.model_dump() for d in destinations]
    return run_geo_distance(
        origin=origin_dict,
        destinations=dest_dicts,
        max_distance_km=max_distance_km,
        limit=limit,
        unit=unit,
    )


@mcp.tool(
    name="targetr_fuzzy_search",
    description=(
        "Search for store locations, projects, or screen label types using fuzzy matching and alias lookup. "
        "Handles typos, Thai misspellings, colloquial names, and abbreviations (e.g. 'CTW', 'เซลทรัลเวิล', 'ลาดพราว'). "
        "Queries the Master Knowledge base and returns canonical storeLocation and storeCode for subsequent queries."
    ),
)
async def targetr_fuzzy_search_tool(
    query: Annotated[str, Field(description="Search text, e.g. 'เซลทรัลเวิล', 'CTW', 'บางพลี', 'ลาดพร้าว'")],
    entity_type: Literal["location", "project", "label"] = "location",
    threshold: Annotated[float, Field(description="Similarity threshold from 0.0 to 1.0")]=0.6,
    limit: Annotated[int, Field(description="Max results to return (default 5, max 20)")]=5,
) -> dict[str, Any]:
    """Fuzzy search across Master Knowledge base."""
    key_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "target-r-assistance-5f4d3703fed8.json")
    spreadsheet_id = os.getenv("TARGETR_SPREADSHEET_ID", "1K0hWy-Mgl52a7TR6Rzy8XvsGSjl7kwNmsm5sxqRpJoE")
    return run_fuzzy_search(
        query=query,
        entity_type=entity_type,
        threshold=threshold,
        limit=limit,
        key_file=key_file,
        spreadsheet_id=spreadsheet_id,
    )


@mcp.tool(
    name="send_email",
    description=(
        "Send an email notification, report, or alert via Gmail SMTP. "
        "Supports plain text or HTML body, multiple recipients, and CC."
    ),
)
async def send_email_tool(
    to: Annotated[list[str], Field(description="List of recipient email addresses (e.g. ['manager@example.com'])")],
    subject: Annotated[str, Field(description="Subject line of the email")],
    body: Annotated[str, Field(description="Body content of the email (plain text or HTML)")],
    is_html: Annotated[bool, Field(description="Set true if body is HTML formatted (default false)")]=False,
    cc: Annotated[list[str] | None, Field(description="Optional list of CC email addresses")]=None,
) -> dict[str, Any]:
    """Send an email via configured Gmail account."""
    return run_send_email(
        to=to,
        subject=subject,
        body=body,
        is_html=is_html,
        cc=cc,
    )


@mcp.tool(
    name="prepare_targetr_update",
    description=(
        "Generate ready-to-paste TSV and JSON payloads (and save files in SANDBOX/) for the user to copy and paste "
        "into the Manage Target-R web tool (https://tops.actx.digital/manage_target_r). "
        "Supports bulk screen field updates (multiple_update_screens), single screen JSON update (single_screen_json), "
        "inserting sequence items (insert_sequence_items), and updating existing sequence items (update_existing_sequence_items). "
        "Does not mutate Target-R directly; outputs formatted content and step-by-step instructions for the user."
    ),
)
async def prepare_targetr_update_tool(
    mode: Annotated[
        UpdateMode,
        Field(
            description=(
                "Operation mode: 'multiple_update_screens', 'single_screen_json', "
                "'insert_sequence_items', or 'update_existing_sequence_items'"
            )
        ),
    ],
    rows: Annotated[
        list[dict[str, Any]],
        Field(
            description=(
                "List of row objects. For multiple_update_screens: [{'screen_id': '...', '<field>': '...'}]. "
                "For single_screen_json: [{'<field>': '...'}]. "
                "For insert_sequence_items: [{'inner_sequence_id': '...', 'slot': 1, 'item': 1, ...}]. "
                "For update_existing_sequence_items: [{'inner_sequence_id': '...', 'slot': 1, 'item': 1, 'customId': '...'}]."
            )
        ),
    ],
    target_id: Annotated[
        str | None,
        Field(description="Target Screen ID (for single_screen_json) or Sequence ID (for sequence modes)"),
    ] = None,
    filename_prefix: Annotated[
        str,
        Field(description="Prefix for generated files inside SANDBOX/ (default 'manage_target_r')"),
    ] = "manage_target_r",
) -> dict[str, Any]:
    """Prepare TSV/JSON payloads and save files in SANDBOX/ for Manage Target-R web tool."""
    return run_prepare_targetr_update(
        mode=mode,
        rows=rows,
        target_id=target_id,
        filename_prefix=filename_prefix,
    )


@mcp.tool(
    name="targetr_stuck_screens",
    description=(
        "List screens suffering from 'Player comms problem' (จอติดใบ้: DS Loader is online via lastLoaderCommsMillis, "
        "but the media player stopped communicating via lastPlayerCommsMillis, resulting in a black screen while appearing Online). "
        "Refreshes Neon screen data by default, sorts by longest stuck duration, and exports full list to SANDBOX/stuck_screens_report.csv."
    ),
)
async def targetr_stuck_screens_tool(
    min_stuck_minutes: Annotated[
        int,
        Field(description="Minimum minutes since lastPlayerCommsMillis compared to lastLoaderCommsMillis (default 60)"),
    ] = 60,
    loader_online_window_minutes: Annotated[
        int,
        Field(description="Window in minutes to consider DS Loader online relative to newest loader comms (default 10)"),
    ] = 10,
    retailer: Annotated[
        str | None,
        Field(description="Optional retailer filter, e.g. 'Tops', 'Big C'"),
    ] = None,
    store_query: Annotated[
        str | None,
        Field(description="Optional substring filter on storeLocation or screen label"),
    ] = None,
    limit: Annotated[
        int,
        Field(description="Max rows returned in tool response (default 50; full list saved to CSV)"),
    ] = 50,
    freshness: Annotated[
        Literal["cached", "refresh"],
        Field(description="Use 'refresh' (default) to sync latest Target-R state to Neon before checking, or 'cached'"),
    ] = "refresh",
) -> dict[str, Any]:
    """List screens where DS Loader is online but Player stopped communicating (Player comms problem)."""
    return await run_find_stuck_screens(
        min_stuck_minutes=min_stuck_minutes,
        loader_online_window_minutes=loader_online_window_minutes,
        retailer=retailer,
        store_query=store_query,
        limit=limit,
        freshness=freshness,
    )


@mcp.tool(
    name="team_knowledge_search",
    description=(
        "Search the shared real-time Team Knowledge Base stored on Google Sheet (Jarvis_TargetR_Master -> Team_Knowledge tab) "
        "and files in the shared Google Drive folder (Editor). Available immediately to all team members without waiting for git push."
    ),
)
async def team_knowledge_search_tool(
    query: Annotated[
        str,
        Field(description="Search keywords (matches title, tags, category, content, or Drive file name). Leave empty to list recent notes."),
    ] = "",
    category: Annotated[
        str | None,
        Field(description="Optional category filter, e.g. 'troubleshooting', 'sop', 'hardware', 'general'"),
    ] = None,
    limit: Annotated[
        int,
        Field(description="Max entries to return (1-50, default 10)"),
    ] = 10,
) -> dict[str, Any]:
    """Search shared team knowledge notes and Drive documents."""
    return run_team_knowledge_search(
        query=query,
        category=category,
        limit=limit,
    )


@mcp.tool(
    name="team_knowledge_save",
    description=(
        "Save or update a shared knowledge note directly to the central Team_Knowledge tab on Google Sheet (Jarvis_TargetR_Master). "
        "Allows both admin and staff to record solutions, SOPs, or field notes that become immediately visible to the whole team."
    ),
)
async def team_knowledge_save_tool(
    title: Annotated[str, Field(description="Clear title of the knowledge note")],
    content: Annotated[str, Field(description="Detailed symptom, cause, solution, or SOP content")],
    category: Annotated[
        str,
        Field(description="Category such as 'troubleshooting', 'sop', 'hardware', 'targetr', or 'general'"),
    ] = "general",
    tags: Annotated[
        str,
        Field(description="Comma-separated search tags, e.g. 'ติดใบ้,จอดำ,android-player'"),
    ] = "",
    updated_by: Annotated[
        str,
        Field(description="Name or role of the team member saving the note"),
    ] = "team",
    topic_id: Annotated[
        str | None,
        Field(description="Optional existing topic_id (e.g. 'KB-001') to update a specific row"),
    ] = None,
) -> dict[str, Any]:
    """Save or update a note in the shared Team_Knowledge Google Sheet tab."""
    return run_team_knowledge_save(
        title=title,
        content=content,
        category=category,
        tags=tags,
        updated_by=updated_by,
        topic_id=topic_id,
    )


@mcp.tool(
    name="tv_control",
    description=(
        "Control the office Sharp Smart TVs via ADB over Tailscale VPN. "
        "Supports opening dashboard web URLs (auto-stops DS Loader), launching/restarting/stopping DS Loader (Target-R), "
        "setting fullscreen/desktop_view, switching HDMI inputs (hdmi1/hdmi2), sending Home/Back/Wake keys, and locking ADB port 5555."
    ),
)
async def tv_control_tool(
    tv: Annotated[
        str,
        Field(description="Target TV: 'sharp_left' (or 'left'/'ซ้าย'/'A4AE125D42DE'), 'sharp_right' (or 'right'/'ขวา'), or direct Tailscale IP"),
    ] = "sharp_left",
    action: Annotated[
        TVAction,
        Field(description="Command action: 'status', 'open_url', 'open_dsloader', 'restart_dsloader', 'stop_dsloader', 'fullscreen', 'desktop_view', 'hdmi1', 'hdmi2', 'home', 'back', 'wake', 'lock_adb_port'"),
    ] = "status",
    url: Annotated[
        str | None,
        Field(description="Required when action='open_url': full http:// or https:// URL to open on the TV browser"),
    ] = None,
) -> dict[str, Any]:
    """Send ADB control commands to an office Sharp Smart TV over Tailscale."""
    return run_tv_control(tv=tv, action=action, url=url)


def _auto_update_if_staff() -> None:
    """เมื่อ PERMISSION=staff ให้ดึงเวอร์ชันล่าสุดจาก origin/main อัตโนมัติตอนเริ่ม MCP Server"""
    permission = os.getenv("PERMISSION", "staff").strip().lower()
    if permission != "staff":
        return

    repo_root = Path(__file__).resolve().parents[2]
    if not (repo_root / ".git").exists():
        return

    try:
        subprocess.run(
            ["git", "fetch", "origin", "main"],
            cwd=str(repo_root),
            capture_output=True,
            timeout=5,
            check=True,
        )
        subprocess.run(
            ["git", "reset", "--hard", "origin/main"],
            cwd=str(repo_root),
            capture_output=True,
            timeout=5,
            check=True,
        )
    except Exception:
        # ห้ามทำให้ MCP Server ล่มหากเครื่องออฟไลน์หรือยังไม่ได้ตั้งค่า remote
        pass


def main() -> None:
    _auto_update_if_staff()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
