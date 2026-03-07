"""Data models for deviceInfo, extraInfo, and identityInfo JSON blocks.

Each class has a ``to_dict()`` method that produces the exact camelCase
keys the Motorola server expects.

Device-specific fields default to empty strings — concrete values come
from ``device.ini`` (loaded via Config) and are injected by the builder
functions in ``motofw.src.device.builder``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class DeviceInfo:
    """``deviceInfo`` section of the OTA request body."""

    manufacturer: str = ""
    hardware: str = ""
    brand: str = ""
    model: str = ""
    product: str = ""
    os: str = "Android"  # Protocol constant — all Motorola OTA devices are Android
    os_version: str = ""
    country: str = ""
    region: str = ""
    language: str = ""
    user_language: str = ""

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

    # Protocol constants — same for all Motorola OTA devices (from smali)
    client_identity: str = "motorola-ota-client-app"
    carrier: str = ""
    bootloader_version: str = ""
    brand: str = ""
    model: str = ""
    fingerprint: str = ""
    radio_version: str = ""
    build_tags: str = ""
    build_type: str = "user"  # Protocol default from BuildPropReader.smali
    build_device: str = ""
    build_id: str = ""
    build_display_id: str = ""
    build_incremental_version: str = ""
    release_version: str = ""
    ota_source_sha1: str = ""
    network: str = "wifi"  # Protocol default from NetworkUtils.smali
    apk_version: int = 3500094  # Protocol constant — OTA APK version
    provisioned_time: int = 0
    incremental_version: int = 0
    additional_info: str = ""
    user_location: str = "Non-CN"  # Protocol default from LocationUtils.smali
    bootloader_status: str = "locked"  # Protocol default from BuildPropReader.smali
    device_rooted: str = "false"
    is_4gb_ram: bool = False
    device_chipset: str = ""
    # --- Fields from BuildPropReader.smali lines 1006–1157 ---
    security_version: str = ""  # ro.build.version.security_patch (line 1098)
    mot_version: int = 0  # ro.mot.version (line 1080)
    enterprise_edition: bool = False  # ro.enterpriseedition (line 1110)
    virtual_ab_enabled: bool = False  # ro.virtual_ab.enabled (line 1122)
    vital_update: bool = False  # BotaSettings vitalUpdate (line 1157)
    hw_storage: str = ""  # ro.vendor.hw.storage (line 1006)
    hw_ram: str = ""  # ro.vendor.hw.ram (line 1014)
    hw_esim: str = ""  # ro.vendor.hw.esim (line 1022)
    product_wave: str = ""  # ro.mot.product_wave (line 1030)
    oem_product: str = ""  # ro.mot.build.oem.product (line 1038)
    system_product: str = ""  # ro.mot.build.system.product (line 1046)
    product_increment: str = ""  # ro.mot.build.product.increment (line 1054)
    verity_mode: str = ""  # ro.boot.veritymode (line 1062)
    system_verified: str = ""  # partition.system.verified (line 1070)
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
            "securityVersion": self.security_version,
            "ro.mot.version": self.mot_version,
            "ro.enterpriseedition": self.enterprise_edition,
            "ro.virtual_ab.enabled": self.virtual_ab_enabled,
            "vitalUpdate": self.vital_update,
            "ro.vendor.hw.storage": self.hw_storage,
            "ro.vendor.hw.ram": self.hw_ram,
            "ro.vendor.hw.esim": self.hw_esim,
            "ro.mot.product_wave": self.product_wave,
            "ro.mot.build.oem.product": self.oem_product,
            "ro.mot.build.system.product": self.system_product,
            "ro.mot.build.product.increment": self.product_increment,
            "ro.boot.veritymode": self.verity_mode,
            "partition.system.verified": self.system_verified,
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

    serial_number: str = ""

    def to_dict(self) -> Dict[str, str]:
        """Serialize with the server's camelCase key names."""
        return {"serialNumber": self.serial_number}
