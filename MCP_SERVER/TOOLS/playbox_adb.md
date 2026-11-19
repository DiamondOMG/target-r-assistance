# MCP Tool Contract: `playbox_adb`

> สถานะ: พร้อมใช้งานใน `MCP_SERVER/jarvis_mcp/playbox_adb.py`

## วัตถุประสงค์

เชื่อมต่อ ตรวจสอบค่า ปรับตั้งค่า และดำเนินการควบคุมกล่อง **Playbox / Android TV Box** ผ่าน **ADB over LAN/Wi-Fi (TCP/IP พอร์ต 5555)** โดยใช้เลข IP ของกล่องที่ผู้ใช้งานแจ้ง

> **เงื่อนไขฝั่งผู้ใช้ก่อนเรียกใช้งาน:** กล่อง Playbox ต้องเชื่อมต่อ Wi-Fi/LAN วงเดียวกับเครื่องโฮสต์ และเปิด Debug Mode (ADB debugging + Internet ADB ถ้ามี + USB Configuration = MTP) รวมถึงกดยอมรับ Pop-up *"Allow USB debugging?"* ในครั้งแรก ดูรายละเอียดที่ [`KNOWLEDGE/android-box/Playbox_ADB_Debug_Setup_Guide.md`](../../KNOWLEDGE/android-box/Playbox_ADB_Debug_Setup_Guide.md)

*(หมายเหตุ: สำหรับควบคุมจอ Sharp Smart TV ในห้องทำงานผ่าน Tailscale ให้ใช้ [`tv_control`](tv_control.md))*

---

## Input Schema

| Field | Type | Required | Default | ความหมาย / ข้อจำกัด |
|---|---|---:|---|---|
| `ip` | string | yes | - | เลข IP ของกล่อง Playbox หรือ `host:port` (เช่น `192.168.1.105`) |
| `action` | string enum | no | `"connect"` | คำสั่งที่ต้องการดำเนินการ (ดูรายการด้านล่าง) |
| `port` | int | no | `5555` | พอร์ต ADB TCP/IP (1–65535) |
| `namespace` | enum (`system`, `secure`, `global`) | no | `None` | บังคับเมื่อ `action="get_setting"` หรือ `"set_setting"` |
| `key` | string | no | `None` | ชื่อ property หรือ setting key (`^[A-Za-z0-9._-]+$`) |
| `value` | string | no | `None` | ค่าที่ต้องการตั้ง (ใช้กับ `set_prop`, `set_setting`, `set_timezone`, `keyevent`, หรือ `"third_party"` กับ `list_packages`) |
| `package` | string | no | `None` | ชื่อ Android package (`^[A-Za-z0-9._]+$`) ค่าเริ่มต้น `net.targetr.stacks.central` สำหรับ `check_app`/`start_app`/`stop_app`/`restart_app`; บังคับระบุสำหรับ `clear_app_data` และ `grant_permission` |
| `permission` | string | no | `None` | บังคับเมื่อ `action="grant_permission"` เช่น `android.permission.ACCESS_FINE_LOCATION` |
| `url` | string | no | `None` | บังคับเมื่อ `action="open_url"` (ต้องขึ้นต้นด้วย `http://` หรือ `https://`) |
| `apk_path` | string | no | `None` | บังคับเมื่อ `action="install_apk"` (path ไฟล์ `.apk` ที่มีอยู่จริงบนเครื่องโฮสต์) |
| `command` | string | no | `None` | บังคับเมื่อ `action="shell"` (เฉพาะคำสั่งใน allowlist เท่านั้น) |
| `filter_text` | string | no | `None` | ตัวกรองข้อความใน Python สำหรับ `list_packages` และ `logcat_tail` |
| `lines` | int | no | `50` | จำนวนบรรทัดสำหรับ `logcat_tail` (1–200) |
| `confirm` | bool | no | `False` | ต้องตั้งเป็น `True` เมื่อเรียกคำสั่งเสี่ยงสูง/เปลี่ยนแปลงระบบ (`clear_app_data`, `install_apk`, `reboot`, และ mutating `shell`) |

---

## รายการ Actions แยกตามระดับสิทธิ์

### 1. Connection & Diagnostics (Read-Only)
- `connect`: เชื่อมต่อ ADB TCP/IP และตรวจ `adb get-state` (แยกสถานะ `connected`, `unauthorized`, `unreachable`)
- `disconnect`: ตัดการเชื่อมต่อ ADB ของเป้าหมาย
- `device_info`: ดึงสรุปสเปกเครื่อง, Android/SDK, RAM, ความจุชิป ROM ฮาร์ดแวร์จริง (`real_hardware_rom` อ่านตรงจาก eMMC block device ป้องกัน UI หลอก), พื้นที่ `/data`, Timezone, เวลาเครื่อง, WebView และสถานะ DS Loader
- `get_prop`: อ่าน system property (ระบุ `key` หรือเว้นว่างเพื่ออ่านชุด property หลัก)
- `get_setting`: อ่านค่า Android Settings (`namespace` + `key`)
- `list_packages`: แสดงรายชื่อแอปในเครื่อง สูงสุด 100 รายการ (รองรับ `filter_text` และ `value="third_party"`)
- `check_app`: ตรวจการติดตั้ง, APK path, PIDs, `versionName`/`versionCode` และสิทธิ์สำคัญของแอป
- `check_webview`: ตรวจสถานะ WebView (`dumpsys webviewupdate`)
- `check_location`: ตรวจ `location_mode`, `wifi_scan_always_enabled`, สถานะ `com.google.android.gms.persistent` และ location providers
- `logcat_tail`: ดึง log ล่าสุด (`lines` 1–200, รองรับ `filter_text`, จำกัดความยาว 8,000 ตัวอักษร)
- `screenshot`: แคปหน้าจอกล่อง Playbox ผ่าน `/data/local/tmp/` แล้ว `pull` ลงโฟลเดอร์ `SANDBOX/`

### 2. Configuration (Write)
- `set_setting`: แก้ไข Android Settings (`namespace` + `key` + `value`) พร้อมคืน `previous_value` และ `new_value` เพื่อตรวจสอบ
- `set_prop`: แก้ไข system property (`key` + `value`) พร้อมอ่านค่าเดิม/ค่าใหม่เทียบ
- `set_timezone`: ตั้งค่า Timezone รูปแบบ IANA (เช่น `Asia/Bangkok`) และคืนเวลาเครื่องล่าสุด
- `grant_permission`: มอบ permission ให้แอป (`package` + `permission`)

### 3. App & Control Operations
- `start_app` / `stop_app` / `restart_app`: เปิด / ปิด / รีสตาร์ทแอป
- `open_url`: เปิด URL บนเบราว์เซอร์ของกล่อง
- `keyevent`: ส่งปุ่มควบคุม (`HOME`, `BACK`, `WAKEUP`, `SLEEP`, `DPAD_UP`, `DPAD_DOWN`, `DPAD_LEFT`, `DPAD_RIGHT`, `DPAD_CENTER`, `ENTER`, `VOLUME_UP`, `VOLUME_DOWN`, `VOLUME_MUTE`, `MENU`, `SETTINGS`)
- `clear_app_data` **(ต้อง `confirm=True`)**: ล้างข้อมูลแอปที่ระบุ (`package` บังคับ)
- `install_apk` **(ต้อง `confirm=True`)**: ติดตั้งไฟล์ `.apk` (`install -r`) ลงกล่อง
- `reboot` **(ต้อง `confirm=True`)**: รีบูตกล่อง Playbox

### 4. Controlled Safe Shell (`action="shell"`)
- **ห้ามใช้** shell chaining/redirection (`;`, `&`, `|`, `` ` ``, `$`, `>`, `<`) และคำสั่งอันตราย (`rm`, `dd`, `mkfs`, `format`, `wipe`, `fastboot`, `su`, `sh`, `bash`, `chmod`, `chown`, `mount`, `reboot`, `recovery`)
- **Read-only allowlist** (รันได้ทันที): `getprop`, `dumpsys`, `df`, `free`, `uptime`, `date`, `uname`, `id`, `whoami`, `ip`, `ifconfig`, `ping`, `pidof`, `ps`, `ls`, `cat`, `logcat`, `pm list/path/dump`, `settings get/list`, `appops get`, `wm size`, `wm density`
- **Controlled write allowlist** **(ต้อง `confirm=True`)**: `setprop`, `input`, `monkey`, `svc`, `cmd`, `settings put/delete`, `pm grant/revoke/enable/disable-user`, `am start/force-stop/broadcast`, `appops set`, `wm size <val>`, `wm density <val>`

---

## โครงสร้าง Output และ Errors

- **สำเร็จ:** คืน JSON ที่มี `status` (`"connected"` หรือ `"success"`), `target` (`<ip>:<port>`), `action` และผลลัพธ์เฉพาะทางของ action นั้น ๆ
- **Errors และสถานะพิเศษ (วิธีที่ Agent ควรตอบ):**
  - `status="unauthorized"`: แจ้งให้ผู้ใช้ดูหน้าจอกล่อง Playbox เพื่อติ๊ก *Always allow* และกด **Allow / อนุญาต** แล้วแจ้งให้ AI ลองใหม่
  - `status="unreachable"` หรือ `"timeout"`: แจ้ง `hint` ให้ตรวจสอบวงแลน/Wi-Fi, เลข IP และการตั้งค่า Developer Options (`ADB debugging` + `Internet ADB` + USB = `MTP`)
  - `status="confirmation_required"`: อธิบายผลกระทบของคำสั่งเสี่ยงสูงให้ผู้ใช้ทราบและขอคำยืนยันก่อนส่ง `confirm=True`
  - `INVALID_INPUT` / `FORBIDDEN_COMMAND` / `UNSUPPORTED_COMMAND`: `ValueError` เมื่อพารามิเตอร์ผิดรูปแบบหรือคำสั่งไม่อยู่ใน allowlist
  - `ADB_NOT_FOUND`: ไม่พบ `adb.exe` ในเครื่องโฮสต์ (ต้องติดตั้ง Android Platform Tools หรือกำหนด `ADB_PATH`)
