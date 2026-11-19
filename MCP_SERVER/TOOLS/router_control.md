# MCP Tool Contract: `router_control`

> สถานะ: พร้อมใช้งานใน `MCP_SERVER/jarvis_mcp/router_control.py`

## วัตถุประสงค์

สแกนค้นหาอุปกรณ์ในวงแลน ตรวจสอบอุปกรณ์ที่เกาะเราเตอร์ และตรวจสอบสถานะเชิงลึกของเราเตอร์สาขา/ออฟฟิศ (โดยเฉพาะ **D-Link DWR-M930 4G LTE Router**) เพื่อวิเคราะห์การเชื่อมต่อของจอ Target-R, กล่อง Android Box, ระดับสัญญาณ Wi-Fi, สัญญาณ 4G Cellular และตรวจสอบสถานะ CGNAT / Port Forwarding

---

## Input Schema

| Field | Type | Required | Default | ความหมาย / ข้อจำกัด |
|---|---|---:|---|---|
| `action` | string enum | no | `"scan_devices"` | คำสั่งที่ต้องการรัน: `"scan_devices"`, `"get_connected_clients"`, `"get_router_status"` |
| `router_ip` | string | no | `"192.168.0.1"` | เลข IP ของเราเตอร์ (Gateway) |
| `username` | string | no | `"admin"` | บัญชีผู้ดูแลระบบของเราเตอร์ (จำเป็นเมื่อใช้ `get_connected_clients` หรือ `get_router_status`) |
| `password` | string | no | `"BC202$1$9@"` | รหัสผ่านเราเตอร์ (ดึงจาก `.env` หรือส่งผ่าน argument) |

---

## รายการ Actions

### 1. `scan_devices` (สแกนเร็วจากเครื่องคอมฯ)
- **เงื่อนไข:** **ไม่ต้องใช้รหัสผ่านเราเตอร์** ขอแค่อยู่ในวงแลนเดียวกัน
- **การทำงาน:** ทำ Ping sweep + ARP table query ใน Subnet ท้องถิ่น (เช่น `192.168.0.0/24`)
- **ผลลัพธ์:** รายการอุปกรณ์ที่ออนไลน์อยู่ (IP, MAC Address, Hostname)

### 2. `get_connected_clients` (ดึงตารางจากเราเตอร์ D-Link)
- **เงื่อนไข:** ใช้รหัสผ่านล็อกอินหลังบ้านเราเตอร์ DWR-M930 (`/boafrm/formLoginSetup`)
- **การทำงาน:** รวมข้อมูลจาก **DHCP Leases Table** (`dhcptbl.htm`) และ **Wireless Station Table** (`wlstatbl.htm`)
- **ผลลัพธ์:**
  - แยกชัดเจนว่าเครื่องไหนต่อ **สาย LAN** หรือ **Wi-Fi**
  - แสดง **ความแรงสัญญาณ Wi-Fi** (เช่น `Strong(80%)`, `Middle(60%)`, `Weak(30%)`)
  - แสดงชื่อ Hostname แท้จริงที่เครื่องส่งมาตอนขอ IP
  - นับสถิติจำนวนเครื่อง Wi-Fi vs สาย LAN

### 3. `get_router_status` (สถานะ 4G LTE และ CGNAT)
- **การทำงาน:** อ่านค่าจาก `status.htm` และทดสอบเทียบกับ Public IP ภายนอก (`api.ipify.org`)
- **ผลลัพธ์:**
  - **โมเดลเราเตอร์ & โมดูล 4G:** DWR-M930 / Quectel EC200A
  - **สถานะซิมและผู้ให้บริการ:** SIM READY, Provider (`dtac.Better Together` / True), IMSI
  - **สัญญาณ 4G Cellular:** RSRP, RSRQ, SINR, Band (เช่น Band 40 2300MHz), Cell ID, PCI
  - **เครือข่าย & CGNAT Analysis:**
    - LTE WAN IP (เช่น `10.215.75.119`)
    - External Public IP (เช่น `1.46.15.72`)
    - `is_cgnat`: `true`/`false`
    - `port_forwarding_feasible_externally`: `false` (ถ้าติด CGNAT จะเปิดพอร์ตตรงจากเน็ตภายนอกไม่ได้)
    - คำแนะนำการเข้าถึงจากภายนอก (Tailscale Subnet Router)

---

## โครงสร้าง Errors

- `ROUTER_UNREACHABLE`: ไม่สามารถติดต่อ IP เราเตอร์ได้ (เช่น อยู่คนละวงแลน หรือเราเตอร์ปิดอยู่)
- `AUTH_FAILED`: รหัสผ่านเราเตอร์ไม่ถูกต้อง
- `INVALID_INPUT`: action นอกเหนือจากที่ระบุ
