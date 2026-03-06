"""Response parser for Motorola OTA server responses.

Mirrors the Java response data objects:
- ``Response`` — base response fields (proceed, context, trackingId, …)
- ``CheckResponse`` — extends ``Response`` with a ``settings`` field
- ``ContentResources`` — download URL + headers + tags
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class ContentResource:
    """A single download resource from a ``contentResources`` array entry."""

    url: str
    headers: Optional[dict[str, str]]
    tags: list[str]
    url_ttl_seconds: int = 0


@dataclass
class OTAResponse:
    """Parsed OTA server response.

    Maps to the ``Response`` / ``CheckResponse`` smali structure.
    """

    proceed: bool = False
    context: str = ""
    context_key: str = ""
    content_timestamp: int = 0
    tracking_id: str = ""
    reporting_tags: str = ""
    poll_after_seconds: int = 0
    smart_update_bitmap: int = -1
    upload_failure_logs: bool = False
    content: Optional[dict[str, Any]] = None
    content_resources: list[ContentResource] = field(default_factory=list)
    settings: Optional[dict[str, Any]] = None
    status_code: int = 0


def parse_check_response(data: dict[str, Any]) -> OTAResponse:
    """Parse the JSON payload from a check-for-upgrade response.

    The server returns a JSON object with ``statusCode`` and ``payload``.

    Parameters
    ----------
    data:
        The full JSON response body (the ``statusCode`` + ``payload`` wrapper,
        or just the inner ``payload`` dict).

    Returns
    -------
    OTAResponse
        Parsed and typed response.
    """
    # The log evidence shows two formats:
    # 1. Bare payload (from "success response :" entries)
    # 2. Wrapped with {"statusCode":200,"payload":{…}} (from InternalResponseHandler)
    status_code = data.get("statusCode", 200)
    payload = data.get("payload", data)

    resources: list[ContentResource] = []
    raw_resources = payload.get("contentResources")
    if raw_resources and isinstance(raw_resources, list):
        for res in raw_resources:
            resources.append(
                ContentResource(
                    url=res.get("url", ""),
                    headers=res.get("headers"),
                    tags=res.get("tags", []),
                    url_ttl_seconds=res.get("urlTtlSeconds", 0),
                )
            )

    response = OTAResponse(
        proceed=payload.get("proceed", False),
        context=payload.get("context", ""),
        context_key=payload.get("contextKey", ""),
        content_timestamp=payload.get("contentTimestamp", 0),
        tracking_id=payload.get("trackingId", ""),
        reporting_tags=payload.get("reportingTags", ""),
        poll_after_seconds=payload.get("pollAfterSeconds", 0),
        smart_update_bitmap=payload.get("smartUpdateBitmap", -1),
        upload_failure_logs=payload.get("uploadFailureLogs", False),
        content=payload.get("content"),
        content_resources=resources,
        settings=payload.get("settings"),
        status_code=status_code,
    )

    logger.debug(
        "Parsed response: proceed=%s, contextKey=%s, resources=%d",
        response.proceed,
        response.context_key,
        len(response.content_resources),
    )
    return response


def get_download_url(response: OTAResponse, prefer_wifi: bool = True) -> Optional[str]:
    """Extract the best download URL from the response.

    The server provides multiple download URLs tagged with network types
    (``WIFI``, ``CELL``).  This function picks the preferred one.

    Parameters
    ----------
    response:
        A parsed OTA response.
    prefer_wifi:
        If *True* prefer the WIFI-tagged resource.

    Returns
    -------
    str or None
        The download URL, or *None* if no resources are available.
    """
    if not response.content_resources:
        return None

    preferred_tag = "WIFI" if prefer_wifi else "CELL"

    for resource in response.content_resources:
        if preferred_tag in resource.tags:
            return resource.url

    # Fallback to the first available resource.
    return response.content_resources[0].url


def get_firmware_metadata(response: OTAResponse) -> Optional[dict[str, Any]]:
    """Extract firmware metadata from the ``content`` field.

    The ``content`` field of a check response contains detailed update
    metadata including version, size, md5_checksum, release notes, etc.

    Parameters
    ----------
    response:
        A parsed OTA response.

    Returns
    -------
    dict or None
        Firmware metadata, or *None* if no content is available.
    """
    return response.content
