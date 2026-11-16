import difflib
import json
import os
import time
from typing import Any, Dict, List, Optional

import httpx

# In-memory cache for sheet data
_CACHE: Dict[str, Any] = {
    "data": {},
    "last_fetched": 0
}
CACHE_TTL = 300  # 5 minutes


def calculate_similarity(query: str, target: str) -> float:
    """คำนวณความคล้ายของข้อความ (0.0 ถึง 1.0)"""
    q = query.strip().lower()
    t = target.strip().lower()

    if not q or not t:
        return 0.0
    if q == t:
        return 1.0
    if q in t or t in q:
        # ให้คะแนนสูงมากถ้าเป็นส่วนหนึ่งของคำ
        len_ratio = min(len(q), len(t)) / max(len(q), len(t))
        return 0.85 + (0.15 * len_ratio)

    return difflib.SequenceMatcher(None, q, t).ratio()


def fetch_sheet_records(key_file: str, spreadsheet_id: str) -> Dict[str, List[Dict[str, str]]]:
    """ดึงข้อมูลจาก Google Sheet หรือใช้ข้อมูลแคช"""
    now = time.time()
    if _CACHE["data"] and (now - _CACHE["last_fetched"] < CACHE_TTL):
        return _CACHE["data"]

    from google.oauth2 import service_account
    import google.auth.transport.requests

    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = service_account.Credentials.from_service_account_file(key_file, scopes=scopes)
    creds.refresh(google.auth.transport.requests.Request())
    headers = {'Authorization': f'Bearer {creds.token}'}

    result = {"location": [], "project": [], "label": []}

    # Fetch Location tab
    try:
        resp = httpx.get(
            f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/Location!A2:F1000',
            headers=headers,
            timeout=10.0
        )
        if resp.status_code == 200:
            for row in resp.json().get('values', []):
                if not row or not row[0]:
                    continue
                result["location"].append({
                    "store_location": row[0] if len(row) > 0 else "",
                    "thai_name": row[1] if len(row) > 1 else "",
                    "aliases": row[2] if len(row) > 2 else "",
                    "retailer": row[3] if len(row) > 3 else "",
                    "store_code": row[4] if len(row) > 4 else "",
                    "notes": row[5] if len(row) > 5 else ""
                })
    except Exception as e:
        print(f"Warning: Failed to fetch Location tab: {e}")

    # Fetch Projects tab
    try:
        resp = httpx.get(
            f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/Projects!A2:E100',
            headers=headers,
            timeout=10.0
        )
        if resp.status_code == 200:
            for row in resp.json().get('values', []):
                if not row or not row[0]:
                    continue
                result["project"].append({
                    "project_name": row[0] if len(row) > 0 else "",
                    "retailer": row[1] if len(row) > 1 else "",
                    "thai_name": row[2] if len(row) > 2 else "",
                    "aliases": row[3] if len(row) > 3 else "",
                    "notes": row[4] if len(row) > 4 else ""
                })
    except Exception as e:
        print(f"Warning: Failed to fetch Projects tab: {e}")

    # Fetch Labels tab
    try:
        resp = httpx.get(
            f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/Labels!A2:E100',
            headers=headers,
            timeout=10.0
        )
        if resp.status_code == 200:
            for row in resp.json().get('values', []):
                if not row or not row[0]:
                    continue
                result["label"].append({
                    "label_type": row[0] if len(row) > 0 else "",
                    "zone": row[1] if len(row) > 1 else "",
                    "thai_name": row[2] if len(row) > 2 else "",
                    "aliases": row[3] if len(row) > 3 else "",
                    "notes": row[4] if len(row) > 4 else ""
                })
    except Exception as e:
        print(f"Warning: Failed to fetch Labels tab: {e}")

    if result["location"] or result["project"] or result["label"]:
        _CACHE["data"] = result
        _CACHE["last_fetched"] = now

    return result


def targetr_fuzzy_search(
    query: str,
    entity_type: str = "location",
    threshold: float = 0.6,
    limit: int = 5,
    records_override: Optional[List[Dict[str, Any]]] = None,
    key_file: str = "target-r-assistance-5f4d3703fed8.json",
    spreadsheet_id: str = "1K0hWy-Mgl52a7TR6Rzy8XvsGSjl7kwNmsm5sxqRpJoE"
) -> Dict[str, Any]:
    """ค้นหาข้อมูลแบบ Fuzzy Matching จาก Master Knowledge"""
    if not query or not query.strip():
        raise ValueError("INVALID_INPUT: query must not be empty")

    query_str = query.strip()
    entity_type = entity_type.lower()
    if entity_type not in ["location", "project", "label"]:
        raise ValueError("INVALID_INPUT: entity_type must be location, project, or label")

    # Get records
    if records_override is not None:
        records = records_override
    else:
        # Load from Google Sheet or fallback
        all_data = fetch_sheet_records(key_file, spreadsheet_id)
        records = all_data.get(entity_type, [])

    matches = []

    for item in records:
        best_score = 0.0
        best_field = ""
        best_text = ""

        # Fields to compare
        fields_to_check = []
        if entity_type == "location":
            fields_to_check = [
                ("store_location", item.get("store_location", "")),
                ("thai_name", item.get("thai_name", "")),
                ("retailer", item.get("retailer", "")),
                ("store_code", item.get("store_code", "")),
            ]
        elif entity_type == "project":
            fields_to_check = [
                ("project_name", item.get("project_name", "")),
                ("thai_name", item.get("thai_name", "")),
                ("retailer", item.get("retailer", "")),
            ]
        elif entity_type == "label":
            fields_to_check = [
                ("label_type", item.get("label_type", "")),
                ("zone", item.get("zone", "")),
                ("thai_name", item.get("thai_name", "")),
            ]

        # Add aliases
        raw_aliases = item.get("aliases", "")
        alias_tokens = [a.strip() for a in raw_aliases.split(",") if a.strip()]
        for a in alias_tokens:
            fields_to_check.append(("aliases", a))

        # Add comma-separated store codes
        raw_codes = item.get("store_code", "")
        code_tokens = [c.strip() for c in raw_codes.split(",") if c.strip()]
        for c in code_tokens:
            fields_to_check.append(("store_code", c))

        # Evaluate similarity
        for field_name, text in fields_to_check:
            if not text:
                continue
            score = calculate_similarity(query_str, text)
            if score > best_score:
                best_score = score
                best_field = field_name
                best_text = text

        if best_score >= threshold:
            entry = dict(item)
            entry["score"] = round(best_score, 3)
            entry["matched_field"] = best_field
            entry["matched_text"] = best_text
            matches.append(entry)

    # Sort descending by score
    matches.sort(key=lambda x: x["score"], reverse=True)

    effective_limit = min(max(1, limit), 20)
    top_results = matches[:effective_limit]

    return {
        "source": "fuzzy_search",
        "query": query_str,
        "entity_type": entity_type,
        "total_matched": len(matches),
        "results": top_results
    }

