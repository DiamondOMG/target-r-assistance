---
type: index
status: active
updated: 2026-11-18
parent: "[[00_INDEX]]"
related:
  - "[[00_INDEX]]"
  - "[[target-r/00_TARGET_R_INDEX]]"
  - "[[android-box/00_ANDROID_BOX_INDEX]]"
  - "[[hikvision/00_HIKVISION_INDEX]]"
---

# Knowledge Index (เสาหลักชั้นที่ 1 — คลังความรู้ทางเทคนิค)

> **Pyramid Navigation:** [`00_INDEX.md`](../00_INDEX.md) (ยอดปิรามิด) > **Knowledge Index (ชั้นที่ 1)** > ดัชนีหมวดหมู่ `00_*_INDEX.md` (ชั้นที่ 2) > เอกสารสเปก/API/Runbook (ชั้นที่ 3)

โฟลเดอร์นี้รวบรวมเอกสารสเปกฮาร์ดแวร์ โครงสร้างข้อมูล (Data Model) API และแนวทางแก้ปัญหาหน้างานของระบบ Target-R เพื่อให้ทีมใช้งานร่วมกันในโปรเจกต์ `target-r-assistance` โดยแยกขาดจากข้อมูล Credentials และ Vault ส่วนตัว (เป็นเสาหลักชั้นที่ 1 ต่อจาก [`00_INDEX.md`](../00_INDEX.md))

## หมวดหมู่เอกสาร

| หมวดหมู่ | เนื้อหาหลัก | ดัชนี (ชั้นที่ 2) |
|---|---|---|
| **Target-R & API** | Data Model ของ Screen/Sequence, Neon Sync APIs, Target-R APIs, อาการจอติดใบ้ (`Player comms problem`), ESC/POS Printer | [`target-r/00_TARGET_R_INDEX.md`](target-r/00_TARGET_R_INDEX.md) |
| **Android Box & Sharp TV** | สเปกกล่อง HK1 RBOX K8, Playbox กลม, RK3328, ปัญหาพิกัด Wi-Fi / GPS และคู่มือ Sharp Smart TV (Tailscale + ADB) | [`android-box/00_ANDROID_BOX_INDEX.md`](android-box/00_ANDROID_BOX_INDEX.md) |
| **HIKVISION** | สเปกจอ HIKVISION, การเปิดสิทธิ์ AnyDesk/ADB, ติดตั้ง MPV และตั้งค่า USB Camera UVC | [`hikvision/00_HIKVISION_INDEX.md`](hikvision/00_HIKVISION_INDEX.md) |

## กฎสำคัญ

- ห้ามบันทึก `password`, `token`, Service Account JSON หรือค่าลับในโฟลเดอร์ `KNOWLEDGE/` โดยเด็ดขาด
- ใช้ไฟล์ `.env` และไฟล์ Google Service Account JSON เฉพาะเครื่อง (ถูกป้องกันไว้ใน `.gitignore`)
- หากเพิ่มหมวดความรู้ใหม่ใน `KNOWLEDGE/` ต้องสร้างไฟล์ `00_<CATEGORY>_INDEX.md` และอัปเดตทั้งตารางนี้กับ [`00_INDEX.md`](../00_INDEX.md)
- สำหรับความรู้หน้างานที่ทีมจดเพิ่มแบบ Real-time ให้ค้นคว้าควบคู่กับ MCP Tool `team_knowledge_search` (ดู [`SKILLS/team_knowledge.md`](../SKILLS/team_knowledge.md))
