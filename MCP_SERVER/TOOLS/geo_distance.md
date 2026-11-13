# MCP Tool Contract: `geo_distance`

> สถานะ: ออกแบบ contract สำหรับคำนวณระยะทางทางภูมิศาสตร์และจัดอันดับสถานที่ใกล้เคียง

## วัตถุประสงค์

ใช้คำนวณระยะห่างระหว่างจุดพิกัดอ้างอิง (origin) กับรายการพิกัดเป้าหมาย (destinations) ด้วยสูตร Haversine โดยกรองเฉพาะจุดที่อยู่ในรัศมีที่กำหนดและจัดอันดับจากใกล้ไปไกล ไม่ส่ง raw coordinates หรือคำนวณซ้ำซ้อนใน context ของ AI

## คำอธิบายสำหรับ Model

ใช้เมื่อต้องการค้นหาจอ ห้าง หรือสถานที่ที่อยู่ใกล้จุดพิกัดอ้างอิง โดยรับพิกัด origin และรายการ destinations พร้อมกำหนดรัศมี (`max_distance_km`) หรือจำนวนผลลัพธ์ (`limit`) Tool จะคำนวณระยะทาง กรอง และเรียงลำดับให้ โดยคืนเฉพาะชื่อ/label และระยะทางที่คำนวณได้

## Input schema

| Field | Type | Required | ความหมาย / ข้อจำกัด |
|---|---|---:|---|
| `origin` | object | yes | พิกัดอ้างอิง `{ "latitude": float, "longitude": float }` |
| `destinations` | array of object | yes | รายการจุดเป้าหมาย แต่ละจุดประกอบด้วย `{ "id": string, "label": string, "latitude": float, "longitude": float }` |
| `max_distance_km` | float | no | รัศมีสูงสุดเป็นกิโลเมตร (เช่น 5.0); หากไม่ระบุจะไม่กรองด้วยระยะทาง |
| `limit` | integer | no | จำนวนผลลัพธ์สูงสุดที่ต้องการคืน (default: 5, max: 20) |
| `unit` | string enum | no | หน่วยระยะทาง: `km` (default) หรือ `m` |

## Output schema

```json
{
  "source": "geo_calc",
  "origin": {
    "latitude": 13.7469,
    "longitude": 100.5398
  },
  "total_matched": 3,
  "returned": 3,
  "results": [
    {
      "id": "screen_001",
      "label": "Central World Fl.2",
      "distance": 0.15,
      "unit": "km"
    },
    {
      "id": "screen_002",
      "label": "Gaysorn Village",
      "distance": 0.42,
      "unit": "km"
    }
  ],
  "warnings": []
}
```

- คืนเฉพาะจุดที่ผ่านเกณฑ์รัศมีและถูกตัดตาม `limit`
- เรียงลำดับจากระยะทางน้อยไปมากเสมอ
- คืนเฉพาะ `id`, `label`, `distance`, `unit` ไม่คืนพิกัดซ้ำ เพื่อความกระชับและปลอดภัย

## Errors ที่ควรแยก

- `INVALID_INPUT`: พิกัดไม่อยู่ในช่วงที่ถูกต้อง (lat: -90 ถึง 90, lng: -180 ถึง 180) หรือ destinations ว่าง
- `CALCULATION_ERROR`: เกิดข้อผิดพลาดทางคณิตศาสตร์ในการคำนวณระยะ

