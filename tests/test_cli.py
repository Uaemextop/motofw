"""Tests for motofw.src.cli (parser, commands, output, log)."""

from motofw.src.cli.commands import _apply_overrides, main
from motofw.src.cli.log import setup_logging
from motofw.src.cli.parser import build_parser
from motofw.src.config.settings import Config


class TestParser:
    def test_query_subcommand(self):
        ap = build_parser()
        args = ap.parse_args(["query"])
        assert args.command == "query"

    def test_download_subcommand(self):
        ap = build_parser()
        args = ap.parse_args(["download", "-o", "/tmp/out"])
        assert args.command == "download"
        assert str(args.output_dir) == "/tmp/out"

    def test_verbose_flag(self):
        ap = build_parser()
        args = ap.parse_args(["-vv", "query"])
        assert args.verbose == 2


class TestApplyOverrides:
    def test_override_sha1(self, default_config: Config):
        c2 = _apply_overrides(default_config, ota_source_sha1="new_sha")
        assert c2.ota_source_sha1 == "new_sha"
        assert c2.serial_number == default_config.serial_number

    def test_override_serial(self, default_config: Config):
        c2 = _apply_overrides(default_config, serial="NEW_SN")
        assert c2.serial_number == "NEW_SN"

    def test_override_no_verify(self, default_config: Config):
        c2 = _apply_overrides(default_config, no_verify=True)
        assert c2.verify_checksum is False


class TestMain:
    def test_no_command_prints_help(self):
        rc = main([])
        assert rc == 1

    def test_unknown_args(self):
        import pytest
        with pytest.raises(SystemExit):
            main(["--bogus"])

    def test_query_without_device_ini_fails(self):
        """query should fail when device is not configured (empty defaults)."""
        rc = main(["query"])
        assert rc == 1

    def test_scan_without_device_ini_fails(self):
        """scan should fail when device is not configured (empty defaults)."""
        rc = main(["scan", "--no-interactive"])
        assert rc == 1


class TestLogging:
    def test_setup_logging_runs(self):
        setup_logging(0)
        setup_logging(1)
        setup_logging(2)
