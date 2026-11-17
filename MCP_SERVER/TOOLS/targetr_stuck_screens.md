# MCP Tool Contract: `targetr_stuck_screens`

> สถานะ: พร้อมใช้งานใน `MCP_SERVER/jarvis_mcp/stuck_screens.py`

## วัตถุประสงค์

ใช้ค้นหาและแสดงรายการจอที่มีอาการ **“ติดใบ้” (`Player comms problem`)** คือ **DS Loader ยังออนไลน์ปกติ (`lastLoaderCommsMillis` ล่าสุด) แต่ตัวเล่นสื่อ (`lastPlayerCommsMillis`) ค้าง/เงียบหายไป** ทำให้หน้าเว็บแสดงสถานะ `On` สีเขียว แต่หน้าจอจริงจอดำไม่เล่นสื่อ

Tool จะคำนวณระยะเวลาที่ค้าง เรียงลำดับจากจอที่ค้างนานที่สุด และบันทึกผลทั้งหมดลงไฟล์ `SANDBOX/stuck_screens_report.csv`

## คำอธิบายสำหรับ Model

เรียกใช้เมื่อผู้ใช้ถามหาจอที่ “ติดใบ้”, จอที่ขึ้นเตือน `Player comms problem`, จอที่ขึ้น On สีเขียวแต่จอดำ/ไม่เล่นสื่อ, หรือขอดูรายการจอที่ต้องรีสตาร์ทแอป

## Input schema

| Field | Type | Required | ความหมาย / ข้อจำกัด |
|---|---|---:|---|
| `min_stuck_minutes` | integer | no | ระยะเวลาขั้นต่ำที่ Player เงียบเมื่อเทียบกับ Loader เป็นนาที (ค่าเริ่มต้น: `60`) |
| `loader_online_window_minutes` | integer | no | ช่วงเวลากี่นาทีล่าสุดที่ถือว่า DS Loader ยังออนไลน์ปกติ (ค่าเริ่มต้น: `10`) |
| `retailer` | string | no | กรองตามชื่อ Retailer เช่น `"Tops"`, `"Big C"` |
| `store_query` | string | no | ค้นหาบางส่วนของชื่อสาขา (`storeLocation`) หรือ `label` |
| `limit` | integer | no | จำนวนรายการสูงสุดที่คืนใน tool response (ค่าเริ่มต้น: `50`; ไฟล์ CSV จะบันทึกทั้งหมด) |
| `freshness` | string enum | no | `"refresh"` (ค่าเริ่มต้น — สั่ง sync จาก Target-R ก่อนอ่าน) หรือ `"cached"` |

## Output schema

```json
{
  "source": "targetr_neon_stuck_screens",
  "as_of_bkk": "2026-11-17 13:49:28",
  "min_stuck_minutes": 60,
  "loader_online_window_minutes": 10,
  "total_stuck": 10,
  "returned": 10,
  "csv_path": "C:\\OMG\\target-r-assistance\\SANDBOX\\stuck_screens_report.csv",
  "screens": [
    {
      "screenId": "02003E2C633A",
      "label": "BigC-Bangphlee...",
      "retailer": "Big C",
      "storeLocation": "Bangphlee",
      "STC": "11106",
      "hardwareModel": "HK1 RBOX K8",
      "activePlayer": "android-player-2023-06-02.apk",
      "lastLoaderCommsBkk": "2026-11-17 13:49:22",
      "lastPlayerCommsBkk": "2026-11-16 22:02:26",
      "stuck_minutes": 946,
      "stuck_duration": "15 ชม. 46 นาที",
      "recentStartCount": 1,
      "memFreeMB": 11.96,
      "anydesk": "1 234 567 890"
    }
  ]
}
```

## Errors ที่ควรแยก

- `INVALID_INPUT`: `min_stuck_minutes < 0`, `loader_online_window_minutes < 1`, หรือ `limit < 1`
- `SOURCE_UNAVAILABLE` / `SOURCE_RESPONSE_INVALID`: ไม่สามารถติดต่อ Neon Function หรือข้อมูลตอบกลับไม่ถูกต้อง
