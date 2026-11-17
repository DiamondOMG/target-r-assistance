# Skill: การเตรียมข้อมูลสำหรับเครื่องมือ Manage Target-R

## เป้าหมาย

ช่วยเตรียมข้อมูลและสร้างไฟล์ (TSV / JSON) สำหรับนำไป Copy-Paste อัปเดตข้อมูลในเครื่องมือ **Manage Target-R** บน Production:
- **Production URL:** https://tops.actx.digital/manage_target_r
- **Source Code อ้างอิง:** `c:\OMG\programmatic\app\manage_target_r`

โดย Jarvis จะทำหน้าที่ค้นหาข้อมูล ตรวจสอบความถูกต้อง และสร้างชุดข้อมูลผ่าน MCP tool `prepare_targetr_update` เพื่อให้ผู้ใช้นำไปวางและกดอัปเดตด้วยตนเองบนหน้าเว็บ

## ใช้เมื่อ

- ผู้ใช้ต้องการอัปเดตฟิลด์ข้อมูล (data fields) ของหน้าจอหลายจอพร้อมกัน (เช่น พิกัด `gpsLatitude`, `gpsLongitude`, `orientation`, `storeLocation`, `storeCode`, `STC`, `volume`, `restartTime`, `wifiSsid`, `blackCondition`)
- ผู้ใช้ต้องการสร้างไฟล์ JSON หรือ TSV เพื่อนำไปวางในเครื่องมือ `manage_target_r`
- ผู้ใช้ต้องการแทรก Item ใหม่เข้า Sequence หรือแก้ไข `customId` ของ Item เดิมใน Sequence ทีละหลายรายการ

## รูปแบบข้อมูลที่เครื่องมือรองรับ

### 1. Multiple Update Screens (`mode="multiple_update_screens"`)
ใช้ในหน้า Modal **"Multiple Update Screens"** (แท็บ `Manage Screen` -> `Update Screen` -> ปุ่ม `Multiple Update`)
- **ฟอร์แมตที่วางในเว็บ:** TSV (Tab-Separated Values / รูปแบบเดียวกับการก๊อปปี้จาก Excel)
- **กติกาของคอลัมน์:**
  - **คอลัมน์แรก (First Column):** ต้องเป็น Screen ID เสมอ (เช่น `screen_id`)
  - **คอลัมน์ถัดไป (Other Columns):** ต้องเป็น JSON key path ของฟิลด์ที่ต้องการแก้ไข เช่น `gpsLongitude`, `gpsLatitude`, `orientation` (ระบบจะตัด prefix `data.` ออกให้อัตโนมัติหากใส่มา)
- **ตัวอย่างข้อมูล TSV:**
  ```text
  screen_id	gpsLatitude	gpsLongitude
  06BC202512DB	13.7367	100.5231
  06BC202512DC	13.7450	100.5340
  ```

### 2. Update Screen เดี่ยว (`mode="single_screen_json"`)
ใช้ในแท็บ **"Manage Screen"** -> โหมด **"Update Screen"**
- **ฟอร์แมตที่วางในเว็บ:** กรอก `Screen ID` ด้านบน และวาง **JSON Object** ในช่อง Payload
- **ตัวอย่าง JSON:**
  ```json
  {
    "gpsLatitude": "13.7367",
    "gpsLongitude": "100.5231"
  }
  ```

### 3. Insert Sequence Items (`mode="insert_sequence_items"`)
ใช้ในแท็บ **"Manage Sequence"** -> โหมด **"Update Sequence"** -> ปุ่มสีม่วง **"Insert Sequence Items"**
- **ฟอร์แมตที่วางในเว็บ:** กรอก `Sequence ID` เป้าหมาย แล้ววาง **TSV**
- **คอลัมน์บังคับ:** `inner_sequence_id`, `slot` (เริ่มที่ 1), `item` (ลำดับเริ่มที่ 1) และสามารถต่อท้ายด้วยฟิลด์อื่นๆ ที่ต้องการใส่ใน `data` ได้ เช่น `label`, `condition`, `durationMillis` (ระบบเว็บจะดึงข้อมูลจาก Inner Sequence และสุ่ม `customId` 10 หลักให้อัตโนมัติ)
- **ตัวอย่างข้อมูล TSV:**
  ```text
  inner_sequence_id	slot	item	label
  15A3FAF5BB4FA7	1	1	test_label
  ```

### 4. Update Existing Sequence Items (`mode="update_existing_sequence_items"`)
ใช้ในแท็บ **"Manage Sequence"** -> โหมด **"Update Sequence"** -> ปุ่มสีเขียว **"Update Existing Items"**
- **ฟอร์แมตที่วางในเว็บ:** กรอก `Sequence ID` เป้าหมาย แล้ววาง **TSV**
- **คอลัมน์บังคับ:** `inner_sequence_id`, `slot`, `item`, `customId`
- **เงื่อนไขความปลอดภัยของเว็บ:** ทุกแถวต้องตรงกับตำแหน่ง `slot`/`item` และ `innerSequenceId` เดิมที่มีอยู่ใน Sequence จริง หากแถวใดไม่ตรง ระบบจะไม่บันทึกทั้งหมด
- **ตัวอย่างข้อมูล TSV:**
  ```text
  inner_sequence_id	slot	item	customId
  15D7F2C8A3B51	6	1	InnerHivestackForTopsPremiumVDOWall2x1 01 Slot 6
  ```

## ขั้นตอนการทำงานของ Agent

1. **ค้นหาและตรวจสอบข้อมูลต้นทาง:**
   - หากผู้ใช้ระบุชื่อสาขาหรือเงื่อนไข ให้ใช้ `targetr_fuzzy_search` และ `targetr_query` เพื่อดึง `screenId` หรือ `sequenceId` ที่ถูกต้องมาก่อน
2. **สร้างข้อมูลและไฟล์ด้วย MCP Tool `prepare_targetr_update`:**
   - เรียกใช้ tool `prepare_targetr_update` ตาม `mode` ที่ตรงกับงาน
   - Tool จะสร้างทั้งข้อมูลพร้อมก๊อปปี้ (`paste_content`) และบันทึกไฟล์ `.tsv` กับ `.json` ลงในโฟลเดอร์ `SANDBOX/` อัตโนมัติ
3. **ส่งมอบผลลัพธ์ให้ผู้ใช้ทำต่อ:**
   - แสดงลิงก์ Production https://tops.actx.digital/manage_target_r
   - แสดงทั้งบล็อก **TSV** (สำหรับก๊อปปี้วางใน Modal Multiple Update ได้ทันที) และบล็อก **JSON** (หรือแนบลิงก์ไฟล์ที่สร้างใน `SANDBOX/`)
   - แจ้งขั้นตอนการกดปุ่มบนหน้าเว็บตาม `instructions` ที่ได้จาก tool
