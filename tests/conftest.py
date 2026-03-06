"""Shared pytest fixtures for motofw tests.

Every literal value in this file originates from captured log evidence
for the Motorola lamu_g (moto g05) device or the smali analysis of the
OTA client APK.  No invented or placeholder data is used.
"""

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Any, Dict

import pytest

from motofw.config import Config, load_config
from motofw.models import (
    CheckResponse,
    ContentInfo,
    ContentResource,
    DeviceInfo,
    ExtraInfo,
    IdentityInfo,
)


# ═══════════════════════════════════════════════════════════════════════════
#  Evidence-based constants (from log records / smali)
# ═══════════════════════════════════════════════════════════════════════════

EVIDENCE_SERVER_URL = "moto-cds.appspot.com"
EVIDENCE_CHECK_PATH = "cds/upgrade/1/check"
EVIDENCE_RESOURCES_PATH = "cds/upgrade/1/resources"
EVIDENCE_STATE_PATH = "cds/upgrade/1/state"
EVIDENCE_CONTEXT = "ota"
EVIDENCE_TIMEOUT = 60
EVIDENCE_RETRY_DELAYS_MS = [5000, 15000, 30000]
EVIDENCE_CLIENT_IDENTITY = "motorola-ota-client-app"
EVIDENCE_ID_TYPE = "serialNumber"

# Device info (log evidence: lamu_g / moto g05)
EVIDENCE_MANUFACTURER = "motorola"
EVIDENCE_HARDWARE = "lamu"
EVIDENCE_BRAND = "motorola"
EVIDENCE_MODEL = "moto g05"
EVIDENCE_PRODUCT = "lamul_g"
EVIDENCE_OS = "Android"
EVIDENCE_OS_VERSION = "15"
EVIDENCE_COUNTRY = "MX"
EVIDENCE_REGION = "MX"
EVIDENCE_LANGUAGE = "es"
EVIDENCE_USER_LANGUAGE = "es_MX"
EVIDENCE_BUILD_ID = "VVTA35.51-28-15"
EVIDENCE_BUILD_DISPLAY_ID = "VVTA35.51-28-15"
EVIDENCE_BUILD_DEVICE = "lamul"
EVIDENCE_BUILD_TYPE = "user"
EVIDENCE_BUILD_TAGS = "release-keys"
EVIDENCE_FINGERPRINT = "motorola/lamul_g/lamul:15/VVTA35.51-28-15/bd4d30:user/release-keys"
EVIDENCE_RELEASE_VERSION = "15"
EVIDENCE_OTA_SOURCE_SHA1 = "23d670d5d06f351"
EVIDENCE_NETWORK = "wifi"
EVIDENCE_APK_VERSION = 3500094
EVIDENCE_USER_LOCATION = "Non-CN"
EVIDENCE_BOOTLOADER_STATUS = "locked"
EVIDENCE_SERIAL_NUMBER = "ZY32LNRW97"
EVIDENCE_IMEI = "359488357396203"

# Check response (log evidence)
EVIDENCE_PACKAGE_ID = (
    "delta-Ota_Version_lamu_g_VVTA35.51-28-15_bd4d30-"
    "VVTA35.51-65-5_b608f4_release-keys.zip."
    "e779db4c45f48461d4de52e569522e43"
)
EVIDENCE_SIZE = 354981143
EVIDENCE_MD5 = "e779db4c45f48461d4de52e569522e43"
EVIDENCE_FLAVOUR = "VVTA35.51-28-15"
EVIDENCE_MIN_VERSION = "VVTA35.51-28-15"
EVIDENCE_VERSION = "VVTA35.51-65-5"
EVIDENCE_RESPONSE_MODEL = "moto g15"
EVIDENCE_OTA_TARGET_SHA1 = "a363e2a67728d8a"
EVIDENCE_DISPLAY_VERSION = "VVTA35.51-65-5"
EVIDENCE_SOURCE_DISPLAY_VERSION = "VVTA35.51-28-15"
EVIDENCE_UPDATE_TYPE = "MR"
EVIDENCE_AB_INSTALL_TYPE = "streamingOnAb"
EVIDENCE_DOWNLOAD_URL = "https://dlmgr.gtm.svcmot.com/dl/dlws/1/download/"
EVIDENCE_URL_TTL_SECONDS = 600
EVIDENCE_TRACKING_ID = "1-72786D44"
EVIDENCE_REPORTING_TAGS = "TRIGGER-USER"
EVIDENCE_POLL_AFTER_SECONDS = 86400
EVIDENCE_SMART_UPDATE_BITMAP = 7


# ═══════════════════════════════════════════════════════════════════════════
#  Fixture: raw server response dict
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture()
def raw_check_response() -> Dict[str, Any]:
    """Return the exact JSON dict captured from the Motorola server for lamu_g."""
    return {
        "proceed": True,
        "context": EVIDENCE_CONTEXT,
        "contextKey": EVIDENCE_OTA_SOURCE_SHA1,
        "content": {
            "packageID": EVIDENCE_PACKAGE_ID,
            "size": str(EVIDENCE_SIZE),
            "md5_checksum": EVIDENCE_MD5,
            "flavour": EVIDENCE_FLAVOUR,
            "minVersion": EVIDENCE_MIN_VERSION,
            "version": EVIDENCE_VERSION,
            "model": EVIDENCE_RESPONSE_MODEL,
            "otaSourceSha1": EVIDENCE_OTA_SOURCE_SHA1,
            "otaTargetSha1": EVIDENCE_OTA_TARGET_SHA1,
            "displayVersion": EVIDENCE_DISPLAY_VERSION,
            "sourceDisplayVersion": EVIDENCE_SOURCE_DISPLAY_VERSION,
            "updateType": EVIDENCE_UPDATE_TYPE,
            "abInstallType": EVIDENCE_AB_INSTALL_TYPE,
            "releaseNotes": "Security update",
        },
        "contentResources": [
            {
                "url": EVIDENCE_DOWNLOAD_URL,
                "headers": None,
                "tags": ["WIFI", "DLMGR_AGENT"],
                "urlTtlSeconds": EVIDENCE_URL_TTL_SECONDS,
            },
        ],
        "trackingId": EVIDENCE_TRACKING_ID,
        "reportingTags": EVIDENCE_REPORTING_TAGS,
        "pollAfterSeconds": EVIDENCE_POLL_AFTER_SECONDS,
        "smartUpdateBitmap": EVIDENCE_SMART_UPDATE_BITMAP,
        "uploadFailureLogs": False,
    }


@pytest.fixture()
def raw_no_update_response() -> Dict[str, Any]:
    """Response when no update is available."""
    return {
        "proceed": False,
        "context": EVIDENCE_CONTEXT,
        "contextKey": EVIDENCE_OTA_SOURCE_SHA1,
        "content": None,
        "contentResources": None,
        "trackingId": "",
        "reportingTags": "",
        "pollAfterSeconds": EVIDENCE_POLL_AFTER_SECONDS,
        "smartUpdateBitmap": 0,
        "uploadFailureLogs": False,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  Fixture: default Config (evidence-based defaults, no config.ini)
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture()
def default_config(tmp_path: Path) -> Config:
    """Config loaded without any config.ini — all evidence-based defaults."""
    # Point to a non-existent path so defaults are used.
    return load_config(tmp_path / "nonexistent.ini")


@pytest.fixture()
def custom_config(tmp_path: Path) -> Config:
    """Config loaded from a temporary config.ini with evidence values."""
    ini = tmp_path / "config.ini"
    ini.write_text(
        textwrap.dedent(f"""\
        [server]
        url = {EVIDENCE_SERVER_URL}
        check_path = {EVIDENCE_CHECK_PATH}
        resources_path = {EVIDENCE_RESOURCES_PATH}
        state_path = {EVIDENCE_STATE_PATH}
        context = {EVIDENCE_CONTEXT}
        timeout = {EVIDENCE_TIMEOUT}
        retry_delays_ms = 5000,15000,30000

        [device]
        manufacturer = {EVIDENCE_MANUFACTURER}
        hardware = {EVIDENCE_HARDWARE}
        brand = {EVIDENCE_BRAND}
        model = {EVIDENCE_MODEL}
        product = {EVIDENCE_PRODUCT}
        os = {EVIDENCE_OS}
        os_version = {EVIDENCE_OS_VERSION}
        country = {EVIDENCE_COUNTRY}
        region = {EVIDENCE_REGION}
        language = {EVIDENCE_LANGUAGE}
        user_language = {EVIDENCE_USER_LANGUAGE}
        client_identity = {EVIDENCE_CLIENT_IDENTITY}
        carrier =
        bootloader_version =
        fingerprint = {EVIDENCE_FINGERPRINT}
        radio_version =
        build_tags = {EVIDENCE_BUILD_TAGS}
        build_type = {EVIDENCE_BUILD_TYPE}
        build_device = {EVIDENCE_BUILD_DEVICE}
        build_id = {EVIDENCE_BUILD_ID}
        build_display_id = {EVIDENCE_BUILD_DISPLAY_ID}
        build_incremental_version =
        release_version = {EVIDENCE_RELEASE_VERSION}
        ota_source_sha1 = {EVIDENCE_OTA_SOURCE_SHA1}
        network = {EVIDENCE_NETWORK}
        apk_version = {EVIDENCE_APK_VERSION}
        provisioned_time = 0
        incremental_version = 0
        additional_info =
        user_location = {EVIDENCE_USER_LOCATION}
        bootloader_status = {EVIDENCE_BOOTLOADER_STATUS}
        device_rooted = false
        is_4gb_ram = false
        device_chipset =
        serial_number = {EVIDENCE_SERIAL_NUMBER}
        imei = {EVIDENCE_IMEI}
        imei2 =
        mccmnc =
        mccmnc2 =

        [identity]
        id_type = {EVIDENCE_ID_TYPE}

        [download]
        output_dir = {tmp_path / "firmware"}
        verify_checksum = true
        """),
    )
    return load_config(ini)


# ═══════════════════════════════════════════════════════════════════════════
#  Fixture: parsed response models
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture()
def parsed_check_response() -> CheckResponse:
    """A CheckResponse built from evidence values (no server call)."""
    return CheckResponse(
        proceed=True,
        context=EVIDENCE_CONTEXT,
        context_key=EVIDENCE_OTA_SOURCE_SHA1,
        content=ContentInfo(
            package_id=EVIDENCE_PACKAGE_ID,
            size=EVIDENCE_SIZE,
            md5_checksum=EVIDENCE_MD5,
            flavour=EVIDENCE_FLAVOUR,
            min_version=EVIDENCE_MIN_VERSION,
            version=EVIDENCE_VERSION,
            model=EVIDENCE_RESPONSE_MODEL,
            ota_source_sha1=EVIDENCE_OTA_SOURCE_SHA1,
            ota_target_sha1=EVIDENCE_OTA_TARGET_SHA1,
            display_version=EVIDENCE_DISPLAY_VERSION,
            source_display_version=EVIDENCE_SOURCE_DISPLAY_VERSION,
            update_type=EVIDENCE_UPDATE_TYPE,
            ab_install_type=EVIDENCE_AB_INSTALL_TYPE,
            release_notes="Security update",
        ),
        content_resources=[
            ContentResource(
                url=EVIDENCE_DOWNLOAD_URL,
                headers=None,
                tags=["WIFI", "DLMGR_AGENT"],
                url_ttl_seconds=EVIDENCE_URL_TTL_SECONDS,
            ),
        ],
        tracking_id=EVIDENCE_TRACKING_ID,
        reporting_tags=EVIDENCE_REPORTING_TAGS,
        poll_after_seconds=EVIDENCE_POLL_AFTER_SECONDS,
        smart_update_bitmap=EVIDENCE_SMART_UPDATE_BITMAP,
        upload_failure_logs=False,
    )
