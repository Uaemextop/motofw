"""Server response parsing for Motorola OTA JSON payloads.

Every function takes a raw ``dict`` (already deserialised from JSON) and
returns the corresponding model dataclass.  Field mapping follows the
exact camelCase keys observed in captured server responses.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from motofw.src.utils.models import CheckResponse, ContentInfo, ContentResource

logger = logging.getLogger(__name__)


def parse_content_info(data: Dict[str, Any]) -> ContentInfo:
    """Parse the ``content`` object from a check response.

    Parameters
    ----------
    data:
        Raw JSON dict of the ``content`` block.

    Returns
    -------
    ContentInfo
    """
    return ContentInfo(
        package_id=data.get("packageID", ""),
        size=int(data.get("size", 0)),
        md5_checksum=data.get("md5_checksum", ""),
        flavour=data.get("flavour", ""),
        min_version=data.get("minVersion", ""),
        version=data.get("version", ""),
        model=data.get("model", ""),
        ota_source_sha1=data.get("otaSourceSha1", ""),
        ota_target_sha1=data.get("otaTargetSha1", ""),
        display_version=data.get("displayVersion", ""),
        source_display_version=data.get("sourceDisplayVersion", ""),
        update_type=data.get("updateType", ""),
        ab_install_type=data.get("abInstallType", ""),
        release_notes=data.get("releaseNotes", ""),
    )


def parse_content_resource(data: Dict[str, Any]) -> ContentResource:
    """Parse a single ``contentResources`` entry.

    Parameters
    ----------
    data:
        Raw JSON dict for one resource.

    Returns
    -------
    ContentResource
    """
    return ContentResource(
        url=data.get("url", ""),
        headers=data.get("headers"),
        tags=data.get("tags", []),
        url_ttl_seconds=int(data.get("urlTtlSeconds", 0)),
    )


def parse_content_resources(
    items: Optional[List[Dict[str, Any]]],
) -> List[ContentResource]:
    """Parse the ``contentResources`` array.

    Parameters
    ----------
    items:
        Raw JSON list or ``None``.

    Returns
    -------
    list[ContentResource]
    """
    if not items:
        return []
    return [parse_content_resource(r) for r in items]


def parse_check_response(data: Dict[str, Any]) -> CheckResponse:
    """Parse a full ``/check`` endpoint response.

    Parameters
    ----------
    data:
        Deserialised JSON dict from the server.

    Returns
    -------
    CheckResponse
        Fully populated response model.
    """
    content_raw = data.get("content")
    content: Optional[ContentInfo] = None
    if content_raw:
        content = parse_content_info(content_raw)

    resources = parse_content_resources(data.get("contentResources"))

    resp = CheckResponse(
        proceed=data.get("proceed", False),
        context=data.get("context", ""),
        context_key=data.get("contextKey", ""),
        content=content,
        content_resources=resources,
        tracking_id=data.get("trackingId", "") or "",
        reporting_tags=data.get("reportingTags", "") or "",
        poll_after_seconds=int(data.get("pollAfterSeconds", 0)),
        smart_update_bitmap=int(data.get("smartUpdateBitmap", 0)),
        upload_failure_logs=data.get("uploadFailureLogs", False),
    )

    if resp.proceed and resp.content:
        logger.info(
            "Update available: %s → %s (size=%d, md5=%s)",
            resp.content.source_display_version,
            resp.content.display_version,
            resp.content.size,
            resp.content.md5_checksum,
        )
    else:
        logger.info("No update available (proceed=%s)", resp.proceed)

    return resp
