---
status: active
type: runbook
created: 2026-06-07
platform: target-r
tags:
  - target-r
  - esc-pos
  - bluetooth-printer
  - cms
  - sequence
  - runbook
related:
  - "[[TARGET_R/00_TARGET_R_INDEX]]"
  - "[[ADB/Android_DSLoader_ESC_POS_Print_Service_Debug_Summary]]"
source: personal-experience
verified: 2026-06-07
---

# Target R × ESC POS Bluetooth Printer Setup

## เป้าหมาย

ตั้งค่าระบบพิมพ์ใบเสร็จ/รายงานจาก Target R ผ่านเครื่องปริ้นเตอร์ Bluetooth ESC POS

## เงื่อนไขก่อนเริ่ม

- มีแอป **ESC POS Bluetooth Printer** ติดตั้งในแท็บเล็ตแล้ว
- เครื่องปริ้นเตอร์ Bluetooth เปิดพร้อมใช้งาน
- เปิด Bluetooth บนแท็บเล็ตแล้ว

## ขั้นตอน

### ส่วนที่ 1: ตั้งค่าแอป ESC POS Bluetooth Printer

1. เปิด Bluetooth จับคู่อุปกรณ์เครื่องปริ้นเตอร์
2. เปิดแอป ESC POS Bluetooth Printer
3. กด **Set Pref Printer** → เลือกเครื่องปริ้นที่พึ่ง pair Bluetooth

> รูปประกอบ: `202_0.jpg`, `199_0.jpg`, `200_0.jpg`, `201_0.jpg`

### ส่วนที่ 2: ตั้งค่าใน CMS (Target R)

#### 2.1 สร้าง Base Sequence

- ต้องมี Base Sequence ที่กดแล้วไปยัง Sub Sequence

> รูปประกอบ: `Pasted image 20260604161845.png`, `Pasted image 20260604161908.png`, `Pasted image 20260604161924.png`

#### 2.2 ตั้งค่า Sub Sequence

> รูปประกอบ: `Pasted image 20260604170720.png` ถึง `Pasted image 20260604171532.png`

**ลำดับสำคัญ** ใน Sub Sequence:
1. **Launch** → อยู่ข้างบน
2. **Show Item** → อยู่ตรงกลาง
3. **Report** → อยู่ข้างล่าง

> ⚠️ ลำดับนี้สำคัญมาก ต้องเรียงตามนี้เท่านั้น

#### 2.3 ดึง URL รูปภาพจาก Sequence Data

1. เอา **Item ID** ของรูปที่จะใช้ไปค้นหา
2. ดูที่ **REST** field
3. ใช้ค่า `blobId` สร้าง URL:
   ```
   https://d2cep6vins8x6z.blobstore.net/<blobId>
   ```
   ตัวอย่าง:
   ```
   https://d2cep6vins8x6z.blobstore.net/983BEE78C97E91922617F238EDC4B59E-27193
   ```

4. ใน Show Sequence → ใช้ **Base Sequence**
5. รูปใส่ **Condition** ตามที่ต้องการ

## Sequence IDs ที่เกี่ยวข้อง

| ชนิด | Sequence ID |
|---|---|
| Base Sequence | `139027BF422564` |
| Sub Sequences | `1318D141138352`, `133236994F2738`, `13A95A7E5DEEBE`, `134C8FB39894FC` |
