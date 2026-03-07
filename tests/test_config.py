"""Tests for motofw.src.config (defaults, loader, settings)."""

from pathlib import Path

from motofw.src.config.defaults import DEVICE_DEFAULTS, SERVER_DEFAULTS
from motofw.src.config.loader import get_bool, get_int, get_value, read_ini
from motofw.src.config.settings import Config, load_config


class TestDefaults:
    def test_server_url(self):
        assert SERVER_DEFAULTS["url"] == "moto-cds.appspot.com"

    def test_device_build_id(self):
        assert "VVTA35.51-100" in DEVICE_DEFAULTS["build_id"]


class TestLoader:
    def test_read_nonexistent(self, tmp_path: Path):
        cp = read_ini(tmp_path / "nope.ini", [], "test")
        assert cp.sections() == []

    def test_read_existing(self, tmp_path: Path):
        ini = tmp_path / "test.ini"
        ini.write_text("[s]\nkey = val\n")
        cp = read_ini(ini, [], "test")
        assert cp.get("s", "key") == "val"

    def test_get_value_fallback(self, tmp_path: Path):
        cp = read_ini(tmp_path / "nope.ini", [], "t")
        assert get_value(cp, "s", "k", "fb") == "fb"

    def test_get_int(self, tmp_path: Path):
        ini = tmp_path / "t.ini"
        ini.write_text("[s]\nn = 42\n")
        cp = read_ini(ini, [], "t")
        assert get_int(cp, "s", "n") == 42

    def test_get_bool(self, tmp_path: Path):
        ini = tmp_path / "t.ini"
        ini.write_text("[s]\nflag = true\n")
        cp = read_ini(ini, [], "t")
        assert get_bool(cp, "s", "flag") is True


class TestConfig:
    def test_defaults_without_files(self, default_config: Config):
        assert default_config.server_url == "moto-cds.appspot.com"
        assert default_config.timeout == 60
        assert default_config.retry_delays_ms == [5000, 15000, 30000]

    def test_custom_config(self, custom_config: Config):
        assert custom_config.serial_number == "ZY32LNRW97"
        assert custom_config.imei == "359488357396203"

    def test_device_ini_override(self, tmp_path: Path):
        dev = tmp_path / "device.ini"
        dev.write_text("[device]\nmodel = test phone\n\n[identity]\nserial_number = TEST123\n")
        cfg = load_config(tmp_path / "missing.ini", device_path=dev)
        assert cfg.model == "test phone"
        assert cfg.serial_number == "TEST123"

    def test_frozen(self, default_config: Config):
        import dataclasses
        assert dataclasses.is_dataclass(default_config)
        # frozen → assignment raises
        try:
            default_config.server_url = "x"  # type: ignore[misc]
            assert False, "Should have raised"
        except AttributeError:
            pass
