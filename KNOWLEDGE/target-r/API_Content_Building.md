---
status: active
type: reference
created: 2026-07-10
platform: target-r
tags:
  - target-r
  - api
  - content-building
related:
  - "[[TARGET_R/00_TARGET_R_INDEX]]"
---

# TargetR Content Building API

API สำหรับจัดการเชื่อมระบบทำภาพหรือเนื้อหาจากผู้ให้บริการภายนอก (Third-party Content Authoring) เข้ามาใช้งานบนพื้นที่จัดการของ TargetR ได้โดยตรง

## 🛠️ โครงสร้างการเชื่อมต่อ (Redirect & Import Flow)

1. ผู้ใช้กดเลือก Content Builder ที่ต้องการบน Admin Panel
2. ระบบจะทำการ Redirect ไปยัง Web Editor ภายนอกเพื่อให้สร้างเนื้อหา (เช่น ออกแบบกราฟิก, ตารางราคาสินค้า, ข้อมูลสภาพอากาศ)
3. เมื่อทำเสร็จ ผู้ใช้บันทึกงาน ระบบภายนอกจะยิงผลลัพธ์กลับเข้ามาเก็บและกระจายไฟล์ผ่าน CDN ของ TargetR ทันที

## 📦 บริการที่มีระบบ Builder สำเร็จรูป

*   **Weather** (สภาพอากาศ)
*   **RSS Feeds**
*   **Currencies** (อัตราแลกเปลี่ยน)
*   **Canva / Pixlr / PicMonkey** (ระบบตกแต่งภาพ)
*   **Twitter** (แสดงฟีดข้อความ)
