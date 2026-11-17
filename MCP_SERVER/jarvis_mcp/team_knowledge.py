from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx

DEFAULT_SPREADSHEET_ID = "1K0hWy-Mgl52a7TR6Rzy8XvsGSjl7kwNmsm5sxqRpJoE"
DEFAULT_DRIVE_FOLDER_ID = "1e7UnHGQHsZjY9svu6Uqqj4bgPcAjJAoN"
TAB_NAME = "Team_Knowledge"
HEADERS = ["topic_id", "title", "category", "tags", "content", "updated_by", "updated_at"]
BKK_TZ = timezone(timedelta(hours=7))


def _resolve_key_file(key_file: str | None) -> str:
    candidate = (
        key_file
        or os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
        or "target-r-assistance-5f4d3703fed8.json"
    )
    path = Path(candidate)
    if path.is_file():
        return str(path)

    repo_root = Path(__file__).resolve().parents[2]
    root_candidate = repo_root / candidate
    if root_candidate.is_file():
        return str(root_candidate)

    # Fallback: search for any target-r-assistance-*.json in repo root
    matches = sorted(repo_root.glob("target-r-assistance-*.json"))
    if matches:
        return str(matches[0])

    raise RuntimeError(f"CREDENTIALS_MISSING: Google Service Account file not found ({candidate})")


def _get_auth_headers(key_file: str | None = None) -> dict[str, str]:
    import google.auth.transport
    from google.oauth2 import service_account

    class _HttpxResponse(google.auth.transport.Response):
        def __init__(self, resp: httpx.Response) -> None:
            self._resp = resp

        @property
        def status(self) -> int:
            return self._resp.status_code

        @property
        def headers(self) -> dict[str, str]:
            return dict(self._resp.headers)

        @property
        def data(self) -> bytes:
            return self._resp.content

    class _HttpxRequest(google.auth.transport.Request):
        def __call__(self, url, method="GET", body=None, headers=None, timeout=None, **kwargs):
            resp = httpx.request(
                method=method,
                url=url,
                content=body,
                headers=headers,
                timeout=timeout or 20.0,
            )
            return _HttpxResponse(resp)

    resolved_key = _resolve_key_file(key_file)
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    creds = service_account.Credentials.from_service_account_file(resolved_key, scopes=scopes)
    creds.refresh(_HttpxRequest())
    return {"Authorization": f"Bearer {creds.token}"}


def _now_bkk_str() -> str:
    return datetime.now(BKK_TZ).strftime("%Y-%m-%d %H:%M:%S")


def ensure_team_knowledge_tab(headers_auth: dict[str, str], spreadsheet_id: str) -> None:
    """ตรวจสอบและสร้างแท็บ Team_Knowledge พร้อม Header หากยังไม่มีใน Google Sheet"""
    meta_resp = httpx.get(
        f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}",
        params={"fields": "sheets.properties.title"},
        headers=headers_auth,
        timeout=20.0,
    )
    if meta_resp.status_code != 200:
        raise RuntimeError(f"SHEETS_UNAVAILABLE: failed to read spreadsheet metadata (HTTP {meta_resp.status_code})")

    titles = {
        s.get("properties", {}).get("title")
        for s in meta_resp.json().get("sheets", [])
        if isinstance(s, dict)
    }

    if TAB_NAME not in titles:
        add_resp = httpx.post(
            f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}:batchUpdate",
            headers=headers_auth,
            json={"requests": [{"addSheet": {"properties": {"title": TAB_NAME}}}]},
            timeout=20.0,
        )
        if add_resp.status_code != 200:
            raise RuntimeError(f"SHEETS_WRITE_FAILED: failed to create tab '{TAB_NAME}' (HTTP {add_resp.status_code})")

        hdr_resp = httpx.put(
            f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{quote(f'{TAB_NAME}!A1:G1')}",
            params={"valueInputOption": "RAW"},
            headers=headers_auth,
            json={"values": [HEADERS]},
            timeout=20.0,
        )
        if hdr_resp.status_code != 200:
            raise RuntimeError(f"SHEETS_WRITE_FAILED: failed to write headers (HTTP {hdr_resp.status_code})")


def _read_sheet_entries(headers_auth: dict[str, str], spreadsheet_id: str) -> list[dict[str, Any]]:
    resp = httpx.get(
        f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{quote(f'{TAB_NAME}!A2:G1000')}",
        headers=headers_auth,
        timeout=20.0,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"SHEETS_UNAVAILABLE: failed to read '{TAB_NAME}' (HTTP {resp.status_code})")

    rows = resp.json().get("values", [])
    entries: list[dict[str, Any]] = []
    for idx, row in enumerate(rows, start=2):
        if not row or not any(str(c).strip() for c in row):
            continue
        padded = [str(row[i]).strip() if i < len(row) else "" for i in range(len(HEADERS))]
        entries.append(
            {
                "row_number": idx,
                "topic_id": padded[0],
                "title": padded[1],
                "category": padded[2],
                "tags": padded[3],
                "content": padded[4],
                "updated_by": padded[5],
                "updated_at": padded[6],
            }
        )
    return entries


def _next_topic_id(entries: list[dict[str, Any]]) -> str:
    max_num = 0
    for item in entries:
        tid = item.get("topic_id", "")
        if tid.upper().startswith("KB-"):
            try:
                num = int(tid.split("-", 1)[1])
                if num > max_num:
                    max_num = num
            except ValueError:
                pass
    return f"KB-{max_num + 1:03d}"


def _read_drive_folder_files(
    headers_auth: dict[str, str],
    drive_folder_id: str,
    query: str,
    limit: int,
) -> list[dict[str, Any]]:
    if not drive_folder_id:
        return []
    try:
        list_resp = httpx.get(
            "https://www.googleapis.com/drive/v3/files",
            params={
                "q": f"'{drive_folder_id}' in parents and trashed = false",
                "fields": "files(id,name,mimeType,modifiedTime,webViewLink)",
                "pageSize": 50,
            },
            headers=headers_auth,
            timeout=15.0,
        )
        if list_resp.status_code != 200:
            return []
        files = list_resp.json().get("files", [])
    except httpx.HTTPError:
        return []

    q_lower = query.strip().casefold()
    matched_files: list[dict[str, Any]] = []
    for f in files:
        name = str(f.get("name") or "")
        mime = str(f.get("mimeType") or "")
        file_id = str(f.get("id") or "")
        if "folder" in mime:
            continue

        snippet = ""
        try:
            if mime == "application/vnd.google-apps.document":
                exp = httpx.get(
                    f"https://www.googleapis.com/drive/v3/files/{file_id}/export",
                    params={"mimeType": "text/plain"},
                    headers=headers_auth,
                    timeout=10.0,
                )
                if exp.status_code == 200:
                    snippet = exp.text[:2500]
            elif mime.startswith("text/") or name.lower().endswith((".md", ".txt", ".json", ".csv")):
                dl = httpx.get(
                    f"https://www.googleapis.com/drive/v3/files/{file_id}",
                    params={"alt": "media"},
                    headers=headers_auth,
                    timeout=10.0,
                )
                if dl.status_code == 200:
                    snippet = dl.text[:2500]
        except httpx.HTTPError:
            snippet = ""

        haystack = f"{name}\n{snippet}".casefold()
        if not q_lower or q_lower in haystack:
            matched_files.append(
                {
                    "id": file_id,
                    "name": name,
                    "mimeType": mime,
                    "modifiedTime": f.get("modifiedTime", ""),
                    "webViewLink": f.get("webViewLink", ""),
                    "content_preview": snippet[:1500],
                }
            )
            if len(matched_files) >= limit:
                break

    return matched_files


def save_knowledge_with_auth(
    headers_auth: dict[str, str],
    spreadsheet_id: str,
    title: str,
    content: str,
    category: str = "general",
    tags: str = "",
    updated_by: str = "team",
    topic_id: str | None = None,
) -> dict[str, Any]:
    """บันทึกหรืออัปเดตหัวข้อความรู้ลงแท็บ Team_Knowledge (รองรับ unit test ด้วย mock auth)"""
    clean_title = (title or "").strip()
    clean_content = (content or "").strip()
    if not clean_title or not clean_content:
        raise ValueError("INVALID_INPUT: title and content are required")

    clean_category = (category or "general").strip() or "general"
    clean_tags = (tags or "").strip()
    clean_user = (updated_by or "team").strip() or "team"
    now_str = _now_bkk_str()

    ensure_team_knowledge_tab(headers_auth, spreadsheet_id)
    entries = _read_sheet_entries(headers_auth, spreadsheet_id)

    target_entry = None
    if topic_id:
        tid_cf = topic_id.strip().casefold()
        target_entry = next((e for e in entries if e["topic_id"].casefold() == tid_cf), None)
    if target_entry is None:
        title_cf = clean_title.casefold()
        target_entry = next((e for e in entries if e["title"].casefold() == title_cf), None)

    if target_entry is not None:
        resolved_id = target_entry["topic_id"] or _next_topic_id(entries)
        row_num = target_entry["row_number"]
        row_values = [resolved_id, clean_title, clean_category, clean_tags, clean_content, clean_user, now_str]
        put_resp = httpx.put(
            f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{quote(f'{TAB_NAME}!A{row_num}:G{row_num}')}",
            params={"valueInputOption": "RAW"},
            headers=headers_auth,
            json={"values": [row_values]},
            timeout=20.0,
        )
        if put_resp.status_code != 200:
            raise RuntimeError(f"SHEETS_WRITE_FAILED: failed to update row {row_num} (HTTP {put_resp.status_code})")
        action = "updated"
    else:
        resolved_id = (topic_id or "").strip() or _next_topic_id(entries)
        row_values = [resolved_id, clean_title, clean_category, clean_tags, clean_content, clean_user, now_str]
        post_resp = httpx.post(
            f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{quote(f'{TAB_NAME}!A:G')}:append",
            params={"valueInputOption": "USER_ENTERED"},
            headers=headers_auth,
            json={"values": [row_values]},
            timeout=20.0,
        )
        if post_resp.status_code != 200:
            raise RuntimeError(f"SHEETS_WRITE_FAILED: failed to append row (HTTP {post_resp.status_code})")
        action = "created"

    return {
        "status": "saved",
        "action": action,
        "topic_id": resolved_id,
        "title": clean_title,
        "category": clean_category,
        "tags": clean_tags,
        "updated_by": clean_user,
        "updated_at": now_str,
        "spreadsheet_url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit",
    }


def search_knowledge_with_auth(
    headers_auth: dict[str, str],
    spreadsheet_id: str,
    drive_folder_id: str,
    query: str = "",
    category: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """ค้นหาความรู้จากแท็บ Team_Knowledge และโฟลเดอร์ Drive กลาง (รองรับ unit test ด้วย mock auth)"""
    if limit < 1 or limit > 50:
        raise ValueError("INVALID_INPUT: limit must be between 1 and 50")

    ensure_team_knowledge_tab(headers_auth, spreadsheet_id)
    entries = _read_sheet_entries(headers_auth, spreadsheet_id)

    cat_cf = category.strip().casefold() if category else None
    q_cf = query.strip().casefold()
    terms = [t for t in q_cf.split() if t]

    matched_entries: list[dict[str, Any]] = []
    for entry in reversed(entries):
        if cat_cf and entry["category"].casefold() != cat_cf:
            continue
        haystack = " ".join(
            [entry["topic_id"], entry["title"], entry["category"], entry["tags"], entry["content"]]
        ).casefold()
        if terms and not all(term in haystack for term in terms):
            continue
        matched_entries.append(
            {
                "topic_id": entry["topic_id"],
                "title": entry["title"],
                "category": entry["category"],
                "tags": entry["tags"],
                "content": entry["content"],
                "updated_by": entry["updated_by"],
                "updated_at": entry["updated_at"],
            }
        )

    drive_files = _read_drive_folder_files(headers_auth, drive_folder_id, query=query, limit=limit)
    limited_entries = matched_entries[:limit]

    return {
        "source": "team_knowledge",
        "spreadsheet_id": spreadsheet_id,
        "spreadsheet_url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit",
        "drive_folder_id": drive_folder_id,
        "total_matched": len(matched_entries),
        "returned": len(limited_entries),
        "sheet_entries": limited_entries,
        "drive_files": drive_files,
    }


def team_knowledge_save(
    title: str,
    content: str,
    category: str = "general",
    tags: str = "",
    updated_by: str = "team",
    topic_id: str | None = None,
    key_file: str | None = None,
    spreadsheet_id: str | None = None,
) -> dict[str, Any]:
    """บันทึกหรืออัปเดตความรู้ลงคลังกลางของทีม (แท็บ Team_Knowledge บน Google Sheet)"""
    resolved_sheet = spreadsheet_id or os.getenv("TARGETR_SPREADSHEET_ID", DEFAULT_SPREADSHEET_ID)
    headers_auth = _get_auth_headers(key_file)
    return save_knowledge_with_auth(
        headers_auth=headers_auth,
        spreadsheet_id=resolved_sheet,
        title=title,
        content=content,
        category=category,
        tags=tags,
        updated_by=updated_by,
        topic_id=topic_id,
    )


def team_knowledge_search(
    query: str = "",
    category: str | None = None,
    limit: int = 10,
    key_file: str | None = None,
    spreadsheet_id: str | None = None,
    drive_folder_id: str | None = None,
) -> dict[str, Any]:
    """ค้นหาความรู้จากคลังกลางของทีม (แท็บ Team_Knowledge + โฟลเดอร์ Editor บน Google Drive)"""
    resolved_sheet = spreadsheet_id or os.getenv("TARGETR_SPREADSHEET_ID", DEFAULT_SPREADSHEET_ID)
    resolved_folder = drive_folder_id or os.getenv("TEAM_DRIVE_FOLDER_ID", DEFAULT_DRIVE_FOLDER_ID)
    headers_auth = _get_auth_headers(key_file)
    return search_knowledge_with_auth(
        headers_auth=headers_auth,
        spreadsheet_id=resolved_sheet,
        drive_folder_id=resolved_folder,
        query=query,
        category=category,
        limit=limit,
    )
