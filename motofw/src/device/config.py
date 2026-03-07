"""Device configuration loader for ``device.ini``.

Reads device-specific parameters (IMEI, serial number, build
fingerprint, etc.) from ``device.ini`` and returns them as a dict
that can be merged into :class:`~motofw.src.config.settings.Config`.
"""

from __future__ import annotations

import configparser
import logging
from pathlib import Path
from typing import Dict

from motofw.src.config.settings import DEVICE_DEFAULTS, IDENTITY_DEFAULTS

logger = logging.getLogger(__name__)

_DEVICE_SEARCH_PATHS: list[Path] = [
    Path("device.ini"),
    Path.home() / ".config" / "motofw" / "device.ini",
]


def load_device_config(path: Path | None = None) -> Dict[str, str]:
    """Load device-specific values from ``device.ini``.

    Parameters
    ----------
    path:
        Explicit path.  When ``None`` the default search locations are tried.

    Returns
    -------
    dict
        Flat dict of all device + identity keys.
    """
    cp = configparser.ConfigParser()

    if path is not None:
        resolved = Path(path)
        if resolved.exists():
            cp.read(resolved)
            logger.info("Loaded device.ini from %s", resolved)
        else:
            logger.warning("device.ini not found at %s; using defaults", resolved)
    else:
        for candidate in _DEVICE_SEARCH_PATHS:
            if candidate.exists():
                cp.read(candidate)
                logger.info("Loaded device.ini from %s", candidate)
                break
        else:
            logger.info("No device.ini found; using evidence-based defaults")

    def _get_device(key: str) -> str:
        try:
            return cp.get("device", key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return DEVICE_DEFAULTS.get(key, "")

    def _get_identity(key: str) -> str:
        try:
            return cp.get("identity", key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return IDENTITY_DEFAULTS.get(key, "")

    result: Dict[str, str] = {}
    for key in DEVICE_DEFAULTS:
        result[key] = _get_device(key)
    for key in IDENTITY_DEFAULTS:
        result[key] = _get_identity(key)
    return result
