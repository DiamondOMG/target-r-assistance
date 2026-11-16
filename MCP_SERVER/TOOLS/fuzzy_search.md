# MCP Tool Contract: `targetr_fuzzy_search`

> สถานะ: implement ใน `MCP_SERVER/jarvis_mcp/fuzzy_search.py`

## วัตถุประสงค์

ค้นหาและจับคู่ชื่อสาขา ห้างสรรพสินค้า โครงการ หรือรูปแบบจอ ด้วยการค้นหาแบบยืดหยุ่น (Fuzzy Matching + Alias Lookup) รองรับการสะกดผิด พิมพ์ตก คำย่อ และการพิมพ์ภาษาไทยหรือภาษาอังกฤษที่ไม่ตรงกับค่าในฐานข้อมูล

## คำอธิบายสำหรับ Model

ใช้เมื่อผู้ใช้ถามหาข้อมูลของสาขา ห้าง โครงการ หรือประเภทจอ โดยที่ชื่ออาจจะสะกดผิด เป็นภาษาไทย หรือเป็นชื่อย่อ (เช่น "เซลทรัลเวิล", "CTW", "ลาดพราว", "Ekamai") Tool จะทำการค้นหาใน Master Knowledge และส่งคืนชื่อ canonical `store_location` ที่ถูกต้อง พร้อมรหัสสาขาและคะแนนความมั่นใจ (score) เพื่อนำไป query ใน Neon ต่อไป

## Input schema

| Field | Type | Required | ความหมาย / ข้อจำกัด |
|---|---|---:|---|
| `query` | string | yes | คำค้นหา เช่น "เซลทรัลเวิล", "CTW", "บ่อวิน", "วอลล์ 3 จอ" |
| `entity_type` | string enum | no | ประเภทที่ต้องการค้น: `location` (default), `project`, `label` |
| `threshold` | float | no | ค่าความคล้ายขั้นต่ำระหว่าง 0.0 ถึง 1.0 (default: 0.6) |
| `limit` | integer | no | จำนวนผลลัพธ์สูงสุด (default: 5, max: 20) |

## Output schema

```json
{
  "source": "fuzzy_search",
  "query": "เซลทรัลเวิล",
  "entity_type": "location",
  "total_matched": 2,
  "results": [
    {
      "store_location": "TopsDigital-Centralworld",
      "thai_name": "ท็อปส์ เซ็นทรัลเวิลด์",
      "retailer": "Tops",
      "store_code": "022, TM022",
      "score": 0.85,
      "matched_field": "thai_name",
      "matched_text": "ท็อปส์ เซ็นทรัลเวิลด์"
    }
  ]
}
```

- คืนเฉพาะผลลัพธ์ที่คะแนน $\ge$ `threshold` และเรียงจากคะแนนสูงสุดไปต่ำสุด
- นำ `store_location` หรือ `store_code` ที่ได้ไปส่งต่อให้ `targetr_query` ได้ทันที

