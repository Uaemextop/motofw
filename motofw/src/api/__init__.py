"""API subpackage — HTTP communication with Motorola OTA servers.

Modules
-------
headers
    Build and validate HTTP headers for OTA requests.
body
    Construct JSON request bodies from device configuration.
response
    Parse JSON responses from the server into model objects.
request
    Low-level HTTP request execution with retries.
session
    Shared HTTP session / connection pool management.
orchestrator
    High-level flow: check → resources → download.
"""

from motofw.src.api.orchestrator import check_update, download_firmware, get_resources, report_state
from motofw.src.api.session import OTASession

__all__ = [
    "check_update",
    "download_firmware",
    "get_resources",
    "report_state",
    "OTASession",
]
