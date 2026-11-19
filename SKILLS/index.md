---
type: index
status: active
updated: 2026-11-19
parent: "[[00_INDEX]]"
related:
  - "[[00_INDEX]]"
  - "[[targetr_system]]"
  - "[[screen_location]]"
  - "[[manage_target_r]]"
  - "[[programmatic_cms_guide]]"
  - "[[team_knowledge]]"
  - "[[tv_control]]"
  - "[[playbox_adb]]"
---

# Skills Index (เสาหลักชั้นที่ 1 — ขั้นตอนการทำงาน)

> **Pyramid Navigation:** [`00_INDEX.md`](../00_INDEX.md) (ยอดปิรามิด) > **Skills Index (ชั้นที่ 1)** > Skill เฉพาะงาน (ชั้นที่ 2)

Skill คือคำแนะนำเฉพาะงานที่ช่วยให้ Agent เข้าใจบริบท กฎการตัดสินใจ และวิธีใช้ MCP tools อย่างเหมาะสม (เป็นเสาหลักชั้นที่ 1 ต่อจาก [`00_INDEX.md`](../00_INDEX.md))

## Skills ที่ลงทะเบียน

| Skill | ใช้เมื่อ | ไฟล์ |
|---|---|---|
| Target-R และ DS Loader | ถามความรู้หรือข้อมูล read-only เกี่ยวกับ Target-R/DS Loader | [`targetr_system.md`](targetr_system.md) |
| ค้นหาจอและสถานที่ใกล้เคียง | ค้นหาจอ ห้าง หรือสาขาที่อยู่ใกล้จุดอ้างอิงผ่านพิกัดภูมิศาสตร์ | [`screen_location.md`](screen_location.md) |
| จัดเตรียมข้อมูลสำหรับ Manage Target-R | สร้างข้อมูล/ไฟล์ (TSV/JSON) พร้อมก๊อปปี้ไปวางอัปเดตฟิลด์หน้าจอหรือ Sequence หลายรายการพร้อมกันที่ `https://tops.actx.digital/manage_target_r` | [`manage_target_r.md`](manage_target_r.md) |
| คู่มือระบบและเครื่องมือ Act-X Programmatic CMS | แนะนำเครื่องมือ ลิงก์หน้าเว็บ และเตรียมข้อมูลให้ผู้ใช้ไปดำเนินการต่อบนระบบ `https://tops.actx.digital` (ครบทั้ง 15+ หน้า/เครื่องมือ) | [`programmatic_cms_guide.md`](programmatic_cms_guide.md) |
| คลังความรู้ส่วนกลางของทีม | จดบันทึกหรือค้นหาวิธีแก้ปัญหาหน้างาน/SOP ร่วมกันทั้งทีมแบบ Real-time โดยไม่ต้องรอ `git push` | [`team_knowledge.md`](team_knowledge.md) |
| ควบคุมจอ Sharp TV ในห้องทำงาน | สั่งเปิดเว็บแดชบอร์ด, เปิด/รีสตาร์ท DS Loader, สลับ HDMI บนจอ Sharp ผ่าน Tailscale + ADB | [`tv_control.md`](tv_control.md) |
| เชื่อมต่อและจัดการกล่อง Playbox ผ่าน ADB | สั่ง ADB เข้ากล่อง Playbox ในวงแลนด้วย IP เพื่อเช็คค่า เปลี่ยนค่า ดำเนินการ หรือดูคู่มือเปิด Debug Mode | [`playbox_adb.md`](playbox_adb.md) |

## แนวทางเพิ่ม Skill

1. สร้างโฟลเดอร์หรือไฟล์สำหรับ Skill โดยตั้งชื่อให้สื่อความหมาย
2. อธิบายเป้าหมายและสถานการณ์ที่ควรใช้
3. ระบุลำดับการทำงานและ MCP tools ที่เกี่ยวข้อง โดยอ้างชื่อ tool จริงจาก `MCP_SERVER/index.md`
4. ระบุข้อห้าม ข้อมูลอ่อนไหว และวิธีจัดการเมื่อข้อมูลหรือ tool ไม่พร้อม
5. เพิ่มรายการในตารางด้านบน พร้อม path ที่เปิดอ่านได้ และอัปเดตเส้นทางนำทางใน [`00_INDEX.md`](../00_INDEX.md)

Skill ไม่ควรเก็บ credentials หรือข้อมูล production และไม่ควรทำซ้ำรายละเอียด input schema ซึ่งเป็นหน้าที่ของ MCP tool
