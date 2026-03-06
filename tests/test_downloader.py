"""Tests for motofw.downloader."""

from __future__ import annotations

import hashlib
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from motofw.downloader import ChecksumMismatchError, _sanitize_filename, download_firmware
from motofw.response_parser import ContentResource, OTAResponse


class TestSanitizeFilename:
    """Verify filename sanitisation."""

    def test_removes_path_separators(self) -> None:
        assert "/" not in _sanitize_filename("a/b/c")
        assert "\\" not in _sanitize_filename("a\\b\\c")

    def test_removes_special_characters(self) -> None:
        result = _sanitize_filename("file<name>.zip")
        assert "<" not in result
        assert ">" not in result

    def test_fallback_on_empty(self) -> None:
        assert _sanitize_filename("") == "firmware.zip"

    def test_real_package_id(self) -> None:
        """PackageID from log evidence should sanitise cleanly."""
        pkg_id = (
            "delta-Ota_Version_lamu_g_VVTA35.51-28-15_bd4d30"
            "-VVTA35.51-65-5_b608f4_release-keys.zip"
            ".e779db4c45f48461d4de52e569522e43"
        )
        result = _sanitize_filename(pkg_id)
        assert result  # non-empty
        assert "/" not in result
        assert "\\" not in result


class TestDownloadFirmware:
    """Verify download + checksum logic with mocked HTTP."""

    def test_successful_download_with_matching_md5(self, tmp_path: Path) -> None:
        content = b"fake firmware content for testing"
        expected_md5 = hashlib.md5(content).hexdigest()  # noqa: S324

        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.iter_content.return_value = [content]
        mock_client.get.return_value = mock_resp

        response = OTAResponse(
            content_resources=[
                ContentResource(
                    url="https://dlmgr.gtm.svcmot.com/dl/test",
                    headers=None,
                    tags=["WIFI"],
                )
            ],
            content={"md5_checksum": expected_md5},
        )

        path = download_firmware(mock_client, response, tmp_path)
        assert path.exists()
        assert path.read_bytes() == content

    def test_checksum_mismatch_raises(self, tmp_path: Path) -> None:
        content = b"fake firmware content"

        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.iter_content.return_value = [content]
        mock_client.get.return_value = mock_resp

        response = OTAResponse(
            content_resources=[
                ContentResource(
                    url="https://dlmgr.gtm.svcmot.com/dl/test",
                    headers=None,
                    tags=["WIFI"],
                )
            ],
            content={"md5_checksum": "0000000000000000000000000000dead"},
        )

        with pytest.raises(ChecksumMismatchError):
            download_firmware(mock_client, response, tmp_path)

    def test_no_download_url_raises(self, tmp_path: Path) -> None:
        mock_client = MagicMock()
        response = OTAResponse()

        with pytest.raises(ValueError, match="No download URL"):
            download_firmware(mock_client, response, tmp_path)
