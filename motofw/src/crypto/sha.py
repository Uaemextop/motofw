"""SHA-1 utilities replicated from Motorola smali evidence.

``generateSHA1`` — from ``BuildPropertyUtils.smali``
``compute_primary_key`` — from ``CheckRequestObj.smali``

The primaryKey is internal only; it is never sent to the server.
"""

from __future__ import annotations

import hashlib
import logging

logger = logging.getLogger(__name__)


def generate_sha1(value: str) -> str:
    """Return the 40-char lowercase hex SHA-1 digest of *value*."""
    digest = hashlib.sha1(value.encode()).hexdigest()
    logger.debug("SHA-1(%r) = %s", value, digest)
    return digest


def compute_primary_key(context_key: str, serial_number: str) -> str:
    """Compute ``SHA1(contextKey + serialNumber)`` (internal use only).

    Returns an empty string when either input is empty.
    """
    if not context_key or not serial_number:
        return ""
    return generate_sha1(context_key + serial_number)
