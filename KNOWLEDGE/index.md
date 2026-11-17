# Knowledge Index (คลังความรู้ทางเทคนิคสำหรับทีม)

โฟลเดอร์นี้รวบรวมเอกสารสเปกฮาร์ดแวร์ โครงสร้างข้อมูล (Data Model) API และแนวทางแก้ปัญหาหน้างานของระบบ Target-R เพื่อให้ทีมใช้งานร่วมกันในโปรเจกต์ `target-r-assistance` โดยแยกขาดจากข้อมูล Credentials และ Vault ส่วนตัว

## หมวดหมู่เอกสาร

| หมวดหมู่ | เนื้อหาหลัก | ดัชนี |
|---|---|---|
| **Target-R & API** | Data Model ของ Screen/Sequence, Neon Sync APIs, Target-R APIs, อาการจอติดใบ้ (`Player comms problem`) | [`target-r/00_TARGET_R_INDEX.md`](target-r/00_TARGET_R_INDEX.md) |
| **Android Box** | สเปกกล่อง HK1 RBOX K8, Playbox กลม, RK3328 และการแก้ปัญหาพิกัด Wi-Fi / GPS | [`android-box/00_ANDROID_BOX_INDEX.md`](android-box/00_ANDROID_BOX_INDEX.md) |
| **HIKVISION** | สเปกจอ HIKVISION, การเปิดสิทธิ์ AnyDesk/ADB, ติดตั้ง MPV และตั้งค่า USB Camera UVC | [`hikvision/00_HIKVISION_INDEX.md`](hikvision/00_HIKVISION_INDEX.md) |

## กฎสำคัญ

- ห้ามบันทึก `password`, `token`, Service Account JSON หรือค่าลับในโฟลเดอร์ `KNOWLEDGE/` โดยเด็ดขาด
- ใช้ไฟล์ `.env` และไฟล์ Google Service Account JSON เฉพาะเครื่อง (ถูกป้องกันไว้ใน `.gitignore`)
