# MCP Server Index

MCP Server เปิด tools ให้ Agent เรียกใช้ความสามารถของระบบและข้อมูลภายใน โดย Agent ต้องตรวจรายการ tools และ schema ที่ MCP Server เปิดให้จริงก่อนเรียกใช้งาน. รันเริ่มต้นผ่าน Python MCP SDK แบบ stdio; tool cache อยู่ใน process memory.

## สถานะ

มี Python MCP tools `targetr_query` สำหรับ query ข้อมูล Target-R ที่ sync อยู่ใน Neon และ `targetr_function` สำหรับรัน declarative JSON pipeline กับ raw rows ที่อ่านจาก Neon โดยประมวลผลภายใน MCP เท่านั้น

## Tool Registry

| Tool | ใช้เมื่อ | Input ที่ต้องมี | Output ที่คืน | รายละเอียด |
|---|---|---|---|---|
| `targetr_query` | Query Screen, Sequence หรือ Library item; DS Loader เป็นคำเรียกที่ผู้ใช้อาจใช้แทน Target-R | entity, operation; filters/fields/group_by ตาม operation; freshness เลือก cached หรือ refresh | count, selected rows หรือ grouped counts แบบจำกัด; ไม่มี raw `data` | [`TOOLS/targetr_query.md`](TOOLS/targetr_query.md) |
| `targetr_function` | ประมวลผล raw JSON ใน Neon แล้ว export CSV ทั้งชุดที่ตรงเงื่อนไข | table; filter/fields/sort/aggregate/limit/offset optional | local CSV file path กับจำนวนแถว; dataset ไม่ถูกส่งใน tool response | [`TOOLS/targetr_function.md`](TOOLS/targetr_function.md) |
| `geo_distance` | คำนวณระยะทางและจัดอันดับสถานที่ใกล้เคียงจากพิกัด lat/long | origin, destinations; max_distance_km, limit, unit optional | รายการสถานที่ใกล้เคียงเรียงตามระยะทาง; ไม่คืน raw coordinates ซ้ำ | [`TOOLS/geo_distance.md`](TOOLS/geo_distance.md) |
| `targetr_fuzzy_search` | ค้นหาชื่อสาขา ห้าง โครงการ หรือประเภทจอแบบยืดหยุ่น ดักคำสะกดผิด/คำย่อ | query; entity_type, threshold, limit optional | รายการชื่อ canonical พร้อมคะแนนความมั่นใจและ matched field | [`TOOLS/fuzzy_search.md`](TOOLS/fuzzy_search.md) |
| `send_email` | ส่งอีเมลแจ้งเตือน รายงาน หรือ Alerts ผ่าน Gmail SMTP | to, subject, body; is_html, cc optional | ผลลัพธ์สถานะการส่ง (success), timestamp, รายชื่อผู้รับ | [`TOOLS/send_email.md`](TOOLS/send_email.md) |
| `prepare_targetr_update` | สร้างข้อมูล TSV/JSON และบันทึกไฟล์ลง `SANDBOX/` เพื่อให้ผู้ใช้นำไปวางอัปเดตข้อมูลหลายรายการพร้อมกันในเครื่องมือ `manage_target_r` | mode, rows; target_id, filename_prefix optional | ข้อความ TSV/JSON พร้อมก๊อปปี้, path ไฟล์ที่บันทึก, ลิงก์เครื่องมือ และขั้นตอนการใช้งาน | [`TOOLS/prepare_targetr_update.md`](TOOLS/prepare_targetr_update.md) |
| `targetr_stuck_screens` | ค้นหาจอที่ติดใบ้ (`Player comms problem` — Loader ออนไลน์แต่ Player ค้างจอดำ) | min_stuck_minutes, loader_online_window_minutes, retailer, store_query, limit, freshness optional | รายการจอติดใบ้เรียงตามเวลาที่ค้าง + path ไฟล์ CSV ใน `SANDBOX/` | [`TOOLS/targetr_stuck_screens.md`](TOOLS/targetr_stuck_screens.md) |

## ข้อกำหนดสำหรับ tools

- คำอธิบาย tool ต้องระบุงานที่ทำและสถานการณ์ที่ควรใช้ให้ชัดเจน
- Input schema ต้องระบุชนิดข้อมูล, required fields, ขอบเขต/ค่าเริ่มต้น และข้อจำกัด
- Output ต้องมีโครงสร้างคงที่ อธิบายตัวเองได้ และระบุ source/เวลาเมื่อเหมาะสม
- จำกัดจำนวนผลลัพธ์และขนาดข้อมูล; คืนเฉพาะฟิลด์ที่จำเป็น ห้ามคืน raw response โดยปริยาย
- กำหนด errors ที่คาดหมายและวิธีที่ Agent ควรตอบเมื่อเกิดข้อผิดพลาด
- ใช้ read-only เป็นค่าเริ่มต้น; tool ที่เขียนหรือสั่งงานต้องมี policy, validation และการยืนยันที่ชัดเจน
- MCP Server/Gateway เป็นผู้ถือ credentials และเรียก upstream API; ห้ามให้ Agent หรือ Model รับ credentials

## วิธีเพิ่ม tool

เมื่อเพิ่ม tool ให้ลงทะเบียนใน Tool Registry พร้อมคำอธิบาย, เงื่อนไขการใช้, input ที่จำเป็น และผลลัพธ์ที่คืน จากนั้นเพิ่มรายละเอียดเชิงเทคนิคและ tests ในตำแหน่ง implementation ของ MCP Server
