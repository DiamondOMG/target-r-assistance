# Skill: คู่มือระบบและเครื่องมือทั้งหมดใน Act-X Programmatic CMS (`tops.actx.digital`)

## เป้าหมาย

ใช้แนะนำผู้ใช้งานว่าเว็บแอปพลิเคชัน **Self-Served Digital Ads CMS (Act-X Programmatic)** บน Production (`https://tops.actx.digital` / source code ที่ `c:\OMG\programmatic`) มีหน้าเครื่องมือและฟีเจอร์อะไรบ้าง พร้อมช่วยเตรียมข้อมูล พารามิเตอร์ หรือไฟล์ (TSV / JSON / Condition) ให้ผู้ใช้นำไปคลิกหรือวางดำเนินการต่อด้วยตนเอง

> **หลักการสำคัญ:** Jarvis มีหน้าที่ค้นหาข้อมูล ตรวจสอบความถูกต้อง เตรียมไฟล์/ข้อความ และแนะนำลิงก์เครื่องมือที่ตรงกับงาน โดยให้ **ผู้ใช้เป็นผู้กดดำเนินการสุดท้ายบนหน้าเว็บด้วยตนเองเสมอ**

---

## ใช้เมื่อ

- ผู้ใช้ถามว่าระบบเว็บ `tops.actx.digital` หรือโปรเจกต์ `programmatic` ทำอะไรได้บ้าง
- ผู้ใช้ต้องการทำงานเกี่ยวกับการลงแคมเปญ, ลบแคมเปญหลายตัว, เช็ค Slot ว่าง, ตรวจสอบจอออฟไลน์, ตรวจสอบจำนวนสื่อที่เล่นจริงบนจอ (Audit), จำลองการเล่นสื่อ (Playback Simulator), จัดการผังสาขา (Floor Plan), ตั้งค่า Sequence/Slot/Store หรืออนุมัติ Smart TV
- ผู้ใช้ต้องการให้ช่วยเตรียมข้อมูลเพื่อนำไปใช้ในหน้าใดหน้าหนึ่งของ `https://tops.actx.digital`

---

## รายการเครื่องมือและหน้าทั้งหมดใน `https://tops.actx.digital`

### หมวดที่ 1: การจัดการแคมเปญโฆษณา (Campaigns)

#### 1. Retailer Campaigns (จัดการแคมเปญฝั่งห้าง)
- **Production URL:** https://tops.actx.digital/campaigns
- **สิทธิ์ที่ต้องใช้:** มีสิทธิ์หน้า `retailer`
- **ทำอะไรได้บ้าง:**
  - กรองดู Sequence ตาม **Retailer** (เช่น Tops, Big C), **Type** (เช่น Tops Daily, Tops Food Hall), และ **Signage Format** (เช่น TV Signage, VDO Wall)
  - ดูสถานะของแต่ละ Slot ใน Sequence (`Online`, `Scheduled`, `Expired`, หรือ `Empty`)
  - **สร้างแคมเปญใหม่ลง Slot:**
    - อัปโหลดไฟล์รูปภาพหรือวิดีโอเข้า Library (มีเครื่องมือ **Custom Video** ช่วยปรับแต่ง/ตัดวิดีโอก่อนอัปโหลด)
    - กำหนดชื่อแคมเปญ (`Label`), รหัสจอง (`Booking Code`), และหมายเหตุ (`Note`)
    - ตั้งวันเริ่ม (`Start Date` — ระบบตั้งเวลาเริ่มที่ `00:05`) และวันสิ้นสุด (`End Date` — ระบบตั้งเวลาสิ้นสุดที่ `23:55`)
    - เลือกสาขาเป้าหมาย (`Store Locations`) ที่ต้องการให้สื่อไปแสดงผล
  - **แก้ไข / ลบแคมเปญ:** แก้ไขวันเวลา สาขา หรือลบแคมเปญออกจาก Slot รายตัว
- **สิ่งที่ Jarvis ช่วยเตรียมให้ผู้ใช้ได้:**
  - ใช้ `targetr_fuzzy_search` และ `targetr_query` ช่วยเช็ครายชื่อสาขา (`storeLocation`), รูปแบบจอ (`signageFormat`), หรือค้นหา `sequenceId` ที่ตรงกับห้างที่ต้องการลงสื่อ

#### 2. Customer Campaigns (จัดการแคมเปญฝั่งลูกค้า / แบรนด์ & ลบแบบกลุ่ม)
- **Production URL:** https://tops.actx.digital/customer_campaigns
- **สิทธิ์ที่ต้องใช้:** มีสิทธิ์หน้า `customer`
- **ทำอะไรได้บ้าง:**
  - สร้างและแก้ไขแคมเปญสำหรับลูกค้า/แบรนด์ (Sale / 3rd Party Slots) เหมือนหน้า Retailer Campaigns
  - **ฟีเจอร์พิเศษ — Multi-Delete (Bulk Deletion):** สามารถติ๊กเลือกแคมเปญหลายรายการพร้อมกัน แล้วกดปุ่มลบครั้งเดียวผ่านหน้าต่างยืนยัน `Confirm Bulk Deletion`
- **สิ่งที่ Jarvis ช่วยเตรียมให้ผู้ใช้ได้:**
  - ช่วยตรวจสอบรายการแคมเปญหรือ Library item ที่หมดอายุหรือซ้ำซ้อน เพื่อให้ผู้ใช้ไปติ๊กลบพร้อมกันที่หน้านี้

---

### หมวดที่ 2: แดชบอร์ดและตรวจสอบคิวว่าง (Dashboard & Slot Monitoring)

#### 3. Pack-Slot Available (เช็คตารางคิวและ Slot ว่าง)
- **Production URL:** https://tops.actx.digital/monitor_customer_campaigns
- **ทำอะไรได้บ้าง:**
  - ดูภาพรวมว่าในแต่ละ **Retailer**, **Type**, และ **Signage Format** มี Slot ว่างกี่ยูนิต และช่องไหนมีแคมเปญจองอยู่แล้วบ้าง
  - แสดงผลเป็นตาราง Grid แยกสีตามสถานะ ช่วยให้ทีมขายและทีมแอดมินเช็คคิวว่างก่อนรับงานได้ทันที

#### 4. Store Process Dashboard (แดชบอร์ดภาพรวมการติดตั้งแยกตามผู้ดูแล)
- **Production URL:** https://tops.actx.digital/dashboard
- **สิทธิ์ที่ต้องใช้:** Manager ขึ้นไป (`permission_user >= 3`)
- **ทำอะไรได้บ้าง:**
  - ดูสรุปจำนวนสาขา (`STC`), จำนวนเครื่องเล่น (`Media Players`), และจำนวนจอที่เชื่อมต่อจริง (`Screens / displaysConnected`)
  - แยกสัดส่วนและกราฟตามผู้ดูแลระบบ (**ActMedia** สำหรับจุดติดตั้งใหม่ `playerInstallation = new` เทียบกับ **Tops / Retailer** สำหรับจุดติดตั้งเดิม `existing`)
  - กรองดูข้อมูลเจาะจงตามสาขา (`storeLocation`) และรูปแบบจอ (`signageFormat`)

---

### หมวดที่ 3: เครื่องมือจัดการและตรวจสอบเชิงลึกสำหรับ Admin (`permission_user >= 4`)

#### 5. Manage Target-R (เครื่องมือยิงอัปเดตข้อมูล Screen และ Sequence โดยตรง)
- **Production URL:** https://tops.actx.digital/manage_target_r
- **รายละเอียดเพิ่มเติม:** ดูได้ที่ [`manage_target_r.md`](manage_target_r.md)
- **ทำอะไรได้บ้าง (5 ฟีเจอร์ย่อย):**
  1. **Multiple Update Screens (อัปเดตฟิลด์ข้อมูลหลายจอพร้อมกัน):**
     - แท็บ `Manage Screen` -> `Update Screen` -> ปุ่ม `Multiple Update`
     - วางข้อมูล **TSV** (ก๊อปจาก Excel) โดยคอลัมน์แรกคือ `screen_id` และคอลัมน์ถัดไปคือชื่อฟิลด์ที่ต้องการแก้ (เช่น `gpsLatitude`, `gpsLongitude`, `orientation`, `storeLocation`, `storeCode`, `STC`, `volume` ฯลฯ)
  2. **Create / Update Screen รายจอด้วย JSON:**
     - แท็บ `Manage Screen` -> วาง JSON Payload เพื่อสร้างจอใหม่หรืออัปเดตจอตาม `Screen ID`
  3. **Insert Sequence Items (แทรก Item เข้า Sequence ทีละหลายรายการ):**
     - แท็บ `Manage Sequence` -> `Update Sequence` -> ปุ่มสีม่วง `Insert Sequence Items`
     - ระบุ `Sequence ID` แล้ววาง **TSV** (`inner_sequence_id`, `slot`, `item` และฟิลด์เสริมอื่นๆ) ระบบจะดึงข้อมูล Inner Sequence และสุ่ม `customId` แทรกเข้า Slot ให้อัตโนมัติ
  4. **Update Existing Sequence Items (อัปเดต `customId` ของ Item เดิมแบบกลุ่ม):**
     - แท็บ `Manage Sequence` -> `Update Sequence` -> ปุ่มสีเขียว `Update Existing Items`
     - ระบุ `Sequence ID` แล้ววาง **TSV** (`inner_sequence_id`, `slot`, `item`, `customId`) ระบบจะตรวจสอบความตรงกันของตำแหน่งก่อนบันทึกทั้งหมด
  5. **Create / Update Sequence รายตัวด้วย JSON:**
     - แท็บ `Manage Sequence` -> วาง JSON Payload เพื่อสร้างหรืออัปเดต Sequence
- **สิ่งที่ Jarvis ช่วยเตรียมให้ผู้ใช้ได้:**
  - เรียก MCP tool `prepare_targetr_update` เพื่อสร้างข้อความ TSV / JSON และบันทึกไฟล์ลง `SANDBOX/` ให้ผู้ใช้ก๊อปปี้ไปวางได้ทันที

#### 6. Perion Dashboard / Screen Monitor (แดชบอร์ดเช็คสถานะจอ Online / Offline สด)
- **Production URL:** https://tops.actx.digital/screen-monitor
- **ทำอะไรได้บ้าง:**
  - ดึงข้อมูลสดจาก API เพื่อตรวจสอบสถานะการติดต่อของจอทั้งหมด
  - แบ่งกลุ่มสถานะอัตโนมัติ:
    - **Online** (ติดต่อภายใน 1 ชั่วโมง)
    - **Offline > 1 ชั่วโมง** (`over_1_hour`)
    - **Offline > 1 วัน** (`over_1_day`)
    - **Offline > 7 วัน** (`over_7_days`)
  - ค้นหาตาม `Screen ID`, `Store Location`, กรองตาม `Retailer` (แสดงป้ายสีแยก Tops / Big C)
  - เรียงลำดับจากจอที่ออฟไลน์นานที่สุดขึ้นก่อน (`offline_desc`)
  - กดปุ่มคัดลอก `Screen ID` หรือกดปุ่ม **Export JSON** เพื่อดาวน์โหลดไฟล์ `perion_dashboard_export_YYYY-MM-DD.json`

#### 7. Screen Playback Audit Table (ตารางตรวจสอบสุขภาพจำนวนสื่อบนจอ & Sync แคช)
- **Production URL:** https://tops.actx.digital/screen-audit
- **ทำอะไรได้บ้าง:**
  - ตรวจสอบจอทั้งหมดกว่า 4,000+ จอที่จับคู่กับ `Sequence V2` แล้วคำนวณจำลอง Playback รายสาขา (`storeCode`) เพื่อดูว่าแต่ละจอมีสื่อไม่ซ้ำกันกี่ชิ้น (**Unique Content / `blobId`**)
  - กรองดูเฉพาะจอที่มีปัญหาสื่อน้อยผิดปกติ:
    - **LOW (`< 3` ชิ้น):** จอที่มีคอนเทนต์เล่นน้อยกว่า 3 ชิ้น (เสี่ยงแสดงผลซ้ำหรือแคมเปญไม่เข้า)
    - **HEALTHY (`>= 3` ชิ้น):** จอที่มีคอนเทนต์ปกติ
  - **ปุ่ม ⚡ Sync แคชลง Supabase:** ยิงดึงข้อมูลจอทั้งหมดจาก Target-R API สดใหม่ไปอัปเดตลงแคช Supabase ของระบบเว็บ

#### 8. Playback Simulator & Console (จำลองการเล่นสื่อบนหน้าจอ)
- **Production URL:** https://tops.actx.digital/playback-test
- **ทำอะไรได้บ้าง:**
  - ทดสอบคำนวณว่าหน้าจอจะเล่นสื่อชิ้นใดบ้าง (ผ่านเกณฑ์วันเวลาและ `condition` ของสาขาหรือไม่) โดยไม่ต้องเดินทางไปดูจอจริง
  - รองรับ 2 โหมดการจำลอง:
    1. **Sequence ID + Store:** เลือก `Sequence ID` คู่กับ `Store Location` เพื่อดูสื่อที่จะเล่นในสาขานั้น
    2. **By Screen ID:** กรอก `Screen ID` (เช่น `06BC2025123E`) เพื่อจำลองการเล่นของจอนั้นโดยตรง
  - แสดงภาพพรีวิวสื่อจริงจาก Blob Store (`blobId`), ลำดับ Slot, และข้อมูล JSON ที่คำนวณได้
- **สิ่งที่ Jarvis ช่วยเตรียมให้ผู้ใช้ได้:**
  - ค้นหา `Screen ID` หรือ `Sequence ID` ของสาขาที่ผู้ใช้สงสัยผ่าน `targetr_query` แล้วส่งรหัสพร้อมลิงก์ https://tops.actx.digital/playback-test ให้ผู้ใช้ไปกด Simulate ดูภาพจริงได้ทันที

#### 9. Sequence & Slot Management (ตั้งค่า Sequence V2 และผังสี Slot)
- **Production URL:** https://tops.actx.digital/sequence
- **ทำอะไรได้บ้าง:**
  - เพิ่ม/แก้ไข/ลบรายการในตาราง `sequence_v2` ซึ่งใช้ผูก `sequence_id` และ `inner_sequence_id` เข้ากับ `retailer`, `type`, `signage_format`, ขนาดความละเอียดจอ (`width` x `height`), รูปตัวอย่างห้าง/รูปแบบจอ และผัง Slot
  - **Slot Management Modal (จัดการผัง Slot):**
    - สร้างและแก้ไขเทมเพลตการจัดสรร Slot (ตั้งแต่ 40 ถึง 480 ช่อง ปรับเพิ่มลดทีละ 40 ช่อง)
    - ระบายสีกำหนดสิทธิ์ของแต่ละช่อง: **Retail** (สีฟ้า), **Sale** (สีเทา), **3Party** (สีชมพู) และตั้งค่า **Special Slot**

#### 10. Store Location Management (ตั้งค่าสาขาและเงื่อนไข Condition)
- **Production URL:** https://tops.actx.digital/store
- **ทำอะไรได้บ้าง:**
  - เพิ่ม/แก้ไข/ลบข้อมูลสาขา (`store_location`) ที่ใช้เป็นตัวเลือกเวลาลงแคมเปญ
  - ดึงรายชื่อจอจาก `Group ID` (ค่าเริ่มต้น `13CF174ED72274`) เพื่อผูกชื่อสาขา (`location`) เข้ากับ `retailer`, `type`, `signage_format` และนิพจน์เงื่อนไข **`condition`** สำหรับกรองการแสดงผลบน Target-R
- **สิ่งที่ Jarvis ช่วยเตรียมให้ผู้ใช้ได้:**
  - ช่วยตรวจสอบชื่อ `storeLocation` ที่แท้จริงในระบบ Target-R เพื่อให้ตั้งค่า `location` และ `condition` ในหน้า `/store` ได้ตรงกันไม่ผิดพลาด

---

### หมวดที่ 4: แผนที่ ผังสาขา และอุปกรณ์ทีวี (Map, Floor Plan & Smart TV)

#### 11. Map & Summary Toolbox (แผนที่จุดติดตั้งทั่วประเทศและกราฟสรุปข้อมูล)
- **Production URL:** https://tops.actx.digital/map (สามารถระบุสาขาผ่าน URL ได้ เช่น `https://tops.actx.digital/map?store=<ชื่อสาขา>`)
- **ทำอะไรได้บ้าง:**
  - แสดงแผนที่ประเทศไทยแบบ Interactive ดูจำนวนจุดติดตั้งแยกตามภูมิภาค จังหวัด และคลิกดูรายละเอียดรายสาขา
  - มี **Summary Toolbox** สำหรับกรองและดูสถิติพร้อมกราฟแยกตาม: `Store`, `Retailer Type`, `Signage Format`, `Screen ID`, `Retailer`, `Player type`, `Player shape`, `RAM`, `Installation`, `STC`, `Asset type`, `Asset name`

#### 12. Custom Map / Store Layout Editor (เครื่องมือปักหมุดจอและแก้ไขผังสาขา)
- **Production URL:** https://tops.actx.digital/custom_map
- **ทำอะไรได้บ้าง:**
  - เลือกสาขาจากฐานข้อมูล Google Sheets เพื่อจัดการภาพแผนผังภายในร้าน (Floor Plan)
  - อัปโหลดรูปแผนผังหรือไฟล์ **PDF** (ระบบแปลงหน้า PDF เป็นรูปภาพให้อัตโนมัติ)
  - ครอป (Crop) และหมุนภาพตามสัดส่วนมาตรฐาน 4 รูปแบบ (`11:9`, `16:7`, `12:9`, `16:7.5`) แล้วอัปโหลดขึ้น Cloudinary
  - **ปักหมุดและลากวางตำแหน่งอุปกรณ์บนผังร้าน:** เลือกวางหมุด `screen` (จอโฆษณา) หรือ `router` (จุดกระจายสัญญาณอินเทอร์เน็ต) พร้อมกรอกรายละเอียดของแต่ละจุด
  - แก้ไขข้อมูลรายละเอียดสาขา (Branch Details) แล้วกดบันทึกลง Google Sheets หรือดาวน์โหลดภาพแผนผังออกมาเป็นไฟล์ PNG

#### 13. Smart TV Setup & Device Approval (เชื่อมต่อและอนุมัติทีวีดูแผนที่)
- **URL สำหรับเปิดบนทีวี:** https://tops.actx.digital/tv-setup
- **URL สำหรับแอดมินอนุมัติ:** https://tops.actx.digital/tv-devices
- **ทำอะไรได้บ้าง:**
  - เปิดหน้า `/tv-setup` บนเบราว์เซอร์ของ Smart TV เพื่อรับรหัสจับคู่ 6-12 หลัก (Pairing Code)
  - แอดมินนำรหัสไปกรอกในหน้า `/tv-devices` แล้วกด **"อนุมัติทีวี"** เพื่อให้ทีวีเข้าสู่หน้าแผนที่ `/map` ได้โดยไม่ต้องล็อกอินซ้ำ (และสามารถกด **"เพิกถอน"** สิทธิ์ทีวีได้ตลอดเวลา)

---

### หมวดที่ 5: การจัดการผู้ใช้และประวัติระบบ (Users & Audit Logs)

#### 14. User Permission Management (จัดการผู้ใช้งานและระดับสิทธิ์)
- **Production URL:** https://tops.actx.digital/list-user
- **สิทธิ์ที่ต้องใช้:** Admin ระดับ 4 เท่านั้น (`permission_user === 4`)
- **ทำอะไรได้บ้าง:**
  - ดูรายชื่อผู้ใช้งานทั้งหมดและลบผู้ใช้
  - กำหนดระดับสิทธิ์ (`permission_user`):
    - `1 = Viewer` (ดูข้อมูลอย่างเดียว)
    - `2 = Editor` (จัดการแคมเปญ)
    - `3 = Manager` (ดู Dashboard ภาพรวมห้างได้)
    - `4 = Admin` (เข้าถึงเมนู Admin ทั้งหมด)
  - กำหนดสิทธิ์ห้างที่ดูแลได้ (`permission_retailer`) และสิทธิ์การเข้าหน้าแคมเปญ (`retailer`, `customer`)

#### 15. Audit Logs (ประวัติการแก้ไขข้อมูลในระบบ)
- **Production URL:** https://tops.actx.digital/logs
- **ทำอะไรได้บ้าง:**
  - ตรวจสอบประวัติการทำรายการ (`INSERT`, `UPDATE`, `DELETE`) ในตารางต่างๆ ของระบบ
  - ดูว่าใครเป็นคนแก้ไข (`Changed By`), แก้ไขเมื่อไหร่ (`GMT+7`), ที่ตารางและแถวใด พร้อมเปิดดูรายละเอียดข้อมูลที่เปลี่ยนแปลงได้

---

## ตารางสรุปลิงก์ด่วนสำหรับแนะนำผู้ใช้

| งานที่ผู้ใช้ต้องการทำ | เครื่องมือที่แนะนำ | ลิงก์ Production |
|---|---|---|
| อัปเดตข้อมูลหลายจอพร้อมกัน (Excel/TSV) หรือแก้ JSON จอ/Sequence | **Manage Target-R** | https://tops.actx.digital/manage_target_r |
| ลงแคมเปญโฆษณาฝั่งห้าง (Retailer) | **Retailer Campaigns** | https://tops.actx.digital/campaigns |
| ลงแคมเปญลูกค้า หรือลบแคมเปญหลายตัวพร้อมกัน (Multi-Delete) | **Customer Campaigns** | https://tops.actx.digital/customer_campaigns |
| เช็คตารางคิวและจำนวน Slot ว่าง | **Pack-Slot Available** | https://tops.actx.digital/monitor_customer_campaigns |
| ดูภาพรวมจำนวนสาขา/เครื่องเล่น แยกตาม ActMedia vs ห้าง | **Store Process Dashboard** | https://tops.actx.digital/dashboard |
| เช็คจอ Online / Offline รายชั่วโมง-รายวัน และ Export JSON | **Perion Dashboard** | https://tops.actx.digital/screen-monitor |
| ตรวจสุขภาพจอว่ามีสื่อเล่นกี่ชิ้น (`< 3` ชิ้น) หรือกด Sync แคชจอ | **Screen Audit Table** | https://tops.actx.digital/screen-audit |
| จำลองดูว่าจอหรือสาขานั้นจะเล่นภาพ/วิดีโอตัวไหนบ้าง | **Playback Test** | https://tops.actx.digital/playback-test |
| ตั้งค่า Sequence V2 หรือจัดผังสี Slot (Retail / Sale / 3Party) | **Sequence Management** | https://tops.actx.digital/sequence |
| เพิ่ม/แก้ไขสาขา และตั้งค่าเงื่อนไข `condition` | **Store Management** | https://tops.actx.digital/store |
| ดูแผนที่จุดติดตั้งทั่วประเทศและกราฟสรุปสเปกเครื่อง | **Map & Summary** | https://tops.actx.digital/map |
| อัปโหลดผังร้าน (Floor Plan) และปักหมุดตำแหน่งจอ/เราเตอร์ | **Custom Map Editor** | https://tops.actx.digital/custom_map |
| อนุมัติรหัสเชื่อมต่อ Smart TV หรือเพิกถอนสิทธิ์ทีวี | **TV Devices Admin** | https://tops.actx.digital/tv-devices |
| จัดการสิทธิ์ผู้ใช้งาน (Viewer / Editor / Manager / Admin) | **List User** | https://tops.actx.digital/list-user |
| ดูประวัติการเพิ่ม/ลบ/แก้ไขข้อมูลในระบบ | **Audit Logs** | https://tops.actx.digital/logs |
