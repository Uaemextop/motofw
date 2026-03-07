"""HTTP session management — shared connection pool for the OTA server."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import httpx

from motofw.src.api.headers import DEFAULT_HEADERS, build_user_agent
from motofw.src.api.request import post_with_retry, stream_get
from motofw.src.config.settings import Config

logger = logging.getLogger(__name__)


class OTASession:
    """Manages a persistent httpx.Client against the Motorola CDS server.

    Use as a context manager to guarantee cleanup::

        with OTASession(cfg) as session:
            resp = session.post("/check", json_body={...})
    """

    def __init__(self, cfg: Config) -> None:
        self._cfg = cfg
        self._base = f"https://{cfg.server_url}"
        self._delays = [d / 1000.0 for d in cfg.retry_delays_ms]

        # Build headers matching the real Motorola OTA app.
        # User-Agent: Dalvik/2.1.0 (Linux; U; Android {ver}; {model} Build/{buildId})
        #   Source: System.getProperty("http.agent") — UEDownloadRequestBuilder.smali:517
        # Content-Type: application/json; charset=utf-8
        #   Source: Volley JsonRequest.smali:49
        session_headers = dict(DEFAULT_HEADERS)
        ua = build_user_agent(cfg.os_version, cfg.model, cfg.build_id)
        session_headers["User-Agent"] = ua

        self._client = httpx.Client(
            base_url=self._base,
            timeout=httpx.Timeout(cfg.timeout, connect=cfg.timeout),
            headers=session_headers,
            follow_redirects=True,
        )
        logger.debug(
            "OTASession opened — %s (timeout=%ds, UA=%s)",
            self._base, cfg.timeout, ua,
        )

    @property
    def base_url(self) -> str:
        """The HTTPS base URL."""
        return self._base

    @property
    def retry_delays(self) -> List[float]:
        """Retry delays in seconds."""
        return list(self._delays)

    def post(
        self,
        path: str,
        *,
        json_body: Dict[str, Any],
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """POST with automatic retries."""
        return post_with_retry(
            self._client,
            path,
            json_body=json_body,
            extra_headers=extra_headers,
            retry_delays_s=self._delays,
            label=self._base,
        )

    def get_stream(
        self,
        url: str,
        *,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """Streaming GET to an absolute URL (firmware download server)."""
        return stream_get(
            url,
            timeout=float(self._cfg.timeout),
            extra_headers=extra_headers,
            retry_delays_s=self._delays,
        )

    def close(self) -> None:
        """Release the underlying connection pool."""
        self._client.close()
        logger.debug("OTASession closed")

    def __enter__(self) -> "OTASession":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()
