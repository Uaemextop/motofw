"""Tests for motofw.api — OTA check/resources/state (mocked HTTP).

All URLs, headers, and body fields come from evidence.  HTTP calls are
mocked with ``respx``.
"""

from __future__ import annotations

import json
from typing import Any, Dict

import httpx
import pytest
import respx

from motofw.api import check_update, get_resources, report_state
from motofw.client import OTAClient
from motofw.config import Config
from tests.conftest import (
    EVIDENCE_CHECK_PATH,
    EVIDENCE_CONTEXT,
    EVIDENCE_DOWNLOAD_URL,
    EVIDENCE_MD5,
    EVIDENCE_OTA_SOURCE_SHA1,
    EVIDENCE_PACKAGE_ID,
    EVIDENCE_POLL_AFTER_SECONDS,
    EVIDENCE_REPORTING_TAGS,
    EVIDENCE_RESOURCES_PATH,
    EVIDENCE_SERVER_URL,
    EVIDENCE_SIZE,
    EVIDENCE_STATE_PATH,
    EVIDENCE_TRACKING_ID,
    EVIDENCE_VERSION,
)


def _check_url(cfg: Config) -> str:
    """Build the expected absolute URL for the check endpoint."""
    return (
        f"https://{cfg.server_url}/{cfg.check_path}"
        f"/ctx/{cfg.context}/key/{cfg.ota_source_sha1}"
    )


def _resources_url(cfg: Config, tracking_id: str) -> str:
    """Build the expected absolute URL for the resources endpoint."""
    return (
        f"https://{cfg.server_url}/{cfg.resources_path}"
        f"/t/{tracking_id}/ctx/{cfg.context}/key/{cfg.ota_source_sha1}"
    )


def _state_url(cfg: Config) -> str:
    """Build the expected absolute URL for the state endpoint."""
    return (
        f"https://{cfg.server_url}/{cfg.state_path}"
        f"/ctx/{cfg.context}/key/{cfg.ota_source_sha1}"
    )


class TestCheckUpdate:
    """check_update() with mocked HTTP."""

    @respx.mock
    def test_update_available(
        self,
        default_config: Config,
        raw_check_response: Dict[str, Any],
    ) -> None:
        url = _check_url(default_config)
        respx.post(url).mock(
            return_value=httpx.Response(200, json=raw_check_response)
        )

        resp = check_update(default_config, request_id="test-check-1")

        assert resp.proceed is True
        assert resp.content is not None
        assert resp.content.package_id == EVIDENCE_PACKAGE_ID
        assert resp.content.version == EVIDENCE_VERSION
        assert resp.content.md5_checksum == EVIDENCE_MD5
        assert resp.content.size == EVIDENCE_SIZE
        assert resp.tracking_id == EVIDENCE_TRACKING_ID
        assert resp.poll_after_seconds == EVIDENCE_POLL_AFTER_SECONDS

    @respx.mock
    def test_no_update(
        self,
        default_config: Config,
        raw_no_update_response: Dict[str, Any],
    ) -> None:
        url = _check_url(default_config)
        respx.post(url).mock(
            return_value=httpx.Response(200, json=raw_no_update_response)
        )

        resp = check_update(default_config)
        assert resp.proceed is False
        assert resp.content is None

    @respx.mock
    def test_check_url_structure(self, default_config: Config) -> None:
        """Verify the URL contains the exact endpoint path from evidence."""
        url = _check_url(default_config)

        # Verify URL components match evidence
        assert EVIDENCE_SERVER_URL in url
        assert EVIDENCE_CHECK_PATH in url
        assert f"ctx/{EVIDENCE_CONTEXT}" in url
        assert f"key/{EVIDENCE_OTA_SOURCE_SHA1}" in url

        respx.post(url).mock(
            return_value=httpx.Response(
                200, json={"proceed": False, "context": "ota", "contextKey": ""}
            )
        )
        check_update(default_config)

    @respx.mock
    def test_request_body_structure(
        self,
        default_config: Config,
        raw_check_response: Dict[str, Any],
    ) -> None:
        """Verify the POST body has exactly the keys from evidence."""
        url = _check_url(default_config)
        route = respx.post(url).mock(
            return_value=httpx.Response(200, json=raw_check_response)
        )

        check_update(default_config, request_id="struct-test")

        # Inspect what was sent
        sent = json.loads(route.calls.last.request.content)
        assert "id" in sent
        assert "contentTimestamp" in sent
        assert "deviceInfo" in sent
        assert "extraInfo" in sent
        assert "identityInfo" in sent
        assert "triggeredBy" in sent
        assert "idType" in sent

    @respx.mock
    def test_content_type_header(
        self,
        default_config: Config,
        raw_check_response: Dict[str, Any],
    ) -> None:
        url = _check_url(default_config)
        route = respx.post(url).mock(
            return_value=httpx.Response(200, json=raw_check_response)
        )

        check_update(default_config)

        content_type = route.calls.last.request.headers.get("content-type")
        assert content_type == "application/json"


class TestGetResources:
    """get_resources() with mocked HTTP."""

    @respx.mock
    def test_fetch_resources(self, default_config: Config) -> None:
        url = _resources_url(default_config, EVIDENCE_TRACKING_ID)
        mock_resp = {
            "contentResources": [
                {"url": EVIDENCE_DOWNLOAD_URL, "tags": ["WIFI"], "urlTtlSeconds": 600}
            ]
        }
        respx.post(url).mock(
            return_value=httpx.Response(200, json=mock_resp)
        )

        data = get_resources(
            default_config,
            tracking_id=EVIDENCE_TRACKING_ID,
        )
        assert "contentResources" in data

    @respx.mock
    def test_resources_url_structure(self, default_config: Config) -> None:
        url = _resources_url(default_config, EVIDENCE_TRACKING_ID)
        assert EVIDENCE_RESOURCES_PATH in url
        assert f"t/{EVIDENCE_TRACKING_ID}" in url
        assert f"ctx/{EVIDENCE_CONTEXT}" in url
        assert f"key/{EVIDENCE_OTA_SOURCE_SHA1}" in url

        respx.post(url).mock(
            return_value=httpx.Response(200, json={})
        )
        get_resources(default_config, tracking_id=EVIDENCE_TRACKING_ID)


class TestReportState:
    """report_state() with mocked HTTP."""

    @respx.mock
    def test_state_post(self, default_config: Config) -> None:
        url = _state_url(default_config)
        respx.post(url).mock(
            return_value=httpx.Response(200, json={"status": "ok"})
        )

        result = report_state(default_config, state_body={"state": "downloaded"})
        assert result == {"status": "ok"}

    @respx.mock
    def test_state_url_structure(self, default_config: Config) -> None:
        url = _state_url(default_config)
        assert EVIDENCE_STATE_PATH in url
        assert f"ctx/{EVIDENCE_CONTEXT}" in url
        assert f"key/{EVIDENCE_OTA_SOURCE_SHA1}" in url

        respx.post(url).mock(
            return_value=httpx.Response(200, json={})
        )
        report_state(default_config, state_body={})
