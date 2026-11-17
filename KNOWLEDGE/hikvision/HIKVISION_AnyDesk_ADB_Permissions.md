---
type: runbook
status: active
platform:
  - hikvision
  - android
  - adb
  - anydesk
tags:
  - hikvision
  - anydesk
  - adb
  - debug-mode
  - accessibility
  - appops
  - remote-control
created: 2026-05-13
updated: 2026-05-13
source: personal-experience
related:
  - "[[00_HIKVISION_INDEX]]"
  - "[[ADB/00_ADB_INDEX]]"
---

# HIKVISION - เปิดสิทธิ์ AnyDesk ด้วย ADB

## เป้าหมาย

เปิดสิทธิ์ที่จำเป็นให้แอป AnyDesk หลังติดตั้ง AnyDesk บนจอ HIKVISION เพื่อให้ใช้งาน remote control ได้ครบขึ้น

## เงื่อนไขก่อนเริ่ม

- จอ HIKVISION ต่อเน็ตอยู่ในวงเดียวกับคอม
- คอมมี `adb` ใช้งานได้
- ติดตั้ง AnyDesk และ AnyDesk control plugin บนจอแล้ว

## ขั้นตอน

1. ต่อจอ HIKVISION เข้ากับเน็ตในวงเดียวกับคอม
2. จด IP ของจอ HIKVISION
3. ที่จอ เปิด Debug mode:

```text
Setting -> System -> System Debug
```

4. กรอก password เพื่อ activate:

```text
Abc@1@2@3
```

5. ที่คอม เชื่อมต่อ ADB ไปที่ IP ของจอ:

```bash
adb connect <ip ที่จด>
```

6. เปิดสิทธิ์ restricted settings ให้ AnyDesk:

```bash
adb shell appops set com.anydesk.anydeskandroid ACCESS_RESTRICTED_SETTINGS allow
adb shell appops set com.anydesk.adcontrol.ad1 ACCESS_RESTRICTED_SETTINGS allow
```

7. เปิดสิทธิ์แสดงหน้าต่างทับแอปอื่น:

```bash
adb shell appops set com.anydesk.anydeskandroid SYSTEM_ALERT_WINDOW allow
adb shell appops set com.anydesk.adcontrol.ad1 SYSTEM_ALERT_WINDOW allow
```

8. เปิด Accessibility service ของ AnyDesk:

```bash
adb shell settings put secure enabled_accessibility_services com.anydesk.anydeskandroid/com.anydesk.anydeskandroid.services.AnyDeskAccessibilityService:com.anydesk.adcontrol.ad1/com.anydesk.adcontrol.ad1.Service
adb shell settings put secure accessibility_enabled 1
```

9. เปิดสิทธิ์ media projection:

```bash
adb shell appops set com.anydesk.anydeskandroid PROJECT_MEDIA allow
```

## คำสั่งรวม

เปลี่ยน `<ip ที่จด>` เป็น IP ของจอ HIKVISION ก่อนรัน

```bash
adb connect <ip ที่จด>
adb shell appops set com.anydesk.anydeskandroid ACCESS_RESTRICTED_SETTINGS allow
adb shell appops set com.anydesk.adcontrol.ad1 ACCESS_RESTRICTED_SETTINGS allow
adb shell appops set com.anydesk.anydeskandroid SYSTEM_ALERT_WINDOW allow
adb shell appops set com.anydesk.adcontrol.ad1 SYSTEM_ALERT_WINDOW allow
adb shell settings put secure enabled_accessibility_services com.anydesk.anydeskandroid/com.anydesk.anydeskandroid.services.AnyDeskAccessibilityService:com.anydesk.adcontrol.ad1/com.anydesk.adcontrol.ad1.Service
adb shell settings put secure accessibility_enabled 1
adb shell appops set com.anydesk.anydeskandroid PROJECT_MEDIA allow
```

## หมายเหตุ

- `AnyDesk/` ยังไม่จำเป็นต้องเป็นโฟลเดอร์ root-level แยกในตอนนี้ เพราะขั้นตอนนี้เป็นเคสเฉพาะของจอ HIKVISION
- ถ้ามี runbook AnyDesk ที่ใช้กับหลายอุปกรณ์ในอนาคต ค่อยแยกหมวด AnyDesk ได้

