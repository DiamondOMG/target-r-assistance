---
status: active
type: reference
created: 2026-07-10
platform: target-r
tags:
  - target-r
  - api
  - reporting
  - customId
  - offline-logging
related:
  - "[[TARGET_R/00_TARGET_R_INDEX]]"
  - "[[TARGET_R/DataModel/TargetR_Sequence_DataModel]]"
---

# TargetR Reporting API

API สำหรับดึงรายงานการเล่นคอนเทนต์ (Proof of Play) จากระบบ TargetR (Stacks)

## 📌 Endpoint

```http
GET https://stacks.targetr.net/api/display-report/full.csv?startMillis={startMillis}&type={type}&id={id}
```

ตัวอย่างการเรียกใช้งาน:
`https://stacks.targetr.net/api/display-report/full.csv?startMillis=1782360000000&type=screen&id=145D34894749`

## ⚙️ Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `startMillis` | Long | Yes | เวลาเริ่มต้นช่วงข้อมูลของรายงาน (Unix Epoch ms) เช่น `1782360000000` |
| `endMillis` | Long | No | เวลาสิ้นสุดช่วงข้อมูลของรายงาน (Unix Epoch ms) |
| `type` | String | Yes | ประเภทตัวกรองข้อมูลที่ต้องการดึง (`screen`, `sequence`, `item`, `libraryitem`) |
| `id` | String | Yes | ID หรือ MAC Address ของ Target ที่ระบุใน `type` (เช่น MAC Address ของหน้าจอ) |
| `fields` | String | No | คอลัมน์ที่ต้องการดึง (Comma-separated) รองรับ dot-notation เช่น `screen.customFieldName` |

## ⚠️ เงื่อนไขสำคัญในการเก็บบันทึกรายงาน (Requirements)

1. **การกำหนด `customId`**:
   * คอนเทนต์ (Item) ที่เล่นจำเป็นต้องมีฟิลด์ `customId` กำหนดอยู่ในระบบ/ข้อมูล Sequence ก่อน จึงจะทำการบันทึกประวัติการเล่น (Playback Log) ได้
2. **การบันทึกแบบออฟไลน์ (Offline Logging)**:
   * ตัวเครื่องเล่นสามารถบันทึกประวัติการเล่น (Log) ลงบนตัวเครื่องขณะออฟไลน์ได้ และจะทำการส่งรายงานกลับมาที่เซิร์ฟเวอร์โดยอัตโนมัติเมื่อออนไลน์
3. **การเปิดใช้รายงาน (Reporting Enabled)**:
   * ในการแสดงผล CSV รายงาน จะขึ้นอยู่กับการเปิดใช้งานฟังก์ชัน Report ที่ตัวไอเทมหรือ sequence นั้นๆ ด้วย
