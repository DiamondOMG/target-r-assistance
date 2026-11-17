---
status: active
type: reference
created: 2026-07-10
platform: target-r
tags:
  - target-r
  - api
  - rest-api
related:
  - "[[TARGET_R/00_TARGET_R_INDEX]]"
---

# TargetR RESTful API

API สำหรับจัดการ CRUD (Create, Read, Update, Delete) ข้อมูลเอนทิตีหรือวัตถุหลัก (System Objects) ภายในระบบ TargetR ทั้งหมด

## 🔐 Authentication

ความปลอดภัยในการเรียกใช้งาน RESTful API:
*   ต้องทำการยืนยันตัวตนผ่าน HTTP Basic Authentication (`Authorization: Basic ...`) ด้วยค่า `STACKS_USERNAME` และ `STACKS_PASSWORD` ที่กำหนด
*   หรือใช้งานผ่าน Session ID ที่ได้จากการ Login (เก็บไว้ใน Cookie หรือ Auth Header)

---

## 📌 สรุป Endpoints ที่ใช้งานหลักในโปรเจกต์

### 1. หมวดหมู่หน้าจอ (Screens)

*   **ดึงข้อมูลหน้าจอทั้งหมด:**
    `GET /rest-api/v1/screen` หรือ `GET /rest-api/v1/screens`
*   **ดึงข้อมูลหน้าจอตาม ID:**
    `GET /rest-api/v1/screens/{screen_id}`
*   **สร้างข้อมูลหน้าจอใหม่:**
    `POST /rest-api/v1/screens`
*   **อัปเดตข้อมูลหน้าจอ:**
    `PUT /rest-api/v1/screens`

#### 🔍 การกรองข้อมูลรายการหน้าจอ (Screen List Filtering)
การดึงข้อมูลรายการหน้าจอสามารถระบุ Parameter `filter` เพื่อกรองข้อมูลตามฟิลด์หรือคุณสมบัติที่กำหนดได้:

*   **Endpoint**: `GET /rest-api/v1/screens?filter={filterQuery}`
*   **รูปแบบของ Filter Query**: `fieldName=="value"`
*   **ตัวอย่างการกรองข้อมูลที่ใช้งานจริง**:
    *   กรองตามรหัสร้านค้า: `?filter=storeCode=="11107"`
    *   กรองตามกลุ่มแบรนด์ร้านค้า: `?filter=retailer=="Tops"`
    *   กรองตามชื่อโปรเจกต์: `?filter=projectName=="TopsDigital"` หรือ `?filter=ProjectName=="TopsDigital"`

#### ตัวอย่างการเขียนโค้ด (Node.js/Axios)
```javascript
// ดึงข้อมูลหน้าจอเดี่ยว
export async function screen_by_id(screen_id) {
  const response = await axios_targetr.get(`/rest-api/v1/screens/${screen_id}`);
  return response.data;
}

// ดึงข้อมูลหน้าจอทั้งหมด
export async function get_all_screens() {
  try {
    const response = await axios_targetr.get("/rest-api/v1/screen");
    return response.data;
  } catch (error) {
    const response = await axios_targetr.get("/rest-api/v1/screens");
    return response.data;
  }
}
```

---

### 2. หมวดหมู่ลำดับการเล่น (Sequences)

*   **ดึงข้อมูล Sequence ตาม ID:**
    `GET /rest-api/v1/sequences/{sequence_id}`
*   **สร้าง Sequence ใหม่:**
    `POST /rest-api/v1/sequences`
*   **อัปเดต Sequence ตาม ID:**
    `PUT /rest-api/v1/sequences/{sequence_id}`

#### ตัวอย่างการเขียนโค้ด (Node.js/Axios)
```javascript
// ดึงข้อมูล Sequence
export async function sequence_by_id(sequence_id) {
  const response = await axios_targetr.get(`/rest-api/v1/sequences/${sequence_id}`);
  return response.data;
}

// อัปเดตข้อมูล Sequence
export async function update_sequence_targetr(sequence_id, payload) {
  const response = await axios_targetr.put(`/rest-api/v1/sequences/${sequence_id}`, payload);
  return response.data;
}
```

---

### 3. ระบบอัปเดตแบบกลุ่ม (Bulk Data Update API)

ใช้ในการอัปเดตคุณสมบัติหรือฟิลด์ข้อมูลจำนวนมากๆ ของหน้าจอพร้อมกันในการส่งครั้งเดียว (เช่น การอัปเดต endpoint ของ DPoP หรือฟิลด์ตั้งค่าของระบบสกรีน)

*   **Endpoint**: `POST https://stacks.targetr.net/api/bulk-data-update`
*   **Request Body**:
    ```json
    {
      "type": "screen",
      "ids": ["MAC_ADDRESS_1", "MAC_ADDRESS_2"],
      "data": {
        "dpopEndpoint": "https://your-monitor-domain.com/api/pusher",
        "dpopType": "SHORT"
      }
    }
    ```

#### ตัวอย่างการเขียนโค้ด (Node.js/Axios)
```javascript
export async function bulk_data_update(ids, dpop_endpoint, dpop_type) {
  const { data } = await axios_targetr.post(
    "https://stacks.targetr.net/api/bulk-data-update",
    {
      type: "screen",
      ids: ids,
      data: {
        dpopEndpoint: dpop_endpoint,
        dpopType: dpop_type,
      },
    }
  );
  return data;
}
```

---

### 4. การสร้าง Library Item และอัปโหลดไฟล์สื่อ (Media Library & File Upload)

การอัปโหลดไฟล์เข้าไปในระบบของ TargetR จะใช้วิธี **2-Step Flow**:
1. **สร้าง Item แบบระบุ Pending ID (POST)**: เพื่อจอง ID และสร้าง Metadata รอไว้บน Stacks Server
2. **อัปโหลดไฟล์ดิบ Raw Binary (POST)**: ยิงส่งข้อมูลไฟล์ดิบเข้าไปผูกกับ Pending ID ที่จองไว้ข้างต้น

#### Step 1: จอง Item และสร้าง Pending Metadata
*   **Endpoint**: `POST https://stacks.targetr.net/rest-api/v1/libraryitems`
*   **Request Body**:
    ```json
    {
      "type": "libraryitem",
      "data": {
        "label": "ชื่อสื่อ",
        "durationMillis": 15000
      },
      "resources": [
        {
          "type": "pending",
          "data": {
            "pendingId": "PENDING_ID_ที่สุ่มขึ้นมา",
            "createdMillis": "UNIX_TIMESTAMP"
          }
        }
      ]
    }
    ```

#### Step 2: อัปโหลดไฟล์ Raw Binary
*   **Endpoint**: `POST https://stacks.targetr.net/upload`
*   **HTTP Headers**:
    *   `X-UploadType`: `"raw"`
    *   `X-FileName`: `"ชื่อไฟล์.mp4"`
    *   `X-ItemType`: `"libraryitem"`
    *   `Content-Type`: `"content/unknown"`
    *   `X-PendingId`: `"PENDING_ID_ที่ใช้ในสเต็ปแรก"`
    *   `X-ItemId`: `"ITEM_ID_ที่ได้กลับมาจากสเต็ปแรก"`
*   **Request Body**: ข้อมูลไฟล์ดิบในรูปแบบ Binary Buffer

#### ตัวอย่างการเขียนโค้ด (Node.js/fetch)
```javascript
// 1. สร้าง Library Item (จอง Pending)
export async function createLibraryItem(label) {
  const pendingId = Math.floor(Math.random() * 1000000000) + Date.now().toString();
  const requestBody = {
    type: "libraryitem",
    data: { label, durationMillis: 15000 },
    resources: [{ type: "pending", data: { pendingId, createdMillis: Date.now().toString() } }]
  };

  const response = await fetch("https://stacks.targetr.net/rest-api/v1/libraryitems", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Basic ${auth}`,
    },
    body: JSON.stringify(requestBody),
  });
  const result = await response.json();
  return { id: result.id, pendingId };
}

// 2. อัปโหลดข้อมูลไฟล์ Raw Binary
export async function uploadFile(fileBuffer, itemId, pendingId, fileName) {
  const response = await fetch("https://stacks.targetr.net/upload", {
    method: "POST",
    headers: {
      "X-UploadType": "raw",
      "X-FileName": fileName,
      "X-ItemType": "libraryitem",
      "Content-Type": "content/unknown",
      "X-PendingId": pendingId,
      "X-ItemId": itemId,
    },
    body: fileBuffer,
  });
  return response;
}
```


