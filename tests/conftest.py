"""Shared fixtures for motofw tests.

Every literal value originates from captured log evidence for the
Motorola lamu_g (moto g05) device.
"""

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Any, Dict

import pytest

from motofw.src.config.settings import Config, load_config
from motofw.src.utils.models import CheckResponse, ContentInfo, ContentResource

# ── Evidence constants ────────────────────────────────────────────────────

E_SERVER_URL = "moto-cds.appspot.com"
E_CHECK_PATH = "cds/upgrade/1/check"
E_RESOURCES_PATH = "cds/upgrade/1/resources"
E_STATE_PATH = "cds/upgrade/1/state"
E_CONTEXT = "ota"
E_TIMEOUT = 60
E_RETRY_DELAYS = [5000, 15000, 30000]
E_CLIENT_IDENTITY = "motorola-ota-client-app"
E_ID_TYPE = "serialNumber"
E_MANUFACTURER = "motorola"
E_HARDWARE = "lamu"
E_BRAND = "motorola"
E_MODEL = "moto g05"
E_PRODUCT = "lamul_g"
E_OS = "Android"
E_OS_VERSION = "15"
E_COUNTRY = "MX"
E_REGION = "MX"
E_LANGUAGE = "es"
E_USER_LANGUAGE = "es_MX"
E_BUILD_ID = "VVTA35.51-28-15"
E_BUILD_DISPLAY_ID = "VVTA35.51-28-15"
E_BUILD_DEVICE = "lamul"
E_BUILD_TYPE = "user"
E_BUILD_TAGS = "release-keys"
E_FINGERPRINT = "motorola/lamul_g/lamul:15/VVTA35.51-28-15/bd4d30:user/release-keys"
E_RELEASE_VERSION = "15"
E_OTA_SHA1 = "23d670d5d06f351"
E_NETWORK = "wifi"
E_APK_VERSION = 3500094
E_USER_LOCATION = "Non-CN"
E_BOOTLOADER_STATUS = "locked"
E_SERIAL = "ZY32LNRW97"
E_IMEI = "359488357396203"

E_PACKAGE_ID = (
    "delta-Ota_Version_lamu_g_VVTA35.51-28-15_bd4d30-"
    "VVTA35.51-65-5_b608f4_release-keys.zip."
    "e779db4c45f48461d4de52e569522e43"
)
E_SIZE = 354981143
E_MD5 = "e779db4c45f48461d4de52e569522e43"
E_FLAVOUR = "VVTA35.51-28-15"
E_MIN_VERSION = "VVTA35.51-28-15"
E_VERSION = "VVTA35.51-65-5"
E_RESPONSE_MODEL = "moto g15"
E_OTA_TARGET_SHA1 = "a363e2a67728d8a"
E_DISPLAY_VERSION = "VVTA35.51-65-5"
E_SOURCE_DISPLAY_VERSION = "VVTA35.51-28-15"
E_UPDATE_TYPE = "MR"
E_AB_INSTALL = "streamingOnAb"
E_DOWNLOAD_URL = "https://dlmgr.gtm.svcmot.com/dl/dlws/1/download/"
E_URL_TTL = 600
E_TRACKING_ID = "1-72786D44"
E_REPORTING_TAGS = "TRIGGER-USER"
E_POLL_SECONDS = 86400
E_SMART_BITMAP = 7


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture()
def raw_check_response() -> Dict[str, Any]:
    """Exact JSON from the Motorola server for a lamu_g update."""
    return {
        "proceed": True,
        "context": E_CONTEXT,
        "contextKey": E_OTA_SHA1,
        "content": {
            "packageID": E_PACKAGE_ID,
            "size": str(E_SIZE),
            "md5_checksum": E_MD5,
            "flavour": E_FLAVOUR,
            "minVersion": E_MIN_VERSION,
            "version": E_VERSION,
            "model": E_RESPONSE_MODEL,
            "otaSourceSha1": E_OTA_SHA1,
            "otaTargetSha1": E_OTA_TARGET_SHA1,
            "displayVersion": E_DISPLAY_VERSION,
            "sourceDisplayVersion": E_SOURCE_DISPLAY_VERSION,
            "updateType": E_UPDATE_TYPE,
            "abInstallType": E_AB_INSTALL,
            "releaseNotes": "Security update",
        },
        "contentResources": [
            {
                "url": E_DOWNLOAD_URL,
                "headers": None,
                "tags": ["WIFI", "DLMGR_AGENT"],
                "urlTtlSeconds": E_URL_TTL,
            },
        ],
        "trackingId": E_TRACKING_ID,
        "reportingTags": E_REPORTING_TAGS,
        "pollAfterSeconds": E_POLL_SECONDS,
        "smartUpdateBitmap": E_SMART_BITMAP,
        "uploadFailureLogs": False,
    }


@pytest.fixture()
def raw_no_update() -> Dict[str, Any]:
    """Server response when no update is available."""
    return {
        "proceed": False,
        "context": E_CONTEXT,
        "contextKey": E_OTA_SHA1,
        "content": None,
        "contentResources": None,
        "trackingId": "",
        "reportingTags": "",
        "pollAfterSeconds": E_POLL_SECONDS,
        "smartUpdateBitmap": 0,
        "uploadFailureLogs": False,
    }


@pytest.fixture()
def default_config(tmp_path: Path) -> Config:
    """Config with all evidence-based defaults (no INI files)."""
    return load_config(tmp_path / "nonexistent.ini")


@pytest.fixture()
def custom_config(tmp_path: Path) -> Config:
    """Config from a temporary config.ini with evidence values."""
    ini = tmp_path / "config.ini"
    dev = tmp_path / "device.ini"
    ini.write_text(textwrap.dedent(f"""\
        [server]
        url = {E_SERVER_URL}
        check_path = {E_CHECK_PATH}
        timeout = {E_TIMEOUT}
        retry_delays_ms = 5000,15000,30000

        [download]
        output_dir = {tmp_path / "firmware"}
        verify_checksum = true
    """))
    dev.write_text(textwrap.dedent(f"""\
        [device]
        manufacturer = {E_MANUFACTURER}
        hardware = {E_HARDWARE}
        brand = {E_BRAND}
        model = {E_MODEL}
        product = {E_PRODUCT}
        os = {E_OS}
        os_version = {E_OS_VERSION}
        country = {E_COUNTRY}
        region = {E_REGION}
        language = {E_LANGUAGE}
        user_language = {E_USER_LANGUAGE}
        client_identity = {E_CLIENT_IDENTITY}
        fingerprint = {E_FINGERPRINT}
        build_tags = {E_BUILD_TAGS}
        build_type = {E_BUILD_TYPE}
        build_device = {E_BUILD_DEVICE}
        build_id = {E_BUILD_ID}
        build_display_id = {E_BUILD_DISPLAY_ID}
        release_version = {E_RELEASE_VERSION}
        ota_source_sha1 = {E_OTA_SHA1}
        network = {E_NETWORK}
        apk_version = {E_APK_VERSION}
        user_location = {E_USER_LOCATION}
        bootloader_status = {E_BOOTLOADER_STATUS}
        device_rooted = false
        is_4gb_ram = false

        [identity]
        serial_number = {E_SERIAL}
        imei = {E_IMEI}
        id_type = {E_ID_TYPE}
    """))
    return load_config(ini, device_path=dev)


@pytest.fixture()
def parsed_check_response() -> CheckResponse:
    """Pre-built CheckResponse from evidence data."""
    return CheckResponse(
        proceed=True,
        context=E_CONTEXT,
        context_key=E_OTA_SHA1,
        content=ContentInfo(
            package_id=E_PACKAGE_ID,
            size=E_SIZE,
            md5_checksum=E_MD5,
            flavour=E_FLAVOUR,
            min_version=E_MIN_VERSION,
            version=E_VERSION,
            model=E_RESPONSE_MODEL,
            ota_source_sha1=E_OTA_SHA1,
            ota_target_sha1=E_OTA_TARGET_SHA1,
            display_version=E_DISPLAY_VERSION,
            source_display_version=E_SOURCE_DISPLAY_VERSION,
            update_type=E_UPDATE_TYPE,
            ab_install_type=E_AB_INSTALL,
            release_notes="Security update",
        ),
        content_resources=[
            ContentResource(
                url=E_DOWNLOAD_URL,
                headers=None,
                tags=["WIFI", "DLMGR_AGENT"],
                url_ttl_seconds=E_URL_TTL,
            ),
        ],
        tracking_id=E_TRACKING_ID,
        reporting_tags=E_REPORTING_TAGS,
        poll_after_seconds=E_POLL_SECONDS,
        smart_update_bitmap=E_SMART_BITMAP,
    )
