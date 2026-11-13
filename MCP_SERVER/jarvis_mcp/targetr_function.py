from __future__ import annotations

import csv
import json
import os
import tempfile
from typing import Any
from urllib.parse import urlparse

import httpx


TABLES = {"screen", "sequence", "libraryitem"}
OPS = {"eq", "ne", "contains", "in", "exists", "gt", "gte", "lt", "lte"}
AGGREGATES = {"count", "sum", "avg", "min", "max"}


class TargetRFunction:
    """Fetch raw Neon table data and export filtered results as a complete CSV file."""

    def __init__(self, function_url: str, token: str, timeout_seconds: float = 60.0) -> None:
        parsed = urlparse(function_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise RuntimeError("NEON_FUNCTION_URL must be an HTTPS URL")
        self.function_url = function_url.rstrip("/")
        self.token = token
        self.timeout_seconds = timeout_seconds

    @classmethod
    def from_env(cls) -> TargetRFunction:
        function_url = os.getenv("NEON_FUNCTION_URL", "").strip()
        token = os.getenv("NEON_MANUAL_SYNC_TOKEN", "").strip()
        if not function_url or not token:
            raise RuntimeError("NEON_FUNCTION_URL and NEON_MANUAL_SYNC_TOKEN must be configured")
        return cls(function_url, token, float(os.getenv("TARGETR_HTTP_TIMEOUT_SECONDS", "60")))

    async def run(
        self,
        table: str,
        filters: list[dict[str, Any]] | None = None,
        fields: list[str] | None = None,
        sort: list[dict[str, str]] | None = None,
        aggregate: dict[str, Any] | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> dict[str, Any]:
        self._validate(table, filters, fields, sort, aggregate, limit, offset)
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=False) as client:
                async with client.stream("GET", f"{self.function_url}/tables/{table}", headers=headers) as response:
                    if response.status_code != 200:
                        raise RuntimeError(f"SOURCE_UNAVAILABLE: Neon table read failed (HTTP {response.status_code})")
                    chunks = [chunk async for chunk in response.aiter_bytes()]
            payload = httpx.Response(200, content=b"".join(chunks)).json()
        except (httpx.HTTPError, ValueError) as exc:
            raise RuntimeError("SOURCE_RESPONSE_INVALID: Neon returned invalid or unavailable JSON") from exc
        if not isinstance(payload, dict) or not isinstance(payload.get("rows"), list):
            raise RuntimeError("SOURCE_RESPONSE_INVALID: Neon table response is missing rows")
        rows = payload["rows"]

        if any(not isinstance(row, dict) for row in rows):
            raise RuntimeError("SOURCE_RESPONSE_INVALID: table rows must be objects")

        matched = [row for row in rows if all(self._matches(row, f) for f in (filters or []))]
        if sort:
            for item in reversed(sort):
                field = item["field"]
                reverse = item["direction"] == "desc"
                matched.sort(key=lambda row: (self._value(row, field) is None, str(self._value(row, field) or "").casefold()), reverse=reverse)
        selected = matched[offset:] if limit is None else matched[offset:offset + limit]
        if aggregate:
            return {
                "source": "targetr_neon_raw_processed",
                "table": table,
                "total_matched": len(matched),
                "aggregate": self._aggregate(matched, aggregate),
            }
        headers = fields or list(dict.fromkeys(key for row in selected for key in row))
        output_dir = os.getenv("TARGETR_EXPORT_DIR", os.path.join(os.getcwd(), "exports"))
        os.makedirs(output_dir, exist_ok=True)
        descriptor, file_path = tempfile.mkstemp(prefix=f"targetr_{table}_", suffix=".csv", dir=output_dir)
        try:
            with os.fdopen(descriptor, "w", newline="", encoding="utf-8-sig") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=headers, extrasaction="ignore")
                writer.writeheader()
                for row in selected:
                    writer.writerow({field: self._csv_value(self._value(row, field) if fields else row.get(field)) for field in headers})
        except Exception:
            os.unlink(file_path)
            raise
        return {
            "source": "targetr_neon_raw_processed",
            "table": table,
            "total_matched": len(matched),
            "returned": len(selected),
            "format": "csv",
            "file_path": os.path.abspath(file_path),
        }

    @staticmethod
    def _validate(table: str, filters: list[dict[str, Any]] | None, fields: list[str] | None,
                  sort: list[dict[str, str]] | None, aggregate: dict[str, Any] | None,
                  limit: int | None, offset: int) -> None:
        if table not in TABLES:
            raise ValueError("INVALID_INPUT: unsupported table")
        if (limit is not None and limit < 1) or offset < 0:
            raise ValueError("INVALID_INPUT: limit must be positive when set and offset non-negative")

        if fields is not None and (not fields or len(set(fields)) != len(fields)):
            raise ValueError("INVALID_INPUT: fields must contain unique paths")
        for item in filters or []:
            if not isinstance(item, dict) or not isinstance(item.get("field"), str) or item.get("operator") not in OPS:
                raise ValueError("INVALID_INPUT: filter requires a field and supported operator")
            if item["operator"] != "exists" and "value" not in item:
                raise ValueError("INVALID_INPUT: filter value is required")
            if item["operator"] == "in" and not isinstance(item.get("value"), list):
                raise ValueError("INVALID_INPUT: in requires an array")
        for item in sort or []:
            if not isinstance(item, dict) or not isinstance(item.get("field"), str) or item.get("direction") not in {"asc", "desc"}:
                raise ValueError("INVALID_INPUT: sort requires field and asc/desc direction")
        if aggregate:
            op = aggregate.get("operation")
            if op not in AGGREGATES | {"group_count"}:
                raise ValueError("INVALID_INPUT: unsupported aggregate operation")
            if op != "count" and not isinstance(aggregate.get("field"), str):
                raise ValueError("INVALID_INPUT: aggregate requires field")
            if op == "group_count" and not isinstance(aggregate.get("group_by"), str):
                raise ValueError("INVALID_INPUT: group_count requires group_by")

    @staticmethod
    def _value(row: dict[str, Any], path: str) -> Any:
        value: Any = row
        for part in path.split("."):
            if isinstance(value, dict):
                value = value.get(part)
            elif isinstance(value, list) and part.isdecimal() and int(part) < len(value):
                value = value[int(part)]
            else:
                return None
        return value

    @staticmethod
    def _csv_value(value: Any) -> Any:
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False, default=str)
        return value

    @classmethod
    def _matches(cls, row: dict[str, Any], item: dict[str, Any]) -> bool:
        value, target, op = cls._value(row, item["field"]), item.get("value"), item["operator"]
        if op == "exists":
            return (value is not None) is bool(target if target is not None else True)
        if value is None:
            return False
        if op == "eq": return value == target or str(value) == str(target)
        if op == "ne": return not (value == target or str(value) == str(target))
        if op == "contains": return str(target).casefold() in str(value).casefold()
        if op == "in" and isinstance(target, list): return any(value == candidate or str(value) == str(candidate) for candidate in target)
        if target is None:
            return False
        try:
            left, right = float(value), float(target)
        except (TypeError, ValueError):
            return False
        return {"gt": left > right, "gte": left >= right, "lt": left < right, "lte": left <= right}[op]

    @classmethod
    def _aggregate(cls, rows: list[dict[str, Any]], spec: dict[str, Any]) -> Any:
        op = spec["operation"]
        if op == "count": return {"operation": op, "value": len(rows)}
        if op == "group_count":
            counts: dict[str, int] = {}
            for row in rows:
                value = cls._value(row, spec["group_by"])
                key = "(null)" if value is None else str(value)
                counts[key] = counts.get(key, 0) + 1
            groups = [{"value": key, "count": count} for key, count in sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))]
            return {"operation": op, "groups": groups}
        vals = []
        for row in rows:
            try: vals.append(float(cls._value(row, spec["field"])))
            except (TypeError, ValueError): pass
        if op == "sum": value = sum(vals)
        elif op == "avg": value = sum(vals) / len(vals) if vals else None
        elif op == "min": value = min(vals) if vals else None
        else: value = max(vals) if vals else None
        return {"operation": op, "field": spec["field"], "value": value, "values_count": len(vals)}
