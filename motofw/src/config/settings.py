"""Immutable Config dataclass and the ``load_config`` factory.

Server/download settings come from ``config.ini``; device-specific
parameters (IMEI, serial, build fingerprint …) come from ``device.ini``.
Both fall back to evidence-based defaults when no file is present.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from motofw.src.config.defaults import (
    DEVICE_DEFAULTS,
    DOWNLOAD_DEFAULTS,
    IDENTITY_DEFAULTS,
    SERVER_DEFAULTS,
)
from motofw.src.config.loader import get_bool, get_int, get_value, read_ini

logger = logging.getLogger(__name__)

_CONFIG_SEARCH: list[Path] = [
    Path("config.ini"),
    Path.home() / ".config" / "motofw" / "config.ini",
]

_DEVICE_SEARCH: list[Path] = [
    Path("device.ini"),
    Path.home() / ".config" / "motofw" / "device.ini",
]


@dataclass(frozen=True)
class Config:
    """Immutable container for every motofw setting."""

    # server
    server_url: str = SERVER_DEFAULTS["url"]
    check_path: str = SERVER_DEFAULTS["check_path"]
    resources_path: str = SERVER_DEFAULTS["resources_path"]
    state_path: str = SERVER_DEFAULTS["state_path"]
    context: str = SERVER_DEFAULTS["context"]
    timeout: int = int(SERVER_DEFAULTS["timeout"])
    retry_delays_ms: List[int] = field(default_factory=lambda: [2000, 5000, 15000, 30000])

    # device / deviceInfo
    manufacturer: str = DEVICE_DEFAULTS["manufacturer"]
    hardware: str = DEVICE_DEFAULTS["hardware"]
    brand: str = DEVICE_DEFAULTS["brand"]
    model: str = DEVICE_DEFAULTS["model"]
    product: str = DEVICE_DEFAULTS["product"]
    os: str = DEVICE_DEFAULTS["os"]
    os_version: str = DEVICE_DEFAULTS["os_version"]
    country: str = DEVICE_DEFAULTS["country"]
    region: str = DEVICE_DEFAULTS["region"]
    language: str = DEVICE_DEFAULTS["language"]
    user_language: str = DEVICE_DEFAULTS["user_language"]

    # device / extraInfo
    client_identity: str = DEVICE_DEFAULTS["client_identity"]
    carrier: str = DEVICE_DEFAULTS["carrier"]
    bootloader_version: str = DEVICE_DEFAULTS["bootloader_version"]
    fingerprint: str = DEVICE_DEFAULTS["fingerprint"]
    radio_version: str = DEVICE_DEFAULTS["radio_version"]
    build_tags: str = DEVICE_DEFAULTS["build_tags"]
    build_type: str = DEVICE_DEFAULTS["build_type"]
    build_device: str = DEVICE_DEFAULTS["build_device"]
    build_id: str = DEVICE_DEFAULTS["build_id"]
    build_display_id: str = DEVICE_DEFAULTS["build_display_id"]
    build_incremental_version: str = DEVICE_DEFAULTS["build_incremental_version"]
    release_version: str = DEVICE_DEFAULTS["release_version"]
    ota_source_sha1: str = DEVICE_DEFAULTS["ota_source_sha1"]
    network: str = DEVICE_DEFAULTS["network"]
    apk_version: int = int(DEVICE_DEFAULTS["apk_version"])
    provisioned_time: int = int(DEVICE_DEFAULTS["provisioned_time"])
    incremental_version: int = int(DEVICE_DEFAULTS["incremental_version"])
    additional_info: str = DEVICE_DEFAULTS["additional_info"]
    user_location: str = DEVICE_DEFAULTS["user_location"]
    bootloader_status: str = DEVICE_DEFAULTS["bootloader_status"]
    device_rooted: str = DEVICE_DEFAULTS["device_rooted"]
    is_4gb_ram: bool = False
    device_chipset: str = DEVICE_DEFAULTS["device_chipset"]

    # identity
    serial_number: str = IDENTITY_DEFAULTS["serial_number"]
    imei: str = IDENTITY_DEFAULTS["imei"]
    imei2: str = IDENTITY_DEFAULTS["imei2"]
    mccmnc: str = IDENTITY_DEFAULTS["mccmnc"]
    mccmnc2: str = IDENTITY_DEFAULTS["mccmnc2"]
    id_type: str = IDENTITY_DEFAULTS["id_type"]

    # download
    output_dir: Path = Path(DOWNLOAD_DEFAULTS["output_dir"])
    verify_checksum: bool = True


def load_config(
    path: Path | None = None,
    *,
    device_path: Path | None = None,
) -> Config:
    """Build a :class:`Config` from ``config.ini`` + ``device.ini``.

    Parameters
    ----------
    path:
        Explicit ``config.ini`` path.
    device_path:
        Explicit ``device.ini`` path.
    """
    srv = read_ini(path, _CONFIG_SEARCH, "config.ini")
    dev = read_ini(device_path, _DEVICE_SEARCH, "device.ini")

    raw_delays = get_value(srv, "server", "retry_delays_ms", SERVER_DEFAULTS["retry_delays_ms"])
    delays = [int(v.strip()) for v in raw_delays.split(",") if v.strip()]

    return Config(
        server_url=get_value(srv, "server", "url", SERVER_DEFAULTS["url"]),
        check_path=get_value(srv, "server", "check_path", SERVER_DEFAULTS["check_path"]),
        resources_path=get_value(srv, "server", "resources_path", SERVER_DEFAULTS["resources_path"]),
        state_path=get_value(srv, "server", "state_path", SERVER_DEFAULTS["state_path"]),
        context=get_value(srv, "server", "context", SERVER_DEFAULTS["context"]),
        timeout=get_int(srv, "server", "timeout", SERVER_DEFAULTS["timeout"]),
        retry_delays_ms=delays,
        manufacturer=get_value(dev, "device", "manufacturer", DEVICE_DEFAULTS["manufacturer"]),
        hardware=get_value(dev, "device", "hardware", DEVICE_DEFAULTS["hardware"]),
        brand=get_value(dev, "device", "brand", DEVICE_DEFAULTS["brand"]),
        model=get_value(dev, "device", "model", DEVICE_DEFAULTS["model"]),
        product=get_value(dev, "device", "product", DEVICE_DEFAULTS["product"]),
        os=get_value(dev, "device", "os", DEVICE_DEFAULTS["os"]),
        os_version=get_value(dev, "device", "os_version", DEVICE_DEFAULTS["os_version"]),
        country=get_value(dev, "device", "country", DEVICE_DEFAULTS["country"]),
        region=get_value(dev, "device", "region", DEVICE_DEFAULTS["region"]),
        language=get_value(dev, "device", "language", DEVICE_DEFAULTS["language"]),
        user_language=get_value(dev, "device", "user_language", DEVICE_DEFAULTS["user_language"]),
        client_identity=get_value(dev, "device", "client_identity", DEVICE_DEFAULTS["client_identity"]),
        carrier=get_value(dev, "device", "carrier", DEVICE_DEFAULTS["carrier"]),
        bootloader_version=get_value(dev, "device", "bootloader_version", DEVICE_DEFAULTS["bootloader_version"]),
        fingerprint=get_value(dev, "device", "fingerprint", DEVICE_DEFAULTS["fingerprint"]),
        radio_version=get_value(dev, "device", "radio_version", DEVICE_DEFAULTS["radio_version"]),
        build_tags=get_value(dev, "device", "build_tags", DEVICE_DEFAULTS["build_tags"]),
        build_type=get_value(dev, "device", "build_type", DEVICE_DEFAULTS["build_type"]),
        build_device=get_value(dev, "device", "build_device", DEVICE_DEFAULTS["build_device"]),
        build_id=get_value(dev, "device", "build_id", DEVICE_DEFAULTS["build_id"]),
        build_display_id=get_value(dev, "device", "build_display_id", DEVICE_DEFAULTS["build_display_id"]),
        build_incremental_version=get_value(dev, "device", "build_incremental_version", DEVICE_DEFAULTS["build_incremental_version"]),
        release_version=get_value(dev, "device", "release_version", DEVICE_DEFAULTS["release_version"]),
        ota_source_sha1=get_value(dev, "device", "ota_source_sha1", DEVICE_DEFAULTS["ota_source_sha1"]),
        network=get_value(dev, "device", "network", DEVICE_DEFAULTS["network"]),
        apk_version=get_int(dev, "device", "apk_version", DEVICE_DEFAULTS["apk_version"]),
        provisioned_time=get_int(dev, "device", "provisioned_time", DEVICE_DEFAULTS["provisioned_time"]),
        incremental_version=get_int(dev, "device", "incremental_version", DEVICE_DEFAULTS["incremental_version"]),
        additional_info=get_value(dev, "device", "additional_info", DEVICE_DEFAULTS["additional_info"]),
        user_location=get_value(dev, "device", "user_location", DEVICE_DEFAULTS["user_location"]),
        bootloader_status=get_value(dev, "device", "bootloader_status", DEVICE_DEFAULTS["bootloader_status"]),
        device_rooted=get_value(dev, "device", "device_rooted", DEVICE_DEFAULTS["device_rooted"]),
        is_4gb_ram=get_bool(dev, "device", "is_4gb_ram", DEVICE_DEFAULTS["is_4gb_ram"]),
        device_chipset=get_value(dev, "device", "device_chipset", DEVICE_DEFAULTS["device_chipset"]),
        serial_number=get_value(dev, "identity", "serial_number", IDENTITY_DEFAULTS["serial_number"]),
        imei=get_value(dev, "identity", "imei", IDENTITY_DEFAULTS["imei"]),
        imei2=get_value(dev, "identity", "imei2", IDENTITY_DEFAULTS["imei2"]),
        mccmnc=get_value(dev, "identity", "mccmnc", IDENTITY_DEFAULTS["mccmnc"]),
        mccmnc2=get_value(dev, "identity", "mccmnc2", IDENTITY_DEFAULTS["mccmnc2"]),
        id_type=get_value(dev, "identity", "id_type", IDENTITY_DEFAULTS["id_type"]),
        output_dir=Path(get_value(srv, "download", "output_dir", DOWNLOAD_DEFAULTS["output_dir"]) or "output"),
        verify_checksum=get_bool(srv, "download", "verify_checksum", DOWNLOAD_DEFAULTS["verify_checksum"]),
    )
