"""Crypto subpackage — cryptographic utilities for the OTA protocol.

Modules
-------
sha
    SHA-1 hashing used by the Motorola OTA client internally.
"""

from motofw.src.crypto.sha import compute_primary_key, generate_sha1

__all__ = ["compute_primary_key", "generate_sha1"]
