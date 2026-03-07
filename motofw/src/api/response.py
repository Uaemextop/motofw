"""Parse JSON responses from the Motorola OTA server into models."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from motofw.src.utils.models import CheckResponse, ContentInfo, ContentResource

logger = logging.getLogger(__name__)


def parse_content_info(data: Dict[str, Any]) -> ContentInfo:
    """Parse the ``content`` block."""
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
    """Parse a single ``contentResources`` entry."""
    return ContentResource(
        url=data.get("url", ""),
        headers=data.get("headers"),
        tags=data.get("tags", []),
        url_ttl_seconds=int(data.get("urlTtlSeconds", 0)),
    )


def parse_content_resources(
    items: Optional[List[Dict[str, Any]]],
) -> List[ContentResource]:
    """Parse the ``contentResources`` array (``None``-safe)."""
    if not items:
        return []
    return [parse_content_resource(r) for r in items]


def parse_check_response(data: Dict[str, Any]) -> CheckResponse:
    """Parse a full ``/check`` endpoint response."""
    content_raw = data.get("content")
    content: Optional[ContentInfo] = None
    if content_raw:
        content = parse_content_info(content_raw)

    resp = CheckResponse(
        proceed=data.get("proceed", False),
        context=data.get("context", ""),
        context_key=data.get("contextKey", ""),
        content=content,
        content_resources=parse_content_resources(data.get("contentResources")),
        tracking_id=data.get("trackingId", "") or "",
        reporting_tags=data.get("reportingTags", "") or "",
        poll_after_seconds=int(data.get("pollAfterSeconds", 0)),
        smart_update_bitmap=int(data.get("smartUpdateBitmap", 0)),
        upload_failure_logs=data.get("uploadFailureLogs", False),
    )

    if resp.proceed and resp.content:
        logger.info(
            "Update available: %s → %s (%d bytes)",
            resp.content.source_display_version,
            resp.content.display_version,
            resp.content.size,
        )
    else:
        logger.info("No update available (proceed=%s)", resp.proceed)

    return resp
