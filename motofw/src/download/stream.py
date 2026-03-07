"""Stream a firmware file to disk while computing its MD5 on-the-fly."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)


def stream_to_file(
    response: httpx.Response,
    dest: Path,
    *,
    chunk_size: int = 65536,
) -> tuple[int, str]:
    """Write *response* bytes to *dest* and return ``(size, md5_hex)``.

    Parameters
    ----------
    response:
        An open streaming httpx response.
    dest:
        Target file path (parent must exist).
    chunk_size:
        Bytes per iteration.

    Returns
    -------
    tuple[int, str]
        Total bytes written and hex MD5 digest.
    """
    total = int(response.headers.get("content-length", 0))
    downloaded = 0
    md5 = hashlib.md5()

    try:
        with dest.open("wb") as fh:
            for chunk in response.iter_bytes(chunk_size=chunk_size):
                fh.write(chunk)
                md5.update(chunk)
                downloaded += len(chunk)
                if total:
                    logger.debug("%.1f%% (%d/%d)", downloaded * 100 / total, downloaded, total)
    finally:
        response.close()

    logger.info("Wrote %d bytes to %s", downloaded, dest.name)
    return downloaded, md5.hexdigest()
