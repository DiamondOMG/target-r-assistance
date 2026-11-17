---
type: troubleshooting
status: active
created: 2026-11-17
updated: 2026-11-17
platform:
  - targetr
  - android
tags:
  - targetr
  - ds-loader
  - player-comms-problem
  - black-screen
  - troubleshooting
related:
  - "[[TARGET_R/00_TARGET_R_INDEX]]"
  - "[[TARGET_R/DataModel/TargetR_Screen_DataModel]]"
  - "[[ANDROID_BOX/00_ANDROID_BOX_INDEX]]"
aliases:
  - "ติดใบ้"
  - "จอติดใบ้"
  - "Player comms problem"
---

# Target-R: อาการ "ติดใบ้" (`Player comms problem`) — ขึ้น On สีเขียวแต่จอดำ

> **ชื่อเรียกหน้างาน:** ผู้ใช้เรียกอาการนี้ว่า **"ติดใบ้"** (เครื่องยังออนไลน์รายงานสถานะได้ แต่เงียบไม่ยอมเล่นสื่อ หน้าจอดำ)

## อาการที่พบ
- บนหน้า Target-R Console แสดงสถานะ **On (สีเขียว)** และ `Status: Available`
- มีไอคอนเตือน **`Player comms problem`**
- หน้าจอจริงหน้างานเป็น **จอดำ ไม่เล่นสื่อ** (`background: "#000000"`)
- **เมื่อรีสตาร์ทแอปหรือรีบูตกล่อง อาการหายและกลับมาเล่นสื่อได้ปกติ**

## ผลการตรวจสอบเวอร์ชันซอฟต์แวร์ (2026-11-17)
- จากการตรวจจับจอติดใบ้ทั้งหมด **10/10 จอ (100%)** — ไม่ว่าจะคัดกรองที่เกณฑ์ค้าง 15 นาที, 30 นาที หรือ 60 นาที — **ทุกจอใช้ซอฟต์แวร์เวอร์ชันเก่า `android-player-2023-06-02.apk` (`loaderVersion: 15.2`) ทั้งหมด**
- **ไม่พบอาการติดใบ้** ในจอที่อัปเดตเป็นเวอร์ชันใหม่กว่า (เช่น `android-player-2026-04-02.apk`, `android-player-28.2.apk`, `android-exoplayer-12.0.apk`)

---

## สาเหตุเชิงเทคนิค (2 ชั้นภายในแอปเดียวกัน)

แอป `net.targetr.stacks.central` บน Android Box แยกการทำงานออกเป็น 2 ส่วนในโปรเซสเดียว:

1. **DS Loader (`lastLoaderCommsMillis`):**
   - ตัวคุมเบื้องหลัง ส่ง heartbeat (UDP/HTTP) ไปยังเซิร์ฟเวอร์ทุก **30 วินาที** (`defaultLoaderCommsPeriod: 30000`)
   - หน้าเว็บ Target-R ใช้สถานะของ DS Loader ในการแสดงปุ่ม **On สีเขียว**
2. **Android Player (`lastPlayerCommsMillis` / `lastDisplayRecordMillis`):**
   - ตัวเล่นภาพ/วิดีโอ (`android-player-2023-06-02.apk`) ส่งรายงานทุก **60 วินาที** (`defaultPlayerCommsPeriod: 60000`)

### กลไกการเกิดอาการ
- ตัว **Player ค้าง/ตาย** โดยท่อถอดรหัสภาพ (Hardware MediaCodec / WebView) เกิด deadlock (ไม่ได้เกิดจาก Java Heap `memMax` 512 MB เต็ม เพราะ `memTotal` ยังอยู่แค่ ~55 MB)
- แต่ **DS Loader ยังทำงานและส่ง heartbeat ปกติ** หน้าเว็บจึงยังขึ้น **On สีเขียว** และแจ้งเตือนว่า **`Player comms problem`**
- แม้ DS Loader จะพยายามสั่งเปิด Player ซ้ำ (สังเกตได้จากค่า `recentStartCount` ที่พุ่งสูง เช่น `4` ถึง `46` ครั้ง) แต่เนื่องจากทั้งคู่แชร์โปรเซสหลัก `net.targetr.stacks.central` เดียวกัน โปรเซสที่ค้างจึงไม่ถูกล้างออก จอจึงยังคงดำต่อไป

### 3 ปัจจัยกระตุ้นที่ทำให้ `android-player-2023-06-02.apk` ติดใบ้
1. **ตัดเข้า/ออกจากโหมดตั้งเวลาจอดำ (`blackCondition`) แล้วตื่นไม่ขึ้น (พบบ่อยที่สุด — 7/10 จอ):** เช่นตั้ง `blackCondition` ถึง `08:00` หรือ `09:45` พอถึงเวลาตื่นตัว Player ค้าง
2. **สัญญาณ HDMI / Splitter / Wall Controller กระพริบชั่วขณะ:** เช่นเปิดสวิตช์ไฟจอทีหลังกล่อง หรือไฟกระพริบระหว่างวัน ทำให้ Display Surface หลุดกลางอากาศ
3. **ความร้อนสะสมสูงจัด (Overheat > 80–86 °C):** ทำให้ CPU Load พุ่งสูง (`systemLoadAverage > 12`) และชิปถอดรหัสวิดีโอค้างกลางคันระหว่างเล่น

---

## ฟิลด์ที่ใช้ตรวจจับอาการนี้ใน Target-R API

| Field | ความหมายเมื่อเกิดอาการติดใบ้ |
|---|---|
| `lastLoaderCommsMillis` | อัปเดตเป็นเวลาปัจจุบันปกติ (ห่างจากปัจจุบันไม่เกิน ~10 นาที) |
| `lastPlayerCommsMillis` | หยุดนิ่งย้อนหลังไปนาน (ห่างจาก `lastLoaderCommsMillis` ตั้งแต่ 1 ชั่วโมงขึ้นไป) |
| `lastDisplayRecordMillis` | หยุดนิ่งใกล้เคียงกับ `lastPlayerCommsMillis` (ไม่มีการเล่นสื่อใหม่) |
| `recentStartCount` | มักสูงขึ้น (> 1) จากการที่ DS Loader พยายามปลุก Player ซ้ำ |
| `systemCpuTemp` / `systemLoadAverage` | ตรวจเช็คกรณีเครื่องร้อนจัดหรือ CPU โหลดค้าง |
| `blackCondition` | ตรวจสอบช่วงเวลาจอดำเทียบกับเวลาที่ Player หยุดรายงาน |
| `ACT_AnyDesk` | รหัส AnyDesk สำหรับรีโมทเข้าไปจัดการเครื่อง |

---

## วิธีแก้ไข

### 1. แก้หน้างาน (ทำทันที)
- รีโมทเข้ากล่องผ่าน **AnyDesk** (`ACT_AnyDesk`) หรือ **ADB over Tailscale**:
  - **Force Stop และเปิดแอปใหม่:**
    ```bash
    adb shell am force-stop net.targetr.stacks.central
    adb shell monkey -p net.targetr.stacks.central -c android.intent.category.LAUNCHER 1
    ```
  - หรือ **รีบูตกล่อง Android Box:**
    ```bash
    adb reboot
    ```

### 2. การป้องกันระยะยาว (ผ่าน `https://tops.actx.digital/manage_target_r`)
1. **อัปเดต `desiredPlayer` เป็นเวอร์ชันใหม่:** ทยอยเปลี่ยนจาก `android-player-2023-06-02.apk` ไปเป็นเวอร์ชันใหม่ (เช่น `android-player-2026-04-02.apk` หรือ `android-exoplayer-12.0.apk`)
2. **ตั้งค่า `restartTime` ให้ถูกจังหวะ:** ตั้งเวลารีสตาร์ทประจำวันให้อยู่ **หลังจากพ้นช่วง `blackCondition` สัก 5 นาที** หรือ **หลังจากพนักงานเปิดสวิตช์ไฟจอเรียบร้อยแล้ว** (เช่น จอดำถึง `08:00` ให้ตั้ง `restartTime = "08:05"`)

### 3. การเฝ้าระวัง / ลิตรายการจอติดใบ้
- ใช้ MCP Tool `targetr_stuck_screens` ในโปรเจกต์ `target-r-assistance` (จะ sync ข้อมูลจาก Target-R และคัดกรองจอที่ `lastLoaderCommsMillis` ออนไลน์แต่ `lastPlayerCommsMillis` ค้าง พร้อมส่งออกไฟล์ CSV ใน `SANDBOX/stuck_screens_report.csv`)
