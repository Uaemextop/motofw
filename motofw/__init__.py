"""
Motofw - A Python tool for querying and downloading OTA firmware updates from Motorola's update servers.

This package provides modular components for:
- Querying available firmware updates
- Downloading OTA packages
- Parsing firmware metadata
- Verifying checksums
"""

__version__ = "0.1.0"
__author__ = "Motofw Contributors"

from .client import OTAClient
from .device_info import DeviceInfo
from .parser import ResponseParser
from .downloader import FirmwareDownloader

__all__ = [
    "OTAClient",
    "DeviceInfo",
    "ResponseParser",
    "FirmwareDownloader",
]
