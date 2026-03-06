"""Tests for motofw.crypto — SHA-1 hashing and primaryKey computation.

Every test value is derived from known device evidence or verified against
the algorithm described in the Motorola OTA smali code.
"""

from __future__ import annotations

import hashlib

from motofw.crypto import compute_primary_key, generate_sha1

from .conftest import EVIDENCE_IMEI, EVIDENCE_OTA_SOURCE_SHA1, EVIDENCE_SERIAL_NUMBER


class TestGenerateSHA1:
    """Tests for the SHA-1 hash function that mirrors BuildPropertyUtils.generateSHA1."""

    def test_returns_40_char_hex(self) -> None:
        result = generate_sha1("test")
        assert len(result) == 40
        assert all(c in "0123456789abcdef" for c in result)

    def test_known_value(self) -> None:
        """SHA-1 of the empty string is the well-known constant."""
        expected = hashlib.sha1(b"").hexdigest()
        assert generate_sha1("") == expected

    def test_matches_hashlib(self) -> None:
        """Output must match Python's hashlib.sha1 for any input."""
        test_input = "hello world"
        expected = hashlib.sha1(test_input.encode()).hexdigest()
        assert generate_sha1(test_input) == expected

    def test_evidence_serial(self) -> None:
        """SHA-1 of the evidence serial number produces a valid hash."""
        result = generate_sha1(EVIDENCE_SERIAL_NUMBER)
        assert len(result) == 40
        assert result == hashlib.sha1(EVIDENCE_SERIAL_NUMBER.encode()).hexdigest()

    def test_lowercase_output(self) -> None:
        """Output must be lowercase hex (matches smali %02x format)."""
        result = generate_sha1("ABC")
        assert result == result.lower()


class TestComputePrimaryKey:
    """Tests for primaryKey = SHA1(contextKey + serialNumber).

    Evidence: CheckRequestObj.smali getPrimaryKey() method.
    """

    def test_concatenation_and_hash(self) -> None:
        """primaryKey must equal SHA-1 of direct concatenation (no separator)."""
        ctx = EVIDENCE_OTA_SOURCE_SHA1
        sn = EVIDENCE_SERIAL_NUMBER
        expected = hashlib.sha1((ctx + sn).encode()).hexdigest()
        assert compute_primary_key(ctx, sn) == expected

    def test_returns_40_char_hex(self) -> None:
        result = compute_primary_key(EVIDENCE_OTA_SOURCE_SHA1, EVIDENCE_SERIAL_NUMBER)
        assert len(result) == 40
        assert all(c in "0123456789abcdef" for c in result)

    def test_empty_context_key_returns_empty(self) -> None:
        """Matches smali guard: if contextKey is empty, return empty."""
        assert compute_primary_key("", EVIDENCE_SERIAL_NUMBER) == ""

    def test_empty_serial_returns_empty(self) -> None:
        """Matches smali guard: if serialNumber is empty, return empty."""
        assert compute_primary_key(EVIDENCE_OTA_SOURCE_SHA1, "") == ""

    def test_both_empty_returns_empty(self) -> None:
        assert compute_primary_key("", "") == ""

    def test_evidence_values(self) -> None:
        """Verify with the real evidence context key and serial number."""
        result = compute_primary_key(
            EVIDENCE_OTA_SOURCE_SHA1,
            EVIDENCE_SERIAL_NUMBER,
        )
        # Manually verify: SHA1("23d670d5d06f351" + "ZY32LNRW97")
        manual = hashlib.sha1(b"23d670d5d06f351ZY32LNRW97").hexdigest()
        assert result == manual

    def test_different_serials_differ(self) -> None:
        """Two different serial numbers must produce different keys."""
        key1 = compute_primary_key(EVIDENCE_OTA_SOURCE_SHA1, "SERIAL_A")
        key2 = compute_primary_key(EVIDENCE_OTA_SOURCE_SHA1, "SERIAL_B")
        assert key1 != key2

    def test_imei_can_be_used_as_input(self) -> None:
        """IMEI is not used for primaryKey per smali, but hashing must still work."""
        result = generate_sha1(EVIDENCE_IMEI)
        assert len(result) == 40
