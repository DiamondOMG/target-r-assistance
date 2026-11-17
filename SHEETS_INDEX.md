# Sheets Index (Data Catalog)

สารบัญและ Data Dictionary ของ Google Sheets ทั้งหมดที่เชื่อมต่อกับระบบ Jarvis เพื่อให้ AI Agent ทราบโครงสร้างข้อมูล (Schema), ความหมายของฟิลด์ และคีย์เชื่อมโยงก่อนเรียกอ่านข้อมูลจริงผ่าน Google Sheets API

---

## 1. `Jarvis_TargetR_Master`

* **File ID:** `1K0hWy-Mgl52a7TR6Rzy8XvsGSjl7kwNmsm5sxqRpJoE`
* **สิทธิ์การเข้าถึง:** Editor
* **โฟลเดอร์:** `Jarvis_Workspace`
* **วัตถุประสงค์:** ฐานข้อมูล Master Reference และ Alias Mapping สำหรับค้นหาชื่อสาขาภาษาไทย คำย่อ และประเภทจอ
* **เงื่อนไขสำคัญ:** เป็น Static Reference ไม่ใช่ข้อมูลสด ห้ามใช้ฟิลด์ในชีตนี้อ้างอิงจำนวนจอหรือสถานะออนไลน์

### โครงสร้างแท็บและ Schema

| แท็บ | วัตถุประสงค์ | Schema (คอลัมน์) | คีย์เชื่อมโยง (Key) |
|---|---|---|---|
| **`Location`** | จับคู่ชื่อสาขาภาษาอังกฤษ-ไทย, คำย่อ, รหัส | `store_location`, `thai_name`, `aliases`, `retailer`, `store_code`, `notes` | `store_location` $\leftrightarrow$ `Screen.storeLocation`<br/>`store_code` $\leftrightarrow$ `Screen.storeCode, STC` |
| **`Projects`** | ข้อมูลโครงการและแบรนด์ค้าปลีก | `project_name`, `retailer`, `thai_name`, `aliases`, `notes` | `project_name` $\leftrightarrow$ `Screen.ProjectName` |
| **`Labels`** | ประเภทและโซนการติดตั้งจอ | `label_type`, `zone`, `thai_name`, `aliases`, `notes` | `label_type` $\leftrightarrow$ `Screen.signageType` |
| **`Team_Knowledge`** | คลังความรู้ส่วนกลางของทีม (Real-time Knowledge Base) | `topic_id`, `title`, `category`, `tags`, `content`, `updated_by`, `updated_at` | จัดการผ่าน `team_knowledge_search` / `team_knowledge_save` |

---

## 2. `Tops Monitor`

* **File ID:** `1FqkrWem-t83KALPVJ94jODKKrBwfuLhbsSJFzCQSy5w`
* **สิทธิ์การเข้าถึง:** Read-Only (Viewer)
* **โฟลเดอร์:** `Jarvis_Team_Workspace / Read Only`
* **วัตถุประสงค์:** แผนผังจุดติดตั้งจอและเราเตอร์บน Floor Plan (ภาพแปลนร้าน) ของ Tops Digital ทุกสาขา

### โครงสร้างแท็บหลัก (Core Master Tabs)

| แท็บ | วัตถุประสงค์ | Schema (คอลัมน์) | คีย์เชื่อมโยง (Key) |
|---|---|---|---|
| **`Link2Store`** | ตารางจับคู่สาขาทางการ | `No.`, `Retail`, `Store Fomat`, `Full Code`, `Store Code`, `Store Name`, `Status` | `Full Code` = `STC`<br/>`Store Code` = `storeCode`<br/>`Store Name` = `storeLocation` |
| **`Store-Summary`** | สรุปความคืบหน้าของแต่ละสาขา | `storeLocation`, `storeCode`, `position`, `progress`, `retailer`, `retailer_type`, `branch_thai`, `gpsLatitude` | `storeLocation`, `storeCode`, `branch_thai` (ชื่อไทยทางการ) |
| **`GoogleSheet-TopsDigital-Summary`** | รวมรายการตำแหน่งจอทุกสาขา | `device`, `macaddress`, `number`, `position_x`, `position_y`, `image`, `formation`, `retailer_type` | รวมทุกจุดติดตั้งในชีตเดียว |
| **`README`** | ที่เก็บ Asset แผนผัง | ลิงก์ Cloudinary โฟลเดอร์เก็บภาพ Floor Plan | - |

### แท็บประจำสาขา (`TopsDigital-<StoreName>`, 130+ แท็บ)

เช่น `TopsDigital-WanghinPlazaLagoon`, `TopsDigital-EkkamaiRamintra`

| คอลัมน์ | ความหมาย | ตัวอย่าง | การนำไปใช้ |
|---|---|---|---|
| `device` | ชนิดอุปกรณ์ | `screen`, `router` | แยกจอออกจากอุปกรณ์เน็ตเวิร์ก |
| `macaddress` | ตัวระบุอุปกรณ์ | `020071734629` (จอ)<br/>`5A93` (เราเตอร์) | **ตรงกับ `screenId` ใน Target-R (Neon)**<br/>*(ถ้าเป็น router คือ 4 ตัวท้ายของ Mac เราเตอร์)* |
| `number` | หมายเลขจอประจำสาขา | `1`, `2`, `3` | ใช้ระบุหมายเลขตำแหน่งบนผัง |
| `position_x` | พิกัดแนวนอนบนภาพแปลน | `67.0%` | จุดพิกัดแกน X บน Floor Plan |
| `position_y` | พิกัดแนวตั้งบนภาพแปลน | `49.1%` | จุดพิกัดแกน Y บน Floor Plan |
| `image` | URL ภาพแผนผังร้าน | `https://res.cloudinary.com/...` | รูป Floor Plan ประจำสาขานั้น |
| `formation` | การจัดวางจอ | `1`, `2x1`, `3x1` | รูปแบบการติดตั้งจอเดี่ยวหรือวิดีโอวอลล์ |
| `retailer_type` | รูปแบบสาขา | `Premium`, `Foodhall`, `Market` | รูปแบบการจัดหมวดหมู่ Tops |

> **หมายเหตุ:** แท็บที่ขึ้นต้นด้วยตัวเลข (เช่น `142 TM142...`) ให้มองข้าม เนื่องจากยังไม่มีข้อมูล

