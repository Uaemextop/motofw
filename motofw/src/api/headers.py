"""Construct HTTP headers for OTA API requests.

Evidence from smali analysis:
- API calls (check/resources/state): Volley JsonObjectRequest sets
  Content-Type and Accept to application/json implicitly.
- Download calls: AdvancedFileDownloader sets Accept-Encoding: identity
  and Connection: close, plus any custom server-provided headers.
"""

from __future__ import annotations

from typing import Dict, Optional

DEFAULT_HEADERS: Dict[str, str] = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

DOWNLOAD_HEADERS: Dict[str, str] = {
    "Accept-Encoding": "identity",
    "Connection": "close",
}


def build_headers(extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """Return merged headers for an OTA API request."""
    merged = dict(DEFAULT_HEADERS)
    if extra:
        merged.update(extra)
    return merged


def build_download_headers(
    extra: Optional[Dict[str, str]] = None,
    *,
    offset: int = 0,
    etag: Optional[str] = None,
) -> Dict[str, str]:
    """Return headers for a firmware download (GET).

    Parameters
    ----------
    extra:
        Server-provided custom headers (from wifiHeaders/cellHeaders).
    offset:
        Resume offset in bytes.  When > 0 a ``Range`` header is added.
    etag:
        ETag from a previous partial response.  When set together with
        *offset* an ``If-Match`` header is added.
    """
    merged = dict(DOWNLOAD_HEADERS)
    if extra:
        merged.update(extra)
    if offset > 0:
        merged["Range"] = f"bytes={offset}-"
        if etag:
            merged["If-Match"] = etag
    return merged
