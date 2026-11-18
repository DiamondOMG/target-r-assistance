---
type: runbook
status: active
created: 2026-11-18
updated: 2026-11-18
platform:
  - android
  - tailscale
  - adb
tags:
  - sharp-tv
  - tailscale
  - adb
  - tv-control
related:
  - "[[00_ANDROID_BOX_INDEX]]"
---

# คู่มือเชื่อมต่อและตั้งค่า Sharp Smart TV ห้องทำงาน (Tailscale + ADB)

คู่มืออ้างอิงสำหรับทีมงานในการเชื่อมต่อและสั่งงานจอ Sharp Smart TV (`AQUOS_TVX19A`, Android 11) ผ่าน **Tailscale VPN + ADB** และ MCP Tool `tv_control`

## ข้อมูลจอในห้องทำงาน

| จอ | รุ่น / OS | MAC Address | LAN IP | Tailscale IP | Domain | สถานะ |
|---|---|---|---|---|---|---|
| **Sharp ตัวซ้าย / จอ 2 (`sharp_left`)** | `AQUOS_TVX19A` (Android 11) | `A4AE125D42DE` | `192.168.0.109` | `100.120.41.101` | `sharp-left.tail6bc567.ts.net` | **Connected** (`Expiry disabled`, Always-on VPN เปิดแล้ว) |
| **Sharp ตัวขวา / จอ 3 (`sharp_right`)** | `AQUOS_TVX19A` (Android 11) | `A4AE125D4ACC` | `192.168.1.105` / `.0.108` | `100.75.151.107` | `sharp-right.tail6bc567.ts.net` | **Connected** (`Expiry disabled`, Always-on VPN เปิดแล้ว) |

## แพ็กเกจแอปสำคัญบนทีวี

- **Tailscale:** `com.tailscale.ipn`
- **Target-R / DS Loader:** `net.targetr.stacks.central`
- **Web Browser:** `com.internet.tvbrowser`

## คำสั่ง ADB สำหรับตั้งค่า Always-on VPN บน Android TV 11

บน Sharp Android TV 11 เมนู `VPN` ถูกซ่อนจากหน้า Settings จึงต้องสั่งเปิด Always-on VPN ผ่าน ADB:

```bash
adb connect 192.168.0.109:5555

# ตั้งค่า Always-on VPN ให้ Tailscale และอนุญาตการทำงานเบื้องหลัง
adb -s 192.168.0.109:5555 shell settings put secure always_on_vpn_app com.tailscale.ipn
adb -s 192.168.0.109:5555 shell settings put secure always_on_vpn_lockdown 0
adb -s 192.168.0.109:5555 shell appops set com.tailscale.ipn RUN_IN_BACKGROUND allow
adb -s 192.168.0.109:5555 shell appops set com.tailscale.ipn RUN_ANY_IN_BACKGROUND allow

# สั่งต่อ VPN ผ่าน Broadcast (กรณีหลุด) และเช็ค IP tun0
adb -s 192.168.0.109:5555 shell am broadcast -a com.tailscale.ipn.CONNECT_VPN -n com.tailscale.ipn/.IPNReceiver
adb -s 192.168.0.109:5555 shell ip addr show tun0
```

> **หมายเหตุ:** หากไม่ได้ Root จะตั้ง `persist.adb.tcp.port 5555` ผ่าน shell ไม่ได้ ให้เปิด Network Debugging ใน Developer Options (`service.adb.tcp.port = 5555`) แทน

## วิธีสั่งงานสำหรับทีมงาน

1. เปิด **Tailscale** บนคอมพิวเตอร์และล็อกอินด้วยบัญชีที่รับ Share จอทีวีไว้แล้ว
2. สั่งผ่านแชท Antigravity ได้เลย (AI จะเรียกใช้ MCP Tool `tv_control` ให้อัตโนมัติ):
   - *"เปิดเว็บ `https://tops.actx.digital/screen-monitor` ขึ้นจอ Sharp ตัวซ้าย"*
   - *"เปิดแอป dsloader บนจอ Sharp ตัวซ้าย"*
   - *"รีสตาร์ท dsloader บนจอ Sharp ตัวซ้าย"*
   - *"สลับจอ Sharp ตัวซ้ายไป HDMI 2"*
