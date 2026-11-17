# MCP Tool Contracts: `team_knowledge_search` & `team_knowledge_save`

> สถานะ: พร้อมใช้งานใน `MCP_SERVER/jarvis_mcp/team_knowledge.py`

## วัตถุประสงค์

ใช้ค้นหาและบันทึก **คลังความรู้ส่วนกลางของทีม (Shared Team Knowledge Base)** แบบ Real-time โดยเก็บข้อมูลไว้บน Google Sheet `Jarvis_TargetR_Master` (แท็บ `Team_Knowledge`) และอ่านเอกสารเสริมจากโฟลเดอร์ `Editor` บน Google Drive ของทีม (`omgdigital.developer.02@gmail.com`)

ทั้งหัวหน้าทีม (`admin`) และทีม Operation (`staff`) สามารถบันทึกและค้นหาความรู้ใหม่ร่วมกันได้ทันที **โดยไม่ต้องรอ `git push`** และไม่ต้องใช้ถังความจำส่วนตัว (`AI Agent Vault`)

---

## 1. `team_knowledge_search`

### Input schema
| Field | Type | Required | ความหมาย / ข้อจำกัด |
|---|---|---:|---|
| `query` | string | no | คำค้นหา (ค้นใน `topic_id`, `title`, `category`, `tags`, `content` และชื่อ/เนื้อหาไฟล์ใน Drive); เว้นว่างเพื่อดูรายการล่าสุด |
| `category` | string | no | กรองตามหมวดหมู่ เช่น `troubleshooting`, `sop`, `hardware`, `targetr`, `general` |
| `limit` | integer | no | จำนวนสูงสุดที่คืน (1–50, ค่าเริ่มต้น `10`) |

### Output schema
- คืน `sheet_entries` (รายการจากแท็บ `Team_Knowledge`) และ `drive_files` (ไฟล์ `.md`/`.txt`/Google Docs ในโฟลเดอร์ `Editor`) พร้อมลิงก์ `spreadsheet_url`

---

## 2. `team_knowledge_save`

### Input schema
| Field | Type | Required | ความหมาย / ข้อจำกัด |
|---|---|---:|---|
| `title` | string | yes | หัวข้อเรื่อง (ถ้าชื่อตรงกับรายการเดิมจะอัปเดตแถวเดิมให้อัตโนมัติ) |
| `content` | string | yes | เนื้อหาความรู้ อาการ สาเหตุ วิธีแก้ หรือขั้นตอนการทำงาน |
| `category` | string | no | หมวดหมู่ (ค่าเริ่มต้น `"general"`) |
| `tags` | string | no | คำค้นหาคั่นด้วยเครื่องหมายจุลภาค เช่น `"ติดใบ้,จอดำ,android"` |
| `updated_by` | string | no | ชื่อผู้บันทึกหรือทีม (ค่าเริ่มต้น `"team"`) |
| `topic_id` | string | no | รหัส `KB-xxx` กรณีต้องการอัปเดตหัวข้อเดิมเจาะจง |

### Output schema
- คืน `status="saved"`, `action` (`"created"` หรือ `"updated"`), `topic_id`, `updated_at`, และ `spreadsheet_url`

---

## Errors ที่ควรแยก
- `INVALID_INPUT`: ขาด `title` หรือ `content` หรือ `limit` นอกช่วง 1–50
- `CREDENTIALS_MISSING`: ไม่พบไฟล์ Google Service Account JSON
- `SHEETS_UNAVAILABLE` / `SHEETS_WRITE_FAILED`: ไม่สามารถอ่านหรือเขียน Google Sheet ได้
