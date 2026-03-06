"""Tests for motofw.config."""

from __future__ import annotations

from pathlib import Path

import pytest

from motofw.config import Config
from tests.fixtures import SERVER_CONSTANTS


class TestConfigDefaults:
    """Verify that built-in defaults match the smali-extracted constants."""

    def test_server_url_matches_smali(self) -> None:
        config = Config()
        assert config.server_url == SERVER_CONSTANTS["SERVER_URL"]

    def test_china_server_url_matches_smali(self) -> None:
        config = Config()
        assert config.china_server_url == SERVER_CONSTANTS["CHINA_PRODUCTION_SERVER"]

    def test_check_base_url_matches_smali(self) -> None:
        config = Config()
        assert config.check_base_url == SERVER_CONSTANTS["CHECK_BASE_URL"]

    def test_resources_base_url_matches_smali(self) -> None:
        config = Config()
        assert config.resources_base_url == SERVER_CONSTANTS["RESOURCES_BASE_URL"]

    def test_state_base_url_matches_smali(self) -> None:
        config = Config()
        assert config.state_base_url == SERVER_CONSTANTS["STATE_BASE_URL"]

    def test_ota_context_matches_smali(self) -> None:
        config = Config()
        assert config.ota_context == SERVER_CONSTANTS["OTA_CONTEXT"]

    def test_is_secure_default(self) -> None:
        config = Config()
        assert config.is_secure is True

    def test_check_http_method_is_post(self) -> None:
        config = Config()
        assert config.check_http_method == "POST"

    def test_backoff_values_match_smali(self) -> None:
        config = Config()
        expected = [int(v) for v in SERVER_CONSTANTS["BACKOFF_VALUES"].split(",")]
        assert config.backoff_values == expected

    def test_max_retries_default(self) -> None:
        config = Config()
        assert config.max_retries == 3

    def test_output_dir_default(self) -> None:
        config = Config()
        assert config.output_dir == Path("output")


class TestConfigFromFile:
    """Verify that config.ini overrides defaults."""

    def test_override_server_url(self, tmp_path: Path) -> None:
        ini = tmp_path / "config.ini"
        ini.write_text("[server]\nserver_url = custom.example.com\n")
        config = Config(ini)
        assert config.server_url == "custom.example.com"

    def test_override_device_fields(self, tmp_path: Path) -> None:
        ini = tmp_path / "config.ini"
        ini.write_text(
            "[device]\n"
            "serial_number = ZY32TESTSERIAL\n"
            "model_id = lamul_g\n"
            "product = lamul_g\n"
            "manufacturer = motorola\n"
        )
        config = Config(ini)
        assert config.serial_number == "ZY32TESTSERIAL"
        assert config.model_id == "lamul_g"
        assert config.product == "lamul_g"
        assert config.manufacturer == "motorola"

    def test_missing_file_uses_defaults(self) -> None:
        config = Config(Path("/nonexistent/config.ini"))
        assert config.server_url == SERVER_CONSTANTS["SERVER_URL"]
