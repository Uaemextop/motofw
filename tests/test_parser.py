"""Tests for motofw.parser — server response parsing.

All expected values come from captured server responses for lamu_g.
"""

from __future__ import annotations

from typing import Any, Dict

from motofw.parser import (
    parse_check_response,
    parse_content_info,
    parse_content_resource,
    parse_content_resources,
)
from tests.conftest import (
    EVIDENCE_AB_INSTALL_TYPE,
    EVIDENCE_CONTEXT,
    EVIDENCE_DISPLAY_VERSION,
    EVIDENCE_DOWNLOAD_URL,
    EVIDENCE_FLAVOUR,
    EVIDENCE_MD5,
    EVIDENCE_MIN_VERSION,
    EVIDENCE_OTA_SOURCE_SHA1,
    EVIDENCE_OTA_TARGET_SHA1,
    EVIDENCE_PACKAGE_ID,
    EVIDENCE_POLL_AFTER_SECONDS,
    EVIDENCE_REPORTING_TAGS,
    EVIDENCE_RESPONSE_MODEL,
    EVIDENCE_SIZE,
    EVIDENCE_SMART_UPDATE_BITMAP,
    EVIDENCE_SOURCE_DISPLAY_VERSION,
    EVIDENCE_TRACKING_ID,
    EVIDENCE_UPDATE_TYPE,
    EVIDENCE_URL_TTL_SECONDS,
    EVIDENCE_VERSION,
)


class TestParseContentInfo:
    """Parse the 'content' object from a real server response."""

    def test_all_fields(self, raw_check_response: Dict[str, Any]) -> None:
        ci = parse_content_info(raw_check_response["content"])
        assert ci.package_id == EVIDENCE_PACKAGE_ID
        assert ci.size == EVIDENCE_SIZE
        assert ci.md5_checksum == EVIDENCE_MD5
        assert ci.flavour == EVIDENCE_FLAVOUR
        assert ci.min_version == EVIDENCE_MIN_VERSION
        assert ci.version == EVIDENCE_VERSION
        assert ci.model == EVIDENCE_RESPONSE_MODEL
        assert ci.ota_source_sha1 == EVIDENCE_OTA_SOURCE_SHA1
        assert ci.ota_target_sha1 == EVIDENCE_OTA_TARGET_SHA1
        assert ci.display_version == EVIDENCE_DISPLAY_VERSION
        assert ci.source_display_version == EVIDENCE_SOURCE_DISPLAY_VERSION
        assert ci.update_type == EVIDENCE_UPDATE_TYPE
        assert ci.ab_install_type == EVIDENCE_AB_INSTALL_TYPE

    def test_size_is_int(self, raw_check_response: Dict[str, Any]) -> None:
        """Server sends size as a string; parser must convert to int."""
        ci = parse_content_info(raw_check_response["content"])
        assert isinstance(ci.size, int)
        assert ci.size == EVIDENCE_SIZE


class TestParseContentResource:
    """Parse a single contentResources entry."""

    def test_fields(self, raw_check_response: Dict[str, Any]) -> None:
        cr = parse_content_resource(raw_check_response["contentResources"][0])
        assert cr.url == EVIDENCE_DOWNLOAD_URL
        assert cr.headers is None
        assert cr.tags == ["WIFI", "DLMGR_AGENT"]
        assert cr.url_ttl_seconds == EVIDENCE_URL_TTL_SECONDS


class TestParseContentResources:
    """Parse the full contentResources array."""

    def test_list(self, raw_check_response: Dict[str, Any]) -> None:
        resources = parse_content_resources(raw_check_response["contentResources"])
        assert len(resources) == 1
        assert resources[0].url == EVIDENCE_DOWNLOAD_URL

    def test_none_returns_empty(self) -> None:
        assert parse_content_resources(None) == []

    def test_empty_list(self) -> None:
        assert parse_content_resources([]) == []


class TestParseCheckResponse:
    """Parse the complete /check response from evidence."""

    def test_proceed_true(self, raw_check_response: Dict[str, Any]) -> None:
        resp = parse_check_response(raw_check_response)
        assert resp.proceed is True

    def test_context_fields(self, raw_check_response: Dict[str, Any]) -> None:
        resp = parse_check_response(raw_check_response)
        assert resp.context == EVIDENCE_CONTEXT
        assert resp.context_key == EVIDENCE_OTA_SOURCE_SHA1

    def test_content_present(self, raw_check_response: Dict[str, Any]) -> None:
        resp = parse_check_response(raw_check_response)
        assert resp.content is not None
        assert resp.content.package_id == EVIDENCE_PACKAGE_ID
        assert resp.content.md5_checksum == EVIDENCE_MD5

    def test_resources_present(self, raw_check_response: Dict[str, Any]) -> None:
        resp = parse_check_response(raw_check_response)
        assert len(resp.content_resources) == 1
        assert resp.content_resources[0].url == EVIDENCE_DOWNLOAD_URL

    def test_tracking_id(self, raw_check_response: Dict[str, Any]) -> None:
        resp = parse_check_response(raw_check_response)
        assert resp.tracking_id == EVIDENCE_TRACKING_ID

    def test_reporting_tags(self, raw_check_response: Dict[str, Any]) -> None:
        resp = parse_check_response(raw_check_response)
        assert resp.reporting_tags == EVIDENCE_REPORTING_TAGS

    def test_poll_after_seconds(self, raw_check_response: Dict[str, Any]) -> None:
        resp = parse_check_response(raw_check_response)
        assert resp.poll_after_seconds == EVIDENCE_POLL_AFTER_SECONDS

    def test_smart_update_bitmap(self, raw_check_response: Dict[str, Any]) -> None:
        resp = parse_check_response(raw_check_response)
        assert resp.smart_update_bitmap == EVIDENCE_SMART_UPDATE_BITMAP

    def test_no_update_response(
        self, raw_no_update_response: Dict[str, Any]
    ) -> None:
        resp = parse_check_response(raw_no_update_response)
        assert resp.proceed is False
        assert resp.content is None
        assert resp.content_resources == []
