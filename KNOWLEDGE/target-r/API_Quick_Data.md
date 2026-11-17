---
status: active
type: reference
created: 2026-07-10
platform: target-r
tags:
  - target-r
  - api
  - quick-data
related:
  - "[[TARGET_R/00_TARGET_R_INDEX]]"
---

# TargetR Quick Data API

ใช้สำหรับการอัปเดตฟิลด์ข้อมูลภายในอ็อบเจ็กต์แบบเกือบเรียลไทม์ ( propagation ผ่าน UDP ความหน่วง <200ms) นิยมใช้เพื่ออัปเดตตัวแปรสำหรับกำหนดเงื่อนไขการเล่นคอนเทนต์ เช่น ข้อมูลสภาพอากาศ ราคา หรือข้อความวิ่ง

## 📌 Endpoints

*   **อัปเดตหน้าจอเดี่ยว (Specific Screen):**
    `POST /api/screen-data/{screen-id}`
*   **อัปเดต Sequence เดี่ยว (Specific Sequence):**
    `POST /api/sequence-data/{seq-id}`
*   **อัปเดตกลุ่มหน้าจอ (Group of Screens):**
    `POST /api/group-screen-data/{group-name}`

## ⚙️ Parameters

*   **Data Key-Value**: ค่าที่ต้องการแก้ไข ให้ส่งเป็น **Query parameters** ท้าย URL หรือส่งแบบ **URL-encoded form data** ใน Request Body เช่น `?temp=25&status=active`
*   **filter**: (เฉพาะ Group Endpoint) ใช้กรองหน้าจอในกลุ่มที่ต้องการให้ผลคำสั่งทำงาน เช่น `?filter=androidSdk>20`

## 💻 ตัวอย่างการใช้งาน (cURL)

**ส่งข้อมูลผ่าน Query string:**
```bash
curl -X POST "https://stacks.targetr.net/api/screen-data/SCREEN_ID?temp=25&status=active" \
     -H "Authorization: Basic <BASE64_CREDENTIALS>"
```

**ส่งข้อมูลผ่าน Form Data:**
```bash
curl -X POST "https://stacks.targetr.net/api/screen-data/SCREEN_ID" \
     -H "Authorization: Basic <BASE64_CREDENTIALS>" \
     -d "temp=25&status=active"
```
