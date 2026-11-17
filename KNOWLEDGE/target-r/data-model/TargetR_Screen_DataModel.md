---
status: active
tags:
  - screen
  - hardware
  - digital-signage
  - targetr
related:
  - "[[TARGET_R/00_TARGET_R_INDEX]]"
  - "[[TARGET_R/DataModel/TargetR_Sequence_DataModel]]"
type: data-model
platform: targetr
updated: 2026-05-12
source: ai-generated
---

# TargetR Screen Data Model

โครงสร้างข้อมูล Screen Object ของระบบ TargetR — ใช้เก็บสถานะหน้าจอ Digital Signage แต่ละตัว

## Root Level Fields

| Field | Description | Example |
| :--- | :--- | :--- |
| `type` | ประเภทข้อมูล | `"screen"` |
| `id` | MAC Address ของอุปกรณ์ | `"A4AE125D42DE"` |
| `sequenceId` | Sequence ที่เล่นอยู่ | `"13958A10507CD3"` |
| `events` | Event triggers/actions | ดู Events section |
| `timeLoaded` | เวลาโหลด (Unix ms) | `1777867916823` |
| `defaultLoaderCommsPeriod` | รอบ Loader (ms) | `30000` |
| `defaultPlayerCommsPeriod` | รอบ Player (ms) | `60000` |

## Data Object — หมวดหลัก

### Hardware
Fields: `hardware`, `hardwareType`, `hardwareBrand`, `hardwareModel`, `hardwareManufacturer`, `hardwareBoard`, `hardwareDevice`, `hardwareProduct`, `hardwareDescription`, `hardwareBuild`, `hardwareId`, `hardwareSerial`, `hardwareBootloader`, `hardwareTags`, `hardwareVersionCodename`, `hardwareBootMillis`

ตัวอย่าง: SHARP AQUOS-TVX19A, TV Box - HK1Max

### Android
Fields: `platform` (`"android"`), `androidRelease` (`"11"`), `androidSdk` (`"30"`)

### Display
Fields: `screenWidth`, `screenHeight`, `screenDpiX/Y`, `displayAspectRatio`, `displayArrangement`, `displaysConnected`, `displayPosition`, `displayState`

### Network
Fields: `wifiSsid`, `wifiRssi`, `wifiSpeed`, `localAddress`, `loaderAddress`, `serverAddress`, `serverUdpIp`, `serverUdpPort`, `serverHttpPort`, `loaderUdpPort`, `localWebServerPort`, `localPeerCount`

- Server: `screens.omg.group` / UDP: `103.106.229.218:9091`

### Location
Fields: `gpsLatitude`, `gpsLongitude`, `gpsAltitude`, `gpsBearing`, `gpsSpeed`, `gpsFixMillis`, `retailer`, `storeCode`, `storeLocation`, `storeSection`, `RetailerType`, `country`, `continent`, `timeZone`, `timeZoneOverride`

### Player Status
Fields: `applicationId` (`net.targetr.stacks.central`), `version`, `loaderVersion`, `activePlayer`, `desiredPlayer`, `customStatus`, `label`, `screenId`, `mainDevice`, `sequenceId`, `startMillis`, `stopMillis`, `startCount`, `recentStartCount`, `createdMillis`, `modifiedMillis`, `userModifiedMillis`

### Data Transfer (Blob)
Fields: `totalData`, `totalBlobs`, `blobDataDownloaded`, `blobDataDownloadedRate`, `blobDataDownloadFailures`, `blobDataShared`, `blobDataSharedRate`, `blobDataCorruption`, `blobDataQueueSize`, `requiredDataAvailable`, `requiredDataTotal`

### Communication Timing
Fields: `lastPlayerCommsMillis`, `lastLoaderCommsMillis`, `lastLoaderUdpCommsMillis`, `lastServerResponseMillis`, `lastDisplayRecordMillis`, `lastDisplayRecordItemId`, `playerCommsPeriod`, `playerCommsPeriodOverride`, `remoteDataFetchPeriod`

### Settings
Fields: `volume`, `plugged`, `autoStart`, `acceptInterrupt`, `syncBroadcast`, `showStatusIcon`, `letsEncryptSupported`, `webviewReuse`, `videoBlankerPeriod`, `blackCondition`, `scrollingText`, `scrollingTextCondition`, `downloadCondition`, `keyId`, `assetTypeId`, `hivestackUuid`

### Memory
Fields: `memFree`, `memTotal`, `memMax`, `memoryClass`, `freeSpace_0/_1/_2/_3`

## Events Structure

```json
{
  "trigger": { "type": "remote", "data": { "name": "example" } },
  "action": {
    "type": "showItem",
    "data": { "resumeDelay": "15000" },
    "item": {
      "type": "libraryitem",
      "data": { "durationMillis": "15000", "label": "filename.mp4" },
      "resources": [
        { "type": "static", "data": { "thumb": "true", "blobId": "...", "contentType": "image/jpeg" } },
        { "type": "static", "data": { "blobId": "...", "contentType": "video/mp4" } }
      ]
    }
  }
}
```

- `trigger.type: "remote"` = สั่งจากเซิร์ฟเวอร์
- `action.type: "showItem"` = แสดง Item แทรก
- `action.data.resumeDelay` = เวลารอก่อนกลับเล่น Sequence ปกติ

---

## 💻 ตัวอย่างไฟล์ JSON ของ Screen จริง (Real-world JSON Example)

```json
{
  "type": "screen",
  "id": "00376DEC1870",
  "data": {
    "screenId": "00376DEC1870",
    "label": "Tops Digital Ladprao Floor 1",
    "sequenceId": "034CD62B516544",
    "GroupID": "034CD62B516544",
    "GroupName": "Monitor - ActMedia Thailand - Big C - Signage",
    "retailer": "Big C",
    "storeCode": "11107",
    "storeLocation": "Ladprao",
    "storeSection": "Premium_Pillar",
    "STC": "Master_C_Value",
    "dpopEndpoint": "https://targetr-monitor.vercel.app/api/pusher",
    "dpopType": "SHORT",
    "displaysConnected": "4",
    "screenWidth": "1920",
    "screenHeight": "1080",
    "platform": "android",
    "androidRelease": "10",
    "androidSdk": "29",
    "wifiSsid": "omgdigital",
    "localAddress": "192.168.0.101",
    "serverAddress": "screens.omg.group",
    "lastPlayerCommsMillis": "1781081424494",
    "lastLoaderCommsMillis": "1781081634762",
    "volume": "100",
    "plugged": "1",
    "memFree": "7688280",
    "memTotal": "8124230"
  }
}
```

