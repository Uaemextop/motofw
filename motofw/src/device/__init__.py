"""Device subpackage — device identity, parameters, and configuration.

Modules
-------
info
    Data models and builders for deviceInfo / extraInfo / identityInfo.
config
    Loader for ``device.ini`` (IMEI, serial number, build fingerprint, …).
"""

from motofw.src.device.info import (
    DeviceInfo,
    ExtraInfo,
    IdentityInfo,
    build_check_request,
    build_device_info,
    build_extra_info,
    build_identity_info,
    build_resources_request,
)
from motofw.src.device.config import load_device_config

__all__ = [
    "DeviceInfo",
    "ExtraInfo",
    "IdentityInfo",
    "build_check_request",
    "build_device_info",
    "build_extra_info",
    "build_identity_info",
    "build_resources_request",
    "load_device_config",
]
