# Skills Index

Skill คือคำแนะนำเฉพาะงานที่ช่วยให้ Agent เข้าใจบริบท กฎการตัดสินใจ และวิธีใช้ MCP tools อย่างเหมาะสม

## Skills ที่ลงทะเบียน

| Skill | ใช้เมื่อ | ไฟล์ |
|---|---|---|
| Target-R และ DS Loader | ถามความรู้หรือข้อมูล read-only เกี่ยวกับ Target-R/DS Loader | [`targetr_system.md`](targetr_system.md) |
| ค้นหาจอและสถานที่ใกล้เคียง | ค้นหาจอ ห้าง หรือสาขาที่อยู่ใกล้จุดอ้างอิงผ่านพิกัดภูมิศาสตร์ | [`screen_location.md`](screen_location.md) |
| จัดเตรียมข้อมูลสำหรับ Manage Target-R | สร้างข้อมูล/ไฟล์ (TSV/JSON) พร้อมก๊อปปี้ไปวางอัปเดตฟิลด์หน้าจอหรือ Sequence หลายรายการพร้อมกันที่ `https://tops.actx.digital/manage_target_r` | [`manage_target_r.md`](manage_target_r.md) |
| คู่มือระบบและเครื่องมือ Act-X Programmatic CMS | แนะนำเครื่องมือ ลิงก์หน้าเว็บ และเตรียมข้อมูลให้ผู้ใช้ไปดำเนินการต่อบนระบบ `https://tops.actx.digital` (ครบทั้ง 15+ หน้า/เครื่องมือ) | [`programmatic_cms_guide.md`](programmatic_cms_guide.md) |

## แนวทางเพิ่ม Skill

1. สร้างโฟลเดอร์หรือไฟล์สำหรับ Skill โดยตั้งชื่อให้สื่อความหมาย
2. อธิบายเป้าหมายและสถานการณ์ที่ควรใช้
3. ระบุลำดับการทำงานและ MCP tools ที่เกี่ยวข้อง โดยอ้างชื่อ tool จริงจาก `MCP_SERVER/index.md`
4. ระบุข้อห้าม ข้อมูลอ่อนไหว และวิธีจัดการเมื่อข้อมูลหรือ tool ไม่พร้อม
5. เพิ่มรายการในตารางด้านบน พร้อม path ที่เปิดอ่านได้

Skill ไม่ควรเก็บ credentials หรือข้อมูล production และไม่ควรทำซ้ำรายละเอียด input schema ซึ่งเป็นหน้าที่ของ MCP tool
