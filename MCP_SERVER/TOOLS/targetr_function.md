# MCP Tool Contract: `targetr_function`

> สถานะ: อ่าน raw JSON จาก Neon ประมวลผลใน MCP และเขียนผลเป็นไฟล์ CSV บนเครื่องที่รัน MCP

## วัตถุประสงค์

ใช้เมื่อต้อง filter/ประมวลผล nested JSON ในตาราง `screen`, `sequence` หรือ `libraryitem` และต้องการส่งออกชุดข้อมูลทั้งหมดที่ตรงเงื่อนไขเป็น CSV ไม่ส่ง JSON dataset เข้า/ออกผ่าน context ของ Model

## Input

- `table`: `screen`, `sequence` หรือ `libraryitem`
- `filters`: รายการ AND filters; field ใช้ dot-path เช่น `data.data.sequenceId`; operators: `eq`, `ne`, `contains`, `in`, `exists`, `gt`, `gte`, `lt`, `lte`
- `fields`: dot-path projection ที่เลือกได้; ถ้าไม่ส่ง จะเขียนทุก top-level column รวม `data` ลง CSV (nested object/list ถูกเก็บเป็น JSON string ใน cell)
- `sort`: รายการ `{field, direction}`; direction `asc` หรือ `desc`
- `aggregate`: `{operation, field?, group_by?}`; operation `count`, `sum`, `avg`, `min`, `max`, `group_count`; เมื่อใช้ aggregate จะคืนผลสรุป JSON แทนไฟล์ CSV
- `limit`: optional; ไม่ส่งหมายถึงไม่จำกัดจำนวนแถว
- `offset`: จำนวนแถวที่ข้าม (default 0)

## Output

เมื่อต้อง export CSV:

```json
{
  "source": "targetr_neon_raw_processed",
  "table": "screen",
  "total_matched": 1000,
  "returned": 1000,
  "format": "csv",
  "file_path": "..."
}
```

ไฟล์ถูกสร้างบนเครื่อง MCP ใน `TARGETR_EXPORT_DIR`; หากไม่ได้ตั้งค่า ใช้ `exports/` ใต้ current working directory ของ MCP process. ผลลัพธ์ของ tool มีเฉพาะ metadata และ path ไม่ได้ส่ง CSV ทั้งก้อนเข้า Model. ผู้ใช้/Agent Host ต้องเข้าถึง path บนเครื่องดังกล่าวเพื่อเปิดหรือดาวน์โหลดไฟล์

## ข้อควรระวังและ errors

- ไม่มี hard cap จำนวน rows, ขนาด input, จำนวน fields หรือ output CSV; dataset ใหญ่มากใช้ memory/disk ตามขนาดข้อมูล เพราะ Neon API ส่งทุกแถวใน response เดียว
- ใช้ filter และ fields เพื่อให้ export ตรงความต้องการ; หากละ `fields` จะรวม raw JSONB `data` ใน CSV ด้วย
- `targetr_query` ยังคงไม่คืน raw `data`
- ห้ามใส่ credentials หรือ raw response ใน error/log; tool ไม่รองรับ arbitrary code execution
- `INVALID_INPUT`: table/filter/projection/sort/aggregate ไม่ถูกต้อง
- `SOURCE_UNAVAILABLE` / `SOURCE_RESPONSE_INVALID`: อ่าน Neon ไม่สำเร็จหรือ response ผิดรูปแบบ
