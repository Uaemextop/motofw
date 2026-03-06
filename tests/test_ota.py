"""Tests for motofw.ota high-level operations."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from motofw.config import Config
from motofw.ota import check_update, get_resources, report_state
from tests.fixtures import (
    CHECK_RESPONSE_WITH_CONTENT_LOG1,
    RESOURCES_RESPONSE_WITH_URLS_LOG1,
)


def _make_config(tmp_path: Path) -> Config:
    """Create a Config for OTA tests."""
    ini = tmp_path / "config.ini"
    ini.write_text(
        "[device]\n"
        "serial_number = ZY32LNRW97\n"
        "model_id = lamul_g\n"
        "product = lamul_g\n"
        "internal_name = lamul\n"
        "manufacturer = motorola\n"
        "carrier =\n"
        "color_id = motorola\n"
        "source_version = 1734008817\n"
        "ota_source_sha1 = 23d670d5d06f351\n"
        "is_prc_device = false\n"
        "is_production_device = true\n"
        "triggered_by = user\n"
    )
    return Config(ini)


class TestCheckUpdate:
    """Verify check_update with mocked HTTP."""

    def test_check_update_returns_parsed_response(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.json.return_value = CHECK_RESPONSE_WITH_CONTENT_LOG1
        mock_client.post_json.return_value = mock_resp

        response = check_update(config, mock_client)

        assert response.proceed is True
        assert response.context_key == "23d670d5d06f351"
        assert response.content is not None
        assert response.content["version"] == "VVTA35.51-65-5"
        mock_client.post_json.assert_called_once()


class TestGetResources:
    """Verify get_resources with mocked HTTP."""

    def test_get_resources_returns_download_urls(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        mock_client = MagicMock()

        # Check response first
        check_resp_mock = MagicMock()
        check_resp_mock.json.return_value = CHECK_RESPONSE_WITH_CONTENT_LOG1
        mock_client.post_json.return_value = check_resp_mock

        check_response = check_update(config, mock_client)

        # Resources response
        resources_mock = MagicMock()
        resources_mock.json.return_value = RESOURCES_RESPONSE_WITH_URLS_LOG1
        mock_client.post_json.return_value = resources_mock

        resources_response = get_resources(config, mock_client, check_response)

        assert len(resources_response.content_resources) == 2
        assert "dlmgr.gtm.svcmot.com" in resources_response.content_resources[0].url


class TestReportState:
    """Verify report_state with mocked HTTP."""

    def test_report_state_sends_request(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "statusCode": 200,
            "payload": {
                "proceed": True,
                "context": "ota",
                "contextKey": "23d670d5d06f351",
                "content": None,
                "contentTimestamp": 0,
                "trackingId": "test-tracking-id",
                "reportingTags": "",
                "pollAfterSeconds": 0,
                "smartUpdateBitmap": -1,
                "uploadFailureLogs": False,
            },
        }
        mock_client.post_json.return_value = mock_resp

        response = report_state(
            config,
            mock_client,
            tracking_id="test-tracking-id",
            state="Downloading",
        )

        assert response.proceed is True
        mock_client.post_json.assert_called_once()
