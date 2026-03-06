"""Tests for motofw.client with mocked HTTP calls."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from motofw.client import OTAClient
from motofw.config import Config


def _make_config(tmp_path: Path) -> Config:
    """Create a minimal Config for client tests."""
    ini = tmp_path / "config.ini"
    ini.write_text(
        "[http]\n"
        "timeout = 5\n"
        "max_retries = 2\n"
        "backoff_values = 10,20,30\n"
        "proxy_host =\n"
        "proxy_port = -1\n"
    )
    return Config(ini)


class TestOTAClient:
    """Verify OTAClient post_json with mocked session."""

    @patch("motofw.client.requests.Session")
    def test_post_json_success(
        self, mock_session_cls: MagicMock, tmp_path: Path
    ) -> None:
        config = _make_config(tmp_path)
        mock_session = mock_session_cls.return_value
        mock_resp = MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_resp

        client = OTAClient(config)
        resp = client.post_json("https://example.com/check", {"key": "value"})

        assert resp.status_code == 200
        mock_session.post.assert_called_once()

    @patch("motofw.client.requests.Session")
    def test_post_json_retry_on_failure(
        self, mock_session_cls: MagicMock, tmp_path: Path
    ) -> None:
        config = _make_config(tmp_path)
        mock_session = mock_session_cls.return_value

        # First call fails, second succeeds.
        fail_resp = MagicMock(spec=requests.Response)
        fail_resp.raise_for_status.side_effect = requests.HTTPError("500")

        ok_resp = MagicMock(spec=requests.Response)
        ok_resp.status_code = 200
        ok_resp.raise_for_status = MagicMock()

        mock_session.post.side_effect = [fail_resp, ok_resp]

        client = OTAClient(config)
        resp = client.post_json("https://example.com/check", {"key": "value"})

        assert resp.status_code == 200
        assert mock_session.post.call_count == 2

    @patch("motofw.client.requests.Session")
    def test_post_json_raises_after_max_retries(
        self, mock_session_cls: MagicMock, tmp_path: Path
    ) -> None:
        config = _make_config(tmp_path)
        mock_session = mock_session_cls.return_value

        fail_resp = MagicMock(spec=requests.Response)
        fail_resp.raise_for_status.side_effect = requests.HTTPError("500")
        mock_session.post.return_value = fail_resp

        client = OTAClient(config)
        with pytest.raises(requests.HTTPError):
            client.post_json("https://example.com/check", {"key": "value"})

        # max_retries=2 means 3 total attempts.
        assert mock_session.post.call_count == 3


class TestOTAClientProxy:
    """Verify proxy configuration."""

    @patch("motofw.client.requests.Session")
    def test_proxy_configured(
        self, mock_session_cls: MagicMock, tmp_path: Path
    ) -> None:
        ini = tmp_path / "config.ini"
        ini.write_text(
            "[http]\n"
            "timeout = 5\n"
            "max_retries = 1\n"
            "backoff_values = 10\n"
            "proxy_host = proxy.example.com\n"
            "proxy_port = 8080\n"
        )
        config = Config(ini)
        mock_session = mock_session_cls.return_value

        OTAClient(config)

        mock_session.proxies.update.assert_called_once_with(
            {
                "http": "http://proxy.example.com:8080",
                "https": "http://proxy.example.com:8080",
            }
        )
