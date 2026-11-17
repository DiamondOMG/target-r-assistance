---
type: hardware
status: active
platform:
  - hikvision
  - android
created: 2026-08-20
updated: 2026-08-24
verified: 2026-08-24
source: user-provided
tags:
  - hikvision
  - display
  - hardware
  - spec
  - android
related:
  - "[[00_HIKVISION_INDEX]]"
  - "[[HIKVISION_AnyDesk_ADB_Permissions]]"
  - "[[HIKVISION_MPV_Install]]"
---

# HIKVISION Display Hardware Spec

## สรุปข้อมูลระบบ (System About)

| รายการ | ค่า |
| --- | --- |
| SoC / Chipset | Amlogic T982 (`AMLT982` / Board: `t982_ar301`) |
| GPU | ARM Mali-G52 (OpenGL ES 3.2, Vulkan supported) |
| Serial No. | `GD2299999` |
| Android Version | 13 |
| Kernel Version | 5.15.119-ab13213 Apr 25 05:40:15 UTC 2026 |
| Device Firmware Version | V3.1.3000 build 260425 |
| Firmware ID | `86bce03c-9617-4367-a3d2-b2f1e1a52378` |

## หน่วยความจำและการจัดเก็บ (Memory & Storage)

| รายการ | ค่า |
| --- | --- |
| Total Memory (RAM) | 4.0 GB |
| Average Usage | 45% (~1.8 GB) |
| Available Memory | 2.2 GB |
| Performance | Normal |

## ตัวถอดรหัสฮาร์ดแวร์ (Hardware Decoders)

- **MJPEG Decoder:** `c2.amlogic.mjpeg.decoder` (Hardware Decode)
- **H.264 / AVC:** `c2.amlogic.avc.decoder`
- **H.265 / HEVC:** `c2.amlogic.hevc.decoder`
- **AV1:** `c2.amlogic.av1.decoder`
- **VP9:** `c2.amlogic.vp9.decoder`
