# MCP Tool Contract: `tv_control`

> สถานะ: พร้อมใช้งานใน `MCP_SERVER/jarvis_mcp/tv_control.py`

## วัตถุประสงค์

ควบคุมจอ **Sharp Smart TV** ในห้องทำงานผ่าน **ADB over Tailscale VPN** (พอร์ต `5555`) เพื่อเปิดเว็บแดชบอร์ดมอนิเตอร์, เปิด/รีสตาร์ทแอป DS Loader (Target-R), สลับช่อง HDMI (`hdmi1`, `hdmi2`) หรือส่งปุ่มควบคุมพื้นฐานจากระยะไกลโดยทีมงานทุกคน

## ทะเบียนจอที่ตั้งค่าไว้

| ชื่อเรียก (`tv`) | รายละเอียด | MAC Address | Tailscale IP |
|---|---|---|---|
| `sharp_left` (`จอ2`, `จอ 2`, `ซ้าย`, `A4AE125D42DE`) | Sharp Smart TV (ตัวซ้าย / จอ 2) | `A4AE125D42DE` | `100.120.41.101` (`sharp-left.tail6bc567.ts.net`) |
| `sharp_right` (`จอ3`, `จอ 3`, `ขวา`, `A4AE125D4ACC`) | Sharp Smart TV (ตัวขวา / จอ 3) | `A4AE125D4ACC` | `100.75.151.107` (`sharp-right.tail6bc567.ts.net`) |

## Input schema

| Field | Type | Required | ความหมาย / ข้อจำกัด |
|---|---|---:|---|
| `tv` | string | no | ชื่อจอ (`sharp_left`, `sharp_right`, หรือระบุ Tailscale IP ตรงๆ) ค่าเริ่มต้น `"sharp_left"` |
| `action` | string enum | no | คำสั่ง: `status`, `open_url` (force-stop dsloader อัตโนมัติ), `open_dsloader`, `restart_dsloader`, `stop_dsloader` (ปิดแอป Target-R ทันที), `fullscreen` (เปิดโหมดเต็มหน้าจอ immersive ซ่อนแถบระบบ), `desktop_view` (สลับโหมด Desktop view ในเบราว์เซอร์), `hdmi1`, `hdmi2`, `home`, `back`, `wake`, `lock_adb_port` |
| `url` | string | no | บังคับเมื่อ `action="open_url"` (ต้องขึ้นต้นด้วย `http://` หรือ `https://`) |

## Errors ที่ควรแยก
- `TV_NOT_CONFIGURED`: จอที่เรียกยังไม่มี Tailscale IP ตั้งค่าไว้
- `ADB_NOT_FOUND`: ไม่พบ `adb.exe` ในเครื่อง (ติดตั้ง Android Platform Tools หรือตั้ง `ADB_PATH`)
- `unauthorized`: ทีวีกำลังรอการกด Allow Debugging บนหน้าจอ (หรือต้องคัดลอก `adbkey` ของทีมมาวาง)
