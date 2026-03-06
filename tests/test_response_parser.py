"""Tests for motofw.response_parser."""

from __future__ import annotations

import pytest

from motofw.response_parser import (
    ContentResource,
    OTAResponse,
    get_download_url,
    get_firmware_metadata,
    parse_check_response,
)
from tests.fixtures import (
    CHECK_RESPONSE_NO_CONTENT_LOG2,
    CHECK_RESPONSE_WITH_CONTENT_LOG1,
    RESOURCES_RESPONSE_LOG3,
    RESOURCES_RESPONSE_WITH_URLS_LOG1,
)


class TestParseCheckResponse:
    """Verify response parsing against real log evidence."""

    def test_parse_response_with_content(self) -> None:
        resp = parse_check_response(CHECK_RESPONSE_WITH_CONTENT_LOG1)
        assert resp.proceed is True
        assert resp.context == "ota"
        assert resp.context_key == "23d670d5d06f351"
        assert resp.status_code == 200
        assert resp.tracking_id == "1-72786D44192134EF5F40BBB2ABD32EAFE269306AD68565330823E745FB5F7533069975B0F7B855F43F53C176FFFB0ECF"
        assert resp.reporting_tags == "TRIGGER-USER"
        assert resp.poll_after_seconds == 86400
        assert resp.content is not None
        assert resp.content["version"] == "VVTA35.51-65-5"
        assert resp.content["md5_checksum"] == "e779db4c45f48461d4de52e569522e43"
        assert resp.content["size"] == "354981143"

    def test_parse_response_no_content(self) -> None:
        resp = parse_check_response(CHECK_RESPONSE_NO_CONTENT_LOG2)
        assert resp.proceed is True
        assert resp.context_key == "a363e2a67728d8a"
        assert resp.content is None
        assert resp.content_timestamp == 1744060700000
        assert len(resp.content_resources) == 0

    def test_parse_resources_response(self) -> None:
        resp = parse_check_response(RESOURCES_RESPONSE_WITH_URLS_LOG1)
        assert resp.proceed is True
        assert resp.context_key == "23d670d5d06f351"
        assert len(resp.content_resources) == 2

        wifi_resource = resp.content_resources[0]
        assert "WIFI" in wifi_resource.tags
        assert "DLMGR_AGENT" in wifi_resource.tags
        assert wifi_resource.url_ttl_seconds == 600
        assert "dlmgr.gtm.svcmot.com" in wifi_resource.url

        cell_resource = resp.content_resources[1]
        assert "CELL" in cell_resource.tags

    def test_parse_resources_response_log3(self) -> None:
        resp = parse_check_response(RESOURCES_RESPONSE_LOG3)
        assert resp.context_key == "190325d96009ac5"
        assert len(resp.content_resources) == 2
        assert "dlmgr.gtm.svcmot.com" in resp.content_resources[0].url


class TestGetDownloadUrl:
    """Verify download URL extraction."""

    def test_prefer_wifi(self) -> None:
        resp = parse_check_response(RESOURCES_RESPONSE_WITH_URLS_LOG1)
        url = get_download_url(resp, prefer_wifi=True)
        assert url is not None
        assert "dlmgr.gtm.svcmot.com" in url

    def test_prefer_cell(self) -> None:
        resp = parse_check_response(RESOURCES_RESPONSE_WITH_URLS_LOG1)
        url = get_download_url(resp, prefer_wifi=False)
        assert url is not None

    def test_no_resources(self) -> None:
        resp = parse_check_response(CHECK_RESPONSE_NO_CONTENT_LOG2)
        url = get_download_url(resp)
        assert url is None


class TestGetFirmwareMetadata:
    """Verify firmware metadata extraction."""

    def test_metadata_present(self) -> None:
        resp = parse_check_response(CHECK_RESPONSE_WITH_CONTENT_LOG1)
        meta = get_firmware_metadata(resp)
        assert meta is not None
        assert meta["version"] == "VVTA35.51-65-5"
        assert meta["displayVersion"] == "VVTA35.51-65-5"
        assert meta["updateType"] == "MR"

    def test_metadata_absent(self) -> None:
        resp = parse_check_response(CHECK_RESPONSE_NO_CONTENT_LOG2)
        meta = get_firmware_metadata(resp)
        assert meta is None
