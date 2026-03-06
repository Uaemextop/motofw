"""High-level API for Motorola OTA server communication.

Each public function corresponds to one of the three endpoints discovered
in evidence:

- ``check``     — query for available updates
- ``resources`` — retrieve download URLs for a known update
- ``state``     — report device state back to the server

All functions accept a :class:`~motofw.config.Config` and optionally a
pre-built :class:`~motofw.client.OTAClient` so the caller can share one
client across multiple calls.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from motofw.client import OTAClient
from motofw.config import Config
from motofw.device import build_check_request, build_resources_request
from motofw.models import CheckResponse
from motofw.parser import parse_check_response

logger = logging.getLogger(__name__)


def check_update(
    cfg: Config,
    *,
    client: Optional[OTAClient] = None,
    content_timestamp: int = 0,
    triggered_by: str = "user",
    request_id: Optional[str] = None,
) -> CheckResponse:
    """Query the Motorola OTA server for available firmware updates.

    Constructs the request body from *cfg*, POSTs it to the ``/check``
    endpoint, and returns a parsed :class:`CheckResponse`.

    Parameters
    ----------
    cfg:
        Parsed motofw configuration.
    client:
        Optional shared :class:`OTAClient`.  A temporary one is created
        (and closed) if not provided.
    content_timestamp:
        Epoch-millis of the last known content (``0`` for first check).
    triggered_by:
        ``"user"`` or ``"system"``.
    request_id:
        Explicit request id; a UUID is generated when omitted.

    Returns
    -------
    CheckResponse
        Parsed server response.
    """
    own_client = client is None
    if own_client:
        client = OTAClient(cfg)

    try:
        req = build_check_request(
            cfg,
            content_timestamp=content_timestamp,
            triggered_by=triggered_by,
            request_id=request_id,
        )
        path = client.build_check_url(cfg.ota_source_sha1)
        logger.info("Checking for update at %s", path)

        response = client.post(path, json_body=req.to_dict())
        data: Dict[str, Any] = response.json()
        return parse_check_response(data)
    finally:
        if own_client:
            assert client is not None
            client.close()


def get_resources(
    cfg: Config,
    *,
    tracking_id: str,
    content_timestamp: int = 0,
    reporting_tags: str = "TRIGGER-USER",
    client: Optional[OTAClient] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Retrieve download resource URLs for a known update.

    Parameters
    ----------
    cfg:
        Parsed motofw configuration.
    tracking_id:
        The ``trackingId`` from the check response.
    content_timestamp:
        Epoch-millis content timestamp from the check response.
    reporting_tags:
        Reporting tags from the check response.
    client:
        Optional shared HTTP client.
    request_id:
        Explicit request id.

    Returns
    -------
    dict
        Raw JSON dict from the resources endpoint.
    """
    own_client = client is None
    if own_client:
        client = OTAClient(cfg)

    try:
        req = build_resources_request(
            cfg,
            content_timestamp=content_timestamp,
            reporting_tags=reporting_tags,
            request_id=request_id,
        )
        path = client.build_resources_url(tracking_id, cfg.ota_source_sha1)
        logger.info("Fetching resources at %s", path)

        response = client.post(path, json_body=req.to_dict())
        return response.json()
    finally:
        if own_client:
            assert client is not None
            client.close()


def report_state(
    cfg: Config,
    *,
    state_body: Dict[str, Any],
    client: Optional[OTAClient] = None,
) -> Dict[str, Any]:
    """Report device update state back to the server.

    Parameters
    ----------
    cfg:
        Parsed motofw configuration.
    state_body:
        Free-form JSON dict to POST as the state payload.
    client:
        Optional shared HTTP client.

    Returns
    -------
    dict
        Raw JSON response from the state endpoint.
    """
    own_client = client is None
    if own_client:
        client = OTAClient(cfg)

    try:
        path = client.build_state_url(cfg.ota_source_sha1)
        logger.info("Reporting state at %s", path)

        response = client.post(path, json_body=state_body)
        return response.json()
    finally:
        if own_client:
            assert client is not None
            client.close()
