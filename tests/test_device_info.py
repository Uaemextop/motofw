"""Unit tests for device_info module."""

import hashlib
import pytest

from motofw.device_info import DeviceInfo


class TestDeviceInfo:
    """Test DeviceInfo class."""

    def test_init_required_fields(self):
        """Test initialization with required fields."""
        device = DeviceInfo(
            serial_number="ZY1234567890",
            model="moto g power",
            product="cebu",
            build_id="S3RC33.18-52-1",
        )

        assert device.serial_number == "ZY1234567890"
        assert device.model == "moto g power"
        assert device.product == "cebu"
        assert device.build_id == "S3RC33.18-52-1"
        assert device.manufacturer == "Motorola"

    def test_init_optional_fields(self):
        """Test initialization with optional fields."""
        device = DeviceInfo(
            serial_number="ZY1234567890",
            model="moto g power",
            product="cebu",
            build_id="S3RC33.18-52-1",
            build_device="cebu_retail",
            carrier="vzw",
            color_id="blue",
            is_prc=True,
            user_language="zh-CN",
        )

        assert device.build_device == "cebu_retail"
        assert device.carrier == "vzw"
        assert device.color_id == "blue"
        assert device.is_prc is True
        assert device.user_language == "zh-CN"

    def test_get_context_key(self):
        """Test context key generation."""
        device = DeviceInfo(
            serial_number="ZY1234567890",
            model="moto g power",
            product="cebu",
            build_id="S3RC33.18-52-1",
        )

        context_key = device.get_context_key()
        expected = hashlib.sha1(b"S3RC33.18-52-1").hexdigest()

        assert context_key == expected
        assert len(context_key) == 40  # SHA1 hex digest length

    def test_get_primary_key(self):
        """Test primary key generation."""
        device = DeviceInfo(
            serial_number="ZY1234567890",
            model="moto g power",
            product="cebu",
            build_id="S3RC33.18-52-1",
        )

        primary_key = device.get_primary_key()
        context_key = device.get_context_key()
        expected = hashlib.sha1((context_key + "ZY1234567890").encode()).hexdigest()

        assert primary_key == expected
        assert len(primary_key) == 40

    def test_to_device_info_dict(self):
        """Test device info dictionary conversion."""
        device = DeviceInfo(
            serial_number="ZY1234567890",
            model="moto g power",
            product="cebu",
            build_id="S3RC33.18-52-1",
            carrier="vzw",
            is_prc=False,
            user_language="en-US",
        )

        device_dict = device.to_device_info_dict()

        assert device_dict["manufacturer"] == "Motorola"
        assert device_dict["model"] == "moto g power"
        assert device_dict["product"] == "cebu"
        assert device_dict["carrier"] == "vzw"
        assert device_dict["isPRC"] is False
        assert device_dict["userLanguage"] == "en-US"

    def test_to_extra_info_dict(self):
        """Test extra info dictionary conversion."""
        device = DeviceInfo(
            serial_number="ZY1234567890",
            model="moto g power",
            product="cebu",
            build_id="S3RC33.18-52-1",
            build_device="cebu_retail",
            color_id="blue",
        )

        extra_dict = device.to_extra_info_dict(apk_version="2.0.0")

        assert extra_dict["clientIdentity"] == "motorola-ota-client-app"
        assert extra_dict["buildDevice"] == "cebu_retail"
        assert extra_dict["buildId"] == "S3RC33.18-52-1"
        assert extra_dict["buildDisplayId"] == "S3RC33.18-52-1"
        assert extra_dict["colorId"] == "blue"
        assert extra_dict["apkPackageName"] == "com.motorola.ccc.ota"
        assert extra_dict["apkVersion"] == "2.0.0"
        assert extra_dict["OtaLibVersion"] == 0x30D44
        assert extra_dict["mobileModel"] == "moto g power"
        assert "otaSourceSha1" in extra_dict
        assert "provisionedTime" in extra_dict

    def test_to_identity_info_dict(self):
        """Test identity info dictionary conversion."""
        device = DeviceInfo(
            serial_number="ZY1234567890",
            model="moto g power",
            product="cebu",
            build_id="S3RC33.18-52-1",
        )

        identity_dict = device.to_identity_info_dict()

        assert identity_dict["serialNumber"] == "ZY1234567890"
        assert len(identity_dict) == 1

    def test_defaults(self):
        """Test default values."""
        device = DeviceInfo(
            serial_number="ZY1234567890",
            model="moto g power",
            product="cebu",
            build_id="S3RC33.18-52-1",
        )

        assert device.build_device == "moto g power"  # defaults to model
        assert device.carrier == "unknown"
        assert device.color_id == "default"
        assert device.is_prc is False
        assert device.user_language == "en-US"
