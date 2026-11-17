---
status: active
type: reference
created: 2026-07-10
platform: target-r
tags:
  - target-r
  - api
  - playback-simulation
related:
  - "[[TARGET_R/00_TARGET_R_INDEX]]"
---

# TargetR Playback Simulation API

API สำหรับจำลองและคาดการณ์ผลตารางเวลาการเล่นคอนเทนต์ล่วงหน้า (Predictive Schedule Simulation) เพื่อตรวจสอบความถูกต้องของเงื่อนไขการเล่น (Condition) ก่อนเผยแพร่จริง

## 📌 Endpoints

*   **จำลองตารางการเล่นระดับหน้าจอ (Screen):**
    `GET /api/simulate-screen/{screen-id}`
*   **จำลองตารางการเล่นระดับลำดับ (Sequence):**
    `GET /api/simulate-sequence/{seq-id}`

## 📦 Response Format

ระบบจะส่งกลับเป็นไฟล์ข้อมูล **JSON** ซึ่งประกอบด้วยโครงสร้างดังนี้:
1.  **Scheduled Items**: รายการและลำดับสื่อที่จะขึ้นเล่นจริง
2.  **Warnings**: คำแจ้งเตือนข้อผิดพลาดที่จำลองเจอ (เช่น สื่อโหลดไม่ทัน หรือทับเวลา)
3.  **Data Snapshot**: ข้อมูลที่ใช้ในกระบวนการจำลอง
4.  **Sequence Stack Paths**: เส้นทางการคำนวณ Slot
5.  **Blobstore Media Reference**: รายการ CDN Endpoint ของไฟล์มีเดีย

---

## 💻 ตัวอย่างการใช้งานในโปรเจกต์ (Next.js Server Action)

ใช้ดึงรายการสื่อที่กำลังเล่นหรือตารางจำลองในเครื่องเล่นปัจจุบันเพื่อหารูปภาพมีเดีย (`blobId`):

```javascript
import axios from "axios";

const axios_targetr = axios.create({
  baseURL: process.env.URL_TARGETR,
  auth: {
    username: process.env.STACKS_USERNAME,
    password: process.env.STACKS_PASSWORD,
  },
});

export async function playback_screen_by_id(screen_id) {
  try {
    const { data } = await axios_targetr.get(
      `/api/simulate-screen/${screen_id}`
    );

    // ทำการ Map ข้อมูลหารูปภาพพรีวิวขนาดกว้าง 200px หรือตัวเลือกสำรอง
    return (data?.result || []).map((entry) => {
      const resource = entry.item?.resources?.find(
        (r) => r.data?.width === "200" || r.data?.width === 200
      );

      return {
        screenId: data.data?.screenId || screen_id,
        libraryItemId: entry.item?.data?.libraryItemId,
        label: entry.item?.data?.label,
        blobId: resource?.data?.blobId || entry.item?.resources?.[0]?.data?.blobId || null,
      };
    });
  } catch (error) {
    console.error(`Error in playback_screen_by_id for ${screen_id}:`, error.message);
    throw error;
  }
}
```

