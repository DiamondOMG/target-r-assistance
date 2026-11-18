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

## ขั้นตอนการทำงาน

1. ตรวจสอบว่าผู้ใช้ต้องการสั่งจอไหน (`sharp_left` หรือ `sharp_right`) และต้องการทำอะไร
2. เรียกใช้ MCP tool **`tv_control`** ตาม action ที่ตรงกัน:
   - เปิดแดชบอร์ด: `tv_control(tv="sharp_left", action="open_url", url="https://tops.actx.digital/screen-monitor")`
   - เปิดแอป Target-R: `tv_control(tv="sharp_left", action="open_dsloader")`
   - รีสตาร์ทแอป Target-R: `tv_control(tv="sharp_left", action="restart_dsloader")`
   - สลับ HDMI 2: `tv_control(tv="sharp_left", action="hdmi2")`
3. หากผลลัพธ์ขึ้น `status="error"` ให้เตือนผู้ใช้ตรวจสอบว่า:
   - คอมพิวเตอร์ของคนสั่งเปิดและล็อกอิน **Tailscale** แล้วหรือไม่
   - บนจอทีวี Sharp เปิด **Always-on VPN** และล็อกพอร์ต `5555` แล้วหรือยัง
4. หากขึ้น `status="unauthorized"` ให้แจ้งว่าต้องกด **Always allow** บนจอทีวี หรือคัดลอก `adbkey` กลางของทีมมาไว้ที่ `%USERPROFILE%\.android\`
