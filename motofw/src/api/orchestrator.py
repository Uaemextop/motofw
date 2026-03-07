"""Orchestrate the OTA check → resources → state flow."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from motofw.src.api.body import check_body, resources_body
from motofw.src.api.response import parse_check_response, parse_resources_response
from motofw.src.api.session import OTASession
from motofw.src.api.urls import check_url, resources_url, state_url
from motofw.src.config.settings import Config
from motofw.src.utils.models import CheckResponse

logger = logging.getLogger(__name__)


def check_update(
    cfg: Config,
    *,
    session: Optional[OTASession] = None,
    content_timestamp: int = 0,
    triggered_by: str = "user",
    request_id: Optional[str] = None,
) -> CheckResponse:
    """Query the server for available firmware updates."""
    own = session is None
    if own:
        session = OTASession(cfg)
    try:
        body = check_body(
            cfg,
            content_timestamp=content_timestamp,
            triggered_by=triggered_by,
            request_id=request_id,
        )
        path = check_url(cfg)
        logger.info("Checking for update at %s", path)
        resp = session.post(path, json_body=body)
        return parse_check_response(resp.json())
    finally:
        if own:
            session.close()


def get_resources(
    cfg: Config,
    *,
    tracking_id: str,
    content_timestamp: int = 0,
    reporting_tags: str = "TRIGGER-USER",
    session: Optional[OTASession] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Retrieve download URLs for a known update."""
    own = session is None
    if own:
        session = OTASession(cfg)
    try:
        body = resources_body(
            cfg,
            content_timestamp=content_timestamp,
            reporting_tags=reporting_tags,
            request_id=request_id,
        )
        path = resources_url(cfg, tracking_id)
        logger.info("Fetching resources at %s", path)
        resp = session.post(path, json_body=body)
        return resp.json()
    finally:
        if own:
            session.close()


def report_state(
    cfg: Config,
    *,
    state_body: Dict[str, Any],
    session: Optional[OTASession] = None,
) -> Dict[str, Any]:
    """Report device update state back to the server."""
    own = session is None
    if own:
        session = OTASession(cfg)
    try:
        path = state_url(cfg)
        logger.info("Reporting state at %s", path)
        resp = session.post(path, json_body=state_body)
        return resp.json()
    finally:
        if own:
            session.close()


def download_firmware(
    cfg: Config,
    check_resp: CheckResponse,
    *,
    session: Optional[OTASession] = None,
) -> CheckResponse:
    """Ensure *check_resp* has download URLs, fetching them if needed.

    Returns the (possibly enriched) CheckResponse.
    """
    if check_resp.content_resources:
        return check_resp

    if not check_resp.tracking_id:
        logger.warning("No tracking ID — cannot fetch resources")
        return check_resp

    logger.info("No resources in check response; fetching via /resources …")
    own = session is None
    if own:
        session = OTASession(cfg)
    try:
        data = get_resources(
            cfg,
            tracking_id=check_resp.tracking_id,
            session=session,
        )
        check_resp.content_resources = parse_resources_response(data)
        return check_resp
    finally:
        if own:
            session.close()
