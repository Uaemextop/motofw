"""Tests for motofw.downloader — streaming download + checksum verification.

Uses mocked HTTP calls.  All values from evidence.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest

from motofw.config import Config
from motofw.downloader import (
    ChecksumMismatchError,
    download_update,
    sanitize_filename,
    verify_md5,
)
from motofw.models import CheckResponse, ContentInfo, ContentResource
from tests.conftest import (
    EVIDENCE_DOWNLOAD_URL,
    EVIDENCE_MD5,
    EVIDENCE_PACKAGE_ID,
    EVIDENCE_SIZE,
    EVIDENCE_URL_TTL_SECONDS,
)


# ═══════════════════════════════════════════════════════════════════════════
#  sanitize_filename
# ═══════════════════════════════════════════════════════════════════════════


class TestSanitizeFilename:
    """Verify filename sanitisation against adversarial inputs."""

    def test_normal_filename(self) -> None:
        assert sanitize_filename("firmware.zip") == "firmware.zip"

    def test_evidence_package_id(self) -> None:
        """packageID from evidence should produce a safe filename."""
        result = sanitize_filename(EVIDENCE_PACKAGE_ID)
        assert "/" not in result
        assert ".." not in result
        assert len(result) <= 200

    def test_directory_traversal(self) -> None:
        result = sanitize_filename("../../etc/passwd")
        assert "/" not in result
        assert ".." not in result

    def test_empty_string(self) -> None:
        assert sanitize_filename("") == "firmware.zip"

    def test_only_unsafe_chars(self) -> None:
        assert sanitize_filename("///") == "firmware.zip"

    def test_very_long_name(self) -> None:
        long_name = "a" * 500 + ".zip"
        result = sanitize_filename(long_name)
        assert len(result) <= 200


# ═══════════════════════════════════════════════════════════════════════════
#  verify_md5
# ═══════════════════════════════════════════════════════════════════════════


class TestVerifyMd5:
    """MD5 checksum verification."""

    def test_matching_checksum(self, tmp_path: Path) -> None:
        data = b"test firmware content"
        fpath = tmp_path / "test.zip"
        fpath.write_bytes(data)
        expected = hashlib.md5(data).hexdigest()
        # Should not raise
        verify_md5(fpath, expected)

    def test_mismatched_checksum(self, tmp_path: Path) -> None:
        data = b"test firmware content"
        fpath = tmp_path / "test.zip"
        fpath.write_bytes(data)
        with pytest.raises(ChecksumMismatchError, match="MD5 mismatch"):
            verify_md5(fpath, "0000000000000000000000000000dead")


# ═══════════════════════════════════════════════════════════════════════════
#  download_update
# ═══════════════════════════════════════════════════════════════════════════


def _make_response(content: ContentInfo, url: str) -> CheckResponse:
    """Build a minimal CheckResponse with one download resource."""
    return CheckResponse(
        proceed=True,
        context="ota",
        context_key="23d670d5d06f351",
        content=content,
        content_resources=[
            ContentResource(
                url=url,
                headers=None,
                tags=["WIFI", "DLMGR_AGENT"],
                url_ttl_seconds=EVIDENCE_URL_TTL_SECONDS,
            ),
        ],
        tracking_id="1-72786D44",
        reporting_tags="TRIGGER-USER",
        poll_after_seconds=86400,
        smart_update_bitmap=7,
        upload_failure_logs=False,
    )


class TestDownloadUpdate:
    """download_update() with mocked HTTP stream."""

    def test_successful_download_with_checksum(
        self, default_config: Config, tmp_path: Path
    ) -> None:
        """Download succeeds and MD5 matches."""
        firmware_data = b"fake firmware bytes for testing md5"
        expected_md5 = hashlib.md5(firmware_data).hexdigest()

        content = ContentInfo(
            package_id="test_firmware.zip",
            size=len(firmware_data),
            md5_checksum=expected_md5,
        )
        resp = _make_response(content, EVIDENCE_DOWNLOAD_URL)

        # Mock the stream response
        mock_http_resp = MagicMock(spec=httpx.Response)
        mock_http_resp.headers = {"content-length": str(len(firmware_data))}
        mock_http_resp.iter_bytes.return_value = [firmware_data]
        mock_http_resp.close = MagicMock()

        with patch("motofw.downloader.OTAClient") as MockClient:
            mock_client = MockClient.return_value
            mock_client.stream_get.return_value = mock_http_resp

            result = download_update(
                default_config, resp, client=mock_client, output_dir=tmp_path
            )

        assert result.exists()
        assert result.read_bytes() == firmware_data

    def test_checksum_mismatch_raises(
        self, default_config: Config, tmp_path: Path
    ) -> None:
        """Download raises ChecksumMismatchError on MD5 mismatch."""
        firmware_data = b"good data"
        bad_md5 = "0000000000000000000000000000dead"

        content = ContentInfo(
            package_id="bad_firmware.zip",
            size=len(firmware_data),
            md5_checksum=bad_md5,
        )
        resp = _make_response(content, EVIDENCE_DOWNLOAD_URL)

        mock_http_resp = MagicMock(spec=httpx.Response)
        mock_http_resp.headers = {"content-length": str(len(firmware_data))}
        mock_http_resp.iter_bytes.return_value = [firmware_data]
        mock_http_resp.close = MagicMock()

        with patch("motofw.downloader.OTAClient") as MockClient:
            mock_client = MockClient.return_value
            mock_client.stream_get.return_value = mock_http_resp

            with pytest.raises(ChecksumMismatchError):
                download_update(
                    default_config, resp, client=mock_client, output_dir=tmp_path
                )

    def test_no_resources_raises(
        self, default_config: Config, tmp_path: Path
    ) -> None:
        """Raise ValueError when no download resources are present."""
        resp = CheckResponse(proceed=True, content_resources=[])
        with pytest.raises(ValueError, match="no download resources"):
            download_update(default_config, resp, output_dir=tmp_path)

    def test_empty_url_raises(
        self, default_config: Config, tmp_path: Path
    ) -> None:
        """Raise ValueError when the resource URL is empty."""
        resp = CheckResponse(
            proceed=True,
            content_resources=[ContentResource(url="")],
        )
        with pytest.raises(ValueError, match="empty URL"):
            download_update(default_config, resp, output_dir=tmp_path)
