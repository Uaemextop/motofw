"""Assemble JSON request bodies for the OTA endpoints."""

from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from motofw.src.config.settings import Config
from motofw.src.device.builder import build_device_info, build_extra_info, build_identity_info


def check_body(
    cfg: Config,
    *,
    content_timestamp: int = 0,
    triggered_by: str = "user",
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Build the JSON payload for the ``/check`` endpoint."""
    return {
        "id": request_id or str(uuid.uuid4()),
        "contentTimestamp": content_timestamp,
        "deviceInfo": build_device_info(cfg).to_dict(),
        "extraInfo": build_extra_info(cfg).to_dict(),
        "identityInfo": build_identity_info(cfg).to_dict(),
        "triggeredBy": triggered_by,
        "idType": cfg.id_type,
    }


def resources_body(
    cfg: Config,
    *,
    content_timestamp: int = 0,
    reporting_tags: str = "TRIGGER-USER",
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Build the JSON payload for the ``/resources`` endpoint."""
    return {
        "id": request_id or str(uuid.uuid4()),
        "contentTimestamp": content_timestamp,
        "deviceInfo": build_device_info(cfg).to_dict(),
        "extraInfo": build_extra_info(cfg).to_dict(),
        "identityInfo": build_identity_info(cfg).to_dict(),
        "idType": cfg.id_type,
        "reportingTags": reporting_tags,
        "reason": None,
    }
