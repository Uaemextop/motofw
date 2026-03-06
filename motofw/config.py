"""Configuration loader for motofw.

All user-configurable values live in ``config.ini`` and are parsed here
using :mod:`configparser`.  Hard-coded defaults mirror the values
extracted from Motorola smali evidence so the tool works out of the box
when no ``config.ini`` is present.
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

_DEFAULTS: dict[str, dict[str, str]] = {
    "server": {
        "url": "moto-cds.appspot.com",
        "check_path": "cds/upgrade/1/check",
        "resources_path": "cds/upgrade/1/resources",
        "state_path": "cds/upgrade/1/state",
        "context": "ota",
        "timeout": "60",
        "retry_delays_ms": "5000,15000,30000",
    },
    "device": {
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
        "fingerprint": "motorola/lamul_g/lamul:15/VVTA35.51-28-15/bd4d30:user/release-keys",
        "radio_version": "",
        "build_tags": "release-keys",
        "build_type": "user",
        "build_device": "lamul",
        "build_id": "VVTA35.51-28-15",
        "build_display_id": "VVTA35.51-28-15",
        "build_incremental_version": "",
        "release_version": "15",
        "ota_source_sha1": "23d670d5d06f351",
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
        "serial_number": "ZY32LNRW97",
        "imei": "359488357396203",
        "imei2": "",
        "mccmnc": "",
        "mccmnc2": "",
    },
    "identity": {
        "id_type": "serialNumber",
    },
    "download": {
        "output_dir": "output",
        "verify_checksum": "true",
    },
}

# Path search order — the first file that exists wins.
_CONFIG_SEARCH_PATHS: list[Path] = [
    Path("config.ini"),
    Path.home() / ".config" / "motofw" / "config.ini",
]


# ---------------------------------------------------------------------------
# Public dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Config:
    """Immutable container for all motofw configuration values.

    Every field corresponds to a ``config.ini`` key and carries the
    evidence-based default when no file is present.
    """

    # --- server ---
    server_url: str = _DEFAULTS["server"]["url"]
    check_path: str = _DEFAULTS["server"]["check_path"]
    resources_path: str = _DEFAULTS["server"]["resources_path"]
    state_path: str = _DEFAULTS["server"]["state_path"]
    context: str = _DEFAULTS["server"]["context"]
    timeout: int = int(_DEFAULTS["server"]["timeout"])
    retry_delays_ms: List[int] = field(
        default_factory=lambda: [5000, 15000, 30000]
    )

    # --- device / deviceInfo ---
    manufacturer: str = _DEFAULTS["device"]["manufacturer"]
    hardware: str = _DEFAULTS["device"]["hardware"]
    brand: str = _DEFAULTS["device"]["brand"]
    model: str = _DEFAULTS["device"]["model"]
    product: str = _DEFAULTS["device"]["product"]
    os: str = _DEFAULTS["device"]["os"]
    os_version: str = _DEFAULTS["device"]["os_version"]
    country: str = _DEFAULTS["device"]["country"]
    region: str = _DEFAULTS["device"]["region"]
    language: str = _DEFAULTS["device"]["language"]
    user_language: str = _DEFAULTS["device"]["user_language"]

    # --- device / extraInfo ---
    client_identity: str = _DEFAULTS["device"]["client_identity"]
    carrier: str = _DEFAULTS["device"]["carrier"]
    bootloader_version: str = _DEFAULTS["device"]["bootloader_version"]
    fingerprint: str = _DEFAULTS["device"]["fingerprint"]
    radio_version: str = _DEFAULTS["device"]["radio_version"]
    build_tags: str = _DEFAULTS["device"]["build_tags"]
    build_type: str = _DEFAULTS["device"]["build_type"]
    build_device: str = _DEFAULTS["device"]["build_device"]
    build_id: str = _DEFAULTS["device"]["build_id"]
    build_display_id: str = _DEFAULTS["device"]["build_display_id"]
    build_incremental_version: str = _DEFAULTS["device"]["build_incremental_version"]
    release_version: str = _DEFAULTS["device"]["release_version"]
    ota_source_sha1: str = _DEFAULTS["device"]["ota_source_sha1"]
    network: str = _DEFAULTS["device"]["network"]
    apk_version: int = int(_DEFAULTS["device"]["apk_version"])
    provisioned_time: int = int(_DEFAULTS["device"]["provisioned_time"])
    incremental_version: int = int(_DEFAULTS["device"]["incremental_version"])
    additional_info: str = _DEFAULTS["device"]["additional_info"]
    user_location: str = _DEFAULTS["device"]["user_location"]
    bootloader_status: str = _DEFAULTS["device"]["bootloader_status"]
    device_rooted: str = _DEFAULTS["device"]["device_rooted"]
    is_4gb_ram: bool = False
    device_chipset: str = _DEFAULTS["device"]["device_chipset"]

    # --- identityInfo ---
    serial_number: str = _DEFAULTS["device"]["serial_number"]

    # --- IMEI / SIM fields (BuildPropReader.smali lines 671-1100+) ---
    imei: str = _DEFAULTS["device"]["imei"]
    imei2: str = _DEFAULTS["device"]["imei2"]
    mccmnc: str = _DEFAULTS["device"]["mccmnc"]
    mccmnc2: str = _DEFAULTS["device"]["mccmnc2"]

    # --- identity ---
    id_type: str = _DEFAULTS["identity"]["id_type"]

    # --- download ---
    output_dir: Path = Path(_DEFAULTS["download"]["output_dir"])
    verify_checksum: bool = True


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def load_config(path: Path | None = None) -> Config:
    """Load configuration from *path* or the first file found on the search path.

    Parameters
    ----------
    path:
        Explicit path to a ``config.ini`` file.  When ``None`` the
        default search locations are tried.

    Returns
    -------
    Config
        Populated configuration.  Missing keys fall back to evidence-based
        defaults.
    """
    cp = configparser.ConfigParser()

    if path is not None:
        resolved = Path(path)
        if resolved.exists():
            cp.read(resolved)
            logger.info("Loaded configuration from %s", resolved)
        else:
            logger.warning(
                "Specified config path %s does not exist; using defaults",
                resolved,
            )
    else:
        for candidate in _CONFIG_SEARCH_PATHS:
            if candidate.exists():
                cp.read(candidate)
                logger.info("Loaded configuration from %s", candidate)
                break
        else:
            logger.info("No config.ini found; using evidence-based defaults")

    def _get(section: str, key: str) -> str:
        """Return value from parsed file or the built-in default."""
        try:
            return cp.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return _DEFAULTS.get(section, {}).get(key, "")

    def _getint(section: str, key: str) -> int:
        val = _get(section, key)
        return int(val) if val else 0

    def _getbool(section: str, key: str) -> bool:
        val = _get(section, key).lower()
        return val in ("true", "yes", "1", "on")

    retry_raw = _get("server", "retry_delays_ms")
    retry_delays = [int(v.strip()) for v in retry_raw.split(",") if v.strip()]

    return Config(
        server_url=_get("server", "url"),
        check_path=_get("server", "check_path"),
        resources_path=_get("server", "resources_path"),
        state_path=_get("server", "state_path"),
        context=_get("server", "context"),
        timeout=_getint("server", "timeout"),
        retry_delays_ms=retry_delays,
        manufacturer=_get("device", "manufacturer"),
        hardware=_get("device", "hardware"),
        brand=_get("device", "brand"),
        model=_get("device", "model"),
        product=_get("device", "product"),
        os=_get("device", "os"),
        os_version=_get("device", "os_version"),
        country=_get("device", "country"),
        region=_get("device", "region"),
        language=_get("device", "language"),
        user_language=_get("device", "user_language"),
        client_identity=_get("device", "client_identity"),
        carrier=_get("device", "carrier"),
        bootloader_version=_get("device", "bootloader_version"),
        fingerprint=_get("device", "fingerprint"),
        radio_version=_get("device", "radio_version"),
        build_tags=_get("device", "build_tags"),
        build_type=_get("device", "build_type"),
        build_device=_get("device", "build_device"),
        build_id=_get("device", "build_id"),
        build_display_id=_get("device", "build_display_id"),
        build_incremental_version=_get("device", "build_incremental_version"),
        release_version=_get("device", "release_version"),
        ota_source_sha1=_get("device", "ota_source_sha1"),
        network=_get("device", "network"),
        apk_version=_getint("device", "apk_version"),
        provisioned_time=_getint("device", "provisioned_time"),
        incremental_version=_getint("device", "incremental_version"),
        additional_info=_get("device", "additional_info"),
        user_location=_get("device", "user_location"),
        bootloader_status=_get("device", "bootloader_status"),
        device_rooted=_get("device", "device_rooted"),
        is_4gb_ram=_getbool("device", "is_4gb_ram"),
        device_chipset=_get("device", "device_chipset"),
        serial_number=_get("device", "serial_number"),
        imei=_get("device", "imei"),
        imei2=_get("device", "imei2"),
        mccmnc=_get("device", "mccmnc"),
        mccmnc2=_get("device", "mccmnc2"),
        id_type=_get("identity", "id_type"),
        output_dir=Path(_get("download", "output_dir") or "output"),
        verify_checksum=_getbool("download", "verify_checksum"),
    )
