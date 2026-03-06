# Motorola OTA Protocol — Findings Document

> **Source**: smali analysis of the Motorola OTA client APK and captured server
> response logs for the lamu_g (moto g05) device.

---

## 1. Server Base URL

| Field       | Value                       | Evidence                   |
|-------------|-----------------------------|----------------------------|
| Hostname    | `moto-cds.appspot.com`      | CDSUtils.smali             |
| Protocol    | HTTPS                       | CDSUtils.smali             |
| Full prefix | `https://moto-cds.appspot.com` | CDSUtils.smali          |

---

## 2. Endpoints

All endpoints accept **POST** requests with `Content-Type: application/json`.

### 2.1 Check for updates

| Attribute | Value |
|-----------|-------|
| Method    | `POST` |
| Path      | `/cds/upgrade/1/check/ctx/{context}/key/{contextKey}` |
| Example   | `/cds/upgrade/1/check/ctx/ota/key/23d670d5d06f351` |
| Purpose   | Query whether a firmware update is available for the device |

### 2.2 Fetch download resources

| Attribute | Value |
|-----------|-------|
| Method    | `POST` |
| Path      | `/cds/upgrade/1/resources/t/{trackingId}/ctx/{context}/key/{contextKey}` |
| Example   | `/cds/upgrade/1/resources/t/1-72786D44/ctx/ota/key/23d670d5d06f351` |
| Purpose   | Obtain time-limited download URLs for a known update |

### 2.3 Report state

| Attribute | Value |
|-----------|-------|
| Method    | `POST` |
| Path      | `/cds/upgrade/1/state/ctx/{context}/key/{contextKey}` |
| Purpose   | Report device state (downloaded, installed, etc.) |

---

## 3. URL Path Variables

| Variable       | Value (evidence)     | Source |
|----------------|----------------------|--------|
| `context`      | `ota`                | CDSUtils.smali |
| `contextKey`   | `23d670d5d06f351`    | otaSourceSha1 from BuildPropReader.smali / log |
| `trackingId`   | `1-72786D44…`        | Returned in check response |

---

## 4. Request Headers

| Header         | Value                  | Evidence |
|----------------|------------------------|----------|
| Content-Type   | `application/json`     | CDSUtils.smali |
| Accept         | `application/json`     | Inferred from JSON request/response cycle |

No custom authentication headers observed. The server identifies the device
by the `contextKey` (otaSourceSha1) in the URL path and the `identityInfo`
in the request body.

---

## 5. Check Request Body Schema

```json
{
  "id": "<UUID string>",
  "contentTimestamp": 0,
  "deviceInfo": {
    "manufacturer": "motorola",
    "hardware": "lamu",
    "brand": "motorola",
    "model": "moto g05",
    "product": "lamul_g",
    "os": "Android",
    "osVersion": "15",
    "country": "MX",
    "region": "MX",
    "language": "es",
    "userLanguage": "es_MX"
  },
  "extraInfo": {
    "clientIdentity": "motorola-ota-client-app",
    "carrier": "",
    "bootloaderVersion": "",
    "brand": "motorola",
    "model": "moto g05",
    "fingerprint": "motorola/lamul_g/lamul:15/VVTA35.51-28-15/bd4d30:user/release-keys",
    "radioVersion": "",
    "buildTags": "release-keys",
    "buildType": "user",
    "buildDevice": "lamul",
    "buildId": "VVTA35.51-28-15",
    "buildDisplayId": "VVTA35.51-28-15",
    "buildIncrementalVersion": "",
    "releaseVersion": "15",
    "otaSourceSha1": "23d670d5d06f351",
    "network": "wifi",
    "apkVersion": 3500094,
    "provisionedTime": 0,
    "incrementalVersion": 0,
    "additionalInfo": "",
    "userLocation": "Non-CN",
    "bootloaderStatus": "locked",
    "deviceRooted": "false",
    "is4GBRam": false,
    "deviceChipset": ""
  },
  "identityInfo": {
    "serialNumber": "DEVICE_SERIAL"
  },
  "triggeredBy": "user",
  "idType": "serialNumber"
}
```

**Evidence**: Reconstructed from BuildPropReader.smali, CDSUtils.smali,
and captured request logs.

---

## 6. Check Response Body Schema (update available)

```json
{
  "proceed": true,
  "context": "ota",
  "contextKey": "23d670d5d06f351",
  "content": {
    "packageID": "delta-Ota_Version_lamu_g_VVTA35.51-28-15_bd4d30-VVTA35.51-65-5_b608f4_release-keys.zip.e779db4c45f48461d4de52e569522e43",
    "size": "354981143",
    "md5_checksum": "e779db4c45f48461d4de52e569522e43",
    "flavour": "VVTA35.51-28-15",
    "minVersion": "VVTA35.51-28-15",
    "version": "VVTA35.51-65-5",
    "model": "moto g15",
    "otaSourceSha1": "23d670d5d06f351",
    "otaTargetSha1": "a363e2a67728d8a",
    "displayVersion": "VVTA35.51-65-5",
    "sourceDisplayVersion": "VVTA35.51-28-15",
    "updateType": "MR",
    "abInstallType": "streamingOnAb",
    "releaseNotes": "..."
  },
  "contentResources": [
    {
      "url": "https://dlmgr.gtm.svcmot.com/dl/dlws/1/download/...",
      "headers": null,
      "tags": ["WIFI", "DLMGR_AGENT"],
      "urlTtlSeconds": 600
    }
  ],
  "trackingId": "1-72786D44...",
  "reportingTags": "TRIGGER-USER",
  "pollAfterSeconds": 86400,
  "smartUpdateBitmap": 7,
  "uploadFailureLogs": false
}
```

**Evidence**: Captured server response for lamu_g VVTA35.51-28-15 → VVTA35.51-65-5.

### Notable fields

| Field              | Type   | Notes |
|--------------------|--------|-------|
| `size`             | string | Server returns as string; parse to int |
| `md5_checksum`     | string | MD5 hex digest of the OTA ZIP |
| `urlTtlSeconds`    | int    | Download URL valid for 600 s (10 min) |
| `pollAfterSeconds` | int    | 86400 s = 24 h between checks |
| `abInstallType`    | string | `streamingOnAb` = A/B seamless update |

---

## 7. Authentication Mechanism

No bearer tokens, API keys, or OAuth flows were observed. Authentication
is implicit via:

1. The `contextKey` (otaSourceSha1) in the URL — identifies the firmware build.
2. The `identityInfo.serialNumber` in the request body — identifies the device.
3. The `extraInfo.clientIdentity` value `"motorola-ota-client-app"` — identifies
   the client application.

**Evidence**: CDSUtils.smali shows no Authorization header construction.
All captured requests contain only `Content-Type` as a custom header.

---

## 8. Dynamic Value Computation

### 8.1 Request ID

A UUID v4 string generated per request. No cryptographic derivation observed.

### 8.2 contentTimestamp

- Initial check: `0`
- Resources request: timestamp from the check response (epoch milliseconds)

### 8.3 contextKey (otaSourceSha1)

A truncated SHA-1 hash of the device's current firmware build fingerprint.
Read from `ro.build.thumbprint` via BuildPropReader.smali.

---

## 9. HTTP Configuration

| Parameter       | Value           | Evidence |
|-----------------|-----------------|----------|
| Timeout         | 60 seconds      | smali constants |
| Retry delays    | 5 s, 15 s, 30 s | smali constants |
| Tag             | `"OTA"`         | smali logging tag |

---

## 10. Download Infrastructure

Firmware files are hosted on a separate CDN:

| Field    | Value |
|----------|-------|
| Hostname | `dlmgr.gtm.svcmot.com` |
| Protocol | HTTPS |
| Method   | GET (streaming) |
| Path     | `/dl/dlws/1/download/…` |

Download URLs are time-limited (TTL = 600 seconds) and returned in the
`contentResources` array of the check response.
