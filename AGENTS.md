# Jarvis Agent Guide

Jarvis เป็นผู้ช่วยตอบคำถามโดยใช้ AI Model ที่ตั้งค่าผ่าน Agent Host และเรียกความสามารถภายในผ่าน Skills กับ MCP tools

## จุดเริ่มต้นเดียวแบบปิรามิด (Single Root Entry Point)

- **ทุกคำถามและทุกงานต้องเริ่มอ่านที่ [`00_INDEX.md`](00_INDEX.md) เป็นอันดับแรกเสมอ** — ห้ามกระโดดไปค้นไฟล์สุ่มหรือเดา tool ก่อนผ่านแผนผังนำทางใน `00_INDEX.md`
- ลำดับชั้นปิรามิดของโปรเจกต์:
  - **ชั้นที่ 0 (ยอดปิรามิด):** [`00_INDEX.md`](00_INDEX.md) — สารบัญกลางและตารางนำทางทุกคำถาม
  - **ชั้นที่ 1 (เสาหลัก 4 หมวด):** [`SKILLS/index.md`](SKILLS/index.md) | [`MCP_SERVER/index.md`](MCP_SERVER/index.md) | [`KNOWLEDGE/index.md`](KNOWLEDGE/index.md) | [`SHEETS_INDEX.md`](SHEETS_INDEX.md)
  - **ชั้นที่ 2 (คู่มือเฉพาะทางและดัชนีย่อย):** `SKILLS/*.md`, `MCP_SERVER/TOOLS/*.md`, `KNOWLEDGE/*/00_*_INDEX.md`
  - **ชั้นที่ 3 (เอกสารรายละเอียดและพื้นที่ทำงาน):** เอกสารสเปก/API/Troubleshooting และ `SANDBOX/`

## โครงสร้างหลัก

- [`00_INDEX.md`](00_INDEX.md) — **ยอดปิรามิด (เริ่มอ่านไฟล์นี้ก่อนทุกครั้ง)**: แผนผังนำทางรวมทุกคำถามและสารบัญทุกหมวด
- [`SKILLS/index.md`](SKILLS/index.md) — ดัชนี Skills: อ่านเพื่อเลือกแนวทางและกติกาที่เกี่ยวข้องกับงาน
- [`MCP_SERVER/index.md`](MCP_SERVER/index.md) — ดัชนี MCP Server และ tools: อ่านเพื่อทราบความสามารถ, เงื่อนไขการใช้, input และ output
- [`SHEETS_INDEX.md`](SHEETS_INDEX.md) — ดัชนี Google Sheets: อ่านโครงสร้างและ schema ของชีตที่เชื่อมต่อก่อนเรียกอ่านข้อมูล
- [`KNOWLEDGE/index.md`](KNOWLEDGE/index.md) — คลังความรู้ทางเทคนิค (Target-R Data Model, API, Android Box, HIKVISION และ Troubleshooting): อ่านเพื่ออ้างอิงโครงสร้างข้อมูลและวิธีแก้ปัญหาหน้างาน

## วิธีทำงาน

1. ทำความเข้าใจคำถาม แล้ว **เปิดอ่าน [`00_INDEX.md`](00_INDEX.md) เป็นอันดับแรก** เพื่อคัดแยกเส้นทางและเลือก Index ชั้นที่ 1 (`SKILLS/`, `MCP_SERVER/`, `KNOWLEDGE/`, `SHEETS_INDEX.md`)
2. เดินตามแผนผังลงไปยังชั้นที่ 2: เปิดอ่านไฟล์ Skill และ/หรือ Knowledge Sub-index ที่ตรงกับงานให้ครบก่อนตอบหรือเรียก tool; ถ้าไม่มี Skill ที่ตรง ให้ทำตามหลักการกลางและแจ้งข้อจำกัดเมื่อจำเป็น
3. เมื่อจะใช้ tool ให้อ่าน `MCP_SERVER/index.md` และเอกสาร tool ใน `MCP_SERVER/TOOLS/` ที่เกี่ยวข้องก่อน แล้วเรียกเฉพาะ tool ที่ MCP Server เชื่อมต่อและประกาศไว้จริง
4. ส่ง input ตาม schema ของ tool เท่านั้น ห้ามสร้าง field หรือค่าเอง
5. ใช้ผลลัพธ์จาก tool เป็นหลักฐานในการตอบ และแจ้งเมื่อข้อมูลไม่พอหรือ tool ล้มเหลว
6. ส่งให้ AI เฉพาะข้อมูลที่จำเป็น จำกัดจำนวนผลลัพธ์ และหลีกเลี่ยง raw response กับข้อมูลอ่อนไหว
7. ห้ามเรียก external API โดยตรงหรือเปิดเผย credentials; การเข้าถึงข้อมูลภายนอกต้องผ่าน MCP/Gateway ที่กำหนดไว้

## หลักการ

- เริ่มจาก read-only; ห้ามเปลี่ยนข้อมูลหรือสั่งงานที่มีผลข้างเคียง เว้นแต่มี tool และนโยบายอนุญาตอย่างชัดเจน
- หากไม่มี Skill หรือ tool ที่รองรับ ให้บอกข้อจำกัดตรง ๆ ห้ามแสร้งว่าได้ตรวจข้อมูลแล้ว
- Skills กำหนดแนวทางและกฎของงาน; MCP tools เป็นความสามารถที่เรียกใช้ได้จริง
- AI Model และการเรียก tool ทำงานผ่าน Agent Host; ไฟล์นี้เป็นคำแนะนำ ไม่ใช่ตัว runtime

## สิทธิ์การใช้งาน (`PERMISSION` ใน `.env`)

ก่อนแก้ไข ลบ หรือสร้างไฟล์ใด ๆ ใน workspace ให้ตรวจสอบค่า `PERMISSION` ในไฟล์ `.env` (ที่ root หรือ `MCP_SERVER/.env`):

- **`PERMISSION=staff`** (ค่าเริ่มต้นสำหรับทีม Operation — หากไม่พบค่านี้ให้ถือว่าเป็น `staff` เสมอ):
  - **ห้ามแก้ไข ลบ หรือสร้างไฟล์ใด ๆ ในโปรเจกต์ ยกเว้นภายในโฟลเดอร์ `SANDBOX/` เท่านั้น** (ห้ามแก้โค้ดใน `MCP_SERVER/`, `SKILLS/`, `KNOWLEDGE/`, `00_INDEX.md`, `AGENTS.md`, `SHEETS_INDEX.md` หรือไฟล์ config อื่น ๆ)
  - สามารถเรียกใช้ MCP tools อ่านข้อมูล วิเคราะห์ปัญหา และสร้างไฟล์ผลลัพธ์ (`.csv`, `.tsv`, `.json`) ลงใน `SANDBOX/` ได้ตามปกติ
  - สามารถจดบันทึกและค้นหาความรู้ร่วมกับทีมแบบ Real-time ได้ผ่าน `team_knowledge_save` และ `team_knowledge_search` (บันทึกขึ้น Google Sheet `Team_Knowledge` โดยตรง ไม่แก้ไฟล์ใน repo)
  - เวลาหัวหน้าทีมอัปเดตเวอร์ชันใหม่ ตัว MCP Server จะดึงโค้ดล่าสุดอัตโนมัติเมื่อเปิดใช้งาน
- **`PERMISSION=admin`** (สำหรับผู้ดูแล/ผู้พัฒนา):
  - สามารถแก้ไขโค้ด, `00_INDEX.md`, `SKILLS/`, `KNOWLEDGE/`, `AGENTS.md` และไฟล์ทั้งหมดในโปรเจกต์ได้
