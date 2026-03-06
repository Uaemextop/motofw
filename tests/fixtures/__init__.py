"""Test fixtures extracted from Motorola OTA release logs.

All values in this module are real values captured from the release logs
in the V1 release of the Uaemextop/motofw repository.

Log sources:
- 06_03-15-00-34_226/recorded_06_03-15-00-34_226.log
- 06_03-15-46-01_099/recorded_06_03-15-46-01_099.log
- 06_03-16-21-06_683/recorded_06_03-16-21-06_683.log

Device info files:
- 06_03-15-00-34_226/device_06_03-15-00-34_226.txt
- 06_03-15-46-01_099/device_06_03-15-46-01_099.txt
- 06_03-16-21-06_683/device_06_03-16-21-06_683.txt
"""

# Device info from device_06_03-15-00-34_226.txt (moto g05 / lamul)
DEVICE_LOG1 = {
    "sdk": 35,
    "product_name": "lamul_g",
    "device_name": "lamul",
    "board_name": "lamu",
    "supported_abis": "arm64-v8a",
    "manufacturer": "motorola",
    "brand": "motorola",
    "model": "moto g05",
}

# Check response with content — from log 1 (06_03-15-00-34_226).
# The first check on this device returned an update with content.
# Source: success response line showing proceed=true with full content.
CHECK_RESPONSE_WITH_CONTENT_LOG1 = {
    "statusCode": 200,
    "payload": {
        "proceed": True,
        "context": "ota",
        "contextKey": "23d670d5d06f351",
        "content": {
            "annoy": "60,60,60,...",
            "installTime": 10,
            "showPreDownloadDialog": True,
            "showDownloadOptions": False,
            "preDownloadNotificationExpiryMins": 1440,
            "preInstallNotificationExpiryMins": 1440,
            "forced": False,
            "wifionly": True,
            "rebootRequired": True,
            "version": "VVTA35.51-65-5",
            "minVersion": "VVTA35.51-28-15",
            "size": "354981143",
            "md5_checksum": "e779db4c45f48461d4de52e569522e43",
            "model": "moto g15",
            "otaSourceSha1": "23d670d5d06f351",
            "otaTargetSha1": "a363e2a67728d8a",
            "sourceBuildTimestamp": 1734008817,
            "targetBuildTimestamp": 1737551015,
            "displayVersion": "VVTA35.51-65-5",
            "sourceDisplayVersion": "VVTA35.51-28-15",
            "abInstallType": "streamingOnAb",
            "updateType": "MR",
            "packageID": "delta-Ota_Version_lamu_g_VVTA35.51-28-15_bd4d30-VVTA35.51-65-5_b608f4_release-keys.zip.e779db4c45f48461d4de52e569522e43",
            "trackingId": "1-72786D44192134EF5F40BBB2ABD32EAFE269306AD68565330823E745FB5F7533069975B0F7B855F43F53C176FFFB0ECF",
        },
        "contentTimestamp": 1734008817000,
        "contentResources": None,
        "trackingId": "1-72786D44192134EF5F40BBB2ABD32EAFE269306AD68565330823E745FB5F7533069975B0F7B855F43F53C176FFFB0ECF",
        "reportingTags": "TRIGGER-USER",
        "pollAfterSeconds": 86400,
        "smartUpdateBitmap": 7,
        "uploadFailureLogs": False,
    },
}

# Check response without content (no update / already up to date).
# Source: log 2 (06_03-15-46-01_099), second check response.
CHECK_RESPONSE_NO_CONTENT_LOG2 = {
    "statusCode": 200,
    "payload": {
        "proceed": True,
        "context": "ota",
        "contextKey": "a363e2a67728d8a",
        "content": None,
        "contentTimestamp": 1744060700000,
        "contentResources": None,
        "trackingId": "1-B58CF7828F2FDDCF50C5C3C5CBC22DF2DDFB3AEE5F35983D1700C623943AF875BE464EFCB1248795F5A7BAD8CD1F9347",
        "reportingTags": "TRIGGER-USER",
        "pollAfterSeconds": 86400,
        "smartUpdateBitmap": -1,
        "uploadFailureLogs": False,
    },
}

# Resources response with download URLs.
# Source: log 1 (06_03-15-00-34_226), third web service response.
RESOURCES_RESPONSE_WITH_URLS_LOG1 = {
    "statusCode": 200,
    "payload": {
        "proceed": True,
        "context": "ota",
        "contextKey": "23d670d5d06f351",
        "content": None,
        "contentTimestamp": 0,
        "contentResources": [
            {
                "url": "https://dlmgr.gtm.svcmot.com/dl/dlws/1/download/YVg4JtcHPkU3EAEJCvs37Inkj9%2FmlRBFuisKgbOUteau%2BT8m0Cnh1ymxGnnmz8wdDiu48puGT44qppEb9Cw0sHs458k%2FUh2%2Ba81wk0E8iZ14l53QvMDMAx%2Fxfncdzc6bMDTBHP6tnspAObybYofNmkFIpTRUoF9emfYJkX7ydTVmuM3qnHD%2FD51YG9feMfLfNn%2FlGoGT71XdQNnF%2FyAtq3SgawshDedgG6Xk6VdjpJI%3D",
                "headers": None,
                "tags": ["WIFI", "DLMGR_AGENT"],
                "urlTtlSeconds": 600,
            },
            {
                "url": "https://dlmgr.gtm.svcmot.com/dl/dlws/1/download/YVg4JtcHPkU3EAEJCvs37Inkj9%2FmlRBFuisKgbOUteau%2BT8m0Cnh1ymxGnnmz8wdDiu48puGT44qppEb9Cw0sHs458k%2FUh2%2Ba81wk0E8iZ14l53QvMDMAx%2Fxfncdzc6bMDTBHP6tnspAObybYofNmkFIpTRUoF9emfYJkX7ydTVmuM3qnHD%2FD51YG9feMfLfNn%2FlGoGT71XdQNnF%2FyAtq3SgawshDedgG6Xk6VdjpJI%3D",
                "headers": None,
                "tags": ["CELL", "DLMGR_AGENT"],
                "urlTtlSeconds": 600,
            },
        ],
        "trackingId": "1-72786D44192134EF5F40BBB2ABD32EAFE269306AD68565330823E745FB5F7533069975B0F7B855F43F53C176FFFB0ECF",
        "reportingTags": "TRIGGER-USER",
        "pollAfterSeconds": 86400,
        "smartUpdateBitmap": -1,
        "uploadFailureLogs": False,
    },
}

# Resources response from log 3 (06_03-16-21-06_683) — different device state.
RESOURCES_RESPONSE_LOG3 = {
    "statusCode": 200,
    "payload": {
        "proceed": True,
        "context": "ota",
        "contextKey": "190325d96009ac5",
        "content": None,
        "contentTimestamp": 0,
        "contentResources": [
            {
                "url": "https://dlmgr.gtm.svcmot.com/dl/dlws/1/download/MdXD%2F9kMTLqfxhiEk75Sm4nkj9%2FmlRBFuisKgbOUteau%2BT8m0Cnh1ymxGnnmz8wdDiu48puGT44qppEb9Cw0sFbNfbJhrP3pCpjt2nmr3vUjzNyRJbWgjXqUcFn%2FwufLQaHA0%2FoR5p%2B577lzylIKLUFIpTRUoF9emfYJkX7ydTW6NK%2Fte3cGfPxnC7lnCs1oYBLb9EASISydo%2Bdhu69Jx8qtB2zBxM7oF4ahSEcbo2c%3D",
                "headers": None,
                "tags": ["WIFI", "DLMGR_AGENT"],
                "urlTtlSeconds": 600,
            },
            {
                "url": "https://dlmgr.gtm.svcmot.com/dl/dlws/1/download/MdXD%2F9kMTLqfxhiEk75Sm4nkj9%2FmlRBFuisKgbOUteau%2BT8m0Cnh1ymxGnnmz8wdDiu48puGT44qppEb9Cw0sFbNfbJhrP3pCpjt2nmr3vUjzNyRJbWgjXqUcFn%2FwufLQaHA0%2FoR5p%2B577lzylIKLUFIpTRUoF9emfYJkX7ydTW6NK%2Fte3cGfPxnC7lnCs1oYBLb9EASISydo%2Bdhu69Jx8qtB2zBxM7oF4ahSEcbo2c%3D",
                "headers": None,
                "tags": ["CELL", "DLMGR_AGENT"],
                "urlTtlSeconds": 600,
            },
        ],
        "trackingId": "1-0F334BC1EA9D9D44288BFF4BB338E23C52E8F9D3D4B7A7CA69B128F8BC84AB40B379AE4191662836366BCA7F81EEC2C1",
        "reportingTags": "TRIGGER-USER",
        "pollAfterSeconds": 86400,
        "smartUpdateBitmap": -1,
        "uploadFailureLogs": False,
    },
}

# Server constants extracted from smali CDSUtils and LibConfigs.
SERVER_CONSTANTS = {
    "SERVER_URL": "moto-cds.appspot.com",
    "CHINA_PRODUCTION_SERVER": "moto-cds.svcmot.cn",
    "CHECK_BASE_URL": "cds/upgrade/1/check",
    "RESOURCES_BASE_URL": "cds/upgrade/1/resources",
    "STATE_BASE_URL": "cds/upgrade/1/state",
    "IDTYPE": "serialNumber",
    "OTA_CONTEXT": "ota",
    "CHECK_HTTP_METHOD": "post",
    "IS_SECURE": "true",
    "BACKOFF_VALUES": "5000,15000,30000",
    "OTA_LIB_VERSION": 200004,  # 0x30d44
    "CLIENT_IDENTITY": "motorola-ota-client-app",
    "DOWNLOAD_BASE_URL": "https://dlmgr.gtm.svcmot.com/dl/dlws/1/download/",
}
