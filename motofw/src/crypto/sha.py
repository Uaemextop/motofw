"""SHA-1 hashing utilities for the Motorola OTA protocol.

The only cryptographic operation used by the Motorola OTA client is SHA-1:

1. **``generateSHA1``** — hash an arbitrary string (40-char hex digest).
   Found in ``BuildPropertyUtils.smali``.

2. **``primaryKey``** — ``SHA1(contextKey + serialNumber)``, used
   internally for logging.  **Not** transmitted to the server.
   Found in ``CheckRequestObj.smali``.

No symmetric/asymmetric encryption or HMAC was found in the APK.
"""

from __future__ import annotations

import hashlib
import logging

logger = logging.getLogger(__name__)


def generate_sha1(value: str) -> str:
    """Compute the SHA-1 hex digest of *value*.

    Replicates ``BuildPropertyUtils.generateSHA1()``.

    Parameters
    ----------
    value:
        The input string to hash.

    Returns
    -------
    str
        40-character lowercase hex digest.
    """
    digest = hashlib.sha1(value.encode()).hexdigest()
    logger.debug("SHA-1(%r) = %s", value, digest)
    return digest


def compute_primary_key(context_key: str, serial_number: str) -> str:
    """Compute the internal ``primaryKey = SHA1(contextKey + serial)``.

    Replicates ``CheckRequestObj.getPrimaryKey()``.  This value is
    **not** sent to the server.

    Parameters
    ----------
    context_key:
        ``ro.mot.build.guid`` value (e.g. ``"96398c9adf48ac1"``).
    serial_number:
        Device serial (e.g. ``"ZY32LNRW97"``).

    Returns
    -------
    str
        40-char lowercase hex SHA-1 digest, or ``""`` if inputs are empty.
    """
    if not context_key or not serial_number:
        logger.warning(
            "Cannot compute primaryKey: context_key=%r, serial_number=%r",
            context_key, serial_number,
        )
        return ""
    concatenated = context_key + serial_number
    primary_key = generate_sha1(concatenated)
    logger.debug(
        "primaryKey = SHA1(%r + %r) = %s",
        context_key, serial_number, primary_key,
    )
    return primary_key
