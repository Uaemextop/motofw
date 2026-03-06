"""Tests for motofw.models — dataclass serialisation.

All expected values come from log evidence.
"""

from __future__ import annotations

from motofw.models import (
    CheckRequest,
    ContentInfo,
    ContentResource,
    DeviceInfo,
    ExtraInfo,
    IdentityInfo,
    ResourcesRequest,
)
from tests.conftest import (
    EVIDENCE_APK_VERSION,
    EVIDENCE_BRAND,
    EVIDENCE_BUILD_ID,
    EVIDENCE_CLIENT_IDENTITY,
    EVIDENCE_DOWNLOAD_URL,
    EVIDENCE_HARDWARE,
    EVIDENCE_ID_TYPE,
    EVIDENCE_MANUFACTURER,
    EVIDENCE_MD5,
    EVIDENCE_MODEL,
    EVIDENCE_OS,
    EVIDENCE_OS_VERSION,
    EVIDENCE_OTA_SOURCE_SHA1,
    EVIDENCE_PACKAGE_ID,
    EVIDENCE_PRODUCT,
    EVIDENCE_SERIAL_NUMBER,
    EVIDENCE_SIZE,
    EVIDENCE_URL_TTL_SECONDS,
    EVIDENCE_VERSION,
)


class TestDeviceInfoSerialization:
    """Verify DeviceInfo.to_dict() produces evidence-matching JSON keys."""

    def test_to_dict_keys(self) -> None:
        di = DeviceInfo()
        d = di.to_dict()
        expected = {
            "manufacturer", "hardware", "brand", "model", "product",
            "os", "osVersion", "country", "region", "language", "userLanguage",
        }
        assert set(d.keys()) == expected

    def test_default_values(self) -> None:
        di = DeviceInfo()
        d = di.to_dict()
        assert d["manufacturer"] == EVIDENCE_MANUFACTURER
        assert d["hardware"] == EVIDENCE_HARDWARE
        assert d["brand"] == EVIDENCE_BRAND
        assert d["model"] == EVIDENCE_MODEL
        assert d["product"] == EVIDENCE_PRODUCT
        assert d["os"] == EVIDENCE_OS
        assert d["osVersion"] == EVIDENCE_OS_VERSION


class TestExtraInfoSerialization:
    """Verify ExtraInfo.to_dict() produces evidence-matching JSON keys."""

    def test_to_dict_has_client_identity(self) -> None:
        ei = ExtraInfo()
        d = ei.to_dict()
        assert d["clientIdentity"] == EVIDENCE_CLIENT_IDENTITY

    def test_to_dict_numeric_types(self) -> None:
        ei = ExtraInfo()
        d = ei.to_dict()
        assert isinstance(d["apkVersion"], int)
        assert d["apkVersion"] == EVIDENCE_APK_VERSION
        assert isinstance(d["is4GBRam"], bool)
        assert d["is4GBRam"] is False

    def test_ota_source_sha1(self) -> None:
        ei = ExtraInfo()
        d = ei.to_dict()
        assert d["otaSourceSha1"] == EVIDENCE_OTA_SOURCE_SHA1


class TestIdentityInfoSerialization:
    """Verify IdentityInfo.to_dict()."""

    def test_serial_number_key(self) -> None:
        ii = IdentityInfo()
        d = ii.to_dict()
        assert "serialNumber" in d
        assert d["serialNumber"] == EVIDENCE_SERIAL_NUMBER


class TestCheckRequestSerialization:
    """Verify CheckRequest.to_dict() matches log evidence structure."""

    def test_complete_structure(self) -> None:
        req = CheckRequest(request_id="req-001")
        d = req.to_dict()
        assert d["id"] == "req-001"
        assert d["contentTimestamp"] == 0
        assert d["triggeredBy"] == "user"
        assert d["idType"] == EVIDENCE_ID_TYPE
        assert "deviceInfo" in d
        assert "extraInfo" in d
        assert "identityInfo" in d

    def test_nested_device_info(self) -> None:
        req = CheckRequest()
        d = req.to_dict()
        assert d["deviceInfo"]["manufacturer"] == EVIDENCE_MANUFACTURER

    def test_nested_extra_info(self) -> None:
        req = CheckRequest()
        d = req.to_dict()
        assert d["extraInfo"]["buildId"] == EVIDENCE_BUILD_ID


class TestResourcesRequestSerialization:
    """Verify ResourcesRequest.to_dict() matches log evidence structure."""

    def test_complete_structure(self) -> None:
        req = ResourcesRequest(request_id="res-001")
        d = req.to_dict()
        assert d["id"] == "res-001"
        assert d["reportingTags"] == "TRIGGER-USER"
        assert d["reason"] is None
        assert d["idType"] == EVIDENCE_ID_TYPE

    def test_content_timestamp(self) -> None:
        req = ResourcesRequest(content_timestamp=1737698063000)
        d = req.to_dict()
        assert d["contentTimestamp"] == 1737698063000


class TestContentInfo:
    """Verify ContentInfo stores evidence values correctly."""

    def test_from_evidence(self) -> None:
        ci = ContentInfo(
            package_id=EVIDENCE_PACKAGE_ID,
            size=EVIDENCE_SIZE,
            md5_checksum=EVIDENCE_MD5,
            version=EVIDENCE_VERSION,
        )
        assert ci.package_id == EVIDENCE_PACKAGE_ID
        assert ci.size == EVIDENCE_SIZE
        assert ci.md5_checksum == EVIDENCE_MD5
        assert ci.version == EVIDENCE_VERSION


class TestContentResource:
    """Verify ContentResource stores evidence values correctly."""

    def test_from_evidence(self) -> None:
        cr = ContentResource(
            url=EVIDENCE_DOWNLOAD_URL,
            headers=None,
            tags=["WIFI", "DLMGR_AGENT"],
            url_ttl_seconds=EVIDENCE_URL_TTL_SECONDS,
        )
        assert cr.url == EVIDENCE_DOWNLOAD_URL
        assert cr.headers is None
        assert cr.tags == ["WIFI", "DLMGR_AGENT"]
        assert cr.url_ttl_seconds == EVIDENCE_URL_TTL_SECONDS
