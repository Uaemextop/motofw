"""Data models for deviceInfo, extraInfo, and identityInfo JSON blocks.

Each class has a ``to_dict()`` method that produces the exact camelCase
keys the Motorola server expects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class DeviceInfo:
    """``deviceInfo`` section of the OTA request body."""

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
        """Serialize with the server's camelCase key names."""
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
    """``extraInfo`` section of the OTA request body."""

    client_identity: str = "motorola-ota-client-app"
    carrier: str = ""
    bootloader_version: str = ""
    brand: str = "motorola"
    model: str = "moto g05"
    fingerprint: str = "motorola/lamul_g/lamul:15/VVTA35.51-100/e51bc9:user/release-keys"
    radio_version: str = ""
    build_tags: str = "release-keys"
    build_type: str = "user"
    build_device: str = "lamul"
    build_id: str = "VVTA35.51-100"
    build_display_id: str = "VVTA35.51-100"
    build_incremental_version: str = ""
    release_version: str = "15"
    ota_source_sha1: str = "190325d96009ac5"
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
        """Serialize with the server's camelCase key names."""
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
    """``identityInfo`` section of the OTA request body."""

    serial_number: str = "ZY32LNRW97"

    def to_dict(self) -> Dict[str, str]:
        """Serialize with the server's camelCase key names."""
        return {"serialNumber": self.serial_number}
