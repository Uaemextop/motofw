"""Streaming firmware downloader with MD5 checksum verification.

Downloads OTA packages from the URLs provided in
:class:`~motofw.models.ContentResource` entries, writing them to disk
with :mod:`pathlib` and verifying the file hash with :mod:`hashlib`.
"""

from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import Optional

from motofw.client import OTAClient
from motofw.config import Config
from motofw.models import CheckResponse

logger = logging.getLogger(__name__)

# Maximum sane filename length (most filesystems cap at 255).
_MAX_FILENAME_LEN = 200

# Characters allowed in sanitised filenames.
_SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._\-]")


class ChecksumMismatchError(Exception):
    """Raised when the downloaded file's MD5 does not match the expected value."""


def sanitize_filename(raw: str) -> str:
    """Sanitise a server-supplied filename for safe local storage.

    - Strips directory traversal components.
    - Replaces unsafe characters with ``_``.
    - Truncates to :data:`_MAX_FILENAME_LEN` characters.

    Parameters
    ----------
    raw:
        The original filename string (e.g. from ``packageID``).

    Returns
    -------
    str
        A filesystem-safe filename.
    """
    # Remove any directory components.
    name = Path(raw).name
    # Replace unsafe chars.
    name = _SAFE_FILENAME_RE.sub("_", name)
    # Collapse consecutive underscores.
    name = re.sub(r"_+", "_", name).strip("_")
    # Truncate.
    if len(name) > _MAX_FILENAME_LEN:
        name = name[:_MAX_FILENAME_LEN]
    return name or "firmware.zip"


def _derive_filename(response: CheckResponse) -> str:
    """Derive a safe filename from the check response's ``packageID``.

    Parameters
    ----------
    response:
        Parsed check response containing content metadata.

    Returns
    -------
    str
        Sanitised filename.
    """
    if response.content and response.content.package_id:
        return sanitize_filename(response.content.package_id)
    return "firmware.zip"


def verify_md5(file_path: Path, expected_md5: str) -> None:
    """Verify that *file_path*'s MD5 matches *expected_md5*.

    Parameters
    ----------
    file_path:
        Path to the downloaded file.
    expected_md5:
        Hex-encoded MD5 string from the server response.

    Raises
    ------
    ChecksumMismatchError
        When the computed hash does not match.
    """
    md5 = hashlib.md5()
    with file_path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            md5.update(chunk)
    actual = md5.hexdigest()
    if actual != expected_md5:
        raise ChecksumMismatchError(
            f"MD5 mismatch for {file_path.name}: "
            f"expected={expected_md5} actual={actual}"
        )
    logger.info("MD5 verified OK for %s (%s)", file_path.name, actual)


def download_update(
    cfg: Config,
    response: CheckResponse,
    *,
    client: Optional[OTAClient] = None,
    output_dir: Optional[Path] = None,
) -> Path:
    """Stream-download the firmware OTA package and verify its checksum.

    The download URL is taken from the first entry in
    ``response.content_resources``.  The file is saved into *output_dir*
    (defaulting to ``cfg.output_dir``).

    Parameters
    ----------
    cfg:
        Parsed motofw configuration.
    response:
        A :class:`CheckResponse` that has ``proceed=True`` and at least
        one content resource URL.
    client:
        Optional shared :class:`OTAClient`.
    output_dir:
        Override for the output directory.

    Returns
    -------
    Path
        Absolute path to the downloaded file.

    Raises
    ------
    ValueError
        If the response contains no download URL.
    ChecksumMismatchError
        If the MD5 of the downloaded file does not match.
    """
    if not response.content_resources:
        raise ValueError("CheckResponse contains no download resources")

    download_url = response.content_resources[0].url
    if not download_url:
        raise ValueError("First content resource has an empty URL")

    dest_dir = Path(output_dir or cfg.output_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    filename = _derive_filename(response)
    dest_path = dest_dir / filename

    logger.info("Downloading %s → %s", download_url, dest_path)

    own_client = client is None
    if own_client:
        client = OTAClient(cfg)

    try:
        resp = client.stream_get(download_url)
        try:
            total = int(resp.headers.get("content-length", 0))
            downloaded = 0
            md5 = hashlib.md5()

            with dest_path.open("wb") as fh:
                for chunk in resp.iter_bytes(chunk_size=65536):
                    fh.write(chunk)
                    md5.update(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = downloaded * 100 / total
                        logger.debug("Progress: %.1f%% (%d / %d)", pct, downloaded, total)
        finally:
            resp.close()

        logger.info(
            "Download complete: %s (%d bytes)", dest_path.name, downloaded
        )

        # Checksum verification
        if cfg.verify_checksum and response.content and response.content.md5_checksum:
            actual_md5 = md5.hexdigest()
            expected_md5 = response.content.md5_checksum
            if actual_md5 != expected_md5:
                raise ChecksumMismatchError(
                    f"MD5 mismatch for {dest_path.name}: "
                    f"expected={expected_md5} actual={actual_md5}"
                )
            logger.info("MD5 verified OK: %s", actual_md5)

        return dest_path.resolve()

    finally:
        if own_client:
            assert client is not None
            client.close()
