"""Tests for motofw.config — configuration loading.

All expected values come from log evidence / smali analysis.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from motofw.config import Config, load_config
from tests.conftest import (
    EVIDENCE_APK_VERSION,
    EVIDENCE_BOOTLOADER_STATUS,
    EVIDENCE_BRAND,
    EVIDENCE_BUILD_DEVICE,
    EVIDENCE_BUILD_DISPLAY_ID,
    EVIDENCE_BUILD_ID,
    EVIDENCE_BUILD_TAGS,
    EVIDENCE_BUILD_TYPE,
    EVIDENCE_CHECK_PATH,
    EVIDENCE_CLIENT_IDENTITY,
    EVIDENCE_CONTEXT,
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
    EVIDENCE_RESOURCES_PATH,
    EVIDENCE_RETRY_DELAYS_MS,
    EVIDENCE_SERIAL_NUMBER,
    EVIDENCE_SERVER_URL,
    EVIDENCE_STATE_PATH,
    EVIDENCE_TIMEOUT,
    EVIDENCE_USER_LANGUAGE,
    EVIDENCE_USER_LOCATION,
)


class TestDefaultConfig:
    """Verify that defaults match evidence-based values."""

    def test_server_url(self, default_config: Config) -> None:
        assert default_config.server_url == EVIDENCE_SERVER_URL

    def test_check_path(self, default_config: Config) -> None:
        assert default_config.check_path == EVIDENCE_CHECK_PATH

    def test_resources_path(self, default_config: Config) -> None:
        assert default_config.resources_path == EVIDENCE_RESOURCES_PATH

    def test_state_path(self, default_config: Config) -> None:
        assert default_config.state_path == EVIDENCE_STATE_PATH

    def test_context(self, default_config: Config) -> None:
        assert default_config.context == EVIDENCE_CONTEXT

    def test_timeout(self, default_config: Config) -> None:
        assert default_config.timeout == EVIDENCE_TIMEOUT

    def test_retry_delays(self, default_config: Config) -> None:
        assert default_config.retry_delays_ms == EVIDENCE_RETRY_DELAYS_MS

    def test_manufacturer(self, default_config: Config) -> None:
        assert default_config.manufacturer == EVIDENCE_MANUFACTURER

    def test_hardware(self, default_config: Config) -> None:
        assert default_config.hardware == EVIDENCE_HARDWARE

    def test_brand(self, default_config: Config) -> None:
        assert default_config.brand == EVIDENCE_BRAND

    def test_model(self, default_config: Config) -> None:
        assert default_config.model == EVIDENCE_MODEL

    def test_product(self, default_config: Config) -> None:
        assert default_config.product == EVIDENCE_PRODUCT

    def test_os(self, default_config: Config) -> None:
        assert default_config.os == EVIDENCE_OS

    def test_os_version(self, default_config: Config) -> None:
        assert default_config.os_version == EVIDENCE_OS_VERSION

    def test_country(self, default_config: Config) -> None:
        assert default_config.country == EVIDENCE_COUNTRY

    def test_region(self, default_config: Config) -> None:
        assert default_config.region == EVIDENCE_REGION

    def test_language(self, default_config: Config) -> None:
        assert default_config.language == EVIDENCE_LANGUAGE

    def test_user_language(self, default_config: Config) -> None:
        assert default_config.user_language == EVIDENCE_USER_LANGUAGE

    def test_client_identity(self, default_config: Config) -> None:
        assert default_config.client_identity == EVIDENCE_CLIENT_IDENTITY

    def test_fingerprint(self, default_config: Config) -> None:
        assert default_config.fingerprint == EVIDENCE_FINGERPRINT

    def test_build_tags(self, default_config: Config) -> None:
        assert default_config.build_tags == EVIDENCE_BUILD_TAGS

    def test_build_type(self, default_config: Config) -> None:
        assert default_config.build_type == EVIDENCE_BUILD_TYPE

    def test_build_device(self, default_config: Config) -> None:
        assert default_config.build_device == EVIDENCE_BUILD_DEVICE

    def test_build_id(self, default_config: Config) -> None:
        assert default_config.build_id == EVIDENCE_BUILD_ID

    def test_build_display_id(self, default_config: Config) -> None:
        assert default_config.build_display_id == EVIDENCE_BUILD_DISPLAY_ID

    def test_release_version(self, default_config: Config) -> None:
        assert default_config.release_version == EVIDENCE_RELEASE_VERSION

    def test_ota_source_sha1(self, default_config: Config) -> None:
        assert default_config.ota_source_sha1 == EVIDENCE_OTA_SOURCE_SHA1

    def test_network(self, default_config: Config) -> None:
        assert default_config.network == EVIDENCE_NETWORK

    def test_apk_version(self, default_config: Config) -> None:
        assert default_config.apk_version == EVIDENCE_APK_VERSION

    def test_user_location(self, default_config: Config) -> None:
        assert default_config.user_location == EVIDENCE_USER_LOCATION

    def test_bootloader_status(self, default_config: Config) -> None:
        assert default_config.bootloader_status == EVIDENCE_BOOTLOADER_STATUS

    def test_serial_number(self, default_config: Config) -> None:
        assert default_config.serial_number == EVIDENCE_SERIAL_NUMBER

    def test_id_type(self, default_config: Config) -> None:
        assert default_config.id_type == EVIDENCE_ID_TYPE

    def test_verify_checksum_default_true(self, default_config: Config) -> None:
        assert default_config.verify_checksum is True


class TestConfigFromFile:
    """Verify loading from an explicit config.ini file."""

    def test_load_from_file(self, custom_config: Config) -> None:
        assert custom_config.server_url == EVIDENCE_SERVER_URL
        assert custom_config.ota_source_sha1 == EVIDENCE_OTA_SOURCE_SHA1

    def test_override_server_url(self, tmp_path: Path) -> None:
        ini = tmp_path / "config.ini"
        ini.write_text("[server]\nurl = custom.example.com\n")
        cfg = load_config(ini)
        assert cfg.server_url == "custom.example.com"

    def test_missing_file_uses_defaults(self, tmp_path: Path) -> None:
        cfg = load_config(tmp_path / "nope.ini")
        assert cfg.server_url == EVIDENCE_SERVER_URL

    def test_config_is_frozen(self, default_config: Config) -> None:
        with pytest.raises(AttributeError):
            default_config.server_url = "x"  # type: ignore[misc]
