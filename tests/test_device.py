"""Tests for motofw.device — device info JSON builder.

All expected values come from log evidence for the lamu_g device.
"""

from __future__ import annotations

from motofw.config import Config
from motofw.device import (
    build_check_request,
    build_device_info,
    build_extra_info,
    build_identity_info,
    build_resources_request,
)
from tests.conftest import (
    EVIDENCE_AB_INSTALL_TYPE,
    EVIDENCE_APK_VERSION,
    EVIDENCE_BOOTLOADER_STATUS,
    EVIDENCE_BRAND,
    EVIDENCE_BUILD_DEVICE,
    EVIDENCE_BUILD_DISPLAY_ID,
    EVIDENCE_BUILD_ID,
    EVIDENCE_BUILD_TAGS,
    EVIDENCE_BUILD_TYPE,
    EVIDENCE_CLIENT_IDENTITY,
    EVIDENCE_COUNTRY,
    EVIDENCE_FINGERPRINT,
    EVIDENCE_HARDWARE,
    EVIDENCE_ID_TYPE,
    EVIDENCE_LANGUAGE,
    EVIDENCE_MANUFACTURER,
    EVIDENCE_MODEL,
    EVIDENCE_NETWORK,
    EVIDENCE_OS,
    EVIDENCE_OS_VERSION,
    EVIDENCE_OTA_SOURCE_SHA1,
    EVIDENCE_PRODUCT,
    EVIDENCE_REGION,
    EVIDENCE_RELEASE_VERSION,
    EVIDENCE_SERIAL_NUMBER,
    EVIDENCE_USER_LANGUAGE,
    EVIDENCE_USER_LOCATION,
)


class TestBuildDeviceInfo:
    """Verify deviceInfo dict matches log evidence."""

    def test_all_fields(self, default_config: Config) -> None:
        di = build_device_info(default_config)
        d = di.to_dict()
        assert d["manufacturer"] == EVIDENCE_MANUFACTURER
        assert d["hardware"] == EVIDENCE_HARDWARE
        assert d["brand"] == EVIDENCE_BRAND
        assert d["model"] == EVIDENCE_MODEL
        assert d["product"] == EVIDENCE_PRODUCT
        assert d["os"] == EVIDENCE_OS
        assert d["osVersion"] == EVIDENCE_OS_VERSION
        assert d["country"] == EVIDENCE_COUNTRY
        assert d["region"] == EVIDENCE_REGION
        assert d["language"] == EVIDENCE_LANGUAGE
        assert d["userLanguage"] == EVIDENCE_USER_LANGUAGE

    def test_camelcase_keys(self, default_config: Config) -> None:
        d = build_device_info(default_config).to_dict()
        # The server expects camelCase — verify no snake_case keys leaked
        assert "os_version" not in d
        assert "user_language" not in d
        assert "osVersion" in d
        assert "userLanguage" in d


class TestBuildExtraInfo:
    """Verify extraInfo dict matches log evidence."""

    def test_identity_fields(self, default_config: Config) -> None:
        ei = build_extra_info(default_config)
        d = ei.to_dict()
        assert d["clientIdentity"] == EVIDENCE_CLIENT_IDENTITY
        assert d["brand"] == EVIDENCE_BRAND
        assert d["model"] == EVIDENCE_MODEL

    def test_build_fields(self, default_config: Config) -> None:
        d = build_extra_info(default_config).to_dict()
        assert d["buildId"] == EVIDENCE_BUILD_ID
        assert d["buildDisplayId"] == EVIDENCE_BUILD_DISPLAY_ID
        assert d["buildDevice"] == EVIDENCE_BUILD_DEVICE
        assert d["buildType"] == EVIDENCE_BUILD_TYPE
        assert d["buildTags"] == EVIDENCE_BUILD_TAGS
        assert d["fingerprint"] == EVIDENCE_FINGERPRINT
        assert d["releaseVersion"] == EVIDENCE_RELEASE_VERSION

    def test_ota_fields(self, default_config: Config) -> None:
        d = build_extra_info(default_config).to_dict()
        assert d["otaSourceSha1"] == EVIDENCE_OTA_SOURCE_SHA1
        assert d["network"] == EVIDENCE_NETWORK
        assert d["apkVersion"] == EVIDENCE_APK_VERSION
        assert d["userLocation"] == EVIDENCE_USER_LOCATION
        assert d["bootloaderStatus"] == EVIDENCE_BOOTLOADER_STATUS
        assert d["deviceRooted"] == "false"
        assert d["is4GBRam"] is False

    def test_no_snake_case_keys(self, default_config: Config) -> None:
        d = build_extra_info(default_config).to_dict()
        for key in d:
            assert "_" not in key or key in ("md5_checksum",), (
                f"Unexpected snake_case key: {key}"
            )


class TestBuildIdentityInfo:
    """Verify identityInfo dict matches log evidence."""

    def test_serial_number(self, default_config: Config) -> None:
        ii = build_identity_info(default_config)
        d = ii.to_dict()
        assert d["serialNumber"] == EVIDENCE_SERIAL_NUMBER


class TestBuildCheckRequest:
    """Verify the full check request body matches log evidence structure."""

    def test_top_level_keys(self, default_config: Config) -> None:
        req = build_check_request(default_config, request_id="test-id-1")
        d = req.to_dict()
        expected_keys = {
            "id", "contentTimestamp", "deviceInfo", "extraInfo",
            "identityInfo", "triggeredBy", "idType",
        }
        assert set(d.keys()) == expected_keys

    def test_id_and_defaults(self, default_config: Config) -> None:
        req = build_check_request(default_config, request_id="test-id-2")
        d = req.to_dict()
        assert d["id"] == "test-id-2"
        assert d["contentTimestamp"] == 0
        assert d["triggeredBy"] == "user"
        assert d["idType"] == EVIDENCE_ID_TYPE

    def test_device_info_nested(self, default_config: Config) -> None:
        req = build_check_request(default_config)
        d = req.to_dict()
        assert d["deviceInfo"]["manufacturer"] == EVIDENCE_MANUFACTURER
        assert d["deviceInfo"]["product"] == EVIDENCE_PRODUCT

    def test_extra_info_nested(self, default_config: Config) -> None:
        req = build_check_request(default_config)
        d = req.to_dict()
        assert d["extraInfo"]["clientIdentity"] == EVIDENCE_CLIENT_IDENTITY
        assert d["extraInfo"]["otaSourceSha1"] == EVIDENCE_OTA_SOURCE_SHA1


class TestBuildResourcesRequest:
    """Verify the resources request body structure."""

    def test_top_level_keys(self, default_config: Config) -> None:
        req = build_resources_request(default_config, request_id="res-id-1")
        d = req.to_dict()
        expected_keys = {
            "id", "contentTimestamp", "deviceInfo", "extraInfo",
            "identityInfo", "idType", "reportingTags", "reason",
        }
        assert set(d.keys()) == expected_keys

    def test_reporting_tags(self, default_config: Config) -> None:
        req = build_resources_request(
            default_config,
            reporting_tags="TRIGGER-USER",
            request_id="res-id-2",
        )
        d = req.to_dict()
        assert d["reportingTags"] == "TRIGGER-USER"
        assert d["reason"] is None
