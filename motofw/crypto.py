"""Cryptographic utilities for Motorola OTA protocol.

The only cryptographic operation used by the Motorola OTA client is SHA-1,
which serves two purposes:

1. **``generateSHA1``** — hash an arbitrary string and return its 40-char
   lowercase hex digest.  Found in
   ``BuildPropertyUtils.smali`` (``generateSHA1`` method).

2. **``primaryKey``** computation — ``SHA1(contextKey + serialNumber)``,
   used **internally** by the app for logging / database storage.  It is
   **not** transmitted to the server.  Found in
   ``CheckRequestObj.smali`` (``getPrimaryKey`` method).

No symmetric (AES/DES) or asymmetric (RSA) encryption, HMAC signing,
or native ``.so`` crypto libraries were found in the decompiled APK.
All server communication relies on HTTPS for confidentiality.
"""

from __future__ import annotations

import hashlib
import logging

logger = logging.getLogger(__name__)


def generate_sha1(value: str) -> str:
    """Compute the SHA-1 hex digest of *value*.

    Replicates the exact ``BuildPropertyUtils.generateSHA1()`` method
    from ``smali_classes2/com/motorola/otalib/common/utils/BuildPropertyUtils.smali``:

    .. code-block:: java

        MessageDigest md = MessageDigest.getInstance("SHA-1");
        md.update(value.getBytes());
        byte[] digest = md.digest();
        // each byte formatted as "%02x"

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
    """Compute the internal ``primaryKey`` used by the OTA app.

    Replicates ``CheckRequestObj.getPrimaryKey()`` from
    ``smali_classes2/com/motorola/otalib/main/checkUpdate/CheckRequestObj.smali``:

    .. code-block:: java

        String concat = contextKey.concat(accsSerialNumber);
        primaryKey = SHA1Generator(concat);

    .. note::

        The ``primaryKey`` is used **only** for internal logging and
        database storage.  It is **not** sent to the Motorola OTA server
        in any request header or body.

    Parameters
    ----------
    context_key:
        The device's ``ro.mot.build.guid`` value (e.g. ``"23d670d5d06f351"``).
    serial_number:
        The device serial number (e.g. ``"ZY32LNRW97"``).

    Returns
    -------
    str
        40-character lowercase hex SHA-1 digest of the concatenation.
    """
    if not context_key or not serial_number:
        logger.warning(
            "Cannot compute primaryKey: context_key=%r, serial_number=%r",
            context_key,
            serial_number,
        )
        return ""
    concatenated = context_key + serial_number
    primary_key = generate_sha1(concatenated)
    logger.debug(
        "primaryKey = SHA1(%r + %r) = %s",
        context_key,
        serial_number,
        primary_key,
    )
    return primary_key
