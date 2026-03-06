"""Shared HTTP client for all outbound Motorola OTA server communication.

Every request goes through :class:`OTAClient` so that headers, retries,
timeouts, and proxy settings are centralised.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from motofw.config import Config

logger = logging.getLogger(__name__)

# Default headers sent with every request — mirrors what the real
# Motorola OTA app sends (Content-Type is application/json for all
# check / resources / state endpoints).
_DEFAULT_HEADERS: dict[str, str] = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}


class OTAClient:
    """Centralised HTTP client for Motorola OTA server communication.

    All outbound requests go through a single :class:`requests.Session`
    configured with retry logic, exponential back-off, optional proxy,
    and consistent headers.
    """

    def __init__(self, config: Config) -> None:
        """Initialise the client from *config*.

        Parameters
        ----------
        config:
            A loaded :class:`~motofw.config.Config` instance.
        """
        self._config = config
        self._session = self._build_session()

    # -- public API -----------------------------------------------------------

    def post_json(
        self,
        url: str,
        payload: dict[str, Any],
        *,
        extra_headers: Optional[dict[str, str]] = None,
    ) -> requests.Response:
        """Send a JSON POST request with exponential back-off retry.

        Parameters
        ----------
        url:
            Fully-qualified URL.
        payload:
            JSON-serialisable body.
        extra_headers:
            Additional headers merged on top of the defaults for this
            request only.

        Returns
        -------
        requests.Response
            The server response.
        """
        headers = dict(_DEFAULT_HEADERS)
        if extra_headers:
            headers.update(extra_headers)

        backoff = self._config.backoff_values
        max_attempts = self._config.max_retries + 1

        last_exc: Optional[Exception] = None
        for attempt in range(max_attempts):
            try:
                resp = self._session.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=self._config.timeout,
                )
                resp.raise_for_status()
                return resp
            except requests.RequestException as exc:
                last_exc = exc
                if attempt < max_attempts - 1:
                    delay_ms = backoff[min(attempt, len(backoff) - 1)]
                    delay_s = delay_ms / 1000.0
                    logger.warning(
                        "Request to %s failed (attempt %d/%d): %s — "
                        "retrying in %.1fs",
                        url,
                        attempt + 1,
                        max_attempts,
                        exc,
                        delay_s,
                    )
                    time.sleep(delay_s)

        assert last_exc is not None  # noqa: S101
        raise last_exc

    def get(
        self,
        url: str,
        *,
        extra_headers: Optional[dict[str, str]] = None,
        stream: bool = False,
    ) -> requests.Response:
        """Send a GET request with exponential back-off retry.

        Parameters
        ----------
        url:
            Fully-qualified URL.
        extra_headers:
            Additional headers merged on top of the defaults.
        stream:
            If *True* the response body is not immediately downloaded.

        Returns
        -------
        requests.Response
        """
        headers = dict(_DEFAULT_HEADERS)
        if extra_headers:
            headers.update(extra_headers)

        backoff = self._config.backoff_values
        max_attempts = self._config.max_retries + 1

        last_exc: Optional[Exception] = None
        for attempt in range(max_attempts):
            try:
                resp = self._session.get(
                    url,
                    headers=headers,
                    timeout=self._config.timeout,
                    stream=stream,
                )
                resp.raise_for_status()
                return resp
            except requests.RequestException as exc:
                last_exc = exc
                if attempt < max_attempts - 1:
                    delay_ms = backoff[min(attempt, len(backoff) - 1)]
                    delay_s = delay_ms / 1000.0
                    logger.warning(
                        "GET %s failed (attempt %d/%d): %s — "
                        "retrying in %.1fs",
                        url,
                        attempt + 1,
                        max_attempts,
                        exc,
                        delay_s,
                    )
                    time.sleep(delay_s)

        assert last_exc is not None  # noqa: S101
        raise last_exc

    def close(self) -> None:
        """Close the underlying session."""
        self._session.close()

    # -- private helpers ------------------------------------------------------

    def _build_session(self) -> requests.Session:
        """Create a configured :class:`requests.Session`."""
        session = requests.Session()

        # Retry adapter (transport-level retries handled by urllib3).
        retry = Retry(
            total=self._config.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        # Proxy configuration.
        proxy_host = self._config.proxy_host
        proxy_port = self._config.proxy_port
        if proxy_host and proxy_port > 0:
            proxy_url = f"http://{proxy_host}:{proxy_port}"
            session.proxies.update({"http": proxy_url, "https": proxy_url})
            logger.info("Using proxy %s", proxy_url)

        return session
