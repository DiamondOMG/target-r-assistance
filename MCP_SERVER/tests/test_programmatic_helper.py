from pathlib import Path

import pytest

from jarvis_mcp.programmatic_helper import prepare_targetr_update


def test_multiple_update_screens(tmp_path: Path):
    rows = [
        {"screen_id": "06BC202512DB", "data.gpsLatitude": "13.7367", "gpsLongitude": "100.5231"},
        {"screenId": "06BC202512DC", "gpsLatitude": "13.7450", "gpsLongitude": "100.5340"},
    ]
    res = prepare_targetr_update(
        mode="multiple_update_screens",
        rows=rows,
        filename_prefix="test_bulk",
        output_dir=tmp_path,
    )

    assert res["url"] == "https://tops.actx.digital/manage_target_r"
    assert res["record_count"] == 2
    assert res["headers"] == ["screen_id", "gpsLatitude", "gpsLongitude"]
    assert res["paste_format"] == "TSV"
    expected_tsv = (
        "screen_id\tgpsLatitude\tgpsLongitude\n"
        "06BC202512DB\t13.7367\t100.5231\n"
        "06BC202512DC\t13.7450\t100.5340"
    )
    assert res["paste_content"] == expected_tsv
    assert Path(res["saved_files"]["tsv_path"]).exists()
    assert Path(res["saved_files"]["json_path"]).exists()


def test_single_screen_json(tmp_path: Path):
    res = prepare_targetr_update(
        mode="single_screen_json",
        rows=[{"data.gpsLatitude": "13.7367", "gpsLongitude": "100.5231"}],
        target_id="06BC202512DB",
        output_dir=tmp_path,
    )
    assert res["target_id"] == "06BC202512DB"
    assert res["paste_format"] == "JSON"
    assert res["json_content"] == {"gpsLatitude": "13.7367", "gpsLongitude": "100.5231"}
    assert Path(res["saved_files"]["json_path"]).exists()


def test_insert_sequence_items(tmp_path: Path):
    res = prepare_targetr_update(
        mode="insert_sequence_items",
        target_id="137CAB135A8CC3",
        rows=[
            {"inner_sequence_id": "15A3FAF5BB4FA7", "slot": 1, "item": 1, "label": "promo_1"}
        ],
        output_dir=tmp_path,
    )
    assert res["target_id"] == "137CAB135A8CC3"
    assert res["headers"] == ["inner_sequence_id", "slot", "item", "label"]
    assert "15A3FAF5BB4FA7\t1\t1\tpromo_1" in res["paste_content"]


def test_update_existing_sequence_items(tmp_path: Path):
    res = prepare_targetr_update(
        mode="update_existing_sequence_items",
        target_id="137CAB135A8CC3",
        rows=[
            {
                "inner_sequence_id": "15D7F2C8A3B51",
                "slot": 6,
                "item": 1,
                "customId": "InnerHivestack Slot 6",
            }
        ],
        output_dir=tmp_path,
    )
    assert res["headers"] == ["inner_sequence_id", "slot", "item", "customId"]
    assert "15D7F2C8A3B51\t6\t1\tInnerHivestack Slot 6" in res["paste_content"]


def test_validation_errors(tmp_path: Path):
    with pytest.raises(ValueError, match="INVALID_INPUT"):
        prepare_targetr_update(mode="multiple_update_screens", rows=[], output_dir=tmp_path)

    with pytest.raises(ValueError, match="missing screen_id"):
        prepare_targetr_update(
            mode="multiple_update_screens",
            rows=[{"gpsLatitude": "13.7"}],
            output_dir=tmp_path,
        )
