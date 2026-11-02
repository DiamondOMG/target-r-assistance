# Skill: ถามข้อมูล Target-R และ DS Loader

## เป้าหมาย

ช่วยตอบคำถามเกี่ยวกับ Target-R ซึ่งเป็น Digital Signage Platform และข้อมูลที่เกี่ยวข้องกับ DS Loader บนอุปกรณ์ Android โดยใช้เอกสารอ้างอิงและ MCP tools ที่ได้รับอนุญาตเท่านั้น

## ใช้เมื่อ

- ผู้ใช้ถามข้อมูล Screen, สาขา, อุปกรณ์ หรือสถานะการติดต่อที่มีอยู่ในข้อมูล Target-R
- ผู้ใช้ถาม Sequence หรือ Library item ที่มีในฐานข้อมูลที่เชื่อมต่อ
- ผู้ใช้ถามความหมายหรือข้อจำกัดของ Target-R/DS Loader ตามเอกสารที่ลงทะเบียนไว้

## ขั้นตอน

1. แยกก่อนว่าคำถามต้องการ **ความรู้จากเอกสาร**, **ข้อมูลสด/ข้อมูลที่ sync ไว้**, หรือทั้งสองอย่าง
2. คำถามเชิงความหมายหรือวิธีทำงาน ให้ใช้เอกสาร Target-R/DS Loader ที่ลงทะเบียนไว้ หากไม่มีเอกสารหรือ tool สำหรับ DS Loader ให้แจ้งข้อจำกัด ห้ามเดา
3. คำถามเกี่ยวกับข้อมูล Screen, Sequence หรือ Library item ให้ใช้ MCP tool `targetr_query` ตาม contract ใน `MCP_SERVER/TOOLS/targetr_query.md`
4. ใช้ `freshness="cached"` โดยปริยาย; เมื่อผู้ใช้ถามข้อมูลล่าสุด, เวลาที่เปลี่ยนแปลงได้ หรือระบุให้ refresh ให้ใช้ `freshness="refresh"` เพื่อ sync entity นั้นกับ Target-R ก่อนอ่าน (การ refresh เขียนข้อมูล sync ลง Neon)
5. เลือก operation ที่คืนข้อมูลน้อยที่สุด: `count` หรือ `group_count` ก่อน `select`; เลือกเฉพาะ fields ที่จำเป็น และจำกัดจำนวนผลลัพธ์
6. ตอบจากผลลัพธ์ tool พร้อมระบุแหล่งและเวลาที่ดึงข้อมูลเมื่อมีให้ หากไม่มีข้อมูลหรือข้อมูลเก่า ให้บอกตรง ๆ
7. หากคำถามถามว่าอุปกรณ์เล่นสื่อจริงหรือไม่ ห้ามสรุปจาก Sequence หรือเวลา Player ติดต่อเพียงอย่างเดียว ต้องมี Display report ที่ตรงช่วงเวลา

## การตีความที่ยืนยันจากเอกสาร

- Screen, Sequence และ Library item มี ID คนละชนิด ห้ามใช้แทนกัน
- `storeCode` เป็น string; รักษาศูนย์นำหน้า
- `STC`, `storeCode` และ `storeLocation` เป็นคนละ field; ห้ามถือว่า map กันได้ทุกกรณี
- `Screen.data.sequenceId` ระบุ Sequence ที่กำหนดให้ Screen ไม่ใช่หลักฐานการเล่นจริง
- `lastPlayerCommsMillis` บอกเวลาติดต่อ Player ล่าสุด ไม่ยืนยันว่าจอแสดงภาพ
- DS Loader เป็นชั้นที่ดูแลการเปิด Player บนอุปกรณ์ ไม่ใช่ชื่อ REST API ทั้งหมด
- `customStatus` ถ้ามีในแหล่งข้อมูล หมายถึงสถานะการจัดการอุปกรณ์ ไม่ใช่ online/offline
- `id`/Screen ID เป็นตัวระบุอุปกรณ์อ่อนไหว; แสดงเฉพาะเมื่อคำถามจำเป็นต้องระบุรายอุปกรณ์

## ข้อห้าม

- ห้ามเรียก API โดยตรงจาก Model/Agent และห้ามสร้าง URL หรือ method เอง
- ห้ามส่ง credentials หรือ raw JSON object ให้ Model
- ห้ามเปิดเผย MAC/Screen ID, พิกัด, resource URL หรือข้อมูลลูกค้า หากไม่จำเป็นและไม่ได้รับอนุญาต
- ห้ามอนุมานสถานะ online, proof of play หรือความหมายของ field ที่เอกสารยังไม่ยืนยัน
- ห้ามใช้ tool สำหรับ sync, write, remote trigger หรือเปลี่ยนค่าบนอุปกรณ์

## แหล่งอ้างอิง

- Target-R API/schema ที่เชื่อมผ่าน MCP tool ตาม `MCP_SERVER/TOOLS/targetr_query.md`
- เอกสารอ้างอิง Target-R ใน `lab-for-ai/DOCUMENTS/TARGET_R/` (เมื่อถูกนำเข้าหรือลงทะเบียนเป็นแหล่งเอกสารของ runtime แล้ว)
- รายละเอียด API Neon ของ Target-R ใน `target-r-neon/API.md`
