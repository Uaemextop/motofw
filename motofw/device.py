"""Build device-specific JSON payloads for OTA API requests.

Every function in this module creates model instances populated from a
:class:`~motofw.config.Config` object, ensuring that all user-editable
values flow through ``config.ini`` rather than being hard-coded.
"""

from __future__ import annotations

import logging
import uuid
from typing import Optional

from motofw.config import Config
from motofw.models import (
    CheckRequest,
    DeviceInfo,
    ExtraInfo,
    IdentityInfo,
    ResourcesRequest,
)

logger = logging.getLogger(__name__)


def build_device_info(cfg: Config) -> DeviceInfo:
    """Create a :class:`DeviceInfo` from the loaded configuration.

    Parameters
    ----------
    cfg:
        Parsed motofw configuration.

    Returns
    -------
    DeviceInfo
        Populated with values from ``[device]`` section.
    """
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
    """Create an :class:`ExtraInfo` from the loaded configuration.

    Parameters
    ----------
    cfg:
        Parsed motofw configuration.

    Returns
    -------
    ExtraInfo
        Populated with values from ``[device]`` section.
    """
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
    """Create an :class:`IdentityInfo` from the loaded configuration.

    Parameters
    ----------
    cfg:
        Parsed motofw configuration.

    Returns
    -------
    IdentityInfo
        Contains the device serial number from config.
    """
    return IdentityInfo(serial_number=cfg.serial_number)


def build_check_request(
    cfg: Config,
    *,
    content_timestamp: int = 0,
    triggered_by: str = "user",
    request_id: Optional[str] = None,
) -> CheckRequest:
    """Build a complete :class:`CheckRequest` ready to serialize.

    Parameters
    ----------
    cfg:
        Parsed motofw configuration.
    content_timestamp:
        Epoch-millis timestamp of the last known content.  ``0`` for
        the initial check (evidence: first request uses ``0``).
    triggered_by:
        Who initiated the check — ``"user"`` or ``"system"``.
    request_id:
        Optional explicit request identifier; a UUID is generated when
        omitted.

    Returns
    -------
    CheckRequest
    """
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
    """Build a :class:`ResourcesRequest` for the resources endpoint.

    Parameters
    ----------
    cfg:
        Parsed motofw configuration.
    content_timestamp:
        Epoch-millis timestamp from the check response.
    reporting_tags:
        Reporting tags from the check response.
    request_id:
        Optional explicit request identifier.

    Returns
    -------
    ResourcesRequest
    """
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
