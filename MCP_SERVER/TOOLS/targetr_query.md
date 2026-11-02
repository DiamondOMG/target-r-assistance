# MCP Tool Contract: `targetr_query`

> สถานะ: implement แล้วใน `jarvis_mcp/targetr_query.py`; ต้องตั้งค่า Neon URL และ token ก่อนรัน

## วัตถุประสงค์

อ่านและสรุปข้อมูล Target-R ที่ sync อยู่ใน Neon โดยให้ Agent ขอเฉพาะ operation/fields ที่จำเป็น ไม่คืน raw JSONB `data` และไม่มีคำสั่งแก้ไขข้อมูลโดยตรง. หากเลือก `freshness="refresh"` จะเรียก workflow sync/upsert ที่มีอยู่แล้วเพื่อดึงข้อมูลต้นทางเข้า Neon ก่อนอ่าน

## คำอธิบายสำหรับ Model

ใช้เมื่อต้อง query ข้อมูล Screen, Sequence หรือ Library item ที่มีในแหล่ง Target-R ที่เชื่อมต่อ เลือก operation และ fields ให้น้อยที่สุด จำกัดจำนวนแถว. Tool เป็น read-only; ไม่ใช้เพื่อส่งคำสั่งไปยัง DS Loader/Android device.

## Input schema (draft)

| Field | Type | Required | ความหมาย / ข้อจำกัดที่เสนอ |
|---|---|---:|---|
| `entity` | string enum | yes | `screen`, `sequence`, `libraryitem` |
| `operation` | string enum | yes | `count`, `select`, `group_count` |
| `filters` | array of filter | no | เงื่อนไขแบบ allowlist; fields/operators ต้องกำหนดตายตัว |
| `fields` | string array | conditional | ฟิลด์ที่ต้องการคืน ใช้กับ `select`; allowlist แยกตาม entity |
| `group_by` | string array | conditional | ฟิลด์จัดกลุ่ม ใช้กับ `group_count`; allowlist แยกตาม entity |
| `limit` | integer | no | จำนวนผลสูงสุด; ต้องกำหนด default และ hard maximum |
| `offset` | integer | no | เริ่มอ่านจากลำดับที่ระบุ เมื่อแหล่งข้อมูลรองรับ pagination |

Filter draft:

| Field | Type | ความหมาย |
|---|---|---|
| `field` | string | canonical field ของ entity ตาม allowlist |
| `operator` | string enum | เช่น `eq`, `in`, `contains`, `exists`; ต้องตกลงและทดสอบก่อนเปิดใช้ |
| `value` | scalar หรือ array | ค่าที่ใช้เปรียบเทียบ; ห้ามรับ SQL, expression หรือ URL |

## Output schema (draft)

```json
{
  "source": "targetr_neon",
  "entity": "screen",
  "operation": "count",
  "as_of": "ISO-8601 timestamp หรือ null",
  "total": 0,
  "returned": 0,
  "rows": [],
  "groups": [],
  "warnings": []
}
```

- `count`: ส่งเฉพาะ `total`; `rows` และ `groups` ว่าง
- `select`: ส่ง `rows` ที่มีเฉพาะ fields ที่ร้องขอ พร้อม `total` และ `returned`
- `group_count`: ส่ง `groups` ในรูป `{ "key": {...}, "count": number }`
- Tool ต้องไม่คืนคอลัมน์ `data` (raw JSONB), credentials หรือผลลัพธ์เกิน `limit`
- `as_of` ต้องแทนเวลาที่ source ยืนยันได้; ถ้าไม่มีข้อมูลเวลาที่น่าเชื่อถือให้เป็น `null` ห้ามอ้างเป็นเวลาข้อมูลสด
- `warnings` ใช้แจ้งข้อมูลไม่ครบ, field ที่ไม่ทราบความหมาย หรือข้อจำกัดของ source

## Errors ที่ควรแยก

- `INVALID_INPUT`: entity/operation/filter/field ไม่อยู่ใน schema หรือ allowlist
- `SOURCE_UNAVAILABLE`: ติดต่อ Neon ไม่ได้
- `SOURCE_RESPONSE_INVALID`: response ไม่ตรง schema ที่คาด
- `RESULT_LIMIT_EXCEEDED`: เงื่อนไขมีผลลัพธ์เกินขอบเขตที่อนุญาต (ถ้า implementation เลือก fail แทนการจำกัดผล)

ห้ามใส่ secret, filter values อ่อนไหว หรือ raw response ใน error/log

## ข้อจำกัดของแหล่งข้อมูลปัจจุบัน

Neon Function ใน `target-r-neon` มี `GET /screens`, `/sequences`, `/libraryitems` ซึ่งไม่ส่งคอลัมน์ `data` แต่แต่ละ endpoint คืนทุกแถวใน response เดียว ไม่มี filter หรือ pagination. ตามข้อตกลงเริ่มต้น MCP ดึงทั้งชุดที่ไม่ raw แล้วกรองใน process; ผลที่คืน Model ยังจำกัด fields และจำนวนแถว

การเรียก `freshness="refresh"` ใช้ `POST /sync`, `/sync-sequences` หรือ `/sync-libraryitems` ก่อนอ่านข้อมูลใหม่ จึงทำให้ Neon sync/upsert ข้อมูลจาก Target-R; ใช้เฉพาะเมื่อผู้ใช้ต้องการข้อมูลล่าสุด/เวลาเปลี่ยนแปลงได้ ส่วน `cached` ใช้ cache ใน memory ของ MCP process ตาม TTL และเมื่อ cache หมดอายุจะอ่านจาก endpoint Neon อีกครั้งโดยไม่ trigger sync

ห้ามใช้ `/tables/{table_name}` สำหรับ tool นี้ เพราะ endpoint นั้นคืน raw `data` ด้วย
