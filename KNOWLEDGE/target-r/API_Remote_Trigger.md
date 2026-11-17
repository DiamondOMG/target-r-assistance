---
status: active
type: reference
created: 2026-07-10
platform: target-r
tags:
  - target-r
  - api
  - remote-trigger
related:
  - "[[TARGET_R/00_TARGET_R_INDEX]]"
---

# TargetR Remote Trigger API

ใช้สำหรับส่งคำสั่งสั่งการหน้าจอจากระยะไกลให้ทำงานทันที (ความหน่วง <200ms ผ่าน UDP Layer 1) เช่น การสั่งเปิดโฆษณาแทรกฉุกเฉิน หรือส่งข้อมูลให้หน้าเว็บ HTML5 แบบ Interactive ทำงานตามจังหวะที่กำหนด

## 📌 Endpoint

```http
GET https://stacks.targetr.net/api/screen-trigger/{SCREEN-MAC}?name={DATA}
```

*   `{SCREEN-MAC}`: MAC Address ของหน้าจอเป้าหมาย
*   `{DATA}`: ข้อความหรือคำสั่งที่จะส่งเข้าไปที่ตัว Player

## 💻 การเชื่อมต่อฝั่ง Client (HTML5 / JS)

หน้าเว็บที่เป็น Interactive คอนเทนต์ซึ่งแสดงผลบนหน้าจอ ต้องมี Callback Function ชื่อ **`DigitalSignageTriggerCallback`** มารับข้อมูลที่ส่งจาก API นี้:

```javascript
function DigitalSignageTriggerCallback(data) {
  // รับข้อมูลและทำ logic บนหน้าเว็บ
  if (data === "PLAY_ALERT") {
    showAlert();
  }
}
```

---

## 📝 การรวมโค้ด Next.js และการทดสอบ

### 1. วิธีสร้าง Client Component มารับคำสั่ง (Global Listener)
สร้างเป็น Client Component แล้วนำไปวางไว้ใน `RootLayout` เพื่อดึงข้อมูลเปลี่ยนหน้าแบบ Real-time:

```javascript
"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function NavigateTrigger() {
  const router = useRouter();

  useEffect(() => {
    window.DigitalSignageTriggerCallback = (data) => {
      if (!data) return;

      console.log("DigitalSignageTriggerCallback received:", data);

      if (data.startsWith("path_")) {
        const target_path = data.substring(5);
        router.push(target_path);
      }
    };

    return () => {
      delete window.DigitalSignageTriggerCallback;
    };
  }, [router]);

  return null;
}
```

### 2. วิธีการทดสอบในหน้าเว็บ (Local Testing)
เปิดบราวเซอร์ กด **F12** ไปที่ Console แล้วรันคำสั่ง:
```javascript
window.DigitalSignageTriggerCallback("path_/map?store=TopsDigital-Ladprao");
```
หน้าเว็บจะต้องเปลี่ยนเส้นทางและฟิลเตอร์ข้อมูลทันที

### 3. วิธีการยิงผ่าน API (Remote Testing)
เรียกยิงด้วย **GET** (ห้ามใช้ POST เพราะระบบ stacks จะแจ้งเป็น *Unknown request type*) และตรวจสอบว่าทำการ **URL Encode** ข้อมูลที่ส่งผ่าน parameter `name` แล้ว:

* **Endpoint**: `https://stacks.targetr.net/api/screen-trigger/{SCREEN-MAC}?name={DATA}`
* **ตัวอย่าง URL**:
  ```http
  GET https://stacks.targetr.net/api/screen-trigger/A4AE125D42DE?name=path_%2Fmap%3Fstore%3DTopsDigital-Ladprao
  ```
  *(หมายเหตุ: ค่าของ `name` ถูกแปลงจาก `path_/map?store=TopsDigital-Ladprao`)*

---

## 📌 เส้นทางด่วนของหน้ามอนิเตอร์บน Sequence Dashboard (13822E1F644502)

เมื่อหน้าจอเปิด Sequence Dashboard (`13822E1F644502`) สามารถใช้ Remote Trigger สั่งเปลี่ยนไปหน้ามอนิเตอร์สรุปออนไลน์/ออฟไลน์ของแต่ละแบรนด์ได้ผ่านคำสั่ง `path_` ต่อไปนี้:

1. **Big C Monitor Dashboard** (หน้าสรุปออนไลน์/ออฟไลน์ Big C)
   * **คำสั่ง (DATA)**: `path_/dashboard/bigc`
   * **ตัวอย่าง URL**:
     ```http
     GET https://stacks.targetr.net/api/screen-trigger/A4AE125D42DE?name=path_%2Fdashboard%2Fbigc
     ```

2. **Tops Digital Monitor Dashboard** (หน้าสรุปออนไลน์/ออฟไลน์ Tops)
   * **คำสั่ง (DATA)**: `path_/dashboard/tops_digital`
   * **ตัวอย่าง URL**:
     ```http
     GET https://stacks.targetr.net/api/screen-trigger/A4AE125D42DE?name=path_%2Fdashboard%2Ftops_digital
     ```
