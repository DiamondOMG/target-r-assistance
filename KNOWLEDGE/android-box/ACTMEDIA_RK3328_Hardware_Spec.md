---
type: hardware
status: active
platform:
  - android
  - rockchip
created: 2026-08-26
updated: 2026-08-26
verified: 2026-08-26
source: user-provided
tags:
  - android-box
  - actmedia
  - rk3328
  - playbox-round
  - hardware
  - spec
related:
  - "[[00_ANDROID_BOX_INDEX]]"
  - "[[ADB/00_ADB_INDEX]]"
---

# ACTMEDIA (RK3328) Hardware Spec

> หรือที่เรียกกันว่า **กล่อง Playbox กลม**

## ข้อมูลระบบ (System & Hardware)

| รายการ | ค่า | หมายเหตุ |
| --- | --- | --- |
| **Model** | `ACTMEDIA` | กล่องทรงกลม (Device/Product: `rockchip037`) |
| **Platform / SoC** | `Rockchip RK3328` (`rk3328`) | Quad-Core ARM Cortex-A53 |
| **Android Version** | `10` (SDK: `29`) | |
| **Display Resolution** | `1920x1080` | Full HD 1080p |

## WebView

| รายการ | ค่า | หมายเหตุ |
| --- | --- | --- |
| **Current WebView** | `com.android.webview` | AOSP WebView (ตัวหลัก) |
| **WebView Version** | `74.0.3729.186` | Version Code: `373018655` |
| **Target SDK** | `29` | Android 10 |
| **Google WebView** | `NOT installed` | ไม่มี `com.google.android.webview` |

## หน่วยความจำและพื้นที่เก็บข้อมูล (Memory & Storage)

| รายการ | ขนาดทั้งหมด | ใช้งานแล้ว | เหลือว่าง |
| --- | --- | --- | --- |
| **RAM** | `1,957 MB` (~2 GB) | ~1,500 MB | ~456 MB |
| **Swap** | `978 MB` (~1 GB) | ~132 MB | ~846 MB |
| **Storage (`/data`)** | `10 GB` (eMMC ~16GB) | ~5.0 GB | ~5.2 GB |

## การเชื่อมต่อและคำสั่ง ADB

```bash
# เชื่อมต่อ ADB ผ่าน LAN / Wi-Fi
adb connect 192.168.0.127:5555

# ตรวจสอบ WebView
adb -s 192.168.0.127:5555 shell dumpsys webviewupdate
```
