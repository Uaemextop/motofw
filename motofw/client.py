"""
HTTP client module for Motofw.

Provides OTAClient class for communicating with Motorola's OTA servers
using the same protocol as the official Motorola CCC OTA app.
"""

import json
import logging
import time
from typing import Dict, Optional, Any
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import Config
from .device_info import DeviceInfo

logger = logging.getLogger(__name__)


class OTAClient:
    """HTTP client for Motorola OTA server communication."""

    def __init__(
        self,
        device_info: DeviceInfo,
        config: Optional[Config] = None,
        use_staging: bool = False,
    ):
        """
        Initialize OTA client.

        Args:
            device_info: Device information for requests
            config: Configuration object (creates default if None)
            use_staging: Use staging environment instead of production
        """
        self.device_info = device_info
        self.config = config or Config()
        self.use_staging = use_staging
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """
        Create configured requests session with retry logic.

        Returns:
            Configured requests.Session object
        """
        session = requests.Session()

        # Configure retry strategy
        retries = self.config.get_http_retries()
        retry_strategy = Retry(
            total=retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Configure proxy if specified
        proxy_host = self.config.get_proxy_host()
        proxy_port = self.config.get_proxy_port()
        if proxy_host and proxy_port:
            proxy_url = f"http://{proxy_host}:{proxy_port}"
            session.proxies = {
                "http": proxy_url,
                "https": proxy_url,
            }
            logger.info(f"Using proxy: {proxy_url}")

        # Set default headers
        session.headers.update(self._get_default_headers())

        return session

    def _get_default_headers(self) -> Dict[str, str]:
        """
        Get default HTTP headers for requests.

        Returns:
            Dictionary of default headers
        """
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": self.config.get_user_agent(),
            "Connection": "Keep-Alive",
        }

    def _get_base_url(self) -> str:
        """
        Get base URL for API requests.

        Returns:
            Base URL with protocol and host
        """
        protocol = "https" if self.config.use_https() else "http"
        host = self.config.get_api_host(
            is_prc=self.device_info.is_prc,
            use_staging=self.use_staging,
        )
        return f"{protocol}://{host}"

    def check_for_update(
        self, upgrade_source: str = "UPGRADED_VIA_PULL"
    ) -> Dict[str, Any]:
        """
        Check for available firmware updates.

        Args:
            upgrade_source: Update trigger source (default: "UPGRADED_VIA_PULL")
                Options: UPGRADED_VIA_PULL, UPGRADED_VIA_PAIR,
                        UPGRADED_VIA_INTIAL_SETUP, UPGRADED_VIA_UNKNOWN_METHOD

        Returns:
            Dictionary containing server response

        Raises:
            requests.RequestException: If request fails
        """
        url = urljoin(
            self._get_base_url(),
            self.config.get_check_update_endpoint(),
        )

        payload = self._build_check_update_payload(upgrade_source)

        logger.info(f"Checking for updates at {url}")
        logger.debug(f"Request payload: {json.dumps(payload, indent=2)}")

        response = self.session.post(
            url,
            json=payload,
            timeout=self.config.get_http_timeout(),
        )
        response.raise_for_status()

        result = response.json()
        logger.debug(f"Response: {json.dumps(result, indent=2)}")

        return result

    def get_download_descriptor(
        self, tracking_id: str, context_timestamp: int
    ) -> Dict[str, Any]:
        """
        Get download descriptor with resource URLs.

        Args:
            tracking_id: Tracking ID from check update response
            context_timestamp: Context timestamp from check update response

        Returns:
            Dictionary containing download URLs and headers

        Raises:
            requests.RequestException: If request fails
        """
        url = urljoin(
            self._get_base_url(),
            self.config.get_download_descriptor_endpoint(),
        )

        payload = self._build_download_descriptor_payload(
            tracking_id, context_timestamp
        )

        logger.info(f"Getting download descriptor at {url}")
        logger.debug(f"Request payload: {json.dumps(payload, indent=2)}")

        response = self.session.post(
            url,
            json=payload,
            timeout=self.config.get_http_timeout(),
        )
        response.raise_for_status()

        result = response.json()
        logger.debug(f"Response: {json.dumps(result, indent=2)}")

        return result

    def _build_check_update_payload(self, upgrade_source: str) -> Dict[str, Any]:
        """
        Build check update request payload.

        Args:
            upgrade_source: Update trigger source

        Returns:
            Dictionary matching Motorola's check update request format
        """
        return {
            "request": {
                "serialNumber": self.device_info.serial_number,
                "timestamp": 0,
                "deviceInfo": self.device_info.to_device_info_dict(),
                "extraInfo": self.device_info.to_extra_info_dict(),
                "identityInfo": self.device_info.to_identity_info_dict(),
                "upgradeSource": upgrade_source,
            }
        }

    def _build_download_descriptor_payload(
        self, tracking_id: str, context_timestamp: int
    ) -> Dict[str, Any]:
        """
        Build download descriptor request payload.

        Args:
            tracking_id: Tracking ID from previous response
            context_timestamp: Context timestamp from previous response

        Returns:
            Dictionary matching Motorola's download descriptor request format
        """
        return {
            "serialNumber": self.device_info.serial_number,
            "timestamp": context_timestamp,
            "deviceInfo": self.device_info.to_device_info_dict(),
            "extraInfo": self.device_info.to_extra_info_dict(),
            "identityInfo": self.device_info.to_identity_info_dict(),
            "fieldName": "serialNumber",
            "reportingTag": tracking_id,
        }

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
