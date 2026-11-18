# Skill: ควบคุมจอ Sharp Smart TV ในห้องทำงานผ่าน Tailscale (`tv_control`)

## เป้าหมาย

ช่วยให้ทีมงานทั้ง 5 คนสามารถสั่งควบคุมจอ **Sharp Smart TV** ในห้องทำงานได้จากทุกที่ผ่าน **Tailscale VPN + ADB** เช่น เปิดเว็บแดชบอร์ดมอนิเตอร์, เปิดหรือรีสตาร์ทแอป DS Loader (`net.targetr.stacks.central`), หรือสลับช่อง HDMI เพื่อเทสกล่อง Playbox

## ข้อมูลจอในห้องทำงาน

- **Sharp ตัวซ้าย / จอ 2 (`sharp_left`):**
  - MAC Address: `A4AE125D42DE` (`R&D Room - 42" Sharp - 2 - Monitor`)
  - Tailscale IP: `100.120.41.101` (`sharp-left.tail6bc567.ts.net`)
  - ADB Port: `5555`
- **Sharp ตัวขวา / จอ 3 (`sharp_right`):**
  - MAC Address: `A4AE125D4ACC` (`R&D Room - 42" Sharp - 3 - Monitor`)
  - Tailscale IP: `100.75.151.107` (`sharp-right.tail6bc567.ts.net`)
  - ADB Port: `5555`

## ใช้เมื่อ

- ผู้ใช้สั่งให้ **เปิดเว็บ / แดชบอร์ด** ขึ้นบนจอ Sharp (เช่น `https://tops.actx.digital/screen-monitor`, `https://tops.actx.digital/map`, `https://tops.actx.digital/dashboard`)
- ผู้ใช้สั่งให้ **เปิดแอป `dsloader` / Target-R** หรือ **รีสตาร์ท `dsloader`** บนจอ Sharp
- ผู้ใช้สั่งให้ **สลับช่อง HDMI 1 / HDMI 2** หรือกดปุ่ม Home / Wake / เช็คสถานะทีวี

## Quick Tool Chain Execution (คำสั่งด่วน ไม่ต้องประมวลผลซ้ำซ้อน)

สำหรับคำสั่งเปิด URL / สลับจอ / เปิด-ปิด dsloader บน Sharp TV ซึ่งมีรูปแบบตายตัวและเกิดขึ้นบ่อย:
1. **Auto Force-Stop DS Loader:** แอป DS Loader (`net.targetr.stacks.central`) มีกลไกพยายาม auto-start ตัวเองขึ้นมาทับแอปอื่นเสมอ ทุกครั้งที่สั่ง `open_url` ตัว MCP tool `tv_control` จะสั่ง `am force-stop` ปิด DS Loader ให้ก่อนเปิด Browser ทันที และสามารถสั่ง `tv_control(tv=..., action="stop_dsloader")` แยกเพื่อปิดแอปได้โดยตรง
2. **Zero-Overhead Dispatch:** เมื่อผู้ใช้ระบุจอและ URL หรือ action ตรงตัว ให้เรียก MCP Tool `tv_control` ทันทีในเทิร์นแรก โดยไม่ต้องอ่านไฟล์ความรู้เพิ่มเติมหรือรันสคริปต์สืบค้น
3. **Auto-Diagnose on Failure:** หากผลลัพธ์เป็น `status="error"` หรือ timeout:
   - ตรวจสอบสถานะ `tailscale status` เพื่อดูว่าทีวีหลุดการเชื่อมต่อหรือไม่
   - ตรวจสอบพอร์ต `5555` ว่าเปิดอยู่หรือไม่
   - แจ้งปัญหาให้ผู้ใช้ทราบแบบตรงจุด (Tailscale หลุด หรือ ADB Unauthorized)
4. **Verified Success:** เมื่อผลลัพธ์คืน `status="success"` ให้แจ้งผลสั้นกระชับทันที
