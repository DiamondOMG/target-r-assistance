from __future__ import annotations

from typing import Annotated, Any, Literal

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

from jarvis_mcp.targetr_query import TargetRQuery

load_dotenv()

_query_client: TargetRQuery | None = None


def get_query_client() -> TargetRQuery:
    global _query_client
    if _query_client is None:
        _query_client = TargetRQuery.from_env()
    return _query_client


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


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
