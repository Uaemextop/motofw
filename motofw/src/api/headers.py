"""Construct HTTP headers for OTA API requests.

Evidence from smali analysis:

User-Agent
----------
Android's ``HttpURLConnection`` sends ``System.getProperty("http.agent")``
which produces the standard Dalvik User-Agent string:

    Dalvik/2.1.0 (Linux; U; Android {osVersion}; {model} Build/{buildId})

See ``UEDownloadRequestBuilder.smali:517`` (reads ``http.agent``) and
``LazyHeaders$Builder.smali:63`` (same property).

Content-Type
------------
Volley ``JsonRequest.smali:49`` sets:

    application/json; charset=utf-8

(format string ``"application/json; charset=%s"`` with ``"utf-8"``).

API calls (check/resources/state)
---------------------------------
Volley's ``HurlStack`` iterates request headers via
``setRequestProperty`` (``HurlStack.smali:551``).  ``JsonObjectRequest``
inherits ``JsonRequest.getBodyContentType()`` for Content-Type.

Download calls
--------------
``AdvancedFileDownloader.smali:1259–1276`` sets:
  Accept-Encoding: identity
  Connection: close
  Range: bytes=N-   (resume)
"""

from __future__ import annotations

from typing import Dict, Optional


def build_user_agent(os_version: str, model: str, build_id: str) -> str:
    """Build the Dalvik User-Agent matching the real Android OTA app.

    Format from ``System.getProperty("http.agent")`` on Android::

        Dalvik/2.1.0 (Linux; U; Android 15; moto g05 Build/VVTA35.51-100)

    Source: ``UEDownloadRequestBuilder.smali:517``,
    ``LazyHeaders$Builder.smali:63``.
    """
    return (
        f"Dalvik/2.1.0 (Linux; U; Android {os_version}; "
        f"{model} Build/{build_id})"
    )


# Volley JsonRequest.smali:49  →  "application/json; charset=utf-8"
DEFAULT_HEADERS: Dict[str, str] = {
    "Content-Type": "application/json; charset=utf-8",
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
        ETag from a previous partial response.  Only used when *offset*
        is > 0 — adds an ``If-Match`` header so the server rejects the
        resume if the file changed.
    """
    merged = dict(DOWNLOAD_HEADERS)
    if extra:
        merged.update(extra)
    if offset > 0:
        merged["Range"] = f"bytes={offset}-"
        if etag:
            merged["If-Match"] = etag
    return merged
