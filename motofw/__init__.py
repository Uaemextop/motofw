"""motofw — Query and download OTA firmware updates from Motorola servers.

Public API
----------
- :func:`check_update` — Query the OTA server for available updates.
- :func:`get_resources` — Retrieve download resources for a known update.
- :func:`download_update` — Stream-download an OTA package with checksum verification.
- :class:`Config` — Parsed configuration container.
- Model dataclasses: :class:`CheckRequest`, :class:`CheckResponse`,
  :class:`ResourcesRequest`, :class:`ContentInfo`, :class:`ContentResource`.
"""

from motofw.config import Config, load_config
from motofw.crypto import compute_primary_key, generate_sha1
from motofw.models import (
    CheckRequest,
    CheckResponse,
    ContentInfo,
    ContentResource,
    DeviceInfo,
    ExtraInfo,
    IdentityInfo,
    ResourcesRequest,
)
from motofw.api import check_update, get_resources, report_state
from motofw.downloader import download_update

__all__ = [
    # Config
    "Config",
    "load_config",
    # Crypto
    "compute_primary_key",
    "generate_sha1",
    # Models
    "CheckRequest",
    "CheckResponse",
    "ContentInfo",
    "ContentResource",
    "DeviceInfo",
    "ExtraInfo",
    "IdentityInfo",
    "ResourcesRequest",
    # API
    "check_update",
    "get_resources",
    "report_state",
    # Downloader
    "download_update",
]

__version__ = "0.1.0"
