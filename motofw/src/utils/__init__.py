"""Utils subpackage — shared helpers used across the project.

Modules
-------
downloader
    Streaming firmware downloader with MD5 checksum verification.
filename
    Filename sanitisation for server-supplied names.
models
    Shared request / response data models (CheckRequest, CheckResponse, etc.).
"""

from motofw.src.utils.downloader import ChecksumMismatchError, download_update, verify_md5
from motofw.src.utils.filename import sanitize_filename
from motofw.src.utils.models import (
    CheckRequest,
    CheckResponse,
    ContentInfo,
    ContentResource,
    ResourcesRequest,
)

__all__ = [
    "CheckRequest",
    "CheckResponse",
    "ChecksumMismatchError",
    "ContentInfo",
    "ContentResource",
    "ResourcesRequest",
    "download_update",
    "sanitize_filename",
    "verify_md5",
]
