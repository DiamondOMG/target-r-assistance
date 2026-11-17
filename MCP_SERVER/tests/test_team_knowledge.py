from unittest.mock import MagicMock

import pytest

from jarvis_mcp.team_knowledge import (
    TAB_NAME,
    save_knowledge_with_auth,
    search_knowledge_with_auth,
)


def _mock_response(status_code: int = 200, json_data: dict | None = None, text_data: str = "") -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    resp.text = text_data
    return resp


def test_save_creates_tab_and_appends_row(monkeypatch: pytest.MonkeyPatch):
    calls: list[tuple[str, str]] = []

    def fake_get(url, **kwargs):
        calls.append(("GET", url))
        if "fields" in kwargs.get("params", {}):
            # Tab does not exist yet
            return _mock_response(200, {"sheets": [{"properties": {"title": "Location"}}]})
        # Existing rows empty
        return _mock_response(200, {"values": []})

    def fake_post(url, **kwargs):
        calls.append(("POST", url))
        return _mock_response(200, {})

    def fake_put(url, **kwargs):
        calls.append(("PUT", url))
        return _mock_response(200, {})

    monkeypatch.setattr("jarvis_mcp.team_knowledge.httpx.get", fake_get)
    monkeypatch.setattr("jarvis_mcp.team_knowledge.httpx.post", fake_post)
    monkeypatch.setattr("jarvis_mcp.team_knowledge.httpx.put", fake_put)

    res = save_knowledge_with_auth(
        headers_auth={"Authorization": "Bearer test"},
        spreadsheet_id="sheet_123",
        title="อาการจอติดใบ้",
        content="รีสตาร์ทแอปแล้วหาย",
        category="troubleshooting",
        tags="ติดใบ้,จอดำ",
        updated_by="admin",
    )

    assert res["status"] == "saved"
    assert res["action"] == "created"
    assert res["topic_id"] == "KB-001"
    assert any("batchUpdate" in url for method, url in calls if method == "POST")
    assert any(":append" in url for method, url in calls if method == "POST")
    assert any("A1%3AG1" in url or "A1:G1" in url for method, url in calls if method == "PUT")


def test_save_updates_existing_entry_by_title(monkeypatch: pytest.MonkeyPatch):
    put_payloads: list[dict] = []

    def fake_get(url, **kwargs):
        if "fields" in kwargs.get("params", {}):
            return _mock_response(200, {"sheets": [{"properties": {"title": TAB_NAME}}]})
        return _mock_response(
            200,
            {
                "values": [
                    ["KB-001", "อาการจอติดใบ้", "troubleshooting", "ติดใบ้", "ข้อความเก่า", "admin", "2026-11-17 10:00:00"]
                ]
            },
        )

    def fake_put(url, **kwargs):
        put_payloads.append({"url": url, "json": kwargs.get("json")})
        return _mock_response(200, {})

    monkeypatch.setattr("jarvis_mcp.team_knowledge.httpx.get", fake_get)
    monkeypatch.setattr("jarvis_mcp.team_knowledge.httpx.put", fake_put)

    res = save_knowledge_with_auth(
        headers_auth={"Authorization": "Bearer test"},
        spreadsheet_id="sheet_123",
        title="อาการจอติดใบ้",
        content="เนื้อหาอัปเดตใหม่",
        category="troubleshooting",
        tags="ติดใบ้,Player comms problem",
        updated_by="staff1",
    )

    assert res["action"] == "updated"
    assert res["topic_id"] == "KB-001"
    assert len(put_payloads) == 1
    assert "A2" in put_payloads[0]["url"]
    assert put_payloads[0]["json"]["values"][0][4] == "เนื้อหาอัปเดตใหม่"


def test_search_matches_sheet_and_drive(monkeypatch: pytest.MonkeyPatch):
    def fake_get(url, **kwargs):
        if "spreadsheets" in url and "fields" in kwargs.get("params", {}):
            return _mock_response(200, {"sheets": [{"properties": {"title": TAB_NAME}}]})
        if "spreadsheets" in url and "values" in url:
            return _mock_response(
                200,
                {
                    "values": [
                        ["KB-001", "อาการจอติดใบ้", "troubleshooting", "ติดใบ้,จอดำ", "Player ค้าง ให้รีสตาร์ท", "admin", "2026-11-17 16:00:00"],
                        ["KB-002", "ตั้งค่า WiFi สาขา", "sop", "wifi", "ใช้ SSID DigitalNatives", "staff", "2026-11-17 16:05:00"],
                    ]
                },
            )
        if "drive/v3/files" in url and "export" not in url and kwargs.get("params", {}).get("alt") != "media":
            return _mock_response(
                200,
                {
                    "files": [
                        {"id": "f1", "name": "คู่มือแก้ติดใบ้.md", "mimeType": "text/markdown", "modifiedTime": "2026-11-17", "webViewLink": "https://drive.google.com/f1"}
                    ]
                },
            )
        return _mock_response(200, text_data="รายละเอียดวิธีแก้จอติดใบ้จาก Drive")

    monkeypatch.setattr("jarvis_mcp.team_knowledge.httpx.get", fake_get)

    res = search_knowledge_with_auth(
        headers_auth={"Authorization": "Bearer test"},
        spreadsheet_id="sheet_123",
        drive_folder_id="folder_123",
        query="ติดใบ้",
    )

    assert res["total_matched"] == 1
    assert res["sheet_entries"][0]["topic_id"] == "KB-001"
    assert len(res["drive_files"]) == 1
    assert res["drive_files"][0]["name"] == "คู่มือแก้ติดใบ้.md"


def test_validation_errors():
    with pytest.raises(ValueError, match="INVALID_INPUT"):
        save_knowledge_with_auth({"Authorization": "Bearer x"}, "s", "", "content")

    with pytest.raises(ValueError, match="INVALID_INPUT"):
        search_knowledge_with_auth({"Authorization": "Bearer x"}, "s", "f", limit=0)
