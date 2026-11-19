---
type: index
status: active
platform:
  - android
tags:
  - android-box
  - tv-box
  - rk3528
  - sharp-tv
  - hardware
created: 2026-08-20
updated: 2026-11-19
source: personal-design
parent: "[[KNOWLEDGE/index]]"
related:
  - "[[00_INDEX]]"
  - "[[KNOWLEDGE/index]]"
  - "[[HK1_RBOX_K8_Hardware_Spec]]"
  - "[[ACTMEDIA_RK3328_Hardware_Spec]]"
  - "[[AIS_Playbox_Round_Hardware_Spec]]"
  - "[[HK1_RBOX_K8_WiFi_Location_TargetR_Troubleshooting]]"
  - "[[Android_Box_Unassigned_GPS_Coordinates]]"
  - "[[Sharp_TV_Tailscale_ADB_Runbook]]"
  - "[[Playbox_ADB_Debug_Setup_Guide]]"
---

# 00_ANDROID_BOX_INDEX (ดัชนีย่อยชั้นที่ 2 — Android Box & Sharp TV)

> **Pyramid Navigation:** [`00_INDEX.md`](../../00_INDEX.md) (ยอดปิรามิด) > [`KNOWLEDGE/index.md`](../index.md) (ชั้นที่ 1) > **Android Box & Sharp TV (ชั้นที่ 2)** > สเปก/Runbook (ชั้นที่ 3)

ไฟล์นี้คือ index ของโฟลเดอร์ `KNOWLEDGE/android-box/` ใช้เก็บสเปกฮาร์ดแวร์ Runbook และ Troubleshooting สำหรับกล่อง Android TV Box และจอ Sharp Smart TV

## สเปกฮาร์ดแวร์ (Hardware Specs)

- [`HK1_RBOX_K8_Hardware_Spec.md`](HK1_RBOX_K8_Hardware_Spec.md) = สเปกฮาร์ดแวร์กล่อง HK1 RBOX K8 (Rockchip RK3528 / RAM 4GB / Android 13)
- [`ACTMEDIA_RK3328_Hardware_Spec.md`](ACTMEDIA_RK3328_Hardware_Spec.md) = สเปกฮาร์ดแวร์และ WebView ของกล่อง ACTMEDIA (Rockchip RK3328 / RAM 2GB / Android 10)
- [`AIS_Playbox_Round_Hardware_Spec.md`](AIS_Playbox_Round_Hardware_Spec.md) = สเปกฮาร์ดแวร์และ AOSP WebView ของกล่อง AIS Playbox (ทรงกลม)

## Troubleshooting & Runbooks

- [`HK1_RBOX_K8_WiFi_Location_TargetR_Troubleshooting.md`](HK1_RBOX_K8_WiFi_Location_TargetR_Troubleshooting.md) = แก้ปัญหาพิกัด Wi-Fi Location เพี้ยนบนกล่อง HK1 RBOX K8 ใน Target-R
- [`Android_Box_Unassigned_GPS_Coordinates.md`](Android_Box_Unassigned_GPS_Coordinates.md) = แก้ปัญหากล่อง Android Box ยังไม่ได้กำหนดพิกัด GPS
- [`Sharp_TV_Tailscale_ADB_Runbook.md`](Sharp_TV_Tailscale_ADB_Runbook.md) = คู่มือเชื่อมต่อและตั้งค่า Sharp Smart TV ห้องทำงาน (`AQUOS_TVX19A` ตัวซ้าย / จอ 2 `A4AE125D42DE` และตัวขวา / จอ 3 `A4AE125D4ACC`) ผ่าน Tailscale + ADB และ `tv_control`
- [`Playbox_ADB_Debug_Setup_Guide.md`](Playbox_ADB_Debug_Setup_Guide.md) = คู่มือเปิด Debug Mode (5 ขั้นตอนสำหรับผู้ใช้) และเชื่อมต่อ ADB เข้ากล่อง Playbox ในวงแลนผ่าน `playbox_adb`
