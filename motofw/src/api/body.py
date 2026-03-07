"""Request body construction for Motorola OTA endpoints.

Builds the JSON payload dicts from device info and configuration,
ready to be serialised by the HTTP layer.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, Optional

from motofw.src.config.settings import Config
from motofw.src.device.info import build_device_info, build_extra_info, build_identity_info

logger = logging.getLogger(__name__)


def build_check_body(
    cfg: Config,
    *,
    content_timestamp: int = 0,
    triggered_by: str = "user",
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Build the JSON body dict for the ``/check`` endpoint.

    Parameters
    ----------
    cfg:
        Parsed motofw configuration.
    content_timestamp:
        Epoch-millis timestamp of the last known content.
    triggered_by:
        ``"user"`` or ``"system"``.
    request_id:
        Explicit request id; a UUID is generated when omitted.

    Returns
    -------
    dict
        Ready-to-serialize JSON payload.
    """
    rid = request_id or str(uuid.uuid4())
    body = {
        "id": rid,
        "contentTimestamp": content_timestamp,
        "deviceInfo": build_device_info(cfg).to_dict(),
        "extraInfo": build_extra_info(cfg).to_dict(),
        "identityInfo": build_identity_info(cfg).to_dict(),
        "triggeredBy": triggered_by,
        "idType": cfg.id_type,
    }
    logger.debug("Built check body (id=%s, triggeredBy=%s)", rid, triggered_by)
    return body


def build_resources_body(
    cfg: Config,
    *,
    content_timestamp: int = 0,
    reporting_tags: str = "TRIGGER-USER",
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Build the JSON body dict for the ``/resources`` endpoint.

    Parameters
    ----------
    cfg:
        Parsed motofw configuration.
    content_timestamp:
        Epoch-millis timestamp from the check response.
    reporting_tags:
        Reporting tags from the check response.
    request_id:
        Explicit request id.

    Returns
    -------
    dict
        Ready-to-serialize JSON payload.
    """
    rid = request_id or str(uuid.uuid4())
    body = {
        "id": rid,
        "contentTimestamp": content_timestamp,
        "deviceInfo": build_device_info(cfg).to_dict(),
        "extraInfo": build_extra_info(cfg).to_dict(),
        "identityInfo": build_identity_info(cfg).to_dict(),
        "idType": cfg.id_type,
        "reportingTags": reporting_tags,
        "reason": None,
    }
    logger.debug("Built resources body (id=%s)", rid)
    return body
