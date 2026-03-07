"""Read device.ini and return a flat dict of device + identity values."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict

from motofw.src.config.defaults import DEVICE_DEFAULTS, IDENTITY_DEFAULTS
from motofw.src.config.loader import get_value, read_ini

logger = logging.getLogger(__name__)

_SEARCH: list[Path] = [
    Path("device.ini"),
    Path.home() / ".config" / "motofw" / "device.ini",
]


def load_device_values(path: Path | None = None) -> Dict[str, str]:
    """Load device-specific values from ``device.ini``.

    Returns a flat dict with every device + identity key.
    """
    cp = read_ini(path, _SEARCH, "device.ini")

    result: Dict[str, str] = {}
    for key, fallback in DEVICE_DEFAULTS.items():
        result[key] = get_value(cp, "device", key, fallback)
    for key, fallback in IDENTITY_DEFAULTS.items():
        result[key] = get_value(cp, "identity", key, fallback)
    return result
