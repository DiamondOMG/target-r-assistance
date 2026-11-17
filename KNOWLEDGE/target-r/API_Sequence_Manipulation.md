---
status: active
type: reference
created: 2026-07-10
platform: target-r
tags:
  - target-r
  - api
  - sequence-manipulation
related:
  - "[[TARGET_R/00_TARGET_R_INDEX]]"
---

# TargetR Sequence Manipulation API

API ที่ใช้สำหรับจัดการแก้ไขข้อมูล Stack และ Item ภายใน Sequence ทีละส่วนแบบเจาะจง (Atomic sequence edits) เพื่อหลีกเลี่ยงการอัปโหลดไฟล์ JSON ของ Sequence ใหม่ทั้งหมด

## 📌 Endpoint ลักษณะการใช้งาน

ใช้ในการส่ง Request ไปจัดการ Slot และ Item บน Sequence
`[METHOD] /rest-api/v1/op/sequence/{seq-id}/{slot}/{item}`

*   รองรับคำสั่งเพิ่มไอเทม (Insert), เปลี่ยนแปลงไอเทม (Replace) และเอาไอเทมออก (Remove)

## ⚠️ Safe Concurrency (`X-If-Version-Match`)

เมื่อมีการแก้ไข Sequence ร่วมกันจากหลายระบบพร้อมกัน (เช่น API, CRM, Admin Panel) ตัว API บังคับให้ใช้ Header พิเศษ:
*   **Header:** `X-If-Version-Match: {version}`
*   **การทำงาน:** หาก Sequence ปัจจุบันบน Server ถูกเปลี่ยนเป็นเวอร์ชันอื่นไปแล้วหลังจากที่ Client อ่านค่าครั้งล่าสุด Server จะส่งกลับรหัส **`HTTP 409 Conflict`** ทันที เพื่อป้องกันข้อมูลทับซ้อนสูญหาย

---

## 💻 ตัวอย่างการใช้งานในโปรเจกต์ (Next.js Server Action)

### 1. การแทรก/แทนที่สื่อลงใน Sequence Slot (POST)

```javascript
// เส้นทาง: /rest-api/v1/op/sequence/{seq_id}/{slot}/{item}
export async function create_item(sequenceId, slot, item, libraryId, label) {
  const SEQUENCE_API_URL = `https://stacks.targetr.net/rest-api/v1/op/sequence/${sequenceId}/${slot}/${item}`;

  const requestBody = {
    type: "libraryitem",
    id: libraryId,
    data: {
      modifiedMillis: Date.now().toString(),
      label: label,
      // ... ข้อมูล meta-data อื่นๆ
    },
  };

  const response = await fetch(SEQUENCE_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Basic ${auth}`,
    },
    body: JSON.stringify(requestBody),
  });

  return await response.json();
}
```

### 2. การลบสื่อออกจาก Sequence (DELETE)

```javascript
// เส้นทาง: /rest-api/v1/op/sequence/{seq_id}/{slot}/{item}
export async function delete_item(sequenceId, slot, item) {
  const DELETE_API_URL = `https://stacks.targetr.net/rest-api/v1/op/sequence/${sequenceId}/${slot}/${item}`;

  const response = await fetch(DELETE_API_URL, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Basic ${auth}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to delete item: ${response.status}`);
  }

  return response;
}
```

