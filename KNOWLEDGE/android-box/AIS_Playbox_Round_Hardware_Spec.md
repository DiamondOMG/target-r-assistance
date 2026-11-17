---
type: hardware
status: active
platform:
  - android
created: 2026-08-26
updated: 2026-08-26
verified: 2026-08-26
source: user-provided
tags:
  - android-box
  - playbox
  - playbox-round
  - webview
  - hardware
  - spec
related:
  - "[[00_ANDROID_BOX_INDEX]]"
  - "[[ADB/00_ADB_INDEX]]"
---

# AIS Playbox (ทรงกลม) Hardware Spec

## ข้อมูลระบบและ WebView (System & WebView)

| รายการ | ค่า | หมายเหตุ |
| --- | --- | --- |
| **Model** | `AIS Playbox (ทรงกลม)` | Android TV Box |
| **Current WebView Package** | `com.android.webview` | AOSP WebView (ตัวหลัก) |
| **WebView Version** | `74.0.3729.186` | Chrome 74 codebase |
| **WebView Version Code** | `373018655` | |
| **Target SDK Version** | `29` | Android 10 |
| **Google WebView (`com.google.android.webview`)** | `NOT installed` | ไม่มี Google WebView ติดตั้ง |

## การเชื่อมต่อและตรวจสอบผ่าน ADB

```bash
# เชื่อมต่อ ADB ผ่าน Wi-Fi/LAN
adb connect 192.168.0.127:5555

# ตรวจสอบสถานะ WebView
adb -s 192.168.0.127:5555 shell dumpsys webviewupdate
```
