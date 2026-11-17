---
type: hardware
status: active
platform:
  - android
  - rockchip
created: 2026-08-20
updated: 2026-08-20
verified: 2026-08-20
source: user-provided
tags:
  - android-box
  - hk1-rbox
  - rk3528
  - hardware
  - spec
related:
  - "[[00_ANDROID_BOX_INDEX]]"
  - "[[ADB/00_ADB_INDEX]]"
---

# HK1 RBOX K8 Hardware Spec

## ข้อมูลระบบ (System & Hardware)

| รายการ | ค่า | หมายเหตุ |
| --- | --- | --- |
| **Model** | `HK1 RBOX K8` | Android TV Box |
| **Platform / SoC** | `Rockchip RK3528` (`rk3528`) | Quad-Core ARM Cortex-A53 |
| **GPU** | ARM Mali-450 | รองรับ OpenGL ES 2.0 (ไม่รองรับ Vulkan/OpenCL) |
| **Android Version** | `13` | |
| **Current WebView** | `com.android.webview` (v`109.0.5414.123`) | Target SDK: 33 / Version Code: 541412303 |
| **Display Resolution** | `1920x1080` | Full HD 1080p |

## หน่วยความจำและพื้นที่เก็บข้อมูล (Memory & Storage)

| รายการ | ขนาดทั้งหมด | ใช้งานแล้ว | เหลือว่าง |
| --- | --- | --- | --- |
| **RAM** | `3,910 MB` (~4 GB) | ~2,711 MB | ~1,199 MB |
| **Swap** | `1,955 MB` (~2 GB) | 0 MB | 1,955 MB |
| **Internal Storage** | `23 GB` (eMMC 32GB) | 2.7 GB | **20 GB** |

## กล้องและ Camera HAL (Camera Capabilities)

| รายการ | ค่า | หมายเหตุ |
| --- | --- | --- |
| **Supported Preview Sizes** | `176x144`, `320x240`, `352x288`, `640x360`, `640x480` | ค่าที่ Driver / Camera HAL อ่านได้ |
| **Max Preview Resolution** | `640x480` | ความละเอียดพรีวิวสูงสุดที่ฮาร์ดแวร์รองรับ |

