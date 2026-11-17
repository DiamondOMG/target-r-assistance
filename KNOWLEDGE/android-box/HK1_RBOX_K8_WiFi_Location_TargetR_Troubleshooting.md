---
status: draft
updated: 2026-10-31
source: user-notes
tags:
  - android-box
  - location
  - adb
  - target-r
related:
  - "[[ANDROID_BOX/00_ANDROID_BOX_INDEX]]"
aliases:
  - "Android Box ดึงพิกัดจาก Wi-Fi"
  - "Android Box ดึงพิกัดจาก Wi-Fi 2"
---

# HK1 RBOX K8: พิกัด Wi-Fi และ Target R

บันทึกจากผู้ใช้ ยังไม่ได้ตรวจทดสอบใหม่ในรอบจัดระเบียบนี้ รุ่นชิประบุ RK3568 ในต้นฉบับ แต่สารบัญฮาร์ดแวร์เดิมระบุ RK3528 จึงต้องตรวจรุ่นจริงก่อนอ้างอิง

ฉบับเพิ่มเติมระบุว่า Target R อ่าน gps เท่านั้น จึงถือว่า TODO เรื่องตรวจ provider ในฉบับแรกมีข้อมูลเพิ่มเติมแล้ว แผน GPS Bridge ยังไม่ได้ compile หรือทดสอบ

## บันทึกครั้งแรก

## Android Box: ดึงพิกัดจาก Wi-Fi (แก้แล้ว)

### อุปกรณ์

- HK1 RBOX K8 (RK3568), Android 13 (SDK 33)
- GMS 21.42.18 ใน `/system/priv-app/PrebuiltGmsCoreQt/`
- IP ADB: `10.210.210.248`

### อาการ

- `network` / `fused` provider ไม่มี location, `connected=false`
- GPS Test เปิดแล้วปิดตัวเอง
- `com.google.android.gms.persistent` crash-loop ทุก ~3 วินาที (PID เปลี่ยนตลอด)

### สาเหตุ

- เครื่องไม่มี `gps` provider (ไม่มีชิป GPS)
- GMS เรียก `LocationManager.getProvider()` ใน `FusionScheduler` → framework ของ firmware โยน NPE (`LocationProviderManager.getProperties()` on null) → FlpThread ของ GMS ตายทั้งโปรเซส
- GPS Test ตายด้วยสาเหตุเดียวกัน
- ข้อสันนิษฐานว่า GMS ถามหา `gps` โดยเฉพาะ เป็นการอนุมาน แต่การทดสอบยืนยันผลแล้ว

### วิธีแก้ (ใช้ได้ผลแล้ว)

เพิ่ม test provider ชื่อ `gps` เพื่อให้ framework มี provider ให้ GMS หาเจอ

bash

```bash
adb shell appops set 2000 android:mock_location allow
adb shell cmd location providers add-test-provider gps
adb shell cmd location providers set-test-provider-enabled gps true
adb shell settings put global wifi_scan_always_enabled 1
adb shell cmd location set-location-enabled true
```

ย้อนกลับ: `adb shell cmd location providers remove-test-provider gps`

### ผลลัพธ์

```
network: 13.748628, 100.547916  hAcc=14.5 m  {networkLocationType=wifi}
fused:   13.748628, 100.547916
```

### ตรวจสอบ

bash

```bash
adb shell pidof com.google.android.gms.persistent    # PID ต้องไม่เปลี่ยน
adb shell dumpsys location | grep -A4 -E "^    network provider:|^    fused provider:"
```

### ข้อจำกัด

- test provider **หายเมื่อรีบูต** ต้องรันคำสั่งใหม่ทุกครั้ง (crash-loop จะกลับมาถ้าไม่รัน)
- test provider `gps` ไม่มีพิกัดจริง ถ้า Target R อ่านจาก `gps` โดยตรงจะไม่ได้ค่า ต้องอ่านจาก `network` หรือ `fused`
- แอปที่ขอพิกัดต้องได้รับสิทธิ์ location
- wireless ADB อาจต้องเปิดใหม่หลังรีบูต

### ทางแก้ถาวร / ที่ยังไม่ได้ทำ

- [ ]  ตั้งให้รันอัตโนมัติตอนบูต (ต้องใช้ root หรือแอป automation เช่น MacroDroid/Tasker)
- [ ]  ขอ firmware ใหม่จากผู้ผลิตที่แก้ LocationManagerService
- [ ]  ยืนยันว่า Target R อ่านพิกัดจาก provider ไหน (`network` / `fused` / `gps`)
- [ ]  ยืนยันว่า box root ได้หรือไม่

### ข้อสังเกตอื่น

- Play Store เป็นเวอร์ชัน 37.8.18 ใหม่กว่า GMS มาก แต่ไม่ได้เป็นสาเหตุ
- ไม่ต้องอัปเดตหรือถอน GMS

## บันทึกเพิ่มเติม

## Android Box: ดึงพิกัดจาก Wi-Fi ให้ Target R

### อุปกรณ์

- HK1 RBOX K8 (RK3568), Android 13 (SDK 33)
- GMS 21.42.18 อยู่ใน `/system/priv-app/PrebuiltGmsCoreQt/`
- Target R = `net.targetr.stacks.central`
- เครื่องทดสอบ: B25A (`10.210.210.248`)
- เครื่องอ้างอิงที่ทำงานปกติ: จอ Sharp ตัวที่ 1 และ 3

### อาการ

- `network` / `fused` provider ไม่มี location และ `connected=false`
- GPS Test เปิดแล้วปิดตัวเอง
- CMS ได้พิกัด default (`13.7366, 100.4995`) แทนพิกัดจริง

### สาเหตุ (พบ 2 ชั้น)

1. **เครื่องไม่มี `gps` provider** (ไม่มีชิป GPS)
    - GMS เรียก `LocationManager.getProvider()` ใน `FusionScheduler`
    - framework ของ firmware โยน NPE (`LocationProviderManager.getProperties()` on null)
    - `com.google.android.gms.persistent` ตายและ restart ทุก ~3 วินาที (PID เปลี่ยนตลอด)
    - ข้อสันนิษฐานว่า GMS ถามหา `gps` ไม่ได้ยืนยันตรง ๆ แต่การทดสอบด้วย test provider ยืนยันผลแล้ว
2. **Target R ไม่ได้สิทธิ์ location** (FINE และ COARSE เป็น `granted=false`)
    - หลัง grant แล้ว พบว่า Target R ฟัง **`gps` provider อย่างเดียว** (HIGH_ACCURACY ทุก 1 วินาที) ไม่ได้อ่าน `network` หรือ `fused`

### วิธีแก้ชั่วคราว (ใช้ได้ผลแล้ว แต่ต้องต่อ ADB ตลอด)

bash

```bash
A="adb -s 10.210.210.248"
$A shell appops set 2000 android:mock_location allow
$A shell cmd location providers add-test-provider gps
$A shell cmd location providers set-test-provider-enabled gps true
$A shell settings put global wifi_scan_always_enabled 1
$A shell cmd location set-location-enabled true
$A shell pm grant net.targetr.stacks.central android.permission.ACCESS_FINE_LOCATION
$A shell pm grant net.targetr.stacks.central android.permission.ACCESS_COARSE_LOCATION
```

จากนั้นรัน loop อ่านพิกัดจาก `network` provider แล้วส่งเข้า `gps` ด้วย `set-test-provider-location gps --location LAT,LNG --accuracy 15` ทุก 10 วินาที

ผลที่ได้: network ให้ `13.748628, 100.547916` (hAcc ~14.5 m, `networkLocationType=wifi`) และ CMS แสดง `13.74863, 100.54792` ตรงกับจอ Sharp

**ข้อจำกัด**

- test provider หายเมื่อรีบูต และ crash-loop กลับมา
- ถ้าปิดคอมหรือ ADB หลุด พิกัดจะค้าง
- ใช้ไม่ได้กับงานจริงที่ต้องทำงานเอง

### แผนถาวร: แอป GPS Bridge บนตัว box

- แอป `com.example.gpsbridge` ทำงานตอนบูต (BOOT_COMPLETED, foreground service)
- สร้าง `gps` test provider เอง ทำให้ GMS ไม่ crash
- อ่านพิกัด Wi-Fi จาก `network` provider แล้วป้อนเข้า `gps` ทุก 5 วินาที
- ใช้ ADB ครั้งเดียวต่อเครื่องผ่าน `setup_all.sh` (ติดตั้ง, grant สิทธิ์, `appops mock_location allow`, whitelist battery, grant สิทธิ์ให้ Target R, เปิดแอปครั้งแรก)
- แต่ละเครื่องได้พิกัดตาม Wi-Fi ของตัวเองโดยอัตโนมัติ

### TODO

- [ ]  **สร้างโปรเจกต์ Android Studio** (Empty Views Activity, Kotlin, package `com.example.gpsbridge`, Min SDK 30)
- [ ]  **ใส่ไฟล์ 3 ตัว** (ขอให้ Claude สร้างใหม่ได้ถ้าหา chat เดิมไม่เจอ)
    - `AndroidManifest.xml` (แทนของ template)
    - `Bridge.kt` (ลบ `MainActivity.kt` เดิมของ template)
    - `setup_all.sh`
- [ ]  Build APK แล้วแก้ error ถ้ามี (โค้ดยังไม่เคย compile หรือทดสอบ)
- [ ]  ทดสอบบน B25A: รัน `./setup_all.sh app-debug.apk 10.210.210.248` แล้ว **รีบูต** ดูว่า CMS ได้พิกัดเองโดยไม่ต่อ ADB
- [ ]  ถ้าผ่าน ให้รันกับ box ตัวอื่นทั้งหมด (ไม่ต้องลงบนจอ Sharp ที่ปกติอยู่แล้ว)
- [ ]  ถ้าไม่ทำงานหลังรีบูต ให้เช็ก `adb logcat -d | grep GpsBridge` (ส่วนใหญ่เป็นเรื่องสิทธิ์ หรือ firmware ปิดการเริ่มแอปตอนบูต)
- [ ]  (ทางเลือก) ตรวจ `dumpsys location` ของ Sharp ตัวที่ 1/3 ว่า `gps` provider ทำงานอย่างไร
- [ ]  (ทางเลือก) ขอ firmware ใหม่จากผู้ผลิตที่แก้ LocationManagerService

### คำสั่งตรวจสอบ

bash

```bash
adb shell pidof com.google.android.gms.persistent   # ต้องไม่เปลี่ยน
adb shell dumpsys location | grep -A4 -E "^    (gps|network|fused) provider"
adb shell dumpsys package net.targetr.stacks.central | grep -E "ACCESS_(FINE|COARSE)_LOCATION: granted"
```

### หมายเหตุ

- Play Store (37.8.18) ใหม่กว่า GMS มาก แต่ไม่ได้เป็นสาเหตุ ไม่ต้องอัปเดตหรือถอน GMS
- `ls /system/...` ใน Git Bash ต้องใส่ `MSYS_NO_PATHCONV=1` นำหน้า ไม่งั้น path ถูกแปลงเป็น `C:/Program Files/Git/...`


## GPS Bridge test progress — 2026-11-02

- Built the APK in C:/OMG/actmedia-gps and installed it on HK1 RBOX K8 (10.210.210.248) using adb install -r. Opening the APK through the TV file installer stalled; ADB installation succeeded.
- Initial APK was absent from Android 13 Select mock location app. Added ACCESS_MOCK_LOCATION to the manifest, rebuilt, installed the update, and GPS Bridge appeared for user selection.
- Location and Background Location permissions were granted. The foreground service was started from the app UI.
- Verified network provider delivered Wi-Fi location 13.748673, 100.547919 with about 14 m accuracy and the mock gps provider received it. dumpsys location showed Target R (net.targetr.stacks.central) listening to gps with HIGH_ACCURACY. Bridge works on this device.
- Automatic start after reboot is not yet verified.

### Next step: first-run APK setup flow

User wants a new APK that guides setup on first launch: request Location and Background Location permissions in sequence; explain and guide selection of GPS Bridge as the mock-location app; then start the foreground bridge after setup. Android requires the user to explicitly select a mock-location app in Developer options; a normal APK cannot silently select itself. Show an in-app explanation, open the relevant Settings screen where possible, resume setup on return, then start the service. Test the first-run flow and reboot auto-start on the HK1 RBOX K8.


### First-run flow iteration — 2026-11-02

- Replaced the multi-button screen with a single guided flow: request foreground location/notification permission, request background location separately, then prompt the user to select GPS Bridge as mock location. On return, the app checks the mock-location AppOp and automatically starts the foreground bridge.
- After updating the APK on the already configured HK1 box, opening GPS Bridge automatically started the service without pressing Start. Verified MOCK_LOCATION app-op allow and a new Wi-Fi-to-gps bridge log at 13.7486326, 100.5479192.
- Current APK: C:/OMG/actmedia-gps/app/build/outputs/apk/debug/app-debug.apk.
- Fresh-install flow still needs testing from a clean install. Developer options and mock-app selection still require user confirmation by Android design. Boot auto-start remains unverified.


## ACTMEDIA round-box provider investigation — 2026-11-02

- Compared with HK1 RBOX K8: the square HK1 successfully obtained Wi-Fi-derived coordinates through Android network provider after creating the gps test provider. The round ACTMEDIA box has not produced a network or fused location. No physical GNSS chip was confirmed for ACTMEDIA during this investigation.
- ACTMEDIA identifies as model ACTMEDIA, SDK 29 / Android 10, with GMS 26.42.31. Location mode is 3 and wifi_scan_always_enabled is 1; GMS fine-location AppOp is allowed.
- After a box reboot, GPS Bridge BootReceiver started the foreground service. LocationManager still reports network provider useable=false, allowed=false, enabled=false and no last location. Framework fused subscription and Google FusedLocationProviderClient high-accuracy request are active, but neither has delivered a location; mock gps last location remains null. Reboot did not fix provider behavior.
- Google Location Settings intent resolves to the generic Android TV Location page, which only shows Use Wi-Fi to estimate location; no separate Google Location Accuracy control is exposed there. Logs showed GMS NetworkLocationService process restarts and a package-manager freeze/ungrant event; these are clues, not a proven root cause.
- GPS Bridge now also subscribes to framework fused and Google FusedLocationProviderClient and ignores stale or mock input locations. Build succeeded and this version was installed on ACTMEDIA through ADB, but it still has no coordinates because providers return none.
- Latest APK remains at C:/OMG/actmedia-gps/app/build/outputs/apk/debug/app-debug.apk. minSdk is 29 for ACTMEDIA Android 10. ADB installation succeeded. The earlier TV graphical installer hang was bypassed with ADB; whether the latest APK installs correctly through the graphical installer has not been verified.
