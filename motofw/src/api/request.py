"""Low-level HTTP request execution with retry logic.

Wraps an :class:`httpx.Client` and adds automatic retry with
configurable back-off delays.  Used by :mod:`motofw.src.api.session`.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


def post_with_retry(
    client: httpx.Client,
    path: str,
    *,
    json_body: Dict[str, Any],
    extra_headers: Optional[Dict[str, str]] = None,
    retry_delays_s: Optional[List[float]] = None,
    base_url: str = "",
) -> httpx.Response:
    """Send a POST request with retry + back-off.

    Parameters
    ----------
    client:
        The :class:`httpx.Client` to use.
    path:
        Relative URL path.
    json_body:
        Python dict to send as JSON.
    extra_headers:
        Additional headers merged on top of the client defaults.
    retry_delays_s:
        List of delay durations in seconds between retries.
    base_url:
        For logging purposes only.

    Returns
    -------
    httpx.Response
        The successful response.

    Raises
    ------
    httpx.HTTPStatusError
        If the final attempt still receives a non-2xx status.
    httpx.TransportError
        If the final attempt fails at the transport level.
    """
    delays = retry_delays_s or []
    attempts = [0.0, *delays]
    last_exc: BaseException | None = None

    for attempt_idx, delay in enumerate(attempts):
        if delay > 0:
            logger.info(
                "Retry %d/%d — waiting %.1f s before next attempt",
                attempt_idx, len(delays), delay,
            )
            time.sleep(delay)

        try:
            logger.debug(
                "POST %s%s (attempt %d/%d)",
                base_url, path, attempt_idx + 1, len(attempts),
            )
            response = client.post(path, json=json_body, headers=extra_headers)
            response.raise_for_status()
            logger.debug("Response %d from %s%s", response.status_code, base_url, path)
            return response

        except (httpx.HTTPStatusError, httpx.TransportError) as exc:
            last_exc = exc
            logger.warning(
                "Attempt %d/%d failed for %s: %s",
                attempt_idx + 1, len(attempts), path, exc,
            )

    assert last_exc is not None
    raise last_exc


def stream_get_with_retry(
    url: str,
    *,
    timeout: float = 60.0,
    extra_headers: Optional[Dict[str, str]] = None,
    retry_delays_s: Optional[List[float]] = None,
) -> httpx.Response:
    """Start a streaming GET to an absolute URL with retry.

    The caller is responsible for iterating and closing the response.

    Parameters
    ----------
    url:
        Absolute URL (e.g. ``https://dlmgr.gtm.svcmot.com/…``).
    timeout:
        Request timeout in seconds.
    extra_headers:
        Optional additional headers.
    retry_delays_s:
        List of delay durations in seconds between retries.

    Returns
    -------
    httpx.Response
        A response with an open byte stream.
    """
    delays = retry_delays_s or []
    attempts = [0.0, *delays]
    last_exc: BaseException | None = None

    for attempt_idx, delay in enumerate(attempts):
        if delay > 0:
            logger.info(
                "Retry %d/%d (stream_get) — waiting %.1f s",
                attempt_idx, len(delays), delay,
            )
            time.sleep(delay)

        try:
            logger.debug("GET %s (stream, attempt %d/%d)", url, attempt_idx + 1, len(attempts))
            dl_client = httpx.Client(
                timeout=httpx.Timeout(timeout, connect=timeout),
                follow_redirects=True,
            )
            response = dl_client.send(
                httpx.Request("GET", url, headers=extra_headers),
                stream=True,
            )
            response.raise_for_status()
            return response

        except (httpx.HTTPStatusError, httpx.TransportError) as exc:
            last_exc = exc
            logger.warning(
                "stream_get attempt %d/%d failed for %s: %s",
                attempt_idx + 1, len(attempts), url, exc,
            )

    assert last_exc is not None
    raise last_exc
