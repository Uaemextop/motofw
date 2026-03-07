"""Data models for motofw OTA protocol messages.

Every dataclass mirrors the exact JSON schema observed in log evidence
from Motorola's ``moto-cds.appspot.com`` server.  Field names use
``snake_case`` in Python and are converted to the server's ``camelCase``
via :meth:`to_dict`.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ═══════════════════════════════════════════════════════════════════════════
#  Request models
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class DeviceInfo:
    """``deviceInfo`` block of the OTA request body.

    Field names and values from log evidence / BuildPropReader.smali.
    """

    manufacturer: str = "motorola"
    hardware: str = "lamu"
    brand: str = "motorola"
    model: str = "moto g05"
    product: str = "lamul_g"
    os: str = "Android"
    os_version: str = "15"
    country: str = "MX"
    region: str = "MX"
    language: str = "es"
    user_language: str = "es_MX"

    def to_dict(self) -> Dict[str, str]:
        """Serialize to the exact JSON key names the server expects."""
        return {
            "manufacturer": self.manufacturer,
            "hardware": self.hardware,
            "brand": self.brand,
            "model": self.model,
            "product": self.product,
            "os": self.os,
            "osVersion": self.os_version,
            "country": self.country,
            "region": self.region,
            "language": self.language,
            "userLanguage": self.user_language,
        }


@dataclass
class ExtraInfo:
    """``extraInfo`` block of the OTA request body.

    All field names and evidence-based defaults sourced from
    ``BuildPropReader.getExtraInfoAsJsonObject()`` in
    ``smali_classes2/com/motorola/ccc/ota/utils/BuildPropReader.smali``
    and captured request logs.
    """

    client_identity: str = "motorola-ota-client-app"
    carrier: str = ""
    bootloader_version: str = ""
    brand: str = "motorola"
    model: str = "moto g05"
    fingerprint: str = "motorola/lamul_g/lamul:15/VVTAS35.51-100-3/bb8ed4:user/release-keys"
    radio_version: str = ""
    build_tags: str = "release-keys"
    build_type: str = "user"
    build_device: str = "lamul"
    build_id: str = "VVTAS35.51-100-3"
    build_display_id: str = "VVTAS35.51-100-3"
    build_incremental_version: str = ""
    release_version: str = "15"
    ota_source_sha1: str = "96398c9adf48ac1"
    network: str = "wifi"
    apk_version: int = 3500094
    provisioned_time: int = 0
    incremental_version: int = 0
    additional_info: str = ""
    user_location: str = "Non-CN"
    bootloader_status: str = "locked"
    device_rooted: str = "false"
    is_4gb_ram: bool = False
    device_chipset: str = ""
    # --- Fields discovered in BuildPropReader.smali (lines 671-1100+) ---
    imei: str = ""
    imei2: str = ""
    mccmnc: str = ""
    mccmnc2: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to the exact JSON key names the server expects."""
        d: Dict[str, Any] = {
            "clientIdentity": self.client_identity,
            "carrier": self.carrier,
            "bootloaderVersion": self.bootloader_version,
            "brand": self.brand,
            "model": self.model,
            "fingerprint": self.fingerprint,
            "radioVersion": self.radio_version,
            "buildTags": self.build_tags,
            "buildType": self.build_type,
            "buildDevice": self.build_device,
            "buildId": self.build_id,
            "buildDisplayId": self.build_display_id,
            "buildIncrementalVersion": self.build_incremental_version,
            "releaseVersion": self.release_version,
            "otaSourceSha1": self.ota_source_sha1,
            "network": self.network,
            "apkVersion": self.apk_version,
            "provisionedTime": self.provisioned_time,
            "incrementalVersion": self.incremental_version,
            "additionalInfo": self.additional_info,
            "userLocation": self.user_location,
            "bootloaderStatus": self.bootloader_status,
            "deviceRooted": self.device_rooted,
            "is4GBRam": self.is_4gb_ram,
            "deviceChipset": self.device_chipset,
        }
        if self.imei:
            d["imei"] = self.imei
        if self.imei2:
            d["imei2"] = self.imei2
        if self.mccmnc:
            d["mccmnc"] = self.mccmnc
        if self.mccmnc2:
            d["mccmnc2"] = self.mccmnc2
        return d


@dataclass
class IdentityInfo:
    """``identityInfo`` block of the OTA request body."""

    serial_number: str = "ZY32LNRW97"

    def to_dict(self) -> Dict[str, str]:
        """Serialize to the exact JSON key names the server expects."""
        return {
            "serialNumber": self.serial_number,
        }


@dataclass
class CheckRequest:
    """Full JSON body POSTed to ``/cds/upgrade/1/check/ctx/ota/key/{key}``.

    Evidence: captured OTA request logs.
    """

    device_info: DeviceInfo = field(default_factory=DeviceInfo)
    extra_info: ExtraInfo = field(default_factory=ExtraInfo)
    identity_info: IdentityInfo = field(default_factory=IdentityInfo)
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_timestamp: int = 0
    triggered_by: str = "user"
    id_type: str = "serialNumber"

    def to_dict(self) -> Dict[str, Any]:
        """Build the complete JSON payload for the check endpoint."""
        return {
            "id": self.request_id,
            "contentTimestamp": self.content_timestamp,
            "deviceInfo": self.device_info.to_dict(),
            "extraInfo": self.extra_info.to_dict(),
            "identityInfo": self.identity_info.to_dict(),
            "triggeredBy": self.triggered_by,
            "idType": self.id_type,
        }


@dataclass
class ResourcesRequest:
    """Full JSON body POSTed to the resources endpoint.

    Evidence: ``/cds/upgrade/1/resources/t/{trackingId}/ctx/ota/key/{key}``
    """

    device_info: DeviceInfo = field(default_factory=DeviceInfo)
    extra_info: ExtraInfo = field(default_factory=ExtraInfo)
    identity_info: IdentityInfo = field(default_factory=IdentityInfo)
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
            "deviceInfo": self.device_info.to_dict(),
            "extraInfo": self.extra_info.to_dict(),
            "identityInfo": self.identity_info.to_dict(),
            "idType": self.id_type,
            "reportingTags": self.reporting_tags,
            "reason": self.reason,
        }


# ═══════════════════════════════════════════════════════════════════════════
#  Response models
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class ContentInfo:
    """``content`` object inside a check response.

    Field names match the server's camelCase JSON keys converted to
    snake_case.  Evidence: captured server response for lamu_g device.
    """

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
    """A single download resource from ``contentResources`` array.

    Evidence: captured server response shows ``url``, ``headers``,
    ``tags``, ``urlTtlSeconds``.
    """

    url: str = ""
    headers: Optional[Dict[str, str]] = None
    tags: List[str] = field(default_factory=list)
    url_ttl_seconds: int = 0


@dataclass
class CheckResponse:
    """Parsed response from the ``/check`` endpoint.

    Evidence: full JSON response captured for lamu_g VVTA35.51-28-15.
    """

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
