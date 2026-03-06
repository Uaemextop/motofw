"""Shared HTTP client for all outbound requests to Motorola OTA servers.

Provides a single :class:`httpx.Client` instance with:

- Timeout from configuration (evidence: 60 s).
- Retry logic with exponential back-off (evidence: 5 000 / 15 000 / 30 000 ms).
- ``Content-Type: application/json`` on every POST.
- Optional proxy passthrough from configuration.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

import httpx

from motofw.config import Config

logger = logging.getLogger(__name__)


class OTAClient:
    """Reusable HTTP client for Motorola OTA communication.

    All API modules must use a single :class:`OTAClient` instance so that
    connection pooling, headers, retries, and timeouts are managed
    centrally.

    Parameters
    ----------
    cfg:
        Parsed motofw configuration.
    """

    def __init__(self, cfg: Config) -> None:
        self._cfg = cfg
        self._base_url = f"https://{cfg.server_url}"
        self._retry_delays_s = [d / 1000.0 for d in cfg.retry_delays_ms]
        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=httpx.Timeout(cfg.timeout, connect=cfg.timeout),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            follow_redirects=True,
        )
        logger.debug(
            "OTAClient initialised — base_url=%s timeout=%ss retries=%s",
            self._base_url,
            cfg.timeout,
            self._retry_delays_s,
        )

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    @property
    def base_url(self) -> str:
        """The HTTPS base URL derived from configuration."""
        return self._base_url

    def build_check_url(self, context_key: str) -> str:
        """Build the full path for the ``/check`` endpoint.

        Parameters
        ----------
        context_key:
            The device's ``otaSourceSha1`` value used as the URL key.

        Returns
        -------
        str
            Relative path like ``cds/upgrade/1/check/ctx/ota/key/23d670d5d06f351``.
        """
        return f"/{self._cfg.check_path}/ctx/{self._cfg.context}/key/{context_key}"

    def build_resources_url(
        self, tracking_id: str, context_key: str
    ) -> str:
        """Build the full path for the ``/resources`` endpoint.

        Parameters
        ----------
        tracking_id:
            Tracking ID returned by the check response.
        context_key:
            The device's ``otaSourceSha1``.

        Returns
        -------
        str
            Relative path.
        """
        return (
            f"/{self._cfg.resources_path}/t/{tracking_id}"
            f"/ctx/{self._cfg.context}/key/{context_key}"
        )

    def build_state_url(self, context_key: str) -> str:
        """Build the full path for the ``/state`` endpoint.

        Parameters
        ----------
        context_key:
            The device's ``otaSourceSha1``.

        Returns
        -------
        str
            Relative path.
        """
        return f"/{self._cfg.state_path}/ctx/{self._cfg.context}/key/{context_key}"

    # ------------------------------------------------------------------
    # Core request method with retries
    # ------------------------------------------------------------------

    def post(
        self,
        path: str,
        *,
        json_body: Dict[str, Any],
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """Send a POST request with retry + back-off.

        Parameters
        ----------
        path:
            Relative URL path (built by one of the ``build_*_url`` helpers).
        json_body:
            Python dict to send as JSON.
        extra_headers:
            Additional headers merged on top of the client defaults.

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
        attempts = [0.0, *self._retry_delays_s]
        last_exc: BaseException | None = None

        for attempt_idx, delay in enumerate(attempts):
            if delay > 0:
                logger.info(
                    "Retry %d/%d — waiting %.1f s before next attempt",
                    attempt_idx,
                    len(self._retry_delays_s),
                    delay,
                )
                time.sleep(delay)

            try:
                logger.debug(
                    "POST %s%s (attempt %d/%d)",
                    self._base_url,
                    path,
                    attempt_idx + 1,
                    len(attempts),
                )
                response = self._client.post(
                    path,
                    json=json_body,
                    headers=extra_headers,
                )
                response.raise_for_status()
                logger.debug(
                    "Response %d from %s%s",
                    response.status_code,
                    self._base_url,
                    path,
                )
                return response

            except (httpx.HTTPStatusError, httpx.TransportError) as exc:
                last_exc = exc
                logger.warning(
                    "Attempt %d/%d failed for %s: %s",
                    attempt_idx + 1,
                    len(attempts),
                    path,
                    exc,
                )

        # All retries exhausted
        assert last_exc is not None
        raise last_exc

    # ------------------------------------------------------------------
    # Streaming GET (for firmware downloads from dlmgr.gtm.svcmot.com)
    # ------------------------------------------------------------------

    def stream_get(
        self,
        url: str,
        *,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """Start a streaming GET to an absolute URL (e.g. firmware download).

        The caller is responsible for iterating over the response stream
        and closing it when done.

        Parameters
        ----------
        url:
            Absolute URL (typically ``https://dlmgr.gtm.svcmot.com/…``).
        extra_headers:
            Optional additional headers.

        Returns
        -------
        httpx.Response
            A response with an open byte stream.

        Raises
        ------
        httpx.HTTPStatusError
            On non-2xx status after retries.
        """
        attempts = [0.0, *self._retry_delays_s]
        last_exc: BaseException | None = None

        for attempt_idx, delay in enumerate(attempts):
            if delay > 0:
                logger.info(
                    "Retry %d/%d (stream_get) — waiting %.1f s",
                    attempt_idx,
                    len(self._retry_delays_s),
                    delay,
                )
                time.sleep(delay)

            try:
                logger.debug(
                    "GET %s (stream, attempt %d/%d)",
                    url,
                    attempt_idx + 1,
                    len(attempts),
                )
                # Use a separate client for absolute URLs (download server
                # is different from the API server).
                response = httpx.Client(
                    timeout=httpx.Timeout(self._cfg.timeout, connect=self._cfg.timeout),
                    follow_redirects=True,
                ).send(
                    httpx.Request("GET", url, headers=extra_headers),
                    stream=True,
                )
                response.raise_for_status()
                return response

            except (httpx.HTTPStatusError, httpx.TransportError) as exc:
                last_exc = exc
                logger.warning(
                    "stream_get attempt %d/%d failed for %s: %s",
                    attempt_idx + 1,
                    len(attempts),
                    url,
                    exc,
                )

        assert last_exc is not None
        raise last_exc

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Release underlying connections."""
        self._client.close()
        logger.debug("OTAClient closed")

    def __enter__(self) -> "OTAClient":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()
