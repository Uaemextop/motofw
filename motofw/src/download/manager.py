"""High-level download manager: pick URL → stream → verify checksum."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from motofw.src.api.session import OTASession
from motofw.src.config.settings import Config
from motofw.src.download.checksum import ChecksumMismatchError, verify_md5
from motofw.src.download.filename import sanitize
from motofw.src.download.stream import stream_to_file
from motofw.src.utils.models import CheckResponse

logger = logging.getLogger(__name__)


def download_update(
    cfg: Config,
    response: CheckResponse,
    *,
    session: Optional[OTASession] = None,
    output_dir: Optional[Path] = None,
) -> Path:
    """Download the firmware from *response* and verify its MD5.

    Returns the absolute path to the saved file.

    Raises
    ------
    ValueError
        No download URL available.
    ChecksumMismatchError
        MD5 does not match.
    """
    if not response.content_resources:
        raise ValueError("No download resources in the response")
    url = response.content_resources[0].url
    if not url:
        raise ValueError("First resource has an empty URL")

    dest_dir = Path(output_dir or cfg.output_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    filename = "firmware.zip"
    if response.content and response.content.package_id:
        filename = sanitize(response.content.package_id)
    dest = dest_dir / filename

    logger.info("Downloading %s → %s", url, dest)

    own = session is None
    if own:
        session = OTASession(cfg)
    try:
        http_resp = session.get_stream(url)
        _size, actual_md5 = stream_to_file(http_resp, dest)

        if cfg.verify_checksum and response.content and response.content.md5_checksum:
            expected = response.content.md5_checksum
            if actual_md5 != expected:
                raise ChecksumMismatchError(
                    f"MD5 mismatch: expected={expected} actual={actual_md5}"
                )
            logger.info("MD5 verified: %s", actual_md5)

        return dest.resolve()
    finally:
        if own:
            session.close()
