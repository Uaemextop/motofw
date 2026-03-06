"""
Configuration module for Motofw.

Handles loading configuration from config.ini and provides default values
for API endpoints, timeouts, retries, and other settings.
"""

import configparser
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for Motofw."""

    # Default API endpoints
    DEFAULT_PRODUCTION_HOST = "moto-cds.appspot.com"
    DEFAULT_STAGING_HOST = "moto-cds-staging.appspot.com"
    DEFAULT_PRC_HOST = "moto-cds.svcmot.cn"
    DEFAULT_PRC_DEV_HOST = "ota-cn-sdc.blurdev.com"

    # Default settings
    DEFAULT_HTTP_TIMEOUT = 30
    DEFAULT_HTTP_RETRIES = 3
    DEFAULT_USE_HTTPS = True

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to config.ini file. If None, uses default locations.
        """
        self.config = configparser.ConfigParser()
        self._load_config(config_path)

    def _load_config(self, config_path: Optional[Path]) -> None:
        """Load configuration from file."""
        if config_path and config_path.exists():
            self.config.read(config_path)
            logger.info(f"Loaded configuration from {config_path}")
        else:
            # Try default locations
            default_paths = [
                Path.cwd() / "config.ini",
                Path.home() / ".motofw" / "config.ini",
            ]
            for path in default_paths:
                if path.exists():
                    self.config.read(path)
                    logger.info(f"Loaded configuration from {path}")
                    break
            else:
                logger.warning("No config.ini found, using default settings")

    def get_api_host(self, is_prc: bool = False, use_staging: bool = False) -> str:
        """
        Get API host based on region and environment.

        Args:
            is_prc: True if device is in PRC (China) region
            use_staging: True to use staging environment

        Returns:
            API host URL
        """
        section = "api"
        if is_prc:
            key = "prc_dev_host" if use_staging else "prc_host"
            default = self.DEFAULT_PRC_DEV_HOST if use_staging else self.DEFAULT_PRC_HOST
        else:
            key = "staging_host" if use_staging else "production_host"
            default = self.DEFAULT_STAGING_HOST if use_staging else self.DEFAULT_PRODUCTION_HOST

        return self.config.get(section, key, fallback=default)

    def get_check_update_endpoint(self) -> str:
        """Get the check update API endpoint."""
        return self.config.get("api", "check_update_endpoint", fallback="/check")

    def get_download_descriptor_endpoint(self) -> str:
        """Get the download descriptor API endpoint."""
        return self.config.get(
            "api", "download_descriptor_endpoint", fallback="/descriptor"
        )

    def get_http_timeout(self) -> int:
        """Get HTTP timeout in seconds."""
        return self.config.getint("http", "timeout", fallback=self.DEFAULT_HTTP_TIMEOUT)

    def get_http_retries(self) -> int:
        """Get number of HTTP retries."""
        return self.config.getint("http", "retries", fallback=self.DEFAULT_HTTP_RETRIES)

    def use_https(self) -> bool:
        """Check if HTTPS should be used."""
        return self.config.getboolean("http", "use_https", fallback=self.DEFAULT_USE_HTTPS)

    def get_proxy_host(self) -> Optional[str]:
        """Get HTTP proxy host."""
        return self.config.get("http", "proxy_host", fallback=None)

    def get_proxy_port(self) -> Optional[int]:
        """Get HTTP proxy port."""
        port = self.config.get("http", "proxy_port", fallback=None)
        return int(port) if port else None

    def get_user_agent(self) -> str:
        """Get User-Agent header."""
        return self.config.get(
            "http",
            "user_agent",
            fallback="motofw/0.1.0 (Python; OTA Client)",
        )
