# MCP Tool Contract: `send_email`

> สถานะ: implement ใน `MCP_SERVER/jarvis_mcp/email_sender.py`

## วัตถุประสงค์

ส่งอีเมลแจ้งเตือน รายงานสรุป หรือการแจ้งเตือนเหตุฉุกเฉิน (Alerts) จากระบบ Jarvis ผ่านบัญชี Gmail SMTP โดยรองรับทั้งข้อความธรรมดา (Plain Text) และ HTML

## คำอธิบายสำหรับ Model

ใช้เมื่อต้องการส่งอีเมลหาผู้ใช้หรือทีมงาน เช่น รายงานสรุปจอ Offline ประจำวัน, แจ้งเตือนความผิดปกติของอุปกรณ์ หรือส่งสรุปผลการค้นหาข้อมูล Target-R/Google Sheet

## Input schema

| Field | Type | Required | ความหมาย / ข้อจำกัด |
|---|---|---:|---|
| `to` | array of string (หรือ string) | yes | อีเมลผู้รับ เช่น `["user@example.com"]` |
| `subject` | string | yes | หัวข้ออีเมล |
| `body` | string | yes | เนื้อหาอีเมล (ข้อความธรรมดา หรือโค้ด HTML) |
| `is_html` | boolean | no | กำหนดว่าเป็น HTML หรือไม่ (default: `false`) |
| `cc` | array of string | no | รายชื่ออีเมล CC (ถ้ามี) |

## Output schema

```json
{
  "source": "gmail_smtp",
  "status": "success",
  "message_id": "...",
  "to": ["user@example.com"],
  "subject": "รายงานจอ Offline ประจำวัน",
  "timestamp": "2026-11-16T16:50:00Z"
}
```

## Errors ที่ควรแยก

- `CONFIG_ERROR`: ไม่ได้ตั้งค่า `GMAIL_USER` หรือ `GMAIL_APP_PASSWORD`
- `INVALID_INPUT`: ไม่มีอีเมลผู้รับ หัวข้อ หรือเนื้อหาว่าง
- `SMTP_AUTH_ERROR`: รหัส App Password ไม่ถูกต้องหรือโดนยกเลิก
- `SEND_FAILED`: ส่งไม่สำเร็จเนื่องจากเน็ตเวิร์กหรือเซิร์ฟเวอร์ปฏิเสธ

