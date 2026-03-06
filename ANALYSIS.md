# 🔬 Smali Analysis Report

This document details the reverse-engineering analysis of Motorola's CCC OTA app to understand the communication protocol with their update servers.

## Analysis Sources

The analysis was performed on decompiled Smali code from the Motorola CCC OTA APK, located in `source_code/smali/` and `source_code/smali_classes2/`.

## Key Findings

### 1. HTTP Client Architecture

**Framework**: Android Volley + Custom HurlStack

- Main HTTP handler: `CDSHurlStack.smali`
- Uses standard `HttpURLConnection` via Volley
- Support for HTTP proxies
- Configurable timeouts and retries

### 2. API Endpoints

**Production Hosts:**
- Non-PRC: `moto-cds.appspot.com`
- PRC (China): `moto-cds.svcmot.cn`

**Staging Hosts:**
- Non-PRC: `moto-cds-staging.appspot.com`
- PRC (China): `ota-cn-sdc.blurdev.com`

**Main Endpoints:**
- Check Update: `/check` (POST)
- Download Descriptor: `/descriptor` (POST)

### 3. Request Structure

#### Check Update Request

```json
{
  "request": {
    "serialNumber": "device_serial",
    "timestamp": 0,
    "deviceInfo": {
      "manufacturer": "Motorola",
      "model": "device_model",
      "product": "product_name",
      "isPRC": false,
      "carrier": "carrier_info",
      "userLanguage": "locale"
    },
    "extraInfo": {
      "clientIdentity": "motorola-ota-client-app",
      "brand": "color_id",
      "buildDevice": "internal_name",
      "otaSourceSha1": "context_key",
      "buildId": "source_version",
      "buildDisplayId": "version_product",
      "network": "network_type",
      "provisionedTime": timestamp,
      "colorId": "color",
      "apkPackageName": "com.motorola.ccc.ota",
      "apkVersion": version_number,
      "OtaLibVersion": 0x30d44,
      "mobileModel": "Build.MODEL",
      "clientState": "current_state"
    },
    "identityInfo": {
      "serialNumber": "device_serial"
    },
    "upgradeSource": "UPGRADED_VIA_PULL"
  }
}
```

#### Download Descriptor Request

```json
{
  "serialNumber": "device_serial",
  "timestamp": content_timestamp,
  "deviceInfo": { /* same as above */ },
  "extraInfo": { /* same as above */ },
  "identityInfo": { /* same as above */ },
  "fieldName": "serialNumber",
  "reportingTag": "tracking_id"
}
```

### 4. Response Structure

#### Success Response

```json
{
  "proceed": true,
  "trackingId": "unique_tracking_id",
  "contextTimeStamp": 1234567890,
  "contentResponse": {
    "contentResources": [
      {
        "url": "https://download.example.com/update.zip",
        "headers": "Authorization: Bearer token",
        "tags": ["WIFI", "CELL"]
      }
    ]
  }
}
```

### 5. Authentication Mechanism

**No Traditional Auth**: The app doesn't use API keys or OAuth tokens.

**Device Identification**:
1. Serial number is the primary identifier
2. Context key = SHA1(build_id)
3. Primary key = SHA1(context_key + serial_number)

### 6. HTTP Headers

**Standard Headers**:
- `Content-Type: application/json`
- `Accept: application/json`
- `User-Agent: Android/[version]`
- `Connection: Keep-Alive`

**Custom Headers**: Can be specified in response for downloads

### 7. Network Optimization

The server can provide different URLs for different network types:
- **WIFI**: WiFi network downloads
- **CELL**: Cellular network downloads
- **ADMIN_APN**: Enterprise APN downloads

### 8. Retry Mechanism

- Default retries: 3
- Automatic retry on transient failures
- Exponential backoff support

### 9. Proxy Support

Optional HTTP proxy configuration:
- `CDS_HTTP_PROXY_HOST`
- `CDS_HTTP_PROXY_PORT`

### 10. Security Features

1. **HTTPS**: All production traffic over TLS
2. **Checksums**: SHA1 verification for downloads
3. **Device Binding**: Serial + context key combination
4. **Regional Isolation**: Separate endpoints for PRC

## Implementation in Motofw

The `motofw` package replicates this protocol exactly:

### Modules Mapping

| Smali Component | Motofw Module |
|---|---|
| `WebService.smali` | `client.py` |
| `WebRequest.smali` | `client.py` (request building) |
| `CheckRequestObj.smali` | `device_info.py` |
| `WebResponse.smali` | `parser.py` |
| `CDSHurlStack.smali` | `client.py` (session config) |
| `DownloadHelper.smali` | `downloader.py` |

### Request Replication

All request payloads match the exact format used by the official app:

```python
# Device info matching deviceInfo JSON
device_info.to_device_info_dict()

# Extra info matching extraInfo JSON
device_info.to_extra_info_dict()

# Identity info matching identityInfo JSON
device_info.to_identity_info_dict()
```

### Headers Replication

```python
{
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "motofw/0.1.0 (Python; OTA Client)",
    "Connection": "Keep-Alive",
}
```

## Protocol Validation

The implementation was validated against:
1. ✅ Smali code structure and flow
2. ✅ JSON payload formats
3. ✅ HTTP header patterns
4. ✅ Authentication mechanism
5. ✅ Network type handling
6. ✅ Retry logic
7. ✅ Proxy support

## Related Files

Key Smali files analyzed:

```
source_code/smali_classes2/com/motorola/otalib/
├── cdsservice/
│   ├── WebService.smali
│   ├── webdataobjects/
│   │   ├── WebRequest.smali
│   │   ├── WebResponse.smali
│   │   └── WebRequestPayload.smali
│   └── utils/
│       └── CDSHurlStack.smali
├── main/
│   └── checkUpdate/
│       ├── CheckUpdateHandler.smali
│       └── CheckRequestObj.smali
└── downloadservice/
    └── download/
        └── HttpUrlBuilder.smali
```

## Conclusion

The `motofw` implementation provides a faithful reproduction of Motorola's OTA protocol, enabling programmatic access to firmware updates without requiring a physical device.
