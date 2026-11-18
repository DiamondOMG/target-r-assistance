# Jarvis — Target-R Assistance & MCP Ecosystem

โปรเจกต์ผู้ช่วย AI สำหรับทีม Operation ใช้ตรวจสอบ วิเคราะห์ เตรียมไฟล์สำหรับเครื่องมือ **Manage Target-R** และตอบคำถามหน้างานผ่าน **Antigravity Desktop** (แยกขาดจากข้อมูลลับส่วนตัว)

---

## โครงสร้างโปรเจกต์

| โฟลเดอร์ / ไฟล์ | หน้าที่ |
|---|---|
| [`00_INDEX.md`](00_INDEX.md) | **ยอดปิรามิด (สารบัญหลัก)**: จุดเริ่มต้นเดียวสำหรับทุกคำถามและแผนผังนำทางสู่หมวดย่อยทั้งหมด |
| [`AGENTS.md`](AGENTS.md) | กฎหลัก ลำดับการอ่านปิรามิด และสิทธิ์การใช้งาน (`PERMISSION=staff` / `admin`) |
| [`SKILLS/`](SKILLS/index.md) | ขั้นตอนการทำงานเฉพาะงาน (เช็คจอ, หาตำแหน่งใกล้เคียง, เตรียมไฟล์ `manage_target_r`, คู่มือ CMS, คลังความรู้ทีม, ควบคุมจอ Sharp) |
| [`KNOWLEDGE/`](KNOWLEDGE/index.md) | คลังความรู้ทางเทคนิค (`target-r`, `android-box`, `hikvision`) |
| [`SHEETS_INDEX.md`](SHEETS_INDEX.md) | โครงสร้างของ Google Sheets ที่เชื่อมต่อ |
| [`MCP_SERVER/`](MCP_SERVER/index.md) | Python FastMCP Server (`jarvis_mcp/`), เอกสาร Tools และ Unit Tests |
| `SANDBOX/` | พื้นที่สำหรับสร้างไฟล์ CSV/TSV/JSON (ทีม Operation ทำงานในโฟลเดอร์นี้เท่านั้น) |
| `setup_team.bat` | สคริปต์ดับเบิลคลิกครั้งเดียวสำหรับติดตั้งบนเครื่องทีม Operation |

---

## คู่มือติดตั้งสำหรับทีม Operation (Antigravity Desktop)

### 1. ติดตั้งโปรแกรมพื้นฐาน (ทำครั้งเดียว)
1. **Git for Windows** (ใช้รับไฟล์และอัปเดตเวอร์ชันอัตโนมัติ)
2. **Python 3.11 ขึ้นไป** *(ตอนติดตั้งให้ติ๊ก **"Add python.exe to PATH"** ด้วย)*
3. **Antigravity Desktop** และล็อกอินด้วยบัญชี **Gmail**

### 2. ดาวน์โหลดโปรเจกต์และวางไฟล์ลับจากหัวหน้าทีม
1. เปิดโฟลเดอร์ที่ต้องการเก็บงาน (เช่น `C:\OMG`) แล้ว Clone โปรเจกต์:
   ```bash
   git clone https://github.com/DiamondOMG/target-r-assistance.git
   ```
2. นำไฟล์ 2 อย่างที่หัวหน้าทีมส่งให้ (ห้ามส่งต่อหรือ commit ขึ้น Git) มาวางที่โฟลเดอร์ `target-r-assistance\`:
   - ไฟล์ **`.env`** (ต้องมี `PERMISSION=staff` เพื่อป้องกันเผลอแก้โค้ดและเปิดระบบ Auto-Update)
   - ไฟล์กุญแจ **Google Service Account JSON** (สิทธิ์ Read-Only เช่น `target-r-assistance-team-readonly.json`)

### 3. ดับเบิลคลิกติดตั้งอัตโนมัติ
- ดับเบิลคลิกไฟล์ **`setup_team.bat`** ที่อยู่หน้าแรกของโฟลเดอร์
- รอจนขึ้นคำว่า **`Setup Complete!`** (หน้าต่างจะพิมพ์โค้ด JSON สำหรับตั้งค่า MCP Server ให้ก๊อปปี้ทันที)

### 4. เชื่อมต่อ MCP Server ใน Antigravity Desktop
1. เปิด **Antigravity Desktop** → คลิกเมนู **`...`** หรือ **`MCP Servers`** → เลือก **Manage MCP Servers** → เปิดไฟล์ Config (`mcp_config.json`)
2. นำ JSON ที่ได้จากหน้าต่าง `setup_team.bat` (หรือก๊อปปี้ด้านล่างโดยเปลี่ยน Path ให้ตรงเครื่อง) ไปวางแล้วบันทึก:
   ```json
   {
     "mcpServers": {
       "jarvis-targetr": {
         "command": "C:/OMG/target-r-assistance/MCP_SERVER/.venv/Scripts/python.exe",
         "args": ["-m", "jarvis_mcp.server"],
         "cwd": "C:/OMG/target-r-assistance/MCP_SERVER",
         "env": {
           "PYTHONPATH": "C:/OMG/target-r-assistance/MCP_SERVER"
         }
       }
     }
   }
   ```
3. รีเฟรช MCP Server ให้ขึ้นสถานะไฟเขียว พร้อมใช้งาน **10 Tools**:
   - `targetr_query`, `targetr_function`, `targetr_stuck_screens` (เช็คจอติดใบ้), `targetr_fuzzy_search`, `geo_distance`, `prepare_targetr_update` (เตรียมไฟล์วางใน `manage_target_r`), `team_knowledge_search`, `team_knowledge_save` (คลังความรู้ทีม Real-time), `tv_control` (ควบคุมจอ Sharp ผ่าน Tailscale + ADB), `send_email`

### 5. วิธีใช้งานประจำวันสำหรับทีม Operation
1. เปิดโปรแกรม **Antigravity Desktop** → กด **Open Folder** เลือกโฟลเดอร์ `target-r-assistance`
2. เลือกโหมดแชท (แนะนำโมเดลสาย Flash เพื่อโควตาที่เยอะและเร็ว)
3. พิมพ์ถามหรือสั่งงานภาษาไทยได้เลย เช่น:
   - *"เช็คจอที่ติดใบ้ตอนนี้มีกี่จอ"*
   - *"สาขาเซ็นทรัลเวิลด์มีจอกี่ตัว ออนไลน์ครบไหม"*
   - *"ทำไฟล์ TSV แก้ฟิลด์ restartTime เป็น 08:05 ให้จอ Big C ทั้งหมดหน่อย"* (กดคลิกเปิดไฟล์ใน `SANDBOX/` แล้ว `Ctrl+A` → `Ctrl+C` ไปวางใน https://tops.actx.digital/manage_target_r)
4. **การอัปเดตเวอร์ชัน:** เมื่อตั้งค่า `PERMISSION=staff` ทุกครั้งที่เปิดโปรแกรม ตัว `MCP_SERVER` จะดึงเวอร์ชันล่าสุดจาก GitHub ให้อัตโนมัติโดยไม่ลบไฟล์ใน `SANDBOX/` และ `.env` ครับ
