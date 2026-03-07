"""Tool-level settings loaded from ``config.ini``.

Server endpoints, timeouts, retry policy, and download preferences live
here.  Device-specific values (IMEI, serial, build fingerprint) are
loaded separately by :mod:`motofw.src.device.config`.
"""

from __future__ import annotations

import configparser
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Defaults — from smali / log evidence
# ---------------------------------------------------------------------------

SERVER_DEFAULTS: dict[str, str] = {
    "url": "moto-cds.appspot.com",
    "check_path": "cds/upgrade/1/check",
    "resources_path": "cds/upgrade/1/resources",
    "state_path": "cds/upgrade/1/state",
    "context": "ota",
    "timeout": "60",
    "retry_delays_ms": "5000,15000,30000",
}

DOWNLOAD_DEFAULTS: dict[str, str] = {
    "output_dir": "output",
    "verify_checksum": "true",
}

DEVICE_DEFAULTS: dict[str, str] = {
    "manufacturer": "motorola",
    "hardware": "lamu",
    "brand": "motorola",
    "model": "moto g05",
    "product": "lamul_g",
    "os": "Android",
    "os_version": "15",
    "country": "MX",
    "region": "MX",
    "language": "es",
    "user_language": "es_MX",
    "client_identity": "motorola-ota-client-app",
    "carrier": "",
    "bootloader_version": "",
    "fingerprint": "motorola/lamul_g/lamul:15/VVTAS35.51-100-3/bb8ed4:user/release-keys",
    "radio_version": "",
    "build_tags": "release-keys",
    "build_type": "user",
    "build_device": "lamul",
    "build_id": "VVTAS35.51-100-3",
    "build_display_id": "VVTAS35.51-100-3",
    "build_incremental_version": "",
    "release_version": "15",
    "ota_source_sha1": "96398c9adf48ac1",
    "network": "wifi",
    "apk_version": "3500094",
    "provisioned_time": "0",
    "incremental_version": "0",
    "additional_info": "",
    "user_location": "Non-CN",
    "bootloader_status": "locked",
    "device_rooted": "false",
    "is_4gb_ram": "false",
    "device_chipset": "",
}

IDENTITY_DEFAULTS: dict[str, str] = {
    "serial_number": "ZY32LNRW97",
    "imei": "359488357396203",
    "imei2": "",
    "mccmnc": "",
    "mccmnc2": "",
    "id_type": "serialNumber",
}

# Backwards-compatible aggregate
_DEFAULTS: dict[str, dict[str, str]] = {
    "server": SERVER_DEFAULTS,
    "download": DOWNLOAD_DEFAULTS,
    "device": {**DEVICE_DEFAULTS, **IDENTITY_DEFAULTS},
    "identity": {"id_type": IDENTITY_DEFAULTS["id_type"]},
}

# Search paths
_CONFIG_SEARCH_PATHS: list[Path] = [
    Path("config.ini"),
    Path.home() / ".config" / "motofw" / "config.ini",
]

_DEVICE_SEARCH_PATHS: list[Path] = [
    Path("device.ini"),
    Path.home() / ".config" / "motofw" / "device.ini",
]


# ---------------------------------------------------------------------------
# Config dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Config:
    """Immutable container for all motofw configuration values.

    Server settings come from ``config.ini``, device-specific values
    come from ``device.ini``.  Both fall back to evidence-based defaults.
    """

    # --- server ---
    server_url: str = SERVER_DEFAULTS["url"]
    check_path: str = SERVER_DEFAULTS["check_path"]
    resources_path: str = SERVER_DEFAULTS["resources_path"]
    state_path: str = SERVER_DEFAULTS["state_path"]
    context: str = SERVER_DEFAULTS["context"]
    timeout: int = int(SERVER_DEFAULTS["timeout"])
    retry_delays_ms: List[int] = field(
        default_factory=lambda: [5000, 15000, 30000]
    )

    # --- device / deviceInfo ---
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

    # --- device / extraInfo ---
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

    # --- identityInfo ---
    serial_number: str = IDENTITY_DEFAULTS["serial_number"]

    # --- IMEI / SIM fields ---
    imei: str = IDENTITY_DEFAULTS["imei"]
    imei2: str = IDENTITY_DEFAULTS["imei2"]
    mccmnc: str = IDENTITY_DEFAULTS["mccmnc"]
    mccmnc2: str = IDENTITY_DEFAULTS["mccmnc2"]

    # --- identity ---
    id_type: str = IDENTITY_DEFAULTS["id_type"]

    # --- download ---
    output_dir: Path = Path(DOWNLOAD_DEFAULTS["output_dir"])
    verify_checksum: bool = True


# ---------------------------------------------------------------------------
# INI reader helper
# ---------------------------------------------------------------------------


def _read_ini(
    path: Path | None,
    search_paths: list[Path],
    label: str,
) -> configparser.ConfigParser:
    """Read an INI file from an explicit path or search locations."""
    cp = configparser.ConfigParser()

    if path is not None:
        resolved = Path(path)
        if resolved.exists():
            cp.read(resolved)
            logger.info("Loaded %s from %s", label, resolved)
        else:
            logger.warning(
                "Specified %s path %s does not exist; using defaults",
                label, resolved,
            )
    else:
        for candidate in search_paths:
            if candidate.exists():
                cp.read(candidate)
                logger.info("Loaded %s from %s", label, candidate)
                break
        else:
            logger.info("No %s found; using evidence-based defaults", label)

    return cp


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def load_config(
    path: Path | None = None,
    *,
    device_path: Path | None = None,
) -> Config:
    """Load configuration from ``config.ini`` and ``device.ini``.

    Parameters
    ----------
    path:
        Explicit path to a ``config.ini`` file.
    device_path:
        Explicit path to a ``device.ini`` file.

    Returns
    -------
    Config
        Populated configuration.
    """
    server_cp = _read_ini(path, _CONFIG_SEARCH_PATHS, "config.ini")
    device_cp = _read_ini(device_path, _DEVICE_SEARCH_PATHS, "device.ini")

    def _get_server(key: str) -> str:
        try:
            return server_cp.get("server", key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return SERVER_DEFAULTS.get(key, "")

    def _get_download(key: str) -> str:
        try:
            return server_cp.get("download", key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return DOWNLOAD_DEFAULTS.get(key, "")

    def _get_device(key: str) -> str:
        try:
            return device_cp.get("device", key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return DEVICE_DEFAULTS.get(key, "")

    def _get_identity(key: str) -> str:
        try:
            return device_cp.get("identity", key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return IDENTITY_DEFAULTS.get(key, "")

    def _getint(getter: object, key: str) -> int:
        val = getter(key)  # type: ignore[operator]
        return int(val) if val else 0

    def _getbool(getter: object, key: str) -> bool:
        val = getter(key).lower()  # type: ignore[operator]
        return val in ("true", "yes", "1", "on")

    retry_raw = _get_server("retry_delays_ms")
    retry_delays = [int(v.strip()) for v in retry_raw.split(",") if v.strip()]

    return Config(
        server_url=_get_server("url"),
        check_path=_get_server("check_path"),
        resources_path=_get_server("resources_path"),
        state_path=_get_server("state_path"),
        context=_get_server("context"),
        timeout=_getint(_get_server, "timeout"),
        retry_delays_ms=retry_delays,
        manufacturer=_get_device("manufacturer"),
        hardware=_get_device("hardware"),
        brand=_get_device("brand"),
        model=_get_device("model"),
        product=_get_device("product"),
        os=_get_device("os"),
        os_version=_get_device("os_version"),
        country=_get_device("country"),
        region=_get_device("region"),
        language=_get_device("language"),
        user_language=_get_device("user_language"),
        client_identity=_get_device("client_identity"),
        carrier=_get_device("carrier"),
        bootloader_version=_get_device("bootloader_version"),
        fingerprint=_get_device("fingerprint"),
        radio_version=_get_device("radio_version"),
        build_tags=_get_device("build_tags"),
        build_type=_get_device("build_type"),
        build_device=_get_device("build_device"),
        build_id=_get_device("build_id"),
        build_display_id=_get_device("build_display_id"),
        build_incremental_version=_get_device("build_incremental_version"),
        release_version=_get_device("release_version"),
        ota_source_sha1=_get_device("ota_source_sha1"),
        network=_get_device("network"),
        apk_version=_getint(_get_device, "apk_version"),
        provisioned_time=_getint(_get_device, "provisioned_time"),
        incremental_version=_getint(_get_device, "incremental_version"),
        additional_info=_get_device("additional_info"),
        user_location=_get_device("user_location"),
        bootloader_status=_get_device("bootloader_status"),
        device_rooted=_get_device("device_rooted"),
        is_4gb_ram=_getbool(_get_device, "is_4gb_ram"),
        device_chipset=_get_device("device_chipset"),
        serial_number=_get_identity("serial_number"),
        imei=_get_identity("imei"),
        imei2=_get_identity("imei2"),
        mccmnc=_get_identity("mccmnc"),
        mccmnc2=_get_identity("mccmnc2"),
        id_type=_get_identity("id_type"),
        output_dir=Path(_get_download("output_dir") or "output"),
        verify_checksum=_getbool(_get_download, "verify_checksum"),
    )
