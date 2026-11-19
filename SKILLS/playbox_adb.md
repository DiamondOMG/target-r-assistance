# Skill: เชื่อมต่อและจัดการกล่อง Playbox ผ่าน ADB (`playbox_adb`)

## เป้าหมาย

ช่วยให้ทีมงานเชื่อมต่อ **ADB over LAN/Wi-Fi** เข้าไปยังกล่อง **Playbox / Android TV Box** เพื่อตรวจสอบข้อมูลเครื่อง เช็คแอป Target-R (DS Loader), WebView, Location, แคปหน้าจอ ปรับตั้งค่า หรือสั่งดำเนินการต่าง ๆ ได้อย่างปลอดภัยและมีขั้นตอนชัดเจน

> **แยกขอบเขตการใช้งานกับ `tv_control`:**
> - **กล่อง Playbox / Android Box หน้างานหรือเครื่องเทสที่รู้เลข IP ในวงแลน** -> ใช้ Skill นี้และ MCP Tool **`playbox_adb`**
> - **จอ Sharp Smart TV 2 ตัวในห้องทำงาน (`sharp_left` / `sharp_right`) ผ่าน Tailscale** -> ใช้ [`tv_control.md`](tv_control.md) และ MCP Tool `tv_control`

---

## ใช้เมื่อ

- ผู้ใช้บอกเลข IP ของกล่อง Playbox และให้เข้าไป **เช็คค่า** (เช่น สเปกเครื่อง, Android version, Timezone, WebView, พื้นที่ว่าง, สถานะ DS Loader, Location/GPS, logcat, แคปหน้าจอ)
- ผู้ใช้ต้องการ **เปลี่ยนค่า** บนกล่อง Playbox (เช่น ตั้ง Timezone, ปรับ Android settings/properties, ให้สิทธิ์ permission แอป)
- ผู้ใช้ต้องการ **สั่งดำเนินการ** บนกล่อง (เช่น เปิด/ปิด/รีสตาร์ทแอป, เปิด URL, ส่งปุ่มรีโมต, ติดตั้ง APK, ล้างข้อมูลแอป, รีบูตเครื่อง)
- ผู้ใช้ถาม **ขั้นตอนการเปิด Debug Mode** บนกล่อง Playbox

---

## เอกสารอ้างอิงที่เกี่ยวข้อง

- **คู่มือฝั่งผู้ใช้ (Debug Mode 5 ขั้นตอน):** [`KNOWLEDGE/android-box/Playbox_ADB_Debug_Setup_Guide.md`](../KNOWLEDGE/android-box/Playbox_ADB_Debug_Setup_Guide.md)
- **สเปกเครื่องอ้างอิง:** [`KNOWLEDGE/android-box/HK1_RBOX_K8_Hardware_Spec.md`](../KNOWLEDGE/android-box/HK1_RBOX_K8_Hardware_Spec.md), [`KNOWLEDGE/android-box/ACTMEDIA_RK3328_Hardware_Spec.md`](../KNOWLEDGE/android-box/ACTMEDIA_RK3328_Hardware_Spec.md), [`KNOWLEDGE/android-box/AIS_Playbox_Round_Hardware_Spec.md`](../KNOWLEDGE/android-box/AIS_Playbox_Round_Hardware_Spec.md)
- **Tool Contract:** [`MCP_SERVER/TOOLS/playbox_adb.md`](../MCP_SERVER/TOOLS/playbox_adb.md)

---

## Quick Tool Chain Execution (คีย์เวิร์ด: "adb เช็ค กล่อง / สมาร์ททีวี")

เมื่อผู้ใช้ส่งข้อความสั่งในลักษณะ **"adb เช็ค กล่อง / สมาร์ททีวี"**:
1. **กรณีผู้ใช้ยังไม่ได้ระบุเลข IP:**
   - ให้ตอบสรุป 5 ขั้นตอนเปิด Debug Mode ทันที (ไม่ต้องรอถาม) พร้อมขอเลข IP ของกล่อง
   - 5 ขั้นตอนสั้น: (1) เปิดกล่องต่อจอ/เมาส์/คีย์บอร์ด -> (2) ล็อกอิน Wi-Fi/LAN วงเดียวกับคอมพ์และจด IP -> (3) เข้า `Settings -> Device Preferences -> About -> Build Number` ดับเบิ้ลคลิก 7 ครั้ง -> ออกมา `Developer options` ติ๊ก `ADB debugging` + `Internet ADB` (ถ้ามี) + USB `MTP` -> (4) ส่งเลข IP ให้ AI -> (5) ครั้งแรกจะมี Pop-up *"Allow USB debugging?"* ให้ติ๊ก `Always allow` และกด `Allow` ฝั่งกล่อง
2. **กรณีผู้ใช้ระบุเลข IP มาแล้ว (เช่น `ไหนลอง 192.168.0.xxx`):**
   - **Zero-Overhead Dispatch:** เรียก MCP Tool `playbox_adb(ip=..., action="device_info")` ทันทีในเทิร์นแรก
   - หากเจอ `status="unauthorized"`: แจ้งให้ผู้ใช้ดู Pop-up บนหน้าจอกล่อง ติ๊ก *Always allow* แล้วกด *Allow*
   - หากเชื่อมต่อสำเร็จ: รายงานข้อมูลเครื่อง สเปก และ **ความจุ ROM ชิปฮาร์ดแวร์จริง (`real_hardware_rom`)** ทันที
3. **การอ่าน ROM จริง (ป้องกัน UI หลอก / Fake Specs):**
   - กล่อง Android Box ทั่วไปมักแก้ Settings UI หรือ build.prop ให้แสดงพื้นที่ 64GB/128GB เกินจริง
   - MCP Tool `playbox_adb` อ่านตรงจาก Partition Table ของเคอร์เนล (`/proc/partitions` และ `/sys/class/block/mmcblk*/`) จึงได้ขนาด Block Device จริงของชิป eMMC, รหัสรุ่นชิป และผู้ผลิตตัวจริง (เช่น Samsung, SK Hynix, SanDisk) ไม่ใช่ค่าจาก UI ปลอม

---

## ลำดับขั้นตอนการทำงานของ Agent

### ขั้นตอนที่ 1: ตรวจสอบความพร้อมก่อนเชื่อมต่อ
- หากผู้ใช้ **ยังไม่ได้แจ้งเลข IP** หรือ **ยังไม่ได้เปิด Debug Mode** ให้สรุปขั้นตอนเตรียมกล่องสั้น ๆ 5 ข้อจาก `Playbox_ADB_Debug_Setup_Guide.md` พร้อมขอเลข IP:
  1. เปิดกล่อง Playbox ต่อจอ ต่อเมาส์ ต่อคีย์บอร์ด
  2. ต่อ Wi-Fi/LAN วงเดียวกับเครื่องนี้ และจดเลข IP
  3. ไปที่ `Settings -> Device Preferences (ค่ากำหนดอุปกรณ์) -> About (เกี่ยวกับ)` กดคลิกย้ำ 7 ครั้งที่ `Build Number (บิลด์ของระบบปฏิบัติการ)` แล้วออกมาที่ `Settings -> Developer options` ติ๊กเปิด `ADB debugging` + `Internet ADB` (ถ้ามี) + เลือก `USB Configuration -> MTP`
  4. แจ้งเลข IP และสิ่งที่ต้องการให้ AI ตรวจสอบ/แก้ไข
  5. หากเชื่อมต่อครั้งแรก ให้รอกดยืนยัน **Allow** บนหน้าจอกล่อง Playbox

### ขั้นตอนที่ 2: เชื่อมต่อและเริ่มจาก Read-Only เสมอ
- เมื่อได้ IP แล้ว ให้เริ่มจากเรียก `playbox_adb` ด้วย action ฝั่งอ่านก่อน เช่น `connect`, `device_info`, `check_webview`, `check_app`, `check_location`, `get_prop`, `get_setting`, `logcat_tail`, `screenshot`
- **กรณีผลลัพธ์เป็น `status="unauthorized"`:**
  - ห้ามวนเรียกซ้ำรัว ๆ ให้แจ้งผู้ใช้ทันทีว่าให้ดูที่หน้าจอกล่อง Playbox แล้วติ๊ก **`Always allow from this computer`** และกด **`Allow / อนุญาต`** จากนั้นแจ้งกลับมาเพื่อให้ Agent เชื่อมต่อต่อทันที
- **กรณีผลลัพธ์เป็น `status="unreachable"` หรือ `"timeout"`:**
  - แจ้งให้ผู้ใช้ตรวจเช็กวงแลนเดียวกัน, เลข IP, และตัวเลือก `ADB debugging` / `Internet ADB` / `USB Configuration = MTP`

### ขั้นตอนที่ 3: กฎความปลอดภัยสำหรับการเปลี่ยนค่าและคำสั่งเสี่ยงสูง
- คำสั่งทำลายข้อมูล/มีผลกระทบสูง ได้แก่ **`clear_app_data`**, **`install_apk`**, **`reboot`**, และ **mutating `shell` commands**:
  - ต้องระบุผลกระทบให้ชัดเจนและให้ผู้ใช้ยืนยันก่อนส่ง **`confirm=True`** เสมอ (ห้ามแอบตั้ง `confirm=True` เองโดยที่ผู้ใช้ยังไม่ได้สั่งหรือยืนยัน)
- สำหรับการเปลี่ยนค่า (`set_setting`, `set_prop`, `set_timezone`, `grant_permission`):
  - หากผู้ใช้สั่งเจาะจงชัดเจน (เช่น "เปลี่ยน timezone เป็น Asia/Bangkok") ให้ดำเนินการและรายงานค่าเดิมเทียบกับค่าใหม่จากผลลัพธ์จริงของ tool
  - หากเป็นการแก้ค่าที่อาจมีผลข้างเคียงหรือผู้ใช้ยังไม่ได้ระบุค่าที่จะแก้ชัดเจน ให้ถามยืนยันก่อน

### ขั้นตอนที่ 4: สรุปผลด้วยหลักฐานจริง
- อ้างอิงเฉพาะค่าที่ tool คืนมาจริง (ห้ามเดาค่า)
- หากมีการใช้ `action="screenshot"` ไฟล์รูปจะถูกบันทึกใน `SANDBOX/` — ให้แนบลิงก์ไฟล์ `file:///...` ให้ผู้ใช้เปิดดูได้ทันที
- ห้ามสั่งรันคำสั่งนอก `playbox_adb` แบบสุ่มสี่สุ่มห้าหรือรันคำสั่งทำลายระบบ (`rm`, `dd`, `su`, ฯลฯ)
