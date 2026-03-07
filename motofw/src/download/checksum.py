"""MD5 checksum verification."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ChecksumMismatchError(Exception):
    """The downloaded file's MD5 does not match the expected value."""


def verify_md5(file_path: Path, expected: str) -> None:
    """Raise :class:`ChecksumMismatchError` if *file_path*'s MD5 ≠ *expected*."""
    md5 = hashlib.md5()
    with file_path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            md5.update(chunk)
    actual = md5.hexdigest()
    if actual != expected:
        raise ChecksumMismatchError(
            f"MD5 mismatch for {file_path.name}: expected={expected} actual={actual}"
        )
    logger.info("MD5 OK: %s (%s)", file_path.name, actual)
