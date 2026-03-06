"""Firmware downloader with streaming and checksum verification.

Downloads OTA packages from the URLs provided in the server response,
verifying the MD5 checksum after each download.
"""

from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import Optional

from motofw.client import OTAClient
from motofw.response_parser import OTAResponse, get_download_url

logger = logging.getLogger(__name__)

# Chunk size for streaming downloads (1 MiB).
_CHUNK_SIZE = 1024 * 1024


class ChecksumMismatchError(Exception):
    """Raised when a downloaded file's checksum does not match."""


def download_firmware(
    client: OTAClient,
    response: OTAResponse,
    output_dir: Path,
    *,
    expected_md5: Optional[str] = None,
    prefer_wifi: bool = True,
) -> Path:
    """Download the OTA firmware package.

    Parameters
    ----------
    client:
        The shared HTTP client.
    response:
        A parsed OTA response containing download URLs.
    output_dir:
        Directory where the file will be saved.
    expected_md5:
        Expected MD5 hex digest.  When provided, the download is verified.
        If it is not provided, the value is read from
        ``response.content["md5_checksum"]`` if available.
    prefer_wifi:
        Prefer the WIFI-tagged download URL.

    Returns
    -------
    Path
        The path to the downloaded file.

    Raises
    ------
    ValueError
        If no download URL is available.
    ChecksumMismatchError
        If the checksum verification fails.
    """
    url = get_download_url(response, prefer_wifi=prefer_wifi)
    if not url:
        raise ValueError("No download URL found in the OTA response")

    # Determine expected MD5 from response content when not explicitly given.
    if expected_md5 is None and response.content:
        expected_md5 = response.content.get("md5_checksum")

    output_dir.mkdir(parents=True, exist_ok=True)
    filename = _sanitize_filename(_extract_filename(url, response))
    dest = output_dir / filename

    logger.info("Downloading firmware to %s", dest)

    resp = client.get(url, stream=True)

    md5 = hashlib.md5()  # noqa: S324
    total_bytes = 0

    with dest.open("wb") as fh:
        for chunk in resp.iter_content(chunk_size=_CHUNK_SIZE):
            if chunk:
                fh.write(chunk)
                md5.update(chunk)
                total_bytes += len(chunk)

    logger.info("Downloaded %d bytes to %s", total_bytes, dest)

    # Verify checksum.
    if expected_md5:
        actual_md5 = md5.hexdigest()
        if actual_md5.lower() != expected_md5.lower():
            raise ChecksumMismatchError(
                f"MD5 mismatch for {dest}: "
                f"expected {expected_md5}, got {actual_md5}"
            )
        logger.info("Checksum verified: %s", actual_md5)
    else:
        logger.warning("No expected MD5 — skipping checksum verification")

    return dest


def _extract_filename(url: str, response: OTAResponse) -> str:
    """Derive a sensible filename from the URL or response metadata.

    Parameters
    ----------
    url:
        The download URL.
    response:
        The OTA response (may contain a ``packageID`` in ``content``).

    Returns
    -------
    str
        Filename string.
    """
    if response.content:
        package_id = response.content.get("packageID", "")
        if package_id:
            return package_id

    # Fall back: use the last path segment of the URL.
    from urllib.parse import unquote, urlparse

    path = urlparse(url).path
    name = unquote(path.rsplit("/", 1)[-1]) if "/" in path else "firmware.zip"
    return name or "firmware.zip"


def _sanitize_filename(name: str) -> str:
    """Remove or replace characters that are unsafe in filenames.

    Parameters
    ----------
    name:
        Raw filename string.

    Returns
    -------
    str
        Sanitised filename safe for writing to disk.
    """
    # Remove path separators and null bytes.
    name = name.replace("/", "_").replace("\\", "_").replace("\x00", "")
    # Keep only safe characters.
    name = re.sub(r"[^\w\.\-]", "_", name)
    # Collapse runs of underscores.
    name = re.sub(r"_+", "_", name).strip("_")
    return name or "firmware.zip"
