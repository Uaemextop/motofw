"""Tests for motofw.src.download (filename, checksum, manager)."""

import hashlib
from pathlib import Path

import pytest

from motofw.src.download.checksum import ChecksumMismatchError, verify_md5
from motofw.src.download.filename import sanitize
from motofw.src.utils.models import CheckResponse, ContentInfo, ContentResource


class TestFilename:
    def test_simple(self):
        assert sanitize("firmware.zip") == "firmware.zip"

    def test_unsafe_chars(self):
        result = sanitize("bad file!@#$.zip")
        assert "!" not in result
        assert result.endswith(".zip")

    def test_directory_traversal(self):
        result = sanitize("../../etc/passwd")
        assert "/" not in result

    def test_empty_becomes_default(self):
        assert sanitize("") == "firmware.zip"

    def test_long_name_truncated(self):
        long = "a" * 300 + ".zip"
        assert len(sanitize(long)) <= 200


class TestChecksum:
    def test_verify_ok(self, tmp_path: Path):
        f = tmp_path / "good.bin"
        f.write_bytes(b"hello world")
        expected = hashlib.md5(b"hello world").hexdigest()
        verify_md5(f, expected)  # should not raise

    def test_verify_mismatch(self, tmp_path: Path):
        f = tmp_path / "bad.bin"
        f.write_bytes(b"data")
        with pytest.raises(ChecksumMismatchError):
            verify_md5(f, "0000000000000000")


class TestDownloadUpdate:
    def test_no_resources_raises(self, default_config):
        resp = CheckResponse(proceed=True, content_resources=[])
        from motofw.src.download.manager import download_update

        with pytest.raises(ValueError, match="No download resources"):
            download_update(default_config, resp)

    def test_empty_url_raises(self, default_config):
        resp = CheckResponse(
            proceed=True,
            content_resources=[ContentResource(url="")],
        )
        from motofw.src.download.manager import download_update

        with pytest.raises(ValueError, match="empty URL"):
            download_update(default_config, resp)
