"""High-level OTA operations.

Ties together the URL builder, request builder, HTTP client, response
parser, and downloader into user-facing workflows.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

from motofw.client import OTAClient
from motofw.config import Config
from motofw.downloader import download_firmware
from motofw.request_builder import (
    build_check_body,
    build_check_url,
    build_resources_body,
    build_resources_url,
    build_state_body,
    build_state_url,
)
from motofw.response_parser import (
    OTAResponse,
    get_download_url,
    get_firmware_metadata,
    parse_check_response,
)

logger = logging.getLogger(__name__)


def check_update(
    config: Config,
    client: OTAClient,
    *,
    content_timestamp: int = 0,
) -> OTAResponse:
    """Query the OTA server for available updates.

    Sends a check-for-upgrade request and returns the parsed response.

    Parameters
    ----------
    config:
        Loaded configuration.
    client:
        Shared HTTP client.
    content_timestamp:
        Timestamp of the last known content version.

    Returns
    -------
    OTAResponse
        The parsed server response.
    """
    url = build_check_url(config)
    body = build_check_body(config, content_timestamp=content_timestamp)

    logger.info("Checking for updates at %s", url)
    resp = client.post_json(url, body)
    return parse_check_response(resp.json())


def get_resources(
    config: Config,
    client: OTAClient,
    check_response: OTAResponse,
) -> OTAResponse:
    """Request download resources (URLs) from the OTA server.

    Parameters
    ----------
    config:
        Loaded configuration.
    client:
        Shared HTTP client.
    check_response:
        A previously obtained check response.

    Returns
    -------
    OTAResponse
        The parsed resources response containing download URLs.
    """
    url = build_resources_url(config)
    body = build_resources_body(
        config,
        content_timestamp=check_response.content_timestamp,
        tracking_id=check_response.tracking_id,
    )

    logger.info("Requesting download resources at %s", url)
    resp = client.post_json(url, body)
    return parse_check_response(resp.json())


def report_state(
    config: Config,
    client: OTAClient,
    *,
    tracking_id: str,
    state: str,
    status: str = "",
) -> OTAResponse:
    """Report the current upgrade state to the OTA server.

    Parameters
    ----------
    config:
        Loaded configuration.
    client:
        Shared HTTP client.
    tracking_id:
        Tracking identifier from the check response.
    state:
        Current upgrade state string.
    status:
        Status code string.

    Returns
    -------
    OTAResponse
        The parsed state response.
    """
    url = build_state_url(config, tracking_id=tracking_id, state=state)
    body = build_state_body(
        config, tracking_id=tracking_id, state=state, status=status
    )

    logger.info("Reporting state '%s' at %s", state, url)
    resp = client.post_json(url, body)
    return parse_check_response(resp.json())


def download_update(
    config: Config,
    client: OTAClient,
    response: OTAResponse,
    *,
    output_dir: Optional[Path] = None,
) -> Path:
    """Download the OTA firmware package.

    Parameters
    ----------
    config:
        Loaded configuration.
    client:
        Shared HTTP client.
    response:
        A parsed OTA response with download resources.
    output_dir:
        Override for the download output directory.

    Returns
    -------
    Path
        The path to the downloaded firmware file.
    """
    dest = output_dir or config.output_dir
    return download_firmware(client, response, dest)


def query_and_download(
    config: Config,
    *,
    output_dir: Optional[Path] = None,
) -> dict[str, Any]:
    """Full workflow: check for updates, get resources, and download.

    Parameters
    ----------
    config:
        Loaded configuration.
    output_dir:
        Override for the download output directory.

    Returns
    -------
    dict
        Summary including the firmware metadata, download path, etc.
    """
    client = OTAClient(config)
    try:
        # Step 1: check for update.
        check_resp = check_update(config, client)
        if not check_resp.proceed:
            logger.info("Server says no update available (proceed=False)")
            return {"update_available": False, "response": check_resp}

        metadata = get_firmware_metadata(check_resp)
        logger.info(
            "Update available: version=%s, size=%s",
            metadata.get("version", "?") if metadata else "?",
            metadata.get("size", "?") if metadata else "?",
        )

        # Step 2: request download resources.
        resources_resp = get_resources(config, client, check_resp)
        download_url = get_download_url(resources_resp)

        if not download_url:
            logger.warning("No download URL in resources response")
            return {
                "update_available": True,
                "metadata": metadata,
                "download_url": None,
            }

        # Step 3: download.
        dest = output_dir or config.output_dir
        firmware_path = download_firmware(client, resources_resp, dest)

        return {
            "update_available": True,
            "metadata": metadata,
            "download_url": download_url,
            "firmware_path": str(firmware_path),
        }
    finally:
        client.close()
