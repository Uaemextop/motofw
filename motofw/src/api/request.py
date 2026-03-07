"""Low-level HTTP request execution with retry and back-off."""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

import httpx

from motofw.src.api.headers import build_download_headers

logger = logging.getLogger(__name__)


def post_with_retry(
    client: httpx.Client,
    path: str,
    *,
    json_body: Dict[str, Any],
    extra_headers: Optional[Dict[str, str]] = None,
    retry_delays_s: Optional[List[float]] = None,
    label: str = "",
) -> httpx.Response:
    """POST *json_body* to *path* with automatic retries.

    Returns the first successful (2xx) response.  Raises the last
    exception when all attempts are exhausted.
    """
    delays = retry_delays_s or []
    attempts = [0.0, *delays]
    last_exc: BaseException | None = None

    for idx, wait in enumerate(attempts):
        if wait > 0:
            logger.info("Retry %d/%d — waiting %.1f s", idx, len(delays), wait)
            time.sleep(wait)
        try:
            logger.debug("POST %s%s (attempt %d/%d)", label, path, idx + 1, len(attempts))
            resp = client.post(path, json=json_body, headers=extra_headers)
            resp.raise_for_status()
            return resp
        except (httpx.HTTPStatusError, httpx.TransportError) as exc:
            last_exc = exc
            logger.warning("Attempt %d/%d failed: %s", idx + 1, len(attempts), exc)

    assert last_exc is not None
    raise last_exc


def stream_get(
    url: str,
    *,
    timeout: float = 60.0,
    extra_headers: Optional[Dict[str, str]] = None,
    retry_delays_s: Optional[List[float]] = None,
    offset: int = 0,
    etag: Optional[str] = None,
) -> httpx.Response:
    """Streaming GET to an absolute URL with retries.

    Uses the exact download headers extracted from AdvancedFileDownloader:
      Accept-Encoding: identity
      Connection: close
      Range: bytes=N-        (when resuming)
      If-Match: <etag>       (when resuming with known ETag)

    The caller must iterate the stream and close the response.
    """
    dl_headers = build_download_headers(extra_headers, offset=offset, etag=etag)

    delays = retry_delays_s or []
    attempts = [0.0, *delays]
    last_exc: BaseException | None = None

    for idx, wait in enumerate(attempts):
        if wait > 0:
            logger.info("Retry %d/%d (stream) — waiting %.1f s", idx, len(delays), wait)
            time.sleep(wait)
        try:
            logger.debug("GET %s (stream, attempt %d/%d)", url, idx + 1, len(attempts))
            dl_client = httpx.Client(
                timeout=httpx.Timeout(timeout, connect=timeout),
                follow_redirects=True,
            )
            resp = dl_client.send(
                httpx.Request("GET", url, headers=dl_headers),
                stream=True,
            )
            resp.raise_for_status()
            return resp
        except (httpx.HTTPStatusError, httpx.TransportError) as exc:
            last_exc = exc
            logger.warning("Stream attempt %d/%d failed: %s", idx + 1, len(attempts), exc)

    assert last_exc is not None
    raise last_exc
