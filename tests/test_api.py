"""Tests for motofw.src.api (headers, urls, body, response, orchestrator)."""

from typing import Any, Dict

import httpx
import pytest
import respx

from motofw.src.api.body import check_body, resources_body
from motofw.src.api.headers import (
    DEFAULT_HEADERS,
    DOWNLOAD_HEADERS,
    build_download_headers,
    build_headers,
)
from motofw.src.api.orchestrator import check_update
from motofw.src.api.response import parse_check_response, parse_content_resources
from motofw.src.api.urls import check_url, resources_url, state_url
from motofw.src.config.settings import Config

from tests.conftest import E_CONTEXT, E_OTA_SHA1, E_SERVER_URL


class TestHeaders:
    def test_default_content_type(self):
        assert DEFAULT_HEADERS["Content-Type"] == "application/json"

    def test_merge_extra(self):
        h = build_headers({"X-Custom": "val"})
        assert h["X-Custom"] == "val"
        assert h["Content-Type"] == "application/json"

    def test_download_headers_identity(self):
        assert DOWNLOAD_HEADERS["Accept-Encoding"] == "identity"
        assert DOWNLOAD_HEADERS["Connection"] == "close"

    def test_download_headers_with_resume(self):
        h = build_download_headers(offset=1024, etag='"abc"')
        assert h["Range"] == "bytes=1024-"
        assert h["If-Match"] == '"abc"'
        assert h["Accept-Encoding"] == "identity"

    def test_download_headers_no_resume(self):
        h = build_download_headers()
        assert "Range" not in h
        assert "If-Match" not in h


class TestUrls:
    def test_check_url(self, default_config: Config):
        url = check_url(default_config)
        assert "/check/ctx/ota/key/" in url

    def test_resources_url(self, default_config: Config):
        url = resources_url(default_config, "TRK-1")
        assert "/resources/t/TRK-1/ctx/ota/key/" in url

    def test_state_url(self, default_config: Config):
        url = state_url(default_config)
        assert "/state/ctx/ota/key/" in url


class TestBody:
    def test_check_body_structure(self, default_config: Config):
        body = check_body(default_config, request_id="test-1")
        assert body["id"] == "test-1"
        assert body["triggeredBy"] == "user"
        assert "deviceInfo" in body
        assert "extraInfo" in body
        assert "identityInfo" in body

    def test_resources_body_structure(self, default_config: Config):
        body = resources_body(default_config, request_id="test-2")
        assert body["id"] == "test-2"
        assert body["reportingTags"] == "TRIGGER-USER"


class TestResponse:
    def test_parse_update_available(self, raw_check_response: Dict[str, Any]):
        resp = parse_check_response(raw_check_response)
        assert resp.proceed is True
        assert resp.content is not None
        assert resp.content.size == 354981143
        assert resp.content.md5_checksum == "e779db4c45f48461d4de52e569522e43"

    def test_parse_no_update(self, raw_no_update: Dict[str, Any]):
        resp = parse_check_response(raw_no_update)
        assert resp.proceed is False
        assert resp.content is None

    def test_parse_content_resources_none(self):
        assert parse_content_resources(None) == []


class TestOrchestrator:
    @respx.mock
    def test_check_update(self, default_config: Config, raw_no_update: Dict[str, Any]):
        url_pattern = f"https://{E_SERVER_URL}/{default_config.check_path}/ctx/{E_CONTEXT}/key/{default_config.ota_source_sha1}"
        respx.post(url_pattern).respond(json=raw_no_update)
        resp = check_update(default_config)
        assert resp.proceed is False
