"""Tests for motofw.src.device (properties, builder, reader)."""

from motofw.src.config.settings import Config
from motofw.src.device.builder import build_device_info, build_extra_info, build_identity_info
from motofw.src.device.properties import DeviceInfo, ExtraInfo, IdentityInfo


class TestDeviceInfo:
    def test_to_dict_keys(self):
        d = DeviceInfo().to_dict()
        assert "osVersion" in d
        assert "userLanguage" in d
        assert d["manufacturer"] == "motorola"


class TestExtraInfo:
    def test_to_dict_has_fingerprint(self):
        d = ExtraInfo().to_dict()
        assert "fingerprint" in d
        assert "VVTA35" in d["fingerprint"]

    def test_imei_omitted_when_empty(self):
        ei = ExtraInfo(imei="", imei2="")
        d = ei.to_dict()
        assert "imei" not in d

    def test_imei_present_when_set(self):
        ei = ExtraInfo(imei="123456789")
        d = ei.to_dict()
        assert d["imei"] == "123456789"


class TestIdentityInfo:
    def test_to_dict(self):
        ii = IdentityInfo(serial_number="ABC")
        assert ii.to_dict() == {"serialNumber": "ABC"}


class TestBuilders:
    def test_build_device_info(self, default_config: Config):
        di = build_device_info(default_config)
        assert di.manufacturer == "motorola"
        assert di.hardware == "lamu"

    def test_build_extra_info(self, default_config: Config):
        ei = build_extra_info(default_config)
        assert ei.client_identity == "motorola-ota-client-app"

    def test_build_identity_info(self, default_config: Config):
        ii = build_identity_info(default_config)
        assert ii.serial_number == default_config.serial_number
