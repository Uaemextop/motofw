"""Tests for motofw.src.device (properties, builder, reader)."""

from motofw.src.config.settings import Config
from motofw.src.device.builder import build_device_info, build_extra_info, build_identity_info
from motofw.src.device.properties import DeviceInfo, ExtraInfo, IdentityInfo


class TestDeviceInfo:
    def test_to_dict_keys(self):
        d = DeviceInfo().to_dict()
        assert "osVersion" in d
        assert "userLanguage" in d
        # Defaults are empty — values come from device.ini
        assert d["manufacturer"] == ""
        assert d["os"] == "Android"


class TestExtraInfo:
    def test_to_dict_has_fingerprint(self):
        d = ExtraInfo().to_dict()
        assert "fingerprint" in d
        # Default is empty — values come from device.ini
        assert d["fingerprint"] == ""

    def test_to_dict_with_configured_fingerprint(self):
        ei = ExtraInfo(fingerprint="motorola/lamul_g/lamul:15/VVTA35.51-100/e51bc9:user/release-keys")
        d = ei.to_dict()
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
    def test_build_device_info(self, custom_config: Config):
        di = build_device_info(custom_config)
        assert di.manufacturer == "motorola"
        assert di.hardware == "lamu"

    def test_build_extra_info(self, custom_config: Config):
        ei = build_extra_info(custom_config)
        assert ei.client_identity == "motorola-ota-client-app"

    def test_build_identity_info(self, custom_config: Config):
        ii = build_identity_info(custom_config)
        assert ii.serial_number == custom_config.serial_number
