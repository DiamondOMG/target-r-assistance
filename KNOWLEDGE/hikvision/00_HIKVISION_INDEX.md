---
type: index
status: active
platform:
  - hikvision
tags:
  - hikvision
  - display
  - android
  - adb
  - anydesk
created: 2026-05-13
updated: 2026-05-13
source: personal-design
related:
  - "[[ADB/00_ADB_INDEX]]"
  - "[[HIKVISION_AnyDesk_ADB_Permissions]]"
  - "[[HIKVISION_Display_Hardware_Spec]]"
  - "[[HIKVISION_MPV_Install]]"
  - "[[HIKVISION_USB_Camera_UVC_Setup]]"
---

# 00_HIKVISION_INDEX

ไฟล์นี้คือ index ของโฟลเดอร์ `HIKVISION/`

ใช้เก็บความรู้ วิธี setup, runbook และ troubleshooting สำหรับอุปกรณ์ HIKVISION

## Main Notes

- [[HIKVISION_AnyDesk_ADB_Permissions]] = เปิดสิทธิ์ให้ AnyDesk บนจอ HIKVISION ด้วย ADB
- [[HIKVISION_Display_Hardware_Spec]] = สเปคเครื่องและระบบของจอ HIKVISION
- [[HIKVISION_MPV_Install]] = ติดตั้ง MPV Player บนจอ HIKVISION ด้วย ADB
- [[HIKVISION_USB_Camera_UVC_Setup]] = บันทึกผลทดสอบ USB Camera (UVC) 1080p และสถาปัตยกรรม Background AI

## Folder Notes

- ตอนนี้ยังไม่จำเป็นต้องสร้างโฟลเดอร์ root-level `AnyDesk/` แยก เพราะโน้ตที่มีอยู่ผูกกับจอ HIKVISION โดยตรง และใช้ ADB เป็นเครื่องมือ
- ถ้ามีโน้ต AnyDesk ที่ใช้ข้ามหลายยี่ห้อ/หลายแพลตฟอร์มมากขึ้น ค่อยแยกเป็น `ANYDESK/` หรือ `AnyDesk/` ภายหลัง

