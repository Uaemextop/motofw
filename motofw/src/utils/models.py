"""Shared data models for OTA protocol messages.

Contains both request and response models used across the project.
Every dataclass mirrors the exact JSON schema observed in log evidence
from Motorola's ``moto-cds.appspot.com`` server.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from motofw.src.device.info import DeviceInfo, ExtraInfo, IdentityInfo


# ═══════════════════════════════════════════════════════════════════════════
#  Request models
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class CheckRequest:
    """Full JSON body POSTed to the ``/check`` endpoint."""

    device_info: Any = None  # DeviceInfo
    extra_info: Any = None   # ExtraInfo
    identity_info: Any = None  # IdentityInfo
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_timestamp: int = 0
    triggered_by: str = "user"
    id_type: str = "serialNumber"

    def to_dict(self) -> Dict[str, Any]:
        """Build the complete JSON payload for the check endpoint."""
        return {
            "id": self.request_id,
            "contentTimestamp": self.content_timestamp,
            "deviceInfo": self.device_info.to_dict() if self.device_info else {},
            "extraInfo": self.extra_info.to_dict() if self.extra_info else {},
            "identityInfo": self.identity_info.to_dict() if self.identity_info else {},
            "triggeredBy": self.triggered_by,
            "idType": self.id_type,
        }


@dataclass
class ResourcesRequest:
    """Full JSON body POSTed to the resources endpoint."""

    device_info: Any = None  # DeviceInfo
    extra_info: Any = None   # ExtraInfo
    identity_info: Any = None  # IdentityInfo
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_timestamp: int = 0
    id_type: str = "serialNumber"
    reporting_tags: str = "TRIGGER-USER"
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Build the complete JSON payload for the resources endpoint."""
        return {
            "id": self.request_id,
            "contentTimestamp": self.content_timestamp,
            "deviceInfo": self.device_info.to_dict() if self.device_info else {},
            "extraInfo": self.extra_info.to_dict() if self.extra_info else {},
            "identityInfo": self.identity_info.to_dict() if self.identity_info else {},
            "idType": self.id_type,
            "reportingTags": self.reporting_tags,
            "reason": self.reason,
        }


# ═══════════════════════════════════════════════════════════════════════════
#  Response models
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class ContentInfo:
    """``content`` object inside a check response."""

    package_id: str = ""
    size: int = 0
    md5_checksum: str = ""
    flavour: str = ""
    min_version: str = ""
    version: str = ""
    model: str = ""
    ota_source_sha1: str = ""
    ota_target_sha1: str = ""
    display_version: str = ""
    source_display_version: str = ""
    update_type: str = ""
    ab_install_type: str = ""
    release_notes: str = ""


@dataclass
class ContentResource:
    """A single download resource from ``contentResources`` array."""

    url: str = ""
    headers: Optional[Dict[str, str]] = None
    tags: List[str] = field(default_factory=list)
    url_ttl_seconds: int = 0


@dataclass
class CheckResponse:
    """Parsed response from the ``/check`` endpoint."""

    proceed: bool = False
    context: str = ""
    context_key: str = ""
    content: Optional[ContentInfo] = None
    content_resources: List[ContentResource] = field(default_factory=list)
    tracking_id: str = ""
    reporting_tags: str = ""
    poll_after_seconds: int = 0
    smart_update_bitmap: int = 0
    upload_failure_logs: bool = False
