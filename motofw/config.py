"""Configuration loader for motofw.

Server settings live in ``config.ini`` and device-specific parameters
(IMEI, serial number, build fingerprint, etc.) live in ``device.ini``.
Both are parsed here using :mod:`configparser`.  Hard-coded defaults
mirror the values extracted from Motorola smali evidence so the tool
works out of the box when neither file is present.
"""

from __future__ import annotations

import configparser
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Defaults — every value comes from smali / log evidence
# ---------------------------------------------------------------------------

_SERVER_DEFAULTS: dict[str, str] = {
    "url": "moto-cds.appspot.com",
    "check_path": "cds/upgrade/1/check",
    "resources_path": "cds/upgrade/1/resources",
    "state_path": "cds/upgrade/1/state",
    "context": "ota",
    "timeout": "60",
    "retry_delays_ms": "5000,15000,30000",
}

_DOWNLOAD_DEFAULTS: dict[str, str] = {
    "output_dir": "output",
    "verify_checksum": "true",
}

_DEVICE_DEFAULTS: dict[str, str] = {
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

_IDENTITY_DEFAULTS: dict[str, str] = {
    "serial_number": "ZY32LNRW97",
    "imei": "359488357396203",
    "imei2": "",
    "mccmnc": "",
    "mccmnc2": "",
    "id_type": "serialNumber",
}

# Backwards-compatible mapping for load_config internals
_DEFAULTS: dict[str, dict[str, str]] = {
    "server": _SERVER_DEFAULTS,
    "download": _DOWNLOAD_DEFAULTS,
    "device": {**_DEVICE_DEFAULTS, **_IDENTITY_DEFAULTS},
    "identity": {"id_type": _IDENTITY_DEFAULTS["id_type"]},
}

# Path search order — the first file that exists wins.
_CONFIG_SEARCH_PATHS: list[Path] = [
    Path("config.ini"),
    Path.home() / ".config" / "motofw" / "config.ini",
]

_DEVICE_SEARCH_PATHS: list[Path] = [
    Path("device.ini"),
    Path.home() / ".config" / "motofw" / "device.ini",
]


# ---------------------------------------------------------------------------
# Public dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Config:
    """Immutable container for all motofw configuration values.

    Server settings come from ``config.ini``, device-specific values
    come from ``device.ini``.  Both fall back to evidence-based defaults.
    """

    # --- server ---
    server_url: str = _SERVER_DEFAULTS["url"]
    check_path: str = _SERVER_DEFAULTS["check_path"]
    resources_path: str = _SERVER_DEFAULTS["resources_path"]
    state_path: str = _SERVER_DEFAULTS["state_path"]
    context: str = _SERVER_DEFAULTS["context"]
    timeout: int = int(_SERVER_DEFAULTS["timeout"])
    retry_delays_ms: List[int] = field(
        default_factory=lambda: [5000, 15000, 30000]
    )

    # --- device / deviceInfo ---
    manufacturer: str = _DEVICE_DEFAULTS["manufacturer"]
    hardware: str = _DEVICE_DEFAULTS["hardware"]
    brand: str = _DEVICE_DEFAULTS["brand"]
    model: str = _DEVICE_DEFAULTS["model"]
    product: str = _DEVICE_DEFAULTS["product"]
    os: str = _DEVICE_DEFAULTS["os"]
    os_version: str = _DEVICE_DEFAULTS["os_version"]
    country: str = _DEVICE_DEFAULTS["country"]
    region: str = _DEVICE_DEFAULTS["region"]
    language: str = _DEVICE_DEFAULTS["language"]
    user_language: str = _DEVICE_DEFAULTS["user_language"]

    # --- device / extraInfo ---
    client_identity: str = _DEVICE_DEFAULTS["client_identity"]
    carrier: str = _DEVICE_DEFAULTS["carrier"]
    bootloader_version: str = _DEVICE_DEFAULTS["bootloader_version"]
    fingerprint: str = _DEVICE_DEFAULTS["fingerprint"]
    radio_version: str = _DEVICE_DEFAULTS["radio_version"]
    build_tags: str = _DEVICE_DEFAULTS["build_tags"]
    build_type: str = _DEVICE_DEFAULTS["build_type"]
    build_device: str = _DEVICE_DEFAULTS["build_device"]
    build_id: str = _DEVICE_DEFAULTS["build_id"]
    build_display_id: str = _DEVICE_DEFAULTS["build_display_id"]
    build_incremental_version: str = _DEVICE_DEFAULTS["build_incremental_version"]
    release_version: str = _DEVICE_DEFAULTS["release_version"]
    ota_source_sha1: str = _DEVICE_DEFAULTS["ota_source_sha1"]
    network: str = _DEVICE_DEFAULTS["network"]
    apk_version: int = int(_DEVICE_DEFAULTS["apk_version"])
    provisioned_time: int = int(_DEVICE_DEFAULTS["provisioned_time"])
    incremental_version: int = int(_DEVICE_DEFAULTS["incremental_version"])
    additional_info: str = _DEVICE_DEFAULTS["additional_info"]
    user_location: str = _DEVICE_DEFAULTS["user_location"]
    bootloader_status: str = _DEVICE_DEFAULTS["bootloader_status"]
    device_rooted: str = _DEVICE_DEFAULTS["device_rooted"]
    is_4gb_ram: bool = False
    device_chipset: str = _DEVICE_DEFAULTS["device_chipset"]

    # --- identityInfo ---
    serial_number: str = _IDENTITY_DEFAULTS["serial_number"]

    # --- IMEI / SIM fields (BuildPropReader.smali lines 671-1100+) ---
    imei: str = _IDENTITY_DEFAULTS["imei"]
    imei2: str = _IDENTITY_DEFAULTS["imei2"]
    mccmnc: str = _IDENTITY_DEFAULTS["mccmnc"]
    mccmnc2: str = _IDENTITY_DEFAULTS["mccmnc2"]

    # --- identity ---
    id_type: str = _IDENTITY_DEFAULTS["id_type"]

    # --- download ---
    output_dir: Path = Path(_DOWNLOAD_DEFAULTS["output_dir"])
    verify_checksum: bool = True


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def _read_ini(path: Path | None, search_paths: list[Path], label: str) -> configparser.ConfigParser:
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
                label,
                resolved,
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


def load_config(
    path: Path | None = None,
    *,
    device_path: Path | None = None,
) -> Config:
    """Load configuration from ``config.ini`` and ``device.ini``.

    Server/download settings come from ``config.ini``.  Device-specific
    parameters (IMEI, serial, build fingerprint, etc.) come from
    ``device.ini``.  Both fall back to evidence-based defaults.

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
        """Get from config.ini [server] or defaults."""
        try:
            return server_cp.get("server", key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return _SERVER_DEFAULTS.get(key, "")

    def _get_download(key: str) -> str:
        """Get from config.ini [download] or defaults."""
        try:
            return server_cp.get("download", key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return _DOWNLOAD_DEFAULTS.get(key, "")

    def _get_device(key: str) -> str:
        """Get from device.ini [device] or defaults."""
        try:
            return device_cp.get("device", key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return _DEVICE_DEFAULTS.get(key, "")

    def _get_identity(key: str) -> str:
        """Get from device.ini [identity] or defaults."""
        try:
            return device_cp.get("identity", key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return _IDENTITY_DEFAULTS.get(key, "")

    def _getint(getter: object, key: str) -> int:
        val = getter(key)  # type: ignore[operator]
        return int(val) if val else 0

    def _getbool(getter: object, key: str) -> bool:
        val = getter(key).lower()  # type: ignore[operator]
        return val in ("true", "yes", "1", "on")

    retry_raw = _get_server("retry_delays_ms")
    retry_delays = [int(v.strip()) for v in retry_raw.split(",") if v.strip()]

    return Config(
        # --- server (from config.ini) ---
        server_url=_get_server("url"),
        check_path=_get_server("check_path"),
        resources_path=_get_server("resources_path"),
        state_path=_get_server("state_path"),
        context=_get_server("context"),
        timeout=_getint(_get_server, "timeout"),
        retry_delays_ms=retry_delays,
        # --- device info (from device.ini) ---
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
        # --- identity (from device.ini) ---
        serial_number=_get_identity("serial_number"),
        imei=_get_identity("imei"),
        imei2=_get_identity("imei2"),
        mccmnc=_get_identity("mccmnc"),
        mccmnc2=_get_identity("mccmnc2"),
        id_type=_get_identity("id_type"),
        # --- download (from config.ini) ---
        output_dir=Path(_get_download("output_dir") or "output"),
        verify_checksum=_getbool(_get_download, "verify_checksum"),
    )
