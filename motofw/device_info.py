"""
Device information module for Motofw.

Provides DeviceInfo class to manage device-specific parameters
required for OTA server communication.
"""

import hashlib
import time
from typing import Optional


class DeviceInfo:
    """Device information container for OTA requests."""

    def __init__(
        self,
        serial_number: str,
        model: str,
        product: str,
        build_id: str,
        build_device: Optional[str] = None,
        carrier: Optional[str] = None,
        color_id: Optional[str] = None,
        is_prc: bool = False,
        user_language: str = "en-US",
    ):
        """
        Initialize device information.

        Args:
            serial_number: Device serial number (required for authentication)
            model: Device model identifier
            product: Product name
            build_id: Current firmware build ID
            build_device: Internal device name (defaults to model)
            carrier: Telecom carrier identifier
            color_id: Device color variant
            is_prc: True if device is in PRC (China) region
            user_language: User language/locale (e.g., "en-US", "zh-CN")
        """
        self.serial_number = serial_number
        self.model = model
        self.product = product
        self.build_id = build_id
        self.build_device = build_device or model
        self.carrier = carrier or "unknown"
        self.color_id = color_id or "default"
        self.is_prc = is_prc
        self.user_language = user_language
        self.manufacturer = "Motorola"

    def get_context_key(self) -> str:
        """
        Generate context key (SHA1 hash of build ID).

        Returns:
            SHA1 hash of the current firmware build ID
        """
        return hashlib.sha1(self.build_id.encode()).hexdigest()

    def get_primary_key(self) -> str:
        """
        Generate primary key for device identification.

        The primary key is a SHA1 hash of (contextKey + serialNumber)
        as per the Motorola OTA protocol.

        Returns:
            SHA1 hash combining context key and serial number
        """
        context_key = self.get_context_key()
        combined = context_key + self.serial_number
        return hashlib.sha1(combined.encode()).hexdigest()

    def to_device_info_dict(self) -> dict:
        """
        Convert to deviceInfo JSON structure.

        Returns:
            Dictionary matching Motorola's deviceInfo format
        """
        return {
            "manufacturer": self.manufacturer,
            "model": self.model,
            "product": self.product,
            "isPRC": self.is_prc,
            "carrier": self.carrier,
            "userLanguage": self.user_language,
        }

    def to_extra_info_dict(self, apk_version: str = "1.0.0") -> dict:
        """
        Convert to extraInfo JSON structure.

        Args:
            apk_version: Version of the OTA client app

        Returns:
            Dictionary matching Motorola's extraInfo format
        """
        return {
            "clientIdentity": "motorola-ota-client-app",
            "brand": self.color_id,
            "buildDevice": self.build_device,
            "otaSourceSha1": self.get_context_key(),
            "buildId": self.build_id,
            "buildDisplayId": self.build_id,
            "network": "unknown",
            "provisionedTime": int(time.time() * 1000),
            "colorId": self.color_id,
            "apkPackageName": "com.motorola.ccc.ota",
            "apkVersion": apk_version,
            "OtaLibVersion": 0x30D44,
            "mobileModel": self.model,
            "clientState": "IDLE",
        }

    def to_identity_info_dict(self) -> dict:
        """
        Convert to identityInfo JSON structure.

        Returns:
            Dictionary matching Motorola's identityInfo format
        """
        return {
            "serialNumber": self.serial_number,
        }
