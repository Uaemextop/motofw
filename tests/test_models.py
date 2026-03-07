"""Tests for motofw.src.utils.models."""

from motofw.src.utils.models import CheckResponse, ContentInfo, ContentResource


class TestContentInfo:
    def test_defaults(self):
        ci = ContentInfo()
        assert ci.package_id == ""
        assert ci.size == 0

    def test_with_values(self):
        ci = ContentInfo(package_id="test.zip", size=100, md5_checksum="abc")
        assert ci.size == 100


class TestContentResource:
    def test_defaults(self):
        cr = ContentResource()
        assert cr.url == ""
        assert cr.tags == []


class TestCheckResponse:
    def test_defaults(self):
        r = CheckResponse()
        assert r.proceed is False
        assert r.content is None
        assert r.content_resources == []

    def test_with_content(self, parsed_check_response: CheckResponse):
        assert parsed_check_response.proceed is True
        assert parsed_check_response.content is not None
        assert parsed_check_response.content.size == 354981143
