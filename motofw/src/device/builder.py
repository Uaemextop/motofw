"""Build device property instances from a Config object."""

from __future__ import annotations

from motofw.src.config.settings import Config
from motofw.src.device.properties import DeviceInfo, ExtraInfo, IdentityInfo


def build_device_info(cfg: Config) -> DeviceInfo:
    """Populate a :class:`DeviceInfo` from configuration."""
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
    """Populate an :class:`ExtraInfo` from configuration."""
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
    """Populate an :class:`IdentityInfo` from configuration."""
    return IdentityInfo(serial_number=cfg.serial_number)
