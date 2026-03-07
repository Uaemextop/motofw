"""INI file reader shared by config.ini and device.ini loaders."""

from __future__ import annotations

import configparser
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def read_ini(
    path: Path | None,
    search_paths: list[Path],
    label: str,
) -> configparser.ConfigParser:
    """Read an INI file from an explicit path or search locations.

    Parameters
    ----------
    path:
        Explicit file path.  When *None* the *search_paths* are tried.
    search_paths:
        Ordered list of candidate locations.
    label:
        Human-readable label for log messages (e.g. ``"config.ini"``).

    Returns
    -------
    configparser.ConfigParser
        Populated parser (may be empty if nothing was found).
    """
    cp = configparser.ConfigParser()

    if path is not None:
        resolved = Path(path)
        if resolved.exists():
            cp.read(resolved)
            logger.info("Loaded %s from %s", label, resolved)
        else:
            logger.warning("%s not found at %s — using defaults", label, resolved)
    else:
        for candidate in search_paths:
            if candidate.exists():
                cp.read(candidate)
                logger.info("Loaded %s from %s", label, candidate)
                break
        else:
            logger.info("No %s found — using defaults", label)

    return cp


def get_value(
    cp: configparser.ConfigParser,
    section: str,
    key: str,
    fallback: str = "",
) -> str:
    """Retrieve a value from *cp* with a fallback."""
    try:
        return cp.get(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError):
        return fallback


def get_int(
    cp: configparser.ConfigParser,
    section: str,
    key: str,
    fallback: str = "0",
) -> int:
    """Retrieve an integer from *cp* with a fallback."""
    raw = get_value(cp, section, key, fallback)
    return int(raw) if raw else 0


def get_bool(
    cp: configparser.ConfigParser,
    section: str,
    key: str,
    fallback: str = "false",
) -> bool:
    """Retrieve a boolean from *cp* with a fallback."""
    raw = get_value(cp, section, key, fallback).lower()
    return raw in ("true", "yes", "1", "on")
