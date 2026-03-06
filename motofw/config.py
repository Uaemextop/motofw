"""Configuration loader for motofw.

Reads ``config.ini`` using :mod:`configparser` and exposes typed helpers
so that the rest of the code base never has to reference raw strings.
"""

from __future__ import annotations

import configparser
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Default values extracted from the Motorola OTA smali source code.
_DEFAULTS: dict[str, dict[str, str]] = {
    "server": {
        "server_url": "moto-cds.appspot.com",
        "china_server_url": "moto-cds.svcmot.cn",
        "check_base_url": "cds/upgrade/1/check",
        "resources_base_url": "cds/upgrade/1/resources",
        "state_base_url": "cds/upgrade/1/state",
        "ota_context": "ota",
        "is_secure": "true",
        "check_http_method": "post",
        "resources_http_method": "post",
        "state_http_method": "post",
    },
    "device": {
        "serial_number": "",
        "model_id": "",
        "product": "",
        "internal_name": "",
        "manufacturer": "motorola",
        "carrier": "",
        "color_id": "",
        "source_version": "0",
        "ota_source_sha1": "",
        "is_prc_device": "false",
        "is_production_device": "true",
        "triggered_by": "user",
    },
    "http": {
        "timeout": "30",
        "max_retries": "3",
        "backoff_values": "5000,15000,30000",
        "proxy_host": "",
        "proxy_port": "-1",
    },
    "download": {
        "output_dir": "output",
    },
}


class Config:
    """Typed wrapper around a parsed ``config.ini``."""

    def __init__(self, path: Optional[Path] = None) -> None:
        """Load configuration from *path*.

        Parameters
        ----------
        path:
            Path to ``config.ini``.  When *None* the file ``config.ini`` in the
            current working directory is tried; if that does not exist the
            built-in defaults are used.
        """
        self._cp = configparser.ConfigParser()
        # Seed with defaults.
        self._cp.read_dict(_DEFAULTS)

        resolved: Optional[Path] = None
        if path is not None:
            resolved = Path(path)
        else:
            candidate = Path("config.ini")
            if candidate.is_file():
                resolved = candidate

        if resolved is not None and resolved.is_file():
            self._cp.read(resolved, encoding="utf-8")
            logger.info("Loaded configuration from %s", resolved)
        else:
            logger.info("No config.ini found — using built-in defaults")

    # -- server section -------------------------------------------------------

    @property
    def server_url(self) -> str:
        """Return the OTA server hostname."""
        return self._cp.get("server", "server_url")

    @property
    def china_server_url(self) -> str:
        """Return the China OTA server hostname."""
        return self._cp.get("server", "china_server_url")

    @property
    def check_base_url(self) -> str:
        """Return the base URL path for the check-for-upgrade endpoint."""
        return self._cp.get("server", "check_base_url")

    @property
    def resources_base_url(self) -> str:
        """Return the base URL path for the resources endpoint."""
        return self._cp.get("server", "resources_base_url")

    @property
    def state_base_url(self) -> str:
        """Return the base URL path for the state endpoint."""
        return self._cp.get("server", "state_base_url")

    @property
    def ota_context(self) -> str:
        """Return the OTA context identifier (e.g. ``ota``)."""
        return self._cp.get("server", "ota_context")

    @property
    def is_secure(self) -> bool:
        """Return whether HTTPS should be used."""
        return self._cp.get("server", "is_secure").lower() == "true"

    @property
    def check_http_method(self) -> str:
        """Return the HTTP method for check requests."""
        return self._cp.get("server", "check_http_method").upper()

    @property
    def resources_http_method(self) -> str:
        """Return the HTTP method for resources requests."""
        return self._cp.get("server", "resources_http_method").upper()

    @property
    def state_http_method(self) -> str:
        """Return the HTTP method for state requests."""
        return self._cp.get("server", "state_http_method").upper()

    # -- device section -------------------------------------------------------

    @property
    def serial_number(self) -> str:
        """Return the device serial number."""
        return self._cp.get("device", "serial_number")

    @property
    def model_id(self) -> str:
        """Return the device model identifier."""
        return self._cp.get("device", "model_id")

    @property
    def product(self) -> str:
        """Return the device product name."""
        return self._cp.get("device", "product")

    @property
    def internal_name(self) -> str:
        """Return the device internal name."""
        return self._cp.get("device", "internal_name")

    @property
    def manufacturer(self) -> str:
        """Return the device manufacturer."""
        return self._cp.get("device", "manufacturer")

    @property
    def carrier(self) -> str:
        """Return the carrier code."""
        return self._cp.get("device", "carrier")

    @property
    def color_id(self) -> str:
        """Return the device color identifier."""
        return self._cp.get("device", "color_id")

    @property
    def source_version(self) -> int:
        """Return the current firmware build version as a timestamp."""
        return self._cp.getint("device", "source_version")

    @property
    def ota_source_sha1(self) -> str:
        """Return the current OTA SHA1 (contextKey)."""
        return self._cp.get("device", "ota_source_sha1")

    @property
    def is_prc_device(self) -> bool:
        """Return whether the device is a PRC (China) device."""
        return self._cp.get("device", "is_prc_device").lower() == "true"

    @property
    def is_production_device(self) -> bool:
        """Return whether the device is a production device."""
        return self._cp.get("device", "is_production_device").lower() == "true"

    @property
    def triggered_by(self) -> str:
        """Return the trigger type for the update check."""
        return self._cp.get("device", "triggered_by")

    # -- http section ---------------------------------------------------------

    @property
    def timeout(self) -> int:
        """Return the HTTP timeout in seconds."""
        return self._cp.getint("http", "timeout")

    @property
    def max_retries(self) -> int:
        """Return the maximum retry count."""
        return self._cp.getint("http", "max_retries")

    @property
    def backoff_values(self) -> list[int]:
        """Return backoff intervals in milliseconds."""
        raw = self._cp.get("http", "backoff_values")
        return [int(v.strip()) for v in raw.split(",") if v.strip()]

    @property
    def proxy_host(self) -> str:
        """Return the HTTP proxy host (empty string means no proxy)."""
        return self._cp.get("http", "proxy_host")

    @property
    def proxy_port(self) -> int:
        """Return the HTTP proxy port (-1 means no proxy)."""
        return self._cp.getint("http", "proxy_port")

    # -- download section -----------------------------------------------------

    @property
    def output_dir(self) -> Path:
        """Return the output directory for downloaded firmware."""
        return Path(self._cp.get("download", "output_dir"))
