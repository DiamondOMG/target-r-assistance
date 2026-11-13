from __future__ import annotations

import pytest

from jarvis_mcp.targetr_function import TargetRFunction


def test_filter_nested_json_and_comparison() -> None:
    row = {"lastPlayerCommsMillis": "1781081424494", "data": {"data": {"sequenceId": "SEQ"}}}
    assert TargetRFunction._matches(row, {"field": "data.data.sequenceId", "operator": "eq", "value": "SEQ"})
    assert TargetRFunction._matches(row, {"field": "lastPlayerCommsMillis", "operator": "gt", "value": 100})
    assert not TargetRFunction._matches(row, {"field": "data.data.missing", "operator": "exists"})


def test_group_aggregate_counts_nested_field() -> None:
    rows = [
        {"data": {"data": {"sequenceId": "A"}}},
        {"data": {"data": {"sequenceId": "A"}}},
        {"data": {"data": {"sequenceId": "B"}}},
    ]
    assert TargetRFunction._aggregate(rows, {"operation": "group_count", "group_by": "data.data.sequenceId"}) == {
        "operation": "group_count",
        "groups": [{"value": "A", "count": 2}, {"value": "B", "count": 1}],
    }


def test_csv_export_allows_unbounded_result_and_omitted_projection() -> None:
    TargetRFunction._validate("screen", None, None, None, None, None, 0)
    TargetRFunction._validate("screen", None, ["label"], None, None, 10_000_000, 0)


def test_rejects_invalid_requests() -> None:
    with pytest.raises(ValueError, match="unsupported table"):
        TargetRFunction._validate("users", None, ["id"], None, None, None, 0)
    with pytest.raises(ValueError, match="positive"):
        TargetRFunction._validate("screen", None, ["label"], None, None, 0, 0)


def test_csv_keeps_nested_json_in_single_cell() -> None:
    assert TargetRFunction._csv_value({"sensitive": "raw"}) == '{"sensitive": "raw"}'
