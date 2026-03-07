"""Tests for motofw.src.device.adb — ADB auto-settings extraction."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from motofw.src.device.adb import (
    ADBError,
    _detect_bootloader_status,
    _detect_device_rooted,
    _detect_is_4gb_ram,
    _detect_user_location,
    _derive_country_language,
    _parse_parcel_string,
    _resolve_prop,
    extract_device_info,
    find_adb,
    get_all_properties,
    get_imei,
    get_serial,
    run_adb,
    write_device_ini,
)
from motofw.src.cli.commands import main
from motofw.src.cli.parser import build_parser


# ── find_adb ──────────────────────────────────────────────────────────


class TestFindAdb:
    @patch("shutil.which", return_value="/usr/bin/adb")
    def test_found(self, mock_which):
        assert find_adb() == "/usr/bin/adb"

    @patch("shutil.which", return_value=None)
    def test_not_found_raises(self, mock_which):
        with pytest.raises(ADBError, match="adb not found"):
            find_adb()


# ── run_adb ───────────────────────────────────────────────────────────


class TestRunAdb:
    @patch("subprocess.run")
    def test_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="output\n", stderr="")
        result = run_adb(["shell", "getprop"], adb_path="/usr/bin/adb")
        assert result == "output\n"
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_error_raises(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error: device not found")
        with pytest.raises(ADBError, match="device not found"):
            run_adb(["shell", "getprop"], adb_path="/usr/bin/adb")

    @patch("subprocess.run", side_effect=FileNotFoundError("adb"))
    def test_file_not_found_raises(self, mock_run):
        with pytest.raises(ADBError, match="adb binary not found"):
            run_adb(["shell", "getprop"], adb_path="/nonexistent/adb")


# ── get_all_properties ────────────────────────────────────────────────


SAMPLE_GETPROP = """\
[ro.build.fingerprint]: [motorola/lamul_g/lamul:15/VVTA35.51-100/e51bc9:user/release-keys]
[ro.build.display.id]: [VVTA35.51-100]
[ro.product.model]: [moto g05]
[ro.product.brand]: [motorola]
[ro.product.name]: [lamul_g]
[ro.hardware]: [lamu]
[ro.build.type]: [user]
[ro.build.tags]: [release-keys]
[ro.build.version.release]: [15]
[ro.mot.build.guid]: [190325d96009ac5]
[ro.mot.build.device]: [lamul]
[ro.serialno]: [ZY32LNRW97]
[ro.product.manufacturer]: [motorola]
[ro.boot.verifiedbootstate]: [green]
[ro.product.locale]: [es_MX]
[ro.vendor.hw.ram]: [4096]
[persist.qe]: [0]
"""


class TestGetAllProperties:
    @patch("motofw.src.device.adb.run_adb", return_value=SAMPLE_GETPROP)
    def test_parses_properties(self, mock_run):
        props = get_all_properties(adb_path="/usr/bin/adb")
        assert props["ro.build.fingerprint"] == "motorola/lamul_g/lamul:15/VVTA35.51-100/e51bc9:user/release-keys"
        assert props["ro.product.model"] == "moto g05"
        assert props["ro.serialno"] == "ZY32LNRW97"
        assert props["ro.mot.build.guid"] == "190325d96009ac5"
        assert len(props) == 17


# ── _resolve_prop ─────────────────────────────────────────────────────


class TestResolveProp:
    def test_first_match(self):
        props = {"ro.build.display.id": "VVTA35.51-100", "ro.build.id": "VVTA35.51"}
        assert _resolve_prop(props, ["ro.build.display.id", "ro.build.id"]) == "VVTA35.51-100"

    def test_fallback_to_second(self):
        props = {"ro.build.id": "VVTA35.51"}
        assert _resolve_prop(props, ["ro.build.display.id", "ro.build.id"]) == "VVTA35.51"

    def test_empty_when_none_match(self):
        assert _resolve_prop({}, ["ro.build.display.id"]) == ""


# ── _parse_parcel_string ─────────────────────────────────────────────


class TestParseParcelString:
    def test_parses_imei_parcel(self):
        # Real-format Parcel dump for IMEI 359488357396203
        # UTF-16LE on little-endian: bytes 33,00,35,00,39,00,34,00...
        # Readable section shows each byte as ASCII char or '.' for non-printable
        raw = """Result: Parcel(
  0x00000000: 00000000 0000000f 00350033 00340039 '........3.5.9.4.'
  0x00000010: 00380038 00350033 00330037 00360039 '8.8.3.5.7.3.9.6.'
  0x00000020: 00300032 00000033                    '2.0.3...')"""
        result = _parse_parcel_string(raw)
        assert result == "359488357396203"

    def test_empty_parcel(self):
        assert _parse_parcel_string("Result: Parcel(size=0)") == ""


# ── get_serial ────────────────────────────────────────────────────────


class TestGetSerial:
    @patch("motofw.src.device.adb.run_adb", return_value="ZY32LNRW97\n")
    def test_from_get_serialno(self, mock_run):
        assert get_serial(adb_path="/usr/bin/adb") == "ZY32LNRW97"

    @patch("motofw.src.device.adb.run_adb", side_effect=[
        ADBError("no device"),
        "ABC123\n",
    ])
    def test_fallback_to_getprop(self, mock_run):
        assert get_serial(adb_path="/usr/bin/adb") == "ABC123"

    @patch("motofw.src.device.adb.run_adb", side_effect=ADBError("no device"))
    def test_returns_empty_on_failure(self, mock_run):
        assert get_serial(adb_path="/usr/bin/adb") == ""


# ── get_imei ──────────────────────────────────────────────────────────


class TestGetImei:
    @patch("motofw.src.device.adb.run_adb")
    def test_parses_imei_from_service_call(self, mock_run):
        parcel = """Result: Parcel(
  0x00000000: 00000000 0000000f 00350033 00340039 '........3.5.9.4.'
  0x00000010: 00380038 00350033 00330037 00360039 '8.8.3.5.7.3.9.6.'
  0x00000020: 00300032 00000033                    '2.0.3...')"""
        mock_run.return_value = parcel
        assert get_imei(slot=0, adb_path="/usr/bin/adb") == "359488357396203"

    @patch("motofw.src.device.adb.run_adb", side_effect=ADBError("not available"))
    def test_returns_empty_on_failure(self, mock_run):
        assert get_imei(slot=0, adb_path="/usr/bin/adb") == ""


# ── _detect_bootloader_status ─────────────────────────────────────────


class TestDetectBootloaderStatus:
    def test_green_is_locked(self):
        assert _detect_bootloader_status({"ro.boot.verifiedbootstate": "green"}) == "locked"

    def test_orange_is_unlocked(self):
        assert _detect_bootloader_status({"ro.boot.verifiedbootstate": "orange"}) == "unlocked"

    def test_oem_unlock_allowed(self):
        assert _detect_bootloader_status({"sys.oem_unlock_allowed": "1"}) == "unlocked"

    def test_default_locked(self):
        assert _detect_bootloader_status({}) == "locked"


# ── _detect_user_location ─────────────────────────────────────────────


class TestDetectUserLocation:
    def test_china_region(self):
        assert _detect_user_location({"ro.lenovo.region": "CN"}) == "CN"

    def test_china_customer_id(self):
        assert _detect_user_location({"ro.mot.build.customerid": "retcn"}) == "CN"

    def test_non_china(self):
        assert _detect_user_location({}) == "Non-CN"


# ── _detect_is_4gb_ram ────────────────────────────────────────────────


class TestDetectIs4GBRam:
    def test_4gb(self):
        assert _detect_is_4gb_ram({"ro.vendor.hw.ram": "4096"}) is True

    def test_8gb(self):
        assert _detect_is_4gb_ram({"ro.vendor.hw.ram": "8192"}) is False

    def test_missing(self):
        assert _detect_is_4gb_ram({}) is False


# ── _detect_device_rooted ─────────────────────────────────────────────


class TestDetectDeviceRooted:
    def test_rooted(self):
        assert _detect_device_rooted({"persist.qe": "1"}) == "true"

    def test_not_rooted(self):
        assert _detect_device_rooted({"persist.qe": "0"}) == "false"

    def test_missing(self):
        assert _detect_device_rooted({}) == "false"


# ── _derive_country_language ──────────────────────────────────────────


class TestDeriveCountryLanguage:
    def test_full_locale(self):
        props = {"ro.product.locale": "es_MX"}
        country, lang, user_lang = _derive_country_language(props)
        assert country == "MX"
        assert lang == "es"
        assert user_lang == "es_MX"

    def test_locale_with_region(self):
        props = {"ro.product.locale": "en_US", "ro.product.locale.region": "US"}
        country, lang, user_lang = _derive_country_language(props)
        assert country == "US"
        assert lang == "en"

    def test_empty(self):
        country, lang, user_lang = _derive_country_language({})
        assert country == "US"
        assert lang == "en"
        assert user_lang == "en_US"


# ── extract_device_info ───────────────────────────────────────────────


class TestExtractDeviceInfo:
    @patch("motofw.src.device.adb.get_imei", return_value="359488357396203")
    @patch("motofw.src.device.adb.get_serial", return_value="ZY32LNRW97")
    @patch("motofw.src.device.adb.get_all_properties")
    def test_extracts_full_info(self, mock_props, mock_serial, mock_imei):
        mock_props.return_value = {
            "ro.build.fingerprint": "motorola/lamul_g/lamul:15/VVTA35.51-100/e51bc9:user/release-keys",
            "ro.build.display.id": "VVTA35.51-100",
            "ro.product.model": "moto g05",
            "ro.product.brand": "motorola",
            "ro.product.name": "lamul_g",
            "ro.hardware": "lamu",
            "ro.build.type": "user",
            "ro.build.tags": "release-keys",
            "ro.build.version.release": "15",
            "ro.mot.build.guid": "190325d96009ac5",
            "ro.mot.build.device": "lamul",
            "ro.serialno": "ZY32LNRW97",
            "ro.product.manufacturer": "motorola",
            "ro.boot.verifiedbootstate": "green",
            "ro.product.locale": "es_MX",
        }
        info = extract_device_info(adb_path="/usr/bin/adb")
        assert info["serial_number"] == "ZY32LNRW97"
        assert info["imei"] == "359488357396203"
        assert info["fingerprint"] == "motorola/lamul_g/lamul:15/VVTA35.51-100/e51bc9:user/release-keys"
        assert info["build_id"] == "VVTA35.51-100"
        assert info["ota_source_sha1"] == "190325d96009ac5"
        assert info["model"] == "moto g05"
        assert info["bootloader_status"] == "locked"
        assert info["country"] == "MX"
        assert info["language"] == "es"


# ── write_device_ini ──────────────────────────────────────────────────


class TestWriteDeviceIni:
    def test_writes_file(self, tmp_path: Path):
        info = {
            "manufacturer": "motorola",
            "hardware": "lamu",
            "brand": "motorola",
            "model": "moto g05",
            "product": "lamul_g",
            "serial_number": "ZY32LNRW97",
            "imei": "359488357396203",
            "fingerprint": "motorola/lamul_g/lamul:15/VVTA35.51-100/e51bc9:user/release-keys",
            "build_id": "VVTA35.51-100",
            "ota_source_sha1": "190325d96009ac5",
        }
        dest = tmp_path / "device.ini"
        result = write_device_ini(info, dest)
        assert dest.exists()
        content = dest.read_text()
        assert "[device]" in content
        assert "[identity]" in content
        assert "serial_number = ZY32LNRW97" in content
        assert "imei = 359488357396203" in content
        assert "ota_source_sha1 = 190325d96009ac5" in content

    def test_creates_parent_dirs(self, tmp_path: Path):
        dest = tmp_path / "subdir" / "nested" / "device.ini"
        write_device_ini({"serial_number": "TEST"}, dest)
        assert dest.exists()


# ── CLI parser tests ──────────────────────────────────────────────────


class TestSettingsParser:
    def test_settings_subcommand(self):
        ap = build_parser()
        args = ap.parse_args(["settings", "auto-settings-adb"])
        assert args.command == "settings"
        assert args.settings_command == "auto-settings-adb"

    def test_settings_with_output(self, tmp_path: Path):
        ap = build_parser()
        dest = str(tmp_path / "my_device.ini")
        args = ap.parse_args(["settings", "auto-settings-adb", "-o", dest])
        assert str(args.output) == dest

    def test_settings_no_subcommand(self):
        ap = build_parser()
        args = ap.parse_args(["settings"])
        assert args.command == "settings"
        assert getattr(args, "settings_command", None) is None

    def test_main_settings_no_subcommand(self):
        rc = main(["settings"])
        assert rc == 1
