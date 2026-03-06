"""Tests for motofw.request_builder."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from motofw.config import Config
from motofw.request_builder import (
    _compute_primary_key,
    _resolve_server,
    build_check_body,
    build_check_url,
    build_resources_url,
    build_state_url,
)
from tests.fixtures import DEVICE_LOG1, SERVER_CONSTANTS


def _make_config(tmp_path: Path, **overrides: str) -> Config:
    """Helper: create a Config with device fields populated."""
    ini = tmp_path / "config.ini"
    sections: dict[str, dict[str, str]] = {
        "device": {
            "serial_number": "ZY32LNRW97",
            "model_id": "lamul_g",
            "product": "lamul_g",
            "internal_name": "lamul",
            "manufacturer": "motorola",
            "carrier": "",
            "color_id": "motorola",
            "source_version": "1734008817",
            "ota_source_sha1": "23d670d5d06f351",
            "is_prc_device": "false",
            "is_production_device": "true",
            "triggered_by": "user",
        },
    }
    for k, v in overrides.items():
        for section in sections.values():
            if k in section:
                section[k] = v
    lines: list[str] = []
    for section_name, kvs in sections.items():
        lines.append(f"[{section_name}]")
        for k, v in kvs.items():
            lines.append(f"{k} = {v}")
    ini.write_text("\n".join(lines))
    return Config(ini)


class TestCheckUrl:
    """Verify check URL construction matches smali CheckUrlConstructor."""

    def test_url_structure(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        url = build_check_url(config)
        assert url.startswith("https://")
        assert SERVER_CONSTANTS["SERVER_URL"] in url
        assert f"/{SERVER_CONSTANTS['CHECK_BASE_URL']}/" in url
        assert "/ctx/ota/" in url
        assert "/key/23d670d5d06f351" in url

    def test_http_scheme_when_not_secure(self, tmp_path: Path) -> None:
        ini = tmp_path / "config.ini"
        ini.write_text(
            "[server]\nis_secure = false\n"
            "[device]\nota_source_sha1 = abc123\n"
        )
        config = Config(ini)
        url = build_check_url(config)
        assert url.startswith("http://")

    def test_resources_url_structure(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        url = build_resources_url(config)
        assert f"/{SERVER_CONSTANTS['RESOURCES_BASE_URL']}/" in url
        assert "/ctx/ota/" in url

    def test_state_url_structure(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        url = build_state_url(config, tracking_id="test-id", state="Downloading")
        assert f"/{SERVER_CONSTANTS['STATE_BASE_URL']}/" in url


class TestResolveServer:
    """Verify server resolution matches smali getMasterCloud()."""

    def test_production_non_prc(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        assert _resolve_server(config) == SERVER_CONSTANTS["SERVER_URL"]

    def test_production_prc(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path, is_prc_device="true")
        assert _resolve_server(config) == SERVER_CONSTANTS["CHINA_PRODUCTION_SERVER"]

    def test_non_production_non_prc(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path, is_production_device="false")
        assert _resolve_server(config) == "moto-cds-staging.appspot.com"

    def test_non_production_prc(self, tmp_path: Path) -> None:
        config = _make_config(
            tmp_path, is_prc_device="true", is_production_device="false"
        )
        assert _resolve_server(config) == "ota-cn-sdc.blurdev.com"


class TestPrimaryKey:
    """Verify primary key computation matches smali getPrimaryKey()."""

    def test_sha1_of_context_key_plus_serial(self) -> None:
        context_key = "23d670d5d06f351"
        serial = "ZY32LNRW97"
        expected = hashlib.sha1(
            (context_key + serial).encode("utf-8")
        ).hexdigest()
        assert _compute_primary_key(context_key, serial) == expected

    def test_empty_inputs(self) -> None:
        assert _compute_primary_key("", "") == ""
        assert _compute_primary_key("abc", "") == ""
        assert _compute_primary_key("", "abc") == ""


class TestCheckBody:
    """Verify check body structure matches smali CheckRequestBuilder."""

    def test_body_has_required_fields(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        body = build_check_body(config)
        assert "id" in body
        assert "contentTimestamp" in body
        assert "deviceInfo" in body
        assert "extraInfo" in body
        assert "identityInfo" in body
        assert "triggeredBy" in body
        assert "idType" in body

    def test_id_type_is_serial_number(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        body = build_check_body(config)
        assert body["idType"] == SERVER_CONSTANTS["IDTYPE"]

    def test_device_info_fields(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        body = build_check_body(config)
        di = body["deviceInfo"]
        assert di["manufacturer"] == DEVICE_LOG1["manufacturer"]
        assert di["model"] == "lamul_g"
        assert di["product"] == "lamul_g"
        assert isinstance(di["isPRC"], bool)
        assert "carrier" in di
        assert "userLanguage" in di

    def test_extra_info_client_identity(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        body = build_check_body(config)
        ei = body["extraInfo"]
        assert ei["clientIdentity"] == SERVER_CONSTANTS["CLIENT_IDENTITY"]
        assert ei["OtaLibVersion"] == SERVER_CONSTANTS["OTA_LIB_VERSION"]

    def test_identity_info_has_serial(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        body = build_check_body(config)
        assert body["identityInfo"]["serialNumber"] == "ZY32LNRW97"

    def test_triggered_by_user(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        body = build_check_body(config)
        assert body["triggeredBy"] == "user"
