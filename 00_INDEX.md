---
type: index
status: active
updated: 2026-11-18
related:
  - "[[AGENTS]]"
  - "[[SKILLS/index]]"
  - "[[MCP_SERVER/index]]"
  - "[[KNOWLEDGE/index]]"
  - "[[SHEETS_INDEX]]"
  - "[[KNOWLEDGE/target-r/00_TARGET_R_INDEX]]"
  - "[[KNOWLEDGE/android-box/00_ANDROID_BOX_INDEX]]"
  - "[[KNOWLEDGE/hikvision/00_HIKVISION_INDEX]]"
---

# 00_INDEX — สารบัญหลักระบบ Jarvis (Pyramid Root)

ไฟล์นี้คือ **ยอดปิรามิดและประตูแรก (Level 0 Entry Point)** ของโปรเจกต์ `target-r-assistance` ใช้เป็นไฟล์แรกที่ AI Agent ต้องอ่านเสมอเมื่อเริ่มต้นทุกคำถามหรือทุกคำสั่ง (คู่กับกฎระบบใน [`AGENTS.md`](AGENTS.md))

---

## Purpose

โปรเจกต์ `target-r-assistance` คือระบบผู้ช่วย AI (Jarvis) สำหรับทีม Operation และผู้ดูแลระบบ ใช้ตรวจสอบ วิเคราะห์ข้อมูล Target-R / DS Loader, ค้นหาตำแหน่งและผังสาขา, เตรียมไฟล์อัปเดตสำหรับ **Act-X Programmatic CMS**, แลกเปลี่ยนคลังความรู้หน้างานของทีมแบบ Real-time และควบคุมจอ Sharp Smart TV ในห้องทำงาน ผ่าน Antigravity Desktop และ Python MCP Server

---

## โครงสร้างปิรามิดการสืบค้น (Pyramid Architecture)

ทุกคำถามต้องวิ่งจาก **ชั้นที่ 0** ลงสู่ **ชั้นที่ 1 -> ชั้นที่ 2 -> ชั้นที่ 3** ตามลำดับ ห้ามกระโดดข้ามไปค้นหรือเดาเองก่อนอ่านสารบัญ:

```text
                       [ ชั้นที่ 0: ยอดปิรามิด ]
                 00_INDEX.md  (+ กฎระบบ AGENTS.md)
                                  │
       ┌──────────────────┬───────┴────────┬──────────────────┐
       ▼                  ▼                ▼                  ▼
 [ ชั้นที่ 1: เสาหลัก ]
 SKILLS/index.md    MCP_SERVER/      KNOWLEDGE/       SHEETS_INDEX.md
 (วิธีคิด/ขั้นตอน)    index.md         index.md         (โครงสร้าง Google
                    (10 Tools)       (คลังเทคนิค)       Sheets ที่เชื่อม)
       │                  │                │                  │
       ▼                  ▼                ▼                  ▼
 [ ชั้นที่ 2: ดัชนีย่อยและคู่มือเฉพาะทาง ]
 SKILLS/*.md        MCP_SERVER/      00_TARGET_R_     Jarvis_TargetR_Master
 (6 Skills)         TOOLS/*.md       INDEX.md         Tops Monitor
                    (9 Tool Docs)    00_ANDROID_BOX_  (Schema & Keys)
                                     INDEX.md
                                     00_HIKVISION_
                                     INDEX.md
                                           │
                                           ▼
 [ ชั้นที่ 3: เอกสารรายละเอียดและพื้นที่ทำงาน ]
 สเปกฮาร์ดแวร์ / Data Model / API Docs / SANDBOX/ (ไฟล์ผลลัพธ์ .csv .tsv .json)
```

---

## แผนผังนำทางตามคำถาม (Master Question Routing)

ทุกคำถามที่เข้ามา ให้จับคู่เจตนาของผู้ใช้จากตารางนี้แล้วเดินลงตามชั้นของปิรามิดทันที:

| # | เรื่องที่ถาม / งานที่สั่ง | ชั้นที่ 1 (Index หมวด) | ชั้นที่ 2 (Skill / Sub-index / Tool Doc ที่ต้องอ่าน) | MCP Tool / แหล่งข้อมูลที่ใช้จริง |
|---|---|---|---|---|
| 1 | ถามจำนวนจอ, สถานะ Online/Offline (เกณฑ์ 1 ชม.), ข้อมูลสาขา, Sequence, Library, หรือขอเลข MAC / Screen ID | [`SKILLS/index.md`](SKILLS/index.md) | [`SKILLS/targetr_system.md`](SKILLS/targetr_system.md) + [`MCP_SERVER/TOOLS/targetr_query.md`](MCP_SERVER/TOOLS/targetr_query.md) + [`MCP_SERVER/TOOLS/fuzzy_search.md`](MCP_SERVER/TOOLS/fuzzy_search.md) + [`MCP_SERVER/TOOLS/targetr_function.md`](MCP_SERVER/TOOLS/targetr_function.md) | `targetr_query`, `targetr_fuzzy_search`, `targetr_function` |
| 2 | ถามเรื่อง **จอติดใบ้ / จอดำแต่ขึ้น On สีเขียว (`Player comms problem`)** | [`SKILLS/index.md`](SKILLS/index.md)<br/>[`KNOWLEDGE/index.md`](KNOWLEDGE/index.md) | [`SKILLS/targetr_system.md`](SKILLS/targetr_system.md) + [`MCP_SERVER/TOOLS/targetr_stuck_screens.md`](MCP_SERVER/TOOLS/targetr_stuck_screens.md) + [`KNOWLEDGE/target-r/TargetR_Player_Comms_Problem_Troubleshooting.md`](KNOWLEDGE/target-r/TargetR_Player_Comms_Problem_Troubleshooting.md) | `targetr_stuck_screens` (ส่งออก CSV ลง `SANDBOX/`) |
| 3 | ค้นหา **จอ ห้าง หรือสาขาใกล้เคียงตามพิกัดภูมิศาสตร์** | [`SKILLS/index.md`](SKILLS/index.md) | [`SKILLS/screen_location.md`](SKILLS/screen_location.md) + [`MCP_SERVER/TOOLS/geo_distance.md`](MCP_SERVER/TOOLS/geo_distance.md) | `targetr_query` -> `geo_distance` (Tool Chaining) |
| 4 | เตรียมไฟล์ **TSV / JSON สำหรับอัปเดตหลายจอหรือแก้ไข Sequence** ใน `manage_target_r` | [`SKILLS/index.md`](SKILLS/index.md) | [`SKILLS/manage_target_r.md`](SKILLS/manage_target_r.md) + [`MCP_SERVER/TOOLS/prepare_targetr_update.md`](MCP_SERVER/TOOLS/prepare_targetr_update.md) | `prepare_targetr_update` (บันทึกไฟล์ลง `SANDBOX/`) |
| 5 | ถามวิธีใช้งานหรือเตรียมข้อมูลเข้าเว็บ **`https://tops.actx.digital`** (Act-X Programmatic CMS ทั้ง 15 เครื่องมือ) | [`SKILLS/index.md`](SKILLS/index.md) | [`SKILLS/programmatic_cms_guide.md`](SKILLS/programmatic_cms_guide.md) | คู่มือ 15 หน้า CMS + `targetr_fuzzy_search` / `targetr_query` / `prepare_targetr_update` |
| 6 | สั่ง **ควบคุมจอ Sharp Smart TV ในห้องทำงาน** (`จอซ้าย`/`จอ 2`, `จอขวา`/`จอ 3` เปิดเว็บ, เปิด/รีสตาร์ท `dsloader`, สลับ HDMI/OS, เช็คสถานะ) | [`SKILLS/index.md`](SKILLS/index.md)<br/>[`KNOWLEDGE/index.md`](KNOWLEDGE/index.md) | [`SKILLS/tv_control.md`](SKILLS/tv_control.md) + [`MCP_SERVER/TOOLS/tv_control.md`](MCP_SERVER/TOOLS/tv_control.md) + [`KNOWLEDGE/android-box/Sharp_TV_Tailscale_ADB_Runbook.md`](KNOWLEDGE/android-box/Sharp_TV_Tailscale_ADB_Runbook.md) | `tv_control` (ADB over Tailscale) |
| 7 | สั่ง **จดบันทึกความรู้หน้างาน/SOP ใหม่** หรือ **ค้นหาวิธีแก้ปัญหาที่ทีมบันทึกไว้แบบ Real-time** | [`SKILLS/index.md`](SKILLS/index.md)<br/>[`SHEETS_INDEX.md`](SHEETS_INDEX.md) | [`SKILLS/team_knowledge.md`](SKILLS/team_knowledge.md) + [`MCP_SERVER/TOOLS/team_knowledge.md`](MCP_SERVER/TOOLS/team_knowledge.md) | `team_knowledge_search`, `team_knowledge_save` (แท็บ `Team_Knowledge` & Google Drive) |
| 8 | ถาม **Data Model, โครงสร้าง JSON, หรือ API เชิงเทคนิคของ Target-R / Neon Sync** | [`KNOWLEDGE/index.md`](KNOWLEDGE/index.md) | [`KNOWLEDGE/target-r/00_TARGET_R_INDEX.md`](KNOWLEDGE/target-r/00_TARGET_R_INDEX.md) | เอกสาร 14 ไฟล์ใน `KNOWLEDGE/target-r/` |
| 9 | ถาม **สเปกกล่อง Android Box (`HK1 RBOX K8`, `AIS Playbox กลม`, `ACTMEDIA RK3328`) หรือปัญหาพิกัด Wi-Fi / GPS เพี้ยน** | [`KNOWLEDGE/index.md`](KNOWLEDGE/index.md) | [`KNOWLEDGE/android-box/00_ANDROID_BOX_INDEX.md`](KNOWLEDGE/android-box/00_ANDROID_BOX_INDEX.md) | เอกสาร 6 ไฟล์ใน `KNOWLEDGE/android-box/` |
| 10 | ถาม **สเปกจอ HIKVISION, การตั้งค่า AnyDesk/ADB, MPV Player, หรือกล้อง USB UVC** | [`KNOWLEDGE/index.md`](KNOWLEDGE/index.md) | [`KNOWLEDGE/hikvision/00_HIKVISION_INDEX.md`](KNOWLEDGE/hikvision/00_HIKVISION_INDEX.md) | เอกสาร 4 ไฟล์ใน `KNOWLEDGE/hikvision/` |
| 11 | ถาม **ชื่อสาขาภาษาไทย/คำย่อ หรือตำแหน่งจุดติดตั้งจอและเราเตอร์บนผังร้าน (Floor Plan)** | [`SHEETS_INDEX.md`](SHEETS_INDEX.md) | [`SHEETS_INDEX.md`](SHEETS_INDEX.md) | Google Sheets `Jarvis_TargetR_Master` (`Location`, `Projects`, `Labels`) และ `Tops Monitor` |
| 12 | สั่ง **ส่งอีเมลรายงานหรือ Alerts** | [`MCP_SERVER/index.md`](MCP_SERVER/index.md) | [`MCP_SERVER/TOOLS/send_email.md`](MCP_SERVER/TOOLS/send_email.md) | `send_email` (Gmail SMTP) |

---

## Main Folders & Root Files

- [`00_INDEX.md`](00_INDEX.md) = ยอดปิรามิด: สารบัญกลางและแผนผังนำทางทุกคำถาม
- [`AGENTS.md`](AGENTS.md) = กฎระบบหลัก ขั้นตอนการทำงานของ Agent และสิทธิ์ `PERMISSION` (`staff` / `admin`)
- `SKILLS/` = กฎการตัดสินใจ ลำดับขั้นการทำงาน และคู่มือเฉพาะงาน (Workflows)
- `MCP_SERVER/` = Python FastMCP Server (`jarvis_mcp/`), เอกสาร Contract (`TOOLS/*.md`) และ Unit Tests (`tests/`)
- `KNOWLEDGE/` = คลังความรู้ทางเทคนิคที่คัดกรองและตัดค่าลับออกแล้ว แบ่งเป็น `target-r/`, `android-box/`, `hikvision/`
- [`SHEETS_INDEX.md`](SHEETS_INDEX.md) = Data Dictionary ของ Google Sheets (`Jarvis_TargetR_Master`, `Tops Monitor`)
- `SANDBOX/` = พื้นที่ทำงานและเก็บไฟล์ผลลัพธ์ชั่วคราว (`.csv`, `.tsv`, `.json`, สคริปต์ทดสอบ) — ดู [`SANDBOX/README.md`](SANDBOX/README.md)
- [`setup_team.bat`](setup_team.bat) & [`README.md`](README.md) = คู่มือและสคริปต์ติดตั้งระบบสำหรับทีม Operation

---

## Folder Indexes (ประตูเชื่อมจากยอดปิรามิด)

### ชั้นที่ 1 — ดัชนีเสาหลัก 4 หมวด
- [`SKILLS/index.md`](SKILLS/index.md) = ประตูแรกของโฟลเดอร์ `SKILLS/` (เลือกแนวทางและกฎของงาน)
- [`MCP_SERVER/index.md`](MCP_SERVER/index.md) = ประตูแรกของโฟลเดอร์ `MCP_SERVER/` (ตรวจสอบ 10 MCP tools ที่เรียกได้จริง)
- [`KNOWLEDGE/index.md`](KNOWLEDGE/index.md) = ประตูแรกของโฟลเดอร์ `KNOWLEDGE/` (คลังความรู้ทางเทคนิค)
- [`SHEETS_INDEX.md`](SHEETS_INDEX.md) = ประตูแรกของข้อมูล Google Sheets และ Floor Plan

### ชั้นที่ 2 — ดัชนีย่อยในคลังความรู้
- [`KNOWLEDGE/target-r/00_TARGET_R_INDEX.md`](KNOWLEDGE/target-r/00_TARGET_R_INDEX.md) = ดัชนีหมวด Target-R Data Model, Neon Sync, Troubleshooting และ API
- [`KNOWLEDGE/android-box/00_ANDROID_BOX_INDEX.md`](KNOWLEDGE/android-box/00_ANDROID_BOX_INDEX.md) = ดัชนีหมวด Android TV Box และคู่มือ Sharp Smart TV
- [`KNOWLEDGE/hikvision/00_HIKVISION_INDEX.md`](KNOWLEDGE/hikvision/00_HIKVISION_INDEX.md) = ดัชนีหมวดจอ HIKVISION, AnyDesk/ADB, MPV และ USB Camera

---

## Search & Retrieval Policy (กฎการสืบค้นแบบปิรามิด)

1. **อ่านยอดปิรามิดก่อนเสมอ**: ทุกคำถามต้องเปิดอ่าน [`00_INDEX.md`](00_INDEX.md) เป็นอันดับแรก ห้ามรัน `grep`/ค้นไฟล์สุ่มหรือเรียก Tool ทันทีโดยไม่ผ่านการคัดแยกเส้นทาง
2. **เดินตามลำดับชั้น (Top-Down Traversal)**:
   - อ่าน `00_INDEX.md` -> เลือกเสาหลักชั้นที่ 1 (`SKILLS/index.md`, `MCP_SERVER/index.md`, `KNOWLEDGE/index.md`, `SHEETS_INDEX.md`)
   - เปิดอ่าน Skill และ Tool Contract หรือ Sub-index ชั้นที่ 2 ให้ครบ
   - ลงไปอ่านเอกสารชั้นที่ 3 หรือเรียก MCP Tool ด้วย Schema ที่ถูกต้อง
3. **ยึดหลักฐานจาก Tool และเอกสารจริง**: ห้ามเดาข้อมูล, ห้ามสร้าง field นอก schema, และให้แจ้งข้อจำกัดตรง ๆ หากไม่มี Skill หรือ Tool รองรับ
4. **กรณีค้นความรู้ทีมหน้างาน**: หากเป็นเคสปัญหาหน้างานหรือ SOP เฉพาะสาขา ให้เช็คทั้ง `KNOWLEDGE/` ในเครื่อง และเรียก `team_knowledge_search` เพื่อดูอัปเดตล่าสุดจากทีมด้วย

---

## Root & Workspace Policy

- **ไฟล์ระดับ Root**: เก็บเฉพาะไฟล์แกนกลาง (`00_INDEX.md`, `AGENTS.md`, `SHEETS_INDEX.md`, `README.md`, `setup_team.bat`, config) **ห้าม** สร้างสคริปต์ทดสอบหรือไฟล์ผลลัพธ์ชั่วคราวที่ Root ให้สร้างใน `SANDBOX/` เท่านั้น
- **ความปลอดภัยและความลับ**: ห้ามเรียก external API โดยตรงจาก Model และห้ามบันทึก `password`, `token`, Credentials หรือ Service Account JSON ลงใน `00_INDEX.md`, `SKILLS/` หรือ `KNOWLEDGE/`
- **สิทธิ์การใช้งาน (`PERMISSION` ใน `.env`)**:
  - `PERMISSION=staff`: อ่านเอกสาร ใช้ MCP tools และสร้างไฟล์ใน `SANDBOX/` เท่านั้น (ห้ามแก้ไฟล์ระบบ/เอกสารใน repo ยกเว้นบันทึกความรู้ทีมผ่าน `team_knowledge_save`)
  - `PERMISSION=admin`: ปรับปรุงโครงสร้างปิรามิด โค้ด `MCP_SERVER/`, `SKILLS/` และ `KNOWLEDGE/` ได้ทั้งหมด
- **กฎการอัปเดตปิรามิด**: เมื่อเพิ่ม Skill ใหม่, MCP Tool ใหม่, ชีตใหม่ หรือโฟลเดอร์ความรู้ใหม่ ต้องอัปเดตทั้งดัชนีชั้นที่ 1/ชั้นที่ 2 ของหมวดนั้น **และ** เพิ่มเส้นทางในตารางนำทางของ [`00_INDEX.md`](00_INDEX.md) เสมอ
