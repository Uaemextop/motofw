# Motorola OTA Protocol Findings

This document describes the Motorola OTA (Over-The-Air) update protocol as
extracted from two evidence sources:

1. **Smali source code** — decompiled from `com.motorola.ccc.ota` (MotoOta.apk)
2. **Release logs** — captured HTTP traffic from three log sessions

## Server Infrastructure

### Endpoints

| Endpoint | Path | HTTP Method | Purpose |
|----------|------|-------------|---------|
| Check | `cds/upgrade/1/check` | POST | Check for available firmware updates |
| Resources | `cds/upgrade/1/resources` | POST | Request download URLs for a known update |
| State | `cds/upgrade/1/state` | POST | Report upgrade progress/state |

**Source:** `CDSUtils.smali` fields `CHECK_BASE_URL`, `RESOURCES_BASE_URL`, `STATE_BASE_URL`; `LibConfigs.smali` default values.

### Server Hostnames

| Server | Hostname | Usage |
|--------|----------|-------|
| Production (Global) | `moto-cds.appspot.com` | Default for non-PRC production devices |
| Production (China) | `moto-cds.svcmot.cn` | PRC production devices |
| Staging (Global) | `moto-cds-staging.appspot.com` | Non-production global devices |
| Staging (China) | `ota-cn-sdc.blurdev.com` | Non-production PRC devices |
| Download Manager | `dlmgr.gtm.svcmot.com` | Firmware file downloads |

**Source:** `CDSUtils.smali` (SERVER_URL), `UpgradeUtils.smali` (CHINA_PRODUCTION_SERVER), `CheckUpdateHandler.smali` (`getMasterCloud()` method).

### URL Construction

The check URL is constructed as:

```
https://<server_url>/<base_url>/ctx/<context>/key/<uri_encoded_context_key>
```

Example:
```
https://moto-cds.appspot.com/cds/upgrade/1/check/ctx/ota/key/23d670d5d06f351
```

**Source:** `CheckUrlConstructor.smali` `constructUrl()` method.

## Request Body Schema

### Check Request

```json
{
  "id": "<SHA-1 of contextKey + serialNumber>",
  "contentTimestamp": 0,
  "deviceInfo": {
    "manufacturer": "motorola",
    "model": "<model_id>",
    "product": "<product>",
    "isPRC": false,
    "carrier": "<carrier>",
    "userLanguage": "es_MX"
  },
  "extraInfo": {
    "clientIdentity": "motorola-ota-client-app",
    "brand": "<color_id>",
    "buildDevice": "<internal_name>",
    "otaSourceSha1": "<context_key>",
    "buildId": <source_version_timestamp>,
    "buildDisplayId": "<source_version>_<product>",
    "network": "",
    "provisionedTime": "<provision_time>",
    "colorId": "<color_id>",
    "apkPackageName": "com.motorola.ccc.ota",
    "apkVersion": <version_code>,
    "OtaLibVersion": 200004,
    "mobileModel": "<model_id>"
  },
  "identityInfo": {
    "serialNumber": "<device_serial_number>"
  },
  "triggeredBy": "user",
  "idType": "serialNumber"
}
```

**Source:** `CheckRequestBuilder.smali` (`toJSONObject()`), `CheckUpdateHandler.smali` (`getDeviceInfoAsJsonObject()`, `getExtraInfoAsJsonObject()`, `getIdentityInfoAsJsonObject()`).

### Primary Key Computation

The `id` field is a SHA-1 hash of `contextKey + serialNumber`:

```python
import hashlib
primary_key = hashlib.sha1((context_key + serial_number).encode()).hexdigest()
```

**Source:** `CheckRequestObj.smali` `getPrimaryKey()` method, which calls `PublicUtilityMethods.SHA1Generator()`.

### Constants

| Constant | Value | Source |
|----------|-------|--------|
| `IDTYPE` | `"serialNumber"` | `CDSUtils.smali` |
| `CLIENT_IDENTITY` | `"motorola-ota-client-app"` | `CheckUpdateHandler.smali` `getExtraInfoAsJsonObject()` |
| `OtaLibVersion` | `200004` (0x30d44) | `CheckUpdateHandler.smali` `getExtraInfoAsJsonObject()` |
| `IS_SECURE` | `"true"` | `LibConfigs.smali` `CHECK_FOR_UPGRADE_HTTP_SECURE` |
| `BACKOFF_VALUES` | `"5000,15000,30000"` | `LibConfigs.smali` `BACKOFF_VALUES` |

## Response Schema

### Check Response (update available)

```json
{
  "statusCode": 200,
  "payload": {
    "proceed": true,
    "context": "ota",
    "contextKey": "23d670d5d06f351",
    "content": {
      "version": "VVTA35.51-65-5",
      "minVersion": "VVTA35.51-28-15",
      "size": "354981143",
      "md5_checksum": "e779db4c45f48461d4de52e569522e43",
      "model": "moto g15",
      "otaSourceSha1": "23d670d5d06f351",
      "otaTargetSha1": "a363e2a67728d8a",
      "updateType": "MR",
      "abInstallType": "streamingOnAb",
      "packageID": "delta-Ota_Version_lamu_g_...",
      "displayVersion": "VVTA35.51-65-5",
      "trackingId": "1-72786D44..."
    },
    "contentTimestamp": 1734008817000,
    "contentResources": null,
    "trackingId": "1-72786D44...",
    "reportingTags": "TRIGGER-USER",
    "pollAfterSeconds": 86400,
    "smartUpdateBitmap": 7,
    "uploadFailureLogs": false
  }
}
```

**Source:** Log `06_03-15-00-34_226/recorded_06_03-15-00-34_226.log`, line containing `InternalResponseHandler:onTransact()`.

### Check Response (no update)

```json
{
  "statusCode": 200,
  "payload": {
    "proceed": true,
    "context": "ota",
    "contextKey": "a363e2a67728d8a",
    "content": null,
    "contentTimestamp": 1744060700000,
    "contentResources": null,
    "trackingId": "1-B58CF782...",
    "reportingTags": "TRIGGER-USER",
    "pollAfterSeconds": 86400,
    "smartUpdateBitmap": -1,
    "uploadFailureLogs": false
  }
}
```

**Source:** Log `06_03-15-46-01_099/recorded_06_03-15-46-01_099.log`.

### Resources Response (download URLs)

```json
{
  "statusCode": 200,
  "payload": {
    "proceed": true,
    "context": "ota",
    "contextKey": "23d670d5d06f351",
    "content": null,
    "contentTimestamp": 0,
    "contentResources": [
      {
        "url": "https://dlmgr.gtm.svcmot.com/dl/dlws/1/download/<encoded_path>",
        "headers": null,
        "tags": ["WIFI", "DLMGR_AGENT"],
        "urlTtlSeconds": 600
      },
      {
        "url": "https://dlmgr.gtm.svcmot.com/dl/dlws/1/download/<encoded_path>",
        "headers": null,
        "tags": ["CELL", "DLMGR_AGENT"],
        "urlTtlSeconds": 600
      }
    ],
    "trackingId": "1-72786D44...",
    "reportingTags": "TRIGGER-USER",
    "pollAfterSeconds": 86400,
    "smartUpdateBitmap": -1,
    "uploadFailureLogs": false
  }
}
```

**Source:** Log `06_03-15-00-34_226/recorded_06_03-15-00-34_226.log`, third web service response.

## Communication Flow

The OTA update flow consists of three sequential steps:

1. **Check** → POST to `/cds/upgrade/1/check/ctx/ota/key/<sha1>` with device info
   - Returns update metadata (version, size, checksum) or `content: null` if up to date
2. **Resources** → POST to `/cds/upgrade/1/resources/ctx/ota/key/<sha1>`
   - Returns download URLs (WIFI and CELL variants) with TTL
3. **Download** → GET the firmware from `dlmgr.gtm.svcmot.com`
   - Verify MD5 checksum from step 1
4. **State** → POST to `/cds/upgrade/1/state/ctx/ota/key/<sha1>`
   - Report download/install progress

**Source:** Log sequence analysis across all three log files, correlated with `CheckUpdateHandler.smali` state machine.

## Authentication

The logs show **no explicit authentication headers** for the OTA check/resources endpoints. The device identity is conveyed through:

- The `contextKey` in the URL path (OTA source SHA1)
- The `serialNumber` in the `identityInfo` field of the request body
- The computed `id` field (SHA-1 hash of contextKey + serialNumber)

A separate `argo.svcmot.com` endpoint uses OAuth with an `appid` parameter, but this is for device registration, not OTA checks.

**Source:** Log `06_03-16-21-06_683/recorded_06_03-16-21-06_683.log` shows `argo.svcmot.com` calls; OTA CDS calls show no Authorization header.

## Network Tags

Download resources are tagged with network types:

| Tag | Meaning |
|-----|---------|
| `WIFI` | Available over WiFi connections |
| `CELL` | Available over cellular connections |
| `DLMGR_AGENT` | Uses the download manager agent |

**Source:** `NetworkTags.smali`, log evidence in `contentResources` arrays.
