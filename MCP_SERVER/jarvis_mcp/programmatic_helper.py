from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

MANAGE_TARGET_R_URL = "https://tops.actx.digital/manage_target_r"

UpdateMode = Literal[
    "multiple_update_screens",
    "single_screen_json",
    "insert_sequence_items",
    "update_existing_sequence_items",
]


def _default_sandbox_dir() -> Path:
    project_root = Path(__file__).resolve().parents[2]
    sandbox_dir = project_root / "SANDBOX"
    sandbox_dir.mkdir(parents=True, exist_ok=True)
    return sandbox_dir


def _clean_key(key: str) -> str:
    cleaned = str(key).strip()
    if cleaned.startswith("data."):
        return cleaned[5:]
    return cleaned


def _clean_cell(val: Any) -> str:
    if val is None:
        return ""
    return str(val).replace("\t", " ").replace("\r", "").replace("\n", " ").strip()


def prepare_targetr_update(
    mode: UpdateMode,
    rows: list[dict[str, Any]],
    target_id: str | None = None,
    filename_prefix: str = "manage_target_r",
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    """สร้างข้อมูล TSV และ JSON พร้อมไฟล์ใน SANDBOX/ สำหรับให้ผู้ใช้นำไปวางใน https://tops.actx.digital/manage_target_r"""
    if not isinstance(rows, list) or len(rows) == 0:
        raise ValueError("INVALID_INPUT: rows must be a non-empty list of objects")

    sandbox_path = Path(output_dir) if output_dir else _default_sandbox_dir()
    sandbox_path.mkdir(parents=True, exist_ok=True)

    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_prefix = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in filename_prefix).strip("_") or "manage_target_r"

    if mode == "multiple_update_screens":
        field_names: list[str] = []
        normalized_rows: list[dict[str, str]] = []

        for idx, raw_row in enumerate(rows, start=1):
            if not isinstance(raw_row, dict):
                raise ValueError(f"INVALID_INPUT: row {idx} must be an object")

            screen_id = (
                raw_row.get("screen_id")
                or raw_row.get("screenId")
                or raw_row.get("id")
                or ""
            )
            screen_id_str = _clean_cell(screen_id)
            if not screen_id_str:
                raise ValueError(f"INVALID_INPUT: row {idx} is missing screen_id")

            row_entry: dict[str, str] = {"screen_id": screen_id_str}
            for k, v in raw_row.items():
                if k in ("screen_id", "screenId", "id"):
                    continue
                clean_k = _clean_key(k)
                if not clean_k:
                    continue
                if clean_k not in field_names:
                    field_names.append(clean_k)
                row_entry[clean_k] = _clean_cell(v)

            normalized_rows.append(row_entry)

        if not field_names:
            raise ValueError("INVALID_INPUT: at least one data field to update is required alongside screen_id")

        headers = ["screen_id"] + field_names
        tsv_lines = ["\t".join(headers)]
        for r in normalized_rows:
            tsv_lines.append("\t".join(r.get(h, "") for h in headers))
        tsv_content = "\n".join(tsv_lines)
        json_content = json.dumps(normalized_rows, ensure_ascii=False, indent=2)

        tsv_file = sandbox_path / f"{safe_prefix}_multiple_screens_{timestamp_str}.tsv"
        json_file = sandbox_path / f"{safe_prefix}_multiple_screens_{timestamp_str}.json"
        tsv_file.write_text(tsv_content, encoding="utf-8")
        json_file.write_text(json_content, encoding="utf-8")

        return {
            "url": MANAGE_TARGET_R_URL,
            "mode": mode,
            "record_count": len(normalized_rows),
            "headers": headers,
            "paste_format": "TSV",
            "paste_content": tsv_content,
            "json_content": normalized_rows,
            "saved_files": {
                "tsv_path": str(tsv_file),
                "json_path": str(json_file),
            },
            "instructions": [
                f"1. เปิดลิงก์ {MANAGE_TARGET_R_URL}",
                "2. คลิกแท็บ 'Manage Screen' แล้วเลือกปุ่ม 'Update Screen'",
                "3. คลิกปุ่ม 'Multiple Update' เพื่อเปิดหน้าต่าง Multiple Update Screens",
                "4. คัดลอกข้อมูล TSV (paste_content) ไปวางในช่อง 'Paste Excel Data (TSV)' ด้านซ้าย",
                "5. ตรวจสอบตาราง Preview & Status ด้านขวา แล้วกดปุ่ม 'Start Update'",
            ],
        }

    if mode == "single_screen_json":
        raw_payload = dict(rows[0])
        resolved_screen_id = _clean_cell(
            target_id
            or raw_payload.pop("screen_id", None)
            or raw_payload.pop("screenId", None)
            or raw_payload.pop("id", None)
            or ""
        )
        if not resolved_screen_id:
            raise ValueError("INVALID_INPUT: target_id (or screen_id in rows[0]) is required for single_screen_json")

        cleaned_payload = {_clean_key(k): v for k, v in raw_payload.items() if _clean_key(k)}
        if not cleaned_payload:
            raise ValueError("INVALID_INPUT: payload must contain at least one field to update")

        json_text = json.dumps(cleaned_payload, ensure_ascii=False, indent=2)
        json_file = sandbox_path / f"{safe_prefix}_screen_{resolved_screen_id}_{timestamp_str}.json"
        json_file.write_text(json_text, encoding="utf-8")

        return {
            "url": MANAGE_TARGET_R_URL,
            "mode": mode,
            "target_id": resolved_screen_id,
            "record_count": 1,
            "paste_format": "JSON",
            "paste_content": json_text,
            "json_content": cleaned_payload,
            "saved_files": {
                "json_path": str(json_file),
            },
            "instructions": [
                f"1. เปิดลิงก์ {MANAGE_TARGET_R_URL}",
                "2. คลิกแท็บ 'Manage Screen' แล้วเลือกโหมด 'Update Screen'",
                f"3. กรอก Screen ID: {resolved_screen_id}",
                "4. คัดลอก JSON (paste_content) ไปวางในช่อง JSON Payload แล้วกด 'Update Screen'",
            ],
        }

    if mode == "insert_sequence_items":
        resolved_seq_id = _clean_cell(target_id or "")
        if not resolved_seq_id:
            raise ValueError("INVALID_INPUT: target_id (Sequence ID) is required for insert_sequence_items")

        extra_fields: list[str] = []
        normalized_rows = []
        base_headers = ["inner_sequence_id", "slot", "item"]

        for idx, raw_row in enumerate(rows, start=1):
            inner_id = _clean_cell(raw_row.get("inner_sequence_id") or raw_row.get("innerSequenceId") or "")
            slot_val = _clean_cell(raw_row.get("slot", "1"))
            item_val = _clean_cell(raw_row.get("item", "1"))
            if not inner_id:
                raise ValueError(f"INVALID_INPUT: row {idx} is missing inner_sequence_id")

            entry: dict[str, str] = {
                "inner_sequence_id": inner_id,
                "slot": slot_val,
                "item": item_val,
            }
            for k, v in raw_row.items():
                if k in ("inner_sequence_id", "innerSequenceId", "slot", "item"):
                    continue
                if k not in extra_fields:
                    extra_fields.append(k)
                entry[k] = _clean_cell(v)
            normalized_rows.append(entry)

        headers = base_headers + extra_fields
        tsv_lines = ["\t".join(headers)]
        for r in normalized_rows:
            tsv_lines.append("\t".join(r.get(h, "") for h in headers))
        tsv_content = "\n".join(tsv_lines)
        json_content = json.dumps(normalized_rows, ensure_ascii=False, indent=2)

        tsv_file = sandbox_path / f"{safe_prefix}_insert_seq_{resolved_seq_id}_{timestamp_str}.tsv"
        json_file = sandbox_path / f"{safe_prefix}_insert_seq_{resolved_seq_id}_{timestamp_str}.json"
        tsv_file.write_text(tsv_content, encoding="utf-8")
        json_file.write_text(json_content, encoding="utf-8")

        return {
            "url": MANAGE_TARGET_R_URL,
            "mode": mode,
            "target_id": resolved_seq_id,
            "record_count": len(normalized_rows),
            "headers": headers,
            "paste_format": "TSV",
            "paste_content": tsv_content,
            "json_content": normalized_rows,
            "saved_files": {
                "tsv_path": str(tsv_file),
                "json_path": str(json_file),
            },
            "instructions": [
                f"1. เปิดลิงก์ {MANAGE_TARGET_R_URL}",
                "2. ในแท็บ 'Manage Sequence' เลือก 'Update Sequence' แล้วคลิกปุ่มสีม่วง 'Insert Sequence Items'",
                f"3. กรอก Sequence ID: {resolved_seq_id}",
                "4. คัดลอกข้อมูล TSV (paste_content) ไปวางในช่อง 'Paste Excel Data (TSV)' แล้วกด 'Insert Items'",
            ],
        }

    if mode == "update_existing_sequence_items":
        resolved_seq_id = _clean_cell(target_id or "")
        if not resolved_seq_id:
            raise ValueError("INVALID_INPUT: target_id (Sequence ID) is required for update_existing_sequence_items")

        headers = ["inner_sequence_id", "slot", "item", "customId"]
        normalized_rows = []
        for idx, raw_row in enumerate(rows, start=1):
            inner_id = _clean_cell(raw_row.get("inner_sequence_id") or raw_row.get("innerSequenceId") or "")
            slot_val = _clean_cell(raw_row.get("slot") or "")
            item_val = _clean_cell(raw_row.get("item") or "")
            custom_id = _clean_cell(raw_row.get("customId") or raw_row.get("custom_id") or "")

            if not inner_id or not slot_val or not item_val or not custom_id:
                raise ValueError(
                    f"INVALID_INPUT: row {idx} requires inner_sequence_id, slot, item, and customId"
                )
            normalized_rows.append(
                {
                    "inner_sequence_id": inner_id,
                    "slot": slot_val,
                    "item": item_val,
                    "customId": custom_id,
                }
            )

        tsv_lines = ["\t".join(headers)]
        for r in normalized_rows:
            tsv_lines.append("\t".join(r[h] for h in headers))
        tsv_content = "\n".join(tsv_lines)
        json_content = json.dumps(normalized_rows, ensure_ascii=False, indent=2)

        tsv_file = sandbox_path / f"{safe_prefix}_update_seq_items_{resolved_seq_id}_{timestamp_str}.tsv"
        json_file = sandbox_path / f"{safe_prefix}_update_seq_items_{resolved_seq_id}_{timestamp_str}.json"
        tsv_file.write_text(tsv_content, encoding="utf-8")
        json_file.write_text(json_content, encoding="utf-8")

        return {
            "url": MANAGE_TARGET_R_URL,
            "mode": mode,
            "target_id": resolved_seq_id,
            "record_count": len(normalized_rows),
            "headers": headers,
            "paste_format": "TSV",
            "paste_content": tsv_content,
            "json_content": normalized_rows,
            "saved_files": {
                "tsv_path": str(tsv_file),
                "json_path": str(json_file),
            },
            "instructions": [
                f"1. เปิดลิงก์ {MANAGE_TARGET_R_URL}",
                "2. ในแท็บ 'Manage Sequence' เลือก 'Update Sequence' แล้วคลิกปุ่มสีเขียว 'Update Existing Items'",
                f"3. กรอก Sequence ID: {resolved_seq_id}",
                "4. คัดลอกข้อมูล TSV (paste_content) ไปวางในช่อง 'Paste Excel Data (TSV)' แล้วกด 'Update Existing Items'",
            ],
        }

    raise ValueError(f"INVALID_INPUT: unsupported mode '{mode}'")
