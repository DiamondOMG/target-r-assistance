# MCP Server Index

MCP Server เปิด tools ให้ Agent เรียกใช้ความสามารถของระบบและข้อมูลภายใน โดย Agent ต้องตรวจรายการ tools และ schema ที่ MCP Server เปิดให้จริงก่อนเรียกใช้งาน. รันเริ่มต้นผ่าน Python MCP SDK แบบ stdio; tool cache อยู่ใน process memory.

## สถานะ

มี Python MCP tool `targetr_query` สำหรับ query ข้อมูล Target-R ที่ sync อยู่ใน Neon

## Tool Registry

| Tool | ใช้เมื่อ | Input ที่ต้องมี | Output ที่คืน | รายละเอียด |
|---|---|---|---|---|
| `targetr_query` | Query Screen, Sequence หรือ Library item; DS Loader เป็นคำเรียกที่ผู้ใช้อาจใช้แทน Target-R | entity, operation; filters/fields/group_by ตาม operation; freshness เลือก cached หรือ refresh | count, selected rows หรือ grouped counts แบบจำกัด; ไม่มี raw `data` | [`TOOLS/targetr_query.md`](TOOLS/targetr_query.md) |

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
