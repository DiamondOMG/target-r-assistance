from __future__ import annotations

import asyncio

import pytest

from jarvis_mcp.targetr_query import TargetRQuery


def make_query() -> TargetRQuery:
    return TargetRQuery("https://example.invalid", "test-token")


def test_count_preserves_store_code_as_string() -> None:
    query = make_query()

    async def get_rows(entity: str, freshness: str):
        return ([
            {"screenId": "SCREEN_A", "storeCode": "0012", "data": {"secret": True}},
            {"screenId": "SCREEN_B", "storeCode": "12", "data": {"secret": True}},
        ], "2026-01-01T00:00:00+00:00", "cached")

    query._get_rows = get_rows  # type: ignore[method-assign]
    result = asyncio.run(query.query(
        entity="screen",
        operation="count",
        filters=[{"field": "storeCode", "operator": "eq", "value": "0012"}],
    ))
    assert result["total"] == 1
    assert result["rows"] == []
    assert result["groups"] == []


def test_query_select_filters_and_projects_fields() -> None:
    query = make_query()

    async def get_rows(entity: str, freshness: str):
        return ([
            {"screenId": "SCREEN_A", "storeCode": "0012", "label": "Branch A", "data": {"secret": True}},
            {"screenId": "SCREEN_B", "storeCode": "12", "label": "Branch B", "data": {"secret": True}},
        ], "2026-01-01T00:00:00+00:00", "cached")

    query._get_rows = get_rows  # type: ignore[method-assign]
    result = asyncio.run(query.query(
        entity="screen",
        operation="select",
        filters=[{"field": "storeCode", "operator": "eq", "value": "0012"}],
        fields=["storeCode", "label"],
    ))
    assert result["total"] == 1
    assert result["rows"] == [{"storeCode": "0012", "label": "Branch A"}]
    assert "data" not in result["rows"][0]


def test_group_count_returns_aggregates() -> None:
    query = make_query()

    async def get_rows(entity: str, freshness: str):
        return ([
            {"storeCode": "0012"},
            {"storeCode": "0012"},
            {"storeCode": "0003"},
        ], "2026-01-01T00:00:00+00:00", "fetched")

    query._get_rows = get_rows  # type: ignore[method-assign]
    result = asyncio.run(query.query(entity="screen", operation="group_count", group_by=["storeCode"]))
    assert result["groups"] == [
        {"key": {"storeCode": "0012"}, "count": 2},
        {"key": {"storeCode": "0003"}, "count": 1},
    ]


def test_rejects_unlisted_fields() -> None:
    with pytest.raises(ValueError, match="unsupported or duplicate"):
        TargetRQuery._validate("screen", "select", None, ["data"], None, 20, 0, "cached")
