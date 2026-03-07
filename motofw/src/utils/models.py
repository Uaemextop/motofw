"""Shared data models for OTA request and response messages."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ── Response models ──────────────────────────────────────────────────────


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
    """Single entry in the ``contentResources`` array."""

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
