"""Device identity models and request builders.

Contains dataclasses for ``deviceInfo``, ``extraInfo``, and
``identityInfo`` JSON blocks, plus functions that populate them from
:class:`~motofw.src.config.settings.Config`.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from motofw.src.config.settings import Config
from motofw.src.utils.models import CheckRequest, ResourcesRequest

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
#  Data models
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class DeviceInfo:
    """``deviceInfo`` block of the OTA request body."""

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
    """``extraInfo`` block of the OTA request body."""

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
        return {"serialNumber": self.serial_number}


# ═══════════════════════════════════════════════════════════════════════════
#  Builders — populate from Config
# ═══════════════════════════════════════════════════════════════════════════


def build_device_info(cfg: Config) -> DeviceInfo:
    """Create a :class:`DeviceInfo` from the loaded configuration."""
    return DeviceInfo(
        manufacturer=cfg.manufacturer,
        hardware=cfg.hardware,
        brand=cfg.brand,
        model=cfg.model,
        product=cfg.product,
        os=cfg.os,
        os_version=cfg.os_version,
        country=cfg.country,
        region=cfg.region,
        language=cfg.language,
        user_language=cfg.user_language,
    )


def build_extra_info(cfg: Config) -> ExtraInfo:
    """Create an :class:`ExtraInfo` from the loaded configuration."""
    return ExtraInfo(
        client_identity=cfg.client_identity,
        carrier=cfg.carrier,
        bootloader_version=cfg.bootloader_version,
        brand=cfg.brand,
        model=cfg.model,
        fingerprint=cfg.fingerprint,
        radio_version=cfg.radio_version,
        build_tags=cfg.build_tags,
        build_type=cfg.build_type,
        build_device=cfg.build_device,
        build_id=cfg.build_id,
        build_display_id=cfg.build_display_id,
        build_incremental_version=cfg.build_incremental_version,
        release_version=cfg.release_version,
        ota_source_sha1=cfg.ota_source_sha1,
        network=cfg.network,
        apk_version=cfg.apk_version,
        provisioned_time=cfg.provisioned_time,
        incremental_version=cfg.incremental_version,
        additional_info=cfg.additional_info,
        user_location=cfg.user_location,
        bootloader_status=cfg.bootloader_status,
        device_rooted=cfg.device_rooted,
        is_4gb_ram=cfg.is_4gb_ram,
        device_chipset=cfg.device_chipset,
        imei=cfg.imei,
        imei2=cfg.imei2,
        mccmnc=cfg.mccmnc,
        mccmnc2=cfg.mccmnc2,
    )


def build_identity_info(cfg: Config) -> IdentityInfo:
    """Create an :class:`IdentityInfo` from the loaded configuration."""
    return IdentityInfo(serial_number=cfg.serial_number)


def build_check_request(
    cfg: Config,
    *,
    content_timestamp: int = 0,
    triggered_by: str = "user",
    request_id: Optional[str] = None,
) -> CheckRequest:
    """Build a complete :class:`CheckRequest` ready to serialize."""
    return CheckRequest(
        device_info=build_device_info(cfg),
        extra_info=build_extra_info(cfg),
        identity_info=build_identity_info(cfg),
        request_id=request_id or str(uuid.uuid4()),
        content_timestamp=content_timestamp,
        triggered_by=triggered_by,
        id_type=cfg.id_type,
    )


def build_resources_request(
    cfg: Config,
    *,
    content_timestamp: int = 0,
    reporting_tags: str = "TRIGGER-USER",
    request_id: Optional[str] = None,
) -> ResourcesRequest:
    """Build a :class:`ResourcesRequest` for the resources endpoint."""
    return ResourcesRequest(
        device_info=build_device_info(cfg),
        extra_info=build_extra_info(cfg),
        identity_info=build_identity_info(cfg),
        request_id=request_id or str(uuid.uuid4()),
        content_timestamp=content_timestamp,
        id_type=cfg.id_type,
        reporting_tags=reporting_tags,
        reason=None,
    )
