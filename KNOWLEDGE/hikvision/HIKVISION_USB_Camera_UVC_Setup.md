---
type: runbook
status: active
platform:
  - hikvision
  - android
created: 2026-08-25
updated: 2026-08-25
verified: 2026-08-25
source: personal-experience
tags:
  - hikvision
  - uvc
  - usb-camera
  - mjpeg
  - libuvc
  - background-service
  - ai-analytics
related:
  - "[[00_HIKVISION_INDEX]]"
  - "[[HIKVISION_Display_Hardware_Spec]]"
---

# HIKVISION - USB Camera (UVC) & Background AI Performance

## เป้าหมาย

สรุปผลการทดสอบการใช้งานกล้อง USB (UVC) บนจอ HIKVISION (ชิป Amlogic T982) สำหรับนำไปพัฒนาระบบ AI วิเคราะห์ภาพเบื้องหลัง (Background Service) ควบคู่กับแอปเล่นคอนเทนต์ Signage (TargetR / dsloader)

## ปัญหาที่พบกับ Android Camera Framework ปกติ

- หากใช้ Camera Framework ปกติของ Android (เช่น Camera1 / Camera2 บนแอปทั่วไปอย่าง Open Camera) ภาพจะกระตุกมากแม้ปรับความละเอียดต่ำ
- **สาเหตุ:** Android TV ROM ของจอไม่มี UVC Hardware HAL Optimization ทำให้ระบบแปลงภาพแบบ Software (CPU Bottleneck)

## ทางออก & วิธีที่ทดสอบแล้วว่าลื่นจริง (LibUVC)

- **กลไก:** ใช้การเชื่อมต่อตรงผ่าน **Android USB Host API + LibUVC (NDK)** เพื่อดึงสตรีม **MJPEG** เข้า Hardware Decoder (`c2.amlogic.mjpeg.decoder`) โดยตรง **Bypass Android Camera Service ของระบบทิ้ง**
- **แอปที่ใช้ทดสอบ:** `USB Camera` (ShenYao `com.shenyaocn.android.usbcamera`)

### ผลการทดสอบ (Benchmark & 100% Verified)

| รายการ | ค่าที่ได้ |
| --- | --- |
| ความละเอียดที่ทดสอบ | **1920x1080 (Full HD 1080p)** |
| ความลื่นไหล | ลื่นไหลมาก (30–60 FPS นิ่ง) |
| CPU Idle ขณะเปิด Full UI | **> 211%** (เหลือพลังประมวลผลว่างเกิน 2 Core จาก 4 Core) |
| การรันเบื้องหลัง (Background) | **ผ่าน 100%** พิสูจน์ด้วยการเปิด IP Camera Web Server ดูผ่านคอมขณะ TargetR รันเต็มจอ |
| การแจ้งเตือนความเป็นส่วนตัว | **เงียบสนิท (0 Notification)** จอไม่มีแถบหรือจุดเขียวแจ้งเตือนว่ากล้องกำลังทำงาน |

### ขั้นตอนเปิด IP Camera Server บนแอป USB Camera เพื่อดูผ่านคอม

1. เปิดแอป `USB Camera` บนจอ -> กดจุด 3 จุด ตั้งค่า Resolution เป็น `1920x1080`
2. ที่หน้าหลักของแอป เลื่อนลงมาด้านล่าง กดปุ่ม **IP Server** (ไอคอนกล้องขีดฆ่า = เปิดการทำงาน)
3. ที่คอมพิวเตอร์ เปิดเบราว์เซอร์เข้า `http://<IP_จอ>:8081/` (เช่น `http://192.168.0.108:8081/`)
4. ล็อกอินด้วย User: `admin` / Password: `admin` จะเห็นภาพสดจากกล้องทันทีแม้แอป Kiosk (TargetR) กำลังเล่นทับอยู่หน้าจอ

## สถาปัตยกรรมสำหรับแอป AI Analytics จริง

1. **Background Service (Headless):** ทำงานเบื้องหลัง ไม่เรนเดอร์ภาพขึ้นจอ ไม่แย่ง GPU/SurfaceFlinger จาก TargetR
2. **Library แนะนำ:**
   - **Android Native:** `AndroidUSBCamera` (by jiangdongguo) หรือ `libuvc-ndk`
   - **Flutter:** `flutter_uvc_camera` หรือ `flutter_usb_camera`
3. **AI Input Buffer:** ย่อขนาดภาพเฟรมเข้าโมเดล AI เหลือ **640x480** หรือ **320x240** เพื่อประหยัด CPU ให้อยู่ระดับต่ำ (<30-50%)

## คำสั่ง ADB ที่มีประโยชน์

```bash
# ติดตั้งแอป USB Camera
adb install USB+Camera_12.2.2_APKPure.apk

# เช็ค Resolution ที่กำลังทำงานอยู่
adb logcat -d | grep -i -E "resolution|NeedResolutionChange|mali_gralloc" | tail -n 20
```
