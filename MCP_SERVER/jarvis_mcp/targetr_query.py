from __future__ import annotations

import asyncio
import os
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal
from urllib.parse import urlparse

import httpx

Entity = Literal["screen", "sequence", "libraryitem"]
Operation = Literal["count", "select", "group_count"]
Freshness = Literal["cached", "refresh"]

ENTITY_FIELDS: dict[str, set[str]] = {
    "screen": {
        "screenId", "sequenceId", "lastPlayerCommsMillis", "label", "AssetName", "AssetTypeId",
        "ProjectName", "ProjectStart", "ProjectEnd", "retailer", "RetailerType", "STC", "storeCode",
        "signageType", "storeSectionZone", "hardwareDevice", "hardwareId", "hardwareManufacturer",
        "hardwareModel", "hardwareProduct", "hardwareVersionCodename", "orientation", "platform",
        "playerInstallation", "playerRam", "playerShape", "playerType", "restartTime", "storeLocation",
        "storeSection", "timeZoneOverride", "version", "volume", "webviewReuse", "wifiSsid",
        "blackCondition", "hardware", "hardwareBoard", "hardwareBrand",
    },
    "sequence": {"sequenceId", "label", "createdMillis", "report", "vastAddress", "customType", "usedBy"},
    "libraryitem": {"id", "sequenceId_0", "createdMillis", "label", "image", "blob-s", "blob-l"},
}

ENTITY_PATHS = {
    "screen": "/screens",
    "sequence": "/sequences",
    "libraryitem": "/libraryitems",
}
SYNC_PATHS = {
    "screen": "/sync",
    "sequence": "/sync-sequences",
    "libraryitem": "/sync-libraryitems",
}
MAX_LIMIT = 100


@dataclass
class CachedDataset:
    rows: list[dict[str, Any]]
    fetched_at: str
    expires_at: float


class TargetRQuery:
    def __init__(
        self,
        function_url: str,
        token: str,
        cache_ttl_seconds: int = 120,
        refresh_wait_seconds: float = 1.0,
        timeout_seconds: float = 60.0,
    ) -> None:
        self.function_url = function_url.rstrip("/")
        self.token = token
        self.cache_ttl_seconds = cache_ttl_seconds
        self.refresh_wait_seconds = refresh_wait_seconds
        self.timeout_seconds = timeout_seconds
        self._cache: dict[str, CachedDataset] = {}
        self._locks = {entity: asyncio.Lock() for entity in ENTITY_PATHS}

    @classmethod
    def from_env(cls) -> TargetRQuery:
        function_url = os.getenv("NEON_FUNCTION_URL", "").strip()
        token = os.getenv("NEON_MANUAL_SYNC_TOKEN", "").strip()
        if not function_url or not token:
            raise RuntimeError("NEON_FUNCTION_URL and NEON_MANUAL_SYNC_TOKEN must be configured")
        parsed_url = urlparse(function_url)
        if parsed_url.scheme != "https" or not parsed_url.netloc:
            raise RuntimeError("NEON_FUNCTION_URL must be an HTTPS URL")
        return cls(
            function_url=function_url,
            token=token,
            cache_ttl_seconds=int(os.getenv("TARGETR_CACHE_TTL_SECONDS", "120")),
            refresh_wait_seconds=float(os.getenv("TARGETR_REFRESH_WAIT_SECONDS", "1")),
            timeout_seconds=float(os.getenv("TARGETR_HTTP_TIMEOUT_SECONDS", "60")),
        )

    async def query(
        self,
        entity: Entity,
        operation: Operation,
        filters: list[dict[str, Any]] | None = None,
        fields: list[str] | None = None,
        group_by: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
        freshness: Freshness = "cached",
    ) -> dict[str, Any]:
        self._validate(entity, operation, filters, fields, group_by, limit, offset, freshness)
        rows, fetched_at, data_status = await self._get_rows(entity, freshness)
        matched = [row for row in rows if self._matches(row, filters or [])]
        result: dict[str, Any] = {
            "source": "targetr_neon",
            "entity": entity,
            "operation": operation,
            "data_status": data_status,
            "as_of": fetched_at,
            "total": len(matched),
            "returned": 0,
            "rows": [],
            "groups": [],
            "warnings": [],
        }

        if operation == "count":
            return result

        if operation == "select":
            selected_fields = fields or []
            page = matched[offset : offset + limit]
            result["rows"] = [{field: row.get(field) for field in selected_fields} for row in page]
            result["returned"] = len(page)
            if any("screenId" in row for row in result["rows"]):
                result["warnings"].append("screenId is a device identifier; only disclose it when necessary")
            return result

        group_keys: dict[tuple[str, ...], int] = {}
        for row in matched:
            key = tuple(self._group_value(row.get(field)) for field in (group_by or []))
            group_keys[key] = group_keys.get(key, 0) + 1
        ordered = sorted(group_keys.items(), key=lambda item: (-item[1], item[0]))
        result["groups"] = [
            {"key": dict(zip(group_by or [], key, strict=True)), "count": count}
            for key, count in ordered[offset : offset + limit]
        ]
        result["returned"] = len(result["groups"])
        return result

    @staticmethod
    def _validate(
        entity: str,
        operation: str,
        filters: list[dict[str, Any]] | None,
        fields: list[str] | None,
        group_by: list[str] | None,
        limit: int,
        offset: int,
        freshness: str,
    ) -> None:
        if entity not in ENTITY_FIELDS:
            raise ValueError("INVALID_INPUT: unsupported entity")
        if operation not in {"count", "select", "group_count"}:
            raise ValueError("INVALID_INPUT: unsupported operation")
        if freshness not in {"cached", "refresh"}:
            raise ValueError("INVALID_INPUT: unsupported freshness")
        if not 1 <= limit <= MAX_LIMIT or offset < 0:
            raise ValueError(f"INVALID_INPUT: limit must be 1-{MAX_LIMIT} and offset must be non-negative")
        allowed = ENTITY_FIELDS[entity]
        if operation == "select" and not fields:
            raise ValueError("INVALID_INPUT: select requires at least one field")
        if fields and (len(set(fields)) != len(fields) or not set(fields) <= allowed):
            raise ValueError("INVALID_INPUT: fields contain unsupported or duplicate values")
        if operation == "group_count" and not group_by:
            raise ValueError("INVALID_INPUT: group_count requires group_by")
        if group_by and (len(set(group_by)) != len(group_by) or not set(group_by) <= allowed):
            raise ValueError("INVALID_INPUT: group_by contains unsupported or duplicate values")
        for item in filters or []:
            if not isinstance(item, dict) or item.get("field") not in allowed:
                raise ValueError("INVALID_INPUT: filter contains unsupported field")
            operator = item.get("operator")
            if operator not in {"eq", "in", "contains", "exists", "gt", "lt"}:
                raise ValueError("INVALID_INPUT: unsupported filter operator")
            if operator != "exists" and "value" not in item:
                raise ValueError("INVALID_INPUT: filter value is required")
            if operator == "in" and not isinstance(item.get("value"), list):
                raise ValueError("INVALID_INPUT: in operator requires an array value")
            if operator in {"gt", "lt"}:
                if item["field"] != "lastPlayerCommsMillis":
                    raise ValueError("INVALID_INPUT: numeric comparisons are only allowed for lastPlayerCommsMillis")
                try:
                    float(item["value"])
                except (TypeError, ValueError) as exc:
                    raise ValueError("INVALID_INPUT: gt/lt requires a numeric value") from exc

    async def _get_rows(self, entity: Entity, freshness: Freshness) -> tuple[list[dict[str, Any]], str, str]:
        async with self._locks[entity]:
            cached = self._cache.get(entity)
            if freshness == "cached" and cached and cached.expires_at > time.monotonic():
                return cached.rows, cached.fetched_at, "cached"

            headers = {"Authorization": f"Bearer {self.token}"}
            async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=False) as client:
                if freshness == "refresh":
                    response = await client.post(f"{self.function_url}{SYNC_PATHS[entity]}", headers=headers)
                    if response.status_code != 200:
                        raise RuntimeError(f"SOURCE_UNAVAILABLE: Target-R refresh failed (HTTP {response.status_code})")
                    try:
                        refresh_result = response.json()
                    except ValueError as exc:
                        raise RuntimeError("SOURCE_RESPONSE_INVALID: Target-R refresh returned invalid JSON") from exc
                    if not isinstance(refresh_result, dict) or refresh_result.get("ok") is not True:
                        raise RuntimeError("SOURCE_RESPONSE_INVALID: Target-R refresh did not confirm success")
                    if self.refresh_wait_seconds > 0:
                        await asyncio.sleep(self.refresh_wait_seconds)

                response = await client.get(f"{self.function_url}{ENTITY_PATHS[entity]}", headers=headers)
                if response.status_code != 200:
                    raise RuntimeError(f"SOURCE_UNAVAILABLE: Target-R read failed (HTTP {response.status_code})")
                try:
                    payload = response.json()
                except ValueError as exc:
                    raise RuntimeError("SOURCE_RESPONSE_INVALID: Target-R returned invalid JSON") from exc

            if not isinstance(payload, dict) or not isinstance(payload.get("rows"), list):
                raise RuntimeError("SOURCE_RESPONSE_INVALID: Target-R response is missing rows")
            rows = payload["rows"]
            if any(not isinstance(row, dict) for row in rows):
                raise RuntimeError("SOURCE_RESPONSE_INVALID: Target-R rows must be objects")
            if any("data" in row for row in rows):
                raise RuntimeError("SOURCE_RESPONSE_INVALID: Neon returned raw data from a non-raw endpoint")
            fetched_at = datetime.now(UTC).isoformat()
            self._cache[entity] = CachedDataset(
                rows=rows,
                fetched_at=fetched_at,
                expires_at=time.monotonic() + self.cache_ttl_seconds,
            )
            return rows, fetched_at, "refreshed" if freshness == "refresh" else "fetched"

    @staticmethod
    def _matches(row: dict[str, Any], filters: list[dict[str, Any]]) -> bool:
        for item in filters:
            value = row.get(item["field"])
            operator = item["operator"]
            target = item.get("value")
            if operator == "exists":
                matched = value is not None
            elif operator == "eq":
                matched = value is not None and str(value) == str(target)
            elif operator == "in":
                matched = value is not None and str(value) in {str(candidate) for candidate in target}
            elif operator in {"gt", "lt"}:
                try:
                    numeric_value = float(value)
                    numeric_target = float(target)
                except (TypeError, ValueError):
                    matched = False
                else:
                    matched = numeric_value > numeric_target if operator == "gt" else numeric_value < numeric_target
            else:
                matched = value is not None and str(target).casefold() in str(value).casefold()
            if not matched:
                return False
        return True

    @staticmethod
    def _group_value(value: Any) -> str:
        return "(null)" if value is None else str(value)
