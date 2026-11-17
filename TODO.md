# Jarvis TODO

## เป้าหมาย

สร้าง Skills และ MCP tools ที่แยกจาก Agent Host เพื่อให้ทดลองใช้กับ Host ได้หลายตัว และเปลี่ยน Host ได้โดยไม่ต้องรื้อความสามารถหลัก

## ลำดับงาน

### 1. วางขอบเขต

- [x] เลือกกรณีใช้งานแรก: ถามข้อมูล Target-R / DS Loader
- [x] เลือก Target-R data ผ่าน Neon: Screen, Sequence และ Library item; DS Loader เป็นชื่อเรียกแทน Target-R
- [x] กำหนดข้อห้ามด้านข้อมูล: ไม่คืน raw JSON, จำกัด fields/จำนวนผล และระวัง Screen ID
- [x] กำหนด read-only query เป็นค่าเริ่มต้น; refresh เรียก sync/upsert เฉพาะเมื่อเลือก freshness=refresh

### 2. ทำ Skills

- [x] เพิ่ม Skill ฉบับแรก `SKILLS/targetr_system.md`
- [x] ระบุแนวทางใช้ tool และตอบเมื่อข้อมูลไม่พอ
- [x] เพิ่มรายการ Skill ใน `SKILLS/index.md`

### 3. ทำ MCP tools

- [x] เลือก Python MCP SDK และ stdio transport สำหรับเริ่มทดลองกับ Host
- [x] กำหนด contract ของ `targetr_query` ใน `MCP_SERVER/TOOLS/targetr_query.md`
- [x] เลือก Neon Function API ที่ไม่ส่ง raw เป็นแหล่งข้อมูล; filter ใน MCP หลังดึงชุดข้อมูล
- [x] พัฒนา `targetr_query` สำหรับ query แบบ read-only และ refresh ตามคำขอ
- [x] จำกัด fields, จำนวนผลลัพธ์ และปฏิเสธ raw `data` ก่อนส่งกลับ Agent
- [x] เก็บ credentials ใน environment; ไม่ log credential หรือ raw response
- [x] เพิ่ม tests สำหรับ validation, filtering, projection และ group count
- [x] อัปเดตรายการ tools ใน `MCP_SERVER/index.md`
- [x] เพิ่ม Tool Contract `geo_distance` ใน `MCP_SERVER/TOOLS/geo_distance.md` และ Skill `SKILLS/screen_location.md` สำหรับค้นหาตำแหน่งใกล้เคียง
- [x] พัฒนา Tool `targetr_fuzzy_search` ใน `MCP_SERVER/jarvis_mcp/fuzzy_search.py` ดึงข้อมูลจาก Google Sheet และเพิ่ม tests ครบถ้วน
- [x] รวมและลงทะเบียน MCP Tools ทั้งหมด 4 ตัวใน `MCP_SERVER/jarvis_mcp/server.py` พร้อมรัน pytest ผ่าน 100% (20 tests passed)
- [x] จัดทำ Data Catalog ของ Google Sheets ใน `SHEETS_INDEX.md` รองรับ `Jarvis_TargetR_Master` และ `Tops Monitor` (Floor Plan Mapping)
- [x] พัฒนา Tool `send_email` ใน `MCP_SERVER/jarvis_mcp/email_sender.py` ผ่าน Gmail SMTP พร้อมบันทึก App Password ลงถังและเทสผ่าน 100%

### 4. ทดลองกับ Agent Host

- [ ] เลือก Host สำหรับทดสอบอย่างน้อยหนึ่งตัว
- [ ] ตรวจว่า Host ค้นพบ MCP tools และส่ง input ตาม schema ได้
- [ ] ตรวจว่า Host จัดการ session/context ได้เหมาะกับการใช้งาน
- [ ] ทดลองเปลี่ยน Host โดยไม่แก้ Skills และ tool contracts
- [ ] บันทึกข้อดี ข้อจำกัด และประเด็นความปลอดภัยของแต่ละ Host ก่อนตัดสินใจ

### 5. ต่อยอดหลังทดสอบ

- [ ] ประเมินการเชื่อมต่อจากระบบอื่นผ่าน API หรือ channel ที่ต้องการ
- [ ] ประเมินช่องทางเสียง เช่น microphone และ speaker
- [ ] พัฒนา MCP ควบคุม Sharp Smart TV / Android TV ผ่าน ADB over Tailscale (งานพรุ่งนี้):
  - [ ] ติดตั้งและตั้งค่าการเชื่อมต่อเน็ตเวิร์ก (Tailscale on TV / Subnet Router)
  - [ ] พัฒนาคำสั่งควบคุม: เปิด/ปิดจอ, สั่งเปิดแอป (Launch App), สั่งเปิดลิงก์เว็บ (Open URL)
  - [ ] ออกแบบ Tool Contract และสร้าง MCP Tool `tv_control` สำหรับให้ Jarvis สั่งการทีวีข้ามวงแลน
- [ ] ออกแบบ memory หลังจากยืนยันรูปแบบการใช้งานและ Host แล้ว

## หลักการตัดสินใจ

- ยังไม่เลือก Agent Host ถาวร; ให้ Skills และ MCP tools เป็นอิสระจาก Host
- ยังไม่สร้างระบบจัดการ session/context เอง จนกว่าจะพบข้อจำกัดที่ Host ปัจจุบันแก้ไม่ได้
- เพิ่มเฉพาะส่วนที่จำเป็นต่อกรณีใช้งานแรก แล้วค่อยขยายจากผลทดสอบ
