# MCP Tool Contract: `prepare_targetr_update`

> สถานะ: พร้อมใช้งานใน `MCP_SERVER/jarvis_mcp/programmatic_helper.py`

## วัตถุประสงค์

ใช้จัดเตรียมข้อความและสร้างไฟล์ (TSV และ JSON) ลงในโฟลเดอร์ `SANDBOX/` เพื่อให้ผู้ใช้ก๊อปปี้ไปวางในหน้าเว็บเครื่องมือ **Manage Target-R** (`https://tops.actx.digital/manage_target_r`) โดย Tool นี้เป็นแบบ **Read/Generate-only** ไม่ยิงแก้ไขข้อมูลเข้า Target-R โดยตรง แต่สร้างชุดข้อมูลที่ผ่านการตรวจสอบฟอร์แมตแล้วพร้อมขั้นตอนให้ผู้ใช้เป็นคนกดอัปเดตเอง

## คำอธิบายสำหรับ Model

เรียกใช้เมื่อผู้ใช้ต้องการอัปเดตฟิลด์ข้อมูลของหน้าจอ (Screen) หลายจอพร้อมกัน, อัปเดตจอเดี่ยวด้วย JSON, แทรก Item เข้า Sequence หรืออัปเดต `customId` ของ Item เดิมใน Sequence บนเครื่องมือ `https://tops.actx.digital/manage_target_r`

## Input schema

| Field | Type | Required | ความหมาย / ข้อจำกัด |
|---|---|---:|---|
| `mode` | string enum | yes | โหมดการทำงาน: `multiple_update_screens`, `single_screen_json`, `insert_sequence_items`, `update_existing_sequence_items` |
| `rows` | array of object | yes | รายการข้อมูลแต่ละแถวตามโหมดที่เลือก (ห้ามว่าง) |
| `target_id` | string | no | รหัส `Screen ID` (สำหรับ `single_screen_json`) หรือ `Sequence ID` (บังคับสำหรับโหมด sequence) |
| `filename_prefix` | string | no | คำนำหน้าชื่อไฟล์ที่จะบันทึกใน `SANDBOX/` (ค่าเริ่มต้น: `manage_target_r`) |

### โครงสร้าง `rows` ตาม `mode`

1. **`multiple_update_screens`** (อัปเดตฟิลด์ข้อมูลหลายจอพร้อมกัน):
   - แต่ละ object ต้องมี `screen_id` (หรือ `screenId`) และฟิลด์ที่ต้องการอัปเดต เช่น `gpsLatitude`, `gpsLongitude`, `orientation`, `storeLocation` (หากมี `data.` นำหน้าจะถูกตัดออกให้อัตโนมัติ)
2. **`single_screen_json`** (อัปเดตจอเดี่ยวด้วย JSON):
   - ส่ง object ของฟิลด์ที่จะอัปเดตใน `rows[0]` พร้อมระบุ `target_id` (หรือใส่ `screen_id` ใน `rows[0]`)
3. **`insert_sequence_items`** (แทรก Item เข้า Sequence):
   - ต้องระบุ `target_id` เป็น Sequence ID เป้าหมาย
   - แต่ละ object ใน `rows` ต้องมี `inner_sequence_id`, `slot` (เริ่มที่ 1), `item` (เริ่มที่ 1) และฟิลด์เสริมอื่นๆ เช่น `label`, `condition`
4. **`update_existing_sequence_items`** (อัปเดต `customId` ของ Item เดิมใน Sequence):
   - ต้องระบุ `target_id` เป็น Sequence ID เป้าหมาย
   - แต่ละ object ใน `rows` ต้องมี `inner_sequence_id`, `slot`, `item`, `customId`

## Output schema

```json
{
  "url": "https://tops.actx.digital/manage_target_r",
  "mode": "multiple_update_screens",
  "record_count": 2,
  "headers": ["screen_id", "gpsLatitude", "gpsLongitude"],
  "paste_format": "TSV",
  "paste_content": "screen_id\tgpsLatitude\tgpsLongitude\n06BC202512DB\t13.7367\t100.5231\n06BC202512DC\t13.7450\t100.5340",
  "json_content": [
    {
      "screen_id": "06BC202512DB",
      "gpsLatitude": "13.7367",
      "gpsLongitude": "100.5231"
    },
    {
      "screen_id": "06BC202512DC",
      "gpsLatitude": "13.7450",
      "gpsLongitude": "100.5340"
    }
  ],
  "saved_files": {
    "tsv_path": "C:\\OMG\\target-r-assistance\\SANDBOX\\manage_target_r_multiple_screens_20261117_035500.tsv",
    "json_path": "C:\\OMG\\target-r-assistance\\SANDBOX\\manage_target_r_multiple_screens_20261117_035500.json"
  },
  "instructions": [
    "1. เปิดลิงก์ https://tops.actx.digital/manage_target_r",
    "2. คลิกแท็บ 'Manage Screen' แล้วเลือกปุ่ม 'Update Screen'",
    "3. คลิกปุ่ม 'Multiple Update' เพื่อเปิดหน้าต่าง Multiple Update Screens",
    "4. คัดลอกข้อมูล TSV (paste_content) ไปวางในช่อง 'Paste Excel Data (TSV)' ด้านซ้าย",
    "5. ตรวจสอบตาราง Preview & Status ด้านขวา แล้วกดปุ่ม 'Start Update'"
  ]
}
```

## Errors ที่ควรแยก

- `INVALID_INPUT`: ขาดฟิลด์บังคับ เช่น ไม่มี `screen_id`, ไม่มีฟิลด์ข้อมูลที่จะอัปเดต, ไม่ได้ระบุ `target_id` ในโหมดที่ต้องใช้ หรือ `rows` เป็นลิสต์ว่าง
