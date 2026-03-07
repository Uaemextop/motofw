"""Tests for motofw.src.crypto.sha."""

from motofw.src.crypto.sha import compute_primary_key, generate_sha1


class TestSHA1:
    def test_generate_sha1(self):
        assert generate_sha1("hello") == "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d"

    def test_empty_string(self):
        assert generate_sha1("") == "da39a3ee5e6b4b0d3255bfef95601890afd80709"


class TestPrimaryKey:
    def test_known_pair(self):
        pk = compute_primary_key("23d670d5d06f351", "ZY32LNRW97")
        assert len(pk) == 40
        assert pk == generate_sha1("23d670d5d06f351ZY32LNRW97")

    def test_empty_context_key(self):
        assert compute_primary_key("", "ZY32LNRW97") == ""

    def test_empty_serial(self):
        assert compute_primary_key("abc", "") == ""
