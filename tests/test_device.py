"""Tests for motofw.src.device (properties, builder, reader)."""

from motofw.src.config.settings import Config
from motofw.src.device.builder import build_device_info, build_extra_info, build_identity_info
from motofw.src.device.properties import DeviceInfo, ExtraInfo, IdentityInfo


class TestDeviceInfo:
    def test_to_dict_keys(self):
        d = DeviceInfo().to_dict()
        assert "osVersion" in d
        assert "userLanguage" in d
        # Device-specific fields default to empty (require device.ini)
        assert d["manufacturer"] == ""
        # Protocol constants retain defaults (same for all Motorola devices)
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

    def test_smali_extra_fields_present(self):
        """All fields from BuildPropReader.smali lines 1006–1157 must appear."""
        d = ExtraInfo().to_dict()
        smali_keys = [
            "securityVersion",
            "ro.mot.version",
            "ro.enterpriseedition",
            "ro.virtual_ab.enabled",
            "vitalUpdate",
            "ro.vendor.hw.storage",
            "ro.vendor.hw.ram",
            "ro.vendor.hw.esim",
            "ro.mot.product_wave",
            "ro.mot.build.oem.product",
            "ro.mot.build.system.product",
            "ro.mot.build.product.increment",
            "ro.boot.veritymode",
            "partition.system.verified",
        ]
        for key in smali_keys:
            assert key in d, f"Missing smali field: {key}"

    def test_smali_extra_fields_types(self):
        """Verify correct types for smali-sourced fields."""
        d = ExtraInfo(security_version="2025-01-01", mot_version=5).to_dict()
        assert d["securityVersion"] == "2025-01-01"
        assert d["ro.mot.version"] == 5
        assert isinstance(d["ro.enterpriseedition"], bool)
        assert isinstance(d["ro.virtual_ab.enabled"], bool)
        assert isinstance(d["vitalUpdate"], bool)


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
