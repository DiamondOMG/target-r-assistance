---
type: runbook
status: active
platform:
  - hikvision
  - android
created: 2026-08-24
updated: 2026-08-24
verified: 2026-08-24
source: personal-experience
tags:
  - hikvision
  - mpv
  - android
  - adb
  - media-player
  - hardware-decode
related:
  - "[[00_HIKVISION_INDEX]]"
  - "[[HIKVISION_Display_Hardware_Spec]]"
  - "[[ADB/00_ADB_INDEX]]"
---

# HIKVISION - ติดตั้ง MPV Player ด้วย ADB

## เป้าหมาย

ดาวน์โหลดและติดตั้ง **mpv-android** ลงจอ HIKVISION ผ่าน ADB เพื่อใช้เล่นวิดีโอและดูภาพ/สตรีมกล้องพร้อม Hardware Acceleration (`mediacodec`)

## เงื่อนไขก่อนเริ่ม

- คอมพิวเตอร์เชื่อมต่อ ADB ไปยังจอ HIKVISION เรียบร้อยแล้ว
- ใช้ Git Bash หรือ Terminal บนคอมพิวเตอร์
- สถาปัตยกรรม CPU ของจอเป็น ARM64 (`arm64-v8a`)

## ขั้นตอน

1. ดาวน์โหลดไฟล์ APK เวอร์ชัน ARM64 จาก GitHub Release:

```bash
curl -L -o mpv-android.apk "https://github.com/mpv-android/mpv-android/releases/download/2026-08-11/app-default-arm64-v8a-release.apk"
```

2. ติดตั้งไฟล์ APK ลงจอผ่าน ADB:

```bash
adb install mpv-android.apk
```

## คำสั่งรวม

```bash
curl -L -o mpv-android.apk "https://github.com/mpv-android/mpv-android/releases/download/2026-08-11/app-default-arm64-v8a-release.apk"
adb install mpv-android.apk
```

## ผลลัพธ์ที่ควรได้

- เทอร์มินัลขึ้น `Success`
- แอป **MPV** ปรากฏในรายชื่อแอปพลิเคชันบนจอ HIKVISION

## หมายเหตุ

- สามารถตรวจสอบเวอร์ชันใหม่ล่าสุดของ mpv-android ได้ที่ [mpv-android Releases](https://github.com/mpv-android/mpv-android/releases)
