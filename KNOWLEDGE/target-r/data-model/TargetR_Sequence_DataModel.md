---
status: active
tags:
  - sequence
  - digital-signage
  - programmatic
  - vast
  - targetr
related:
  - "[[TARGET_R/00_TARGET_R_INDEX]]"
  - "[[TARGET_R/DataModel/TargetR_Screen_DataModel]]"
type: data-model
platform: targetr
updated: 2026-05-12
source: ai-generated
---

# TargetR Sequence Data Model

โครงสร้างข้อมูล Sequence Object ของระบบ TargetR — ใช้จัดเรียงคอนเทนต์ในระบบ Digital Signage

## 1. Hierarchy Overview

- **Sequence (Root)**: ข้อมูลหลักและ Metadata
  - **Stacks[]**: ลำดับของกลุ่มรายการ (Columns)
    - **Items[]**: รายการแต่ละช่อง (Slots/Rows)
      - **Resources[]**: ไฟล์สื่อ (ภาพ/วิดีโอ) ที่ผูกกับ Item นั้นๆ

## 2. JSON Structure Examples

### 2.1 Basic Structure (Multi-Slot & Multi-Item)

```json
{
  "type": "sequence",
  "id": "SEQ_ID",
  "data": { "label": "Multi-Slot Example", "sync": "true" },
  "stacks": [
    {
      "items": [
        {
          "data": { "itemId": "ITEM_A1", "label": "Video 1", "durationMillis": "15000" },
          "resources": [{ "type": "static", "data": { "blobId": "ID_1" } }]
        },
        {
          "data": { "itemId": "ITEM_A2", "innerSequenceId": "NEST_ID", "label": "Nested Play" }
        }
      ]
    },
    {
      "items": [
        {
          "data": { "itemId": "ITEM_B1", "label": "Image 1", "durationMillis": "10000" },
          "resources": [{ "type": "static", "data": { "blobId": "ID_2" } }]
        }
      ]
    }
  ]
}
```

### 2.2 Advanced Structure (VAST / Dynamic Content)

```json
{
  "type": "sequence",
  "id": "VAST_SEQ_ID",
  "data": {
    "customType": "vast",
    "vastAddress": "https://example.com/vast.xml",
    "vastPreview": "true",
    "sync": "true"
  },
  "stacks": [
    {
      "items": [
        {
          "data": { "importType": "vast", "importMillis": "1770000000000", "label": "External Campaign" },
          "resources": [
            {
              "type": "dynamic",
              "data": { "uri": "https://external-media.mp4" },
              "snapshot": [
                { "type": "static", "data": { "blobId": "CACHE_ID_1", "thumb": "true" } },
                { "type": "static", "data": { "blobId": "CACHE_ID_2", "contentType": "video/mp4" } }
              ]
            }
          ]
        }
      ]
    }
  ],
  "usedBy": ["PARENT_SEQUENCE_ID"]
}
```

### 2.3 Conditional Structure (Time & Logic)

```json
{
  "items": [
    {
      "data": {
        "itemId": "COND_ITEM_001",
        "label": "Promotion Ad",
        "startMillis": "1775543400000",
        "endMillis": "1777019700000",
        "condition": "storeCode == \"123\""
      },
      "resources": [...]
    }
  ]
}
```

### 2.4 Programmatic Item (จาก Production จริง)

จาก sequence_v2.json — Item ที่มาจากระบบ Programmatic:

```json
{
  "data": {
    "startMillis": "1773594300000",
    "form_programmatic": "default",
    "apiTest": "true",
    "libraryItemId": "15ED4BA2A06085",
    "transitionShader": "none",
    "durationMillis": "15000",
    "label": "Ads Mechanic En-1 - 1920x1080",
    "email_programmatic": "deathsense06@gmail.com",
    "endMillis": "1798736100000",
    "seq_id": "13EE9469DEF1DF",
    "id_programmatic": "8098523d-c8ac-4cde-9ad1-410fdb501812",
    "slot_name": "Slot#C1",
    "seq_slot": "4"
  },
  "resources": [
    { "type": "static", "data": { "thumb": "true", "blobId": "...", "contentType": "image/jpeg" } },
    { "type": "static", "data": { "blobId": "...", "width": "1920", "height": "1080", "contentType": "image/jpeg" } },
    { "type": "static", "data": { "blobId": "...", "contentType": "video/mp4", "fps": "29.97", "durationMillis": "15020" } }
  ]
}
```

Fields เฉพาะ Programmatic: `form_programmatic`, `email_programmatic`, `id_programmatic`, `apiTest`, `seq_id`, `slot_name`, `seq_slot`

### 2.5 Inner Sequence Item (Hivestack/Report)

```json
{
  "data": {
    "itemId": "13431B4E6A8BA2",
    "condition": "screenId==\"688FC900365E\"",
    "report": "true",
    "durationMillis": "15000",
    "innerSequenceId": "15A9F3865CC64B",
    "userId": "10350CDB706893",
    "customId": "InnerHivestackForBigCTVsignage 01"
  }
}
```

## 3. Key Field Definitions

### Root Level

| Field | Description |
| :--- | :--- |
| `type` | `"sequence"` |
| `id` | Unique ID ของ Sequence |
| `data.label` | ชื่อ Sequence |
| `data.createdMillis` / `modifiedMillis` | Timestamp สร้าง/แก้ไข |
| `data.report` | เปิด/ปิดรายงาน (Boolean string) |
| `data.sync` | สถานะ sync |
| `data.version` | เวอร์ชัน |
| `data.maxStacks` | จำนวน Slot สูงสุด |
| `data.defaultNewItemDuration` | Duration เริ่มต้น (ms) |
| `data.syncVideoMode` | โหมด sync วิดีโอ |
| `data.customType` | ประเภทพิเศษ (เช่น `"vast"`) |
| `data.vastAddress` | URL สำหรับ VAST XML |
| `usedBy` | Array ของ parent Sequence IDs |
| `stacks` | Array ของ Stacks |

### Stack Level

| Field | Description |
| :--- | :--- |
| `data.top` | อยู่ด้านบน |
| `data.maxDuration` | Duration สูงสุด (ms) |
| `data.slot_number` | ลำดับ Slot |
| `items` | Array ของ Items ใน Stack นี้ |

### Item Level

| Field | Description |
| :--- | :--- |
| `data.itemId` | ID ของรายการ |
| `data.durationMillis` | ระยะเวลาแสดงผล (ms) |
| `data.innerSequenceId` | Sequence ซ้อนใน (Special Slot) |
| `data.libraryItemId` | อ้างอิงจาก Library |
| `data.label` | ชื่อไฟล์/รายการ |
| `data.customId` | ID สำหรับ Playback Logs |
| `data.report` | เปิดรายงานระดับ Item |
| `data.userId` | ผู้จัดการรายการ |
| `data.transitionShader` | เอฟเฟกต์เปลี่ยนผ่าน |
| `data.condition` | เงื่อนไขตรรกะ |
| `data.startMillis` / `endMillis` | ช่วงเวลาที่เล่นได้ |
| `resources` | Array ของ Assets |

### Resource Level

| Field | Description |
| :--- | :--- |
| `type` | `"static"` หรือ `"dynamic"` |
| `data.blobId` | ID ไฟล์ใน Storage |
| `data.uri` | URL ไฟล์ภายนอก (dynamic) |
| `data.contentType` | MIME type |
| `data.width` / `height` | ขนาด (px) |
| `data.contentLength` | ขนาดไฟล์ (bytes) |
| `data.durationMillis` | ความยาววิดีโอ |
| `data.fps` / `bitrate` | FPS / Bitrate |
| `data.thumb` | `"true"` = รูป Preview |
| `data.videoDetails` / `audioDetails` | Codec info |
| `snapshot` | Static cache ของ dynamic content |

## 4. Playback Logic

ระบบเล่น **1 รายการต่อ 1 Slot** ในเวลาเดียวกัน:

1. **Conditions**: ตรวจ condition ก่อน (เวลา, storeCode, screenId ฯลฯ)
2. **Order**: ผ่านหลายรายการ → index น้อยกว่าเล่นก่อน
3. **Empty Slots**: Stack เป็น `{}` = ไม่แสดงอะไร

## 5. Production Sequence Summary (จาก sequence_v2.json)

- **Sequence ID**: `13E35841A57020`
- **Label**: `5-5-2026 Copy of Production 240 Slot BigCDigital_Walkway 1920x1080 - Base`
- **Max Stacks**: 240
- **Version**: 2959
- **Sync**: true
- **Item Types ที่พบ**:
  - Programmatic items (มี `form_programmatic`, `id_programmatic`)
  - MC2 condition items (`condition: "E == \"MC2\""`)
  - Inner Sequence items (`innerSequenceId`)
  - Hivestack/Report items (`report: "true"`, `customId`)
- **Resources**: ส่วนใหญ่มี 3 resources ต่อ item (thumb, full image, video)
  - Resolution: 1920x1080
  - Format: H.264 MP4 + AAC audio

---
**หมายเหตุ:**
1. **Special Slot:** สังเกตจากฟิลด์ `innerSequenceId`
2. **Media Item:** จะมี `resources` สำหรับระบุไฟล์ภาพหรือวิดีโอ
3. **VAST / Dynamic:** ใช้ `customType: "vast"` + `resource type: "dynamic"` + `snapshot`
