"""Tests for motofw.src.api.scanner and the scan CLI subcommand."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from motofw.src.api.scanner import (
    KNOWN_BUILDS,
    ScanReport,
    ScanResult,
    _make_cfg_for_build,
    scan_updates,
)
from motofw.src.cli.commands import main
from motofw.src.cli.output import print_scan_results
from motofw.src.cli.parser import build_parser
from motofw.src.config.settings import Config
from motofw.src.utils.models import CheckResponse, ContentInfo


# ── Scanner tests ─────────────────────────────────────────────────────


class TestKnownBuilds:
    def test_has_at_least_four_builds(self):
        assert len(KNOWN_BUILDS) >= 4

    def test_builds_have_required_keys(self):
        for b in KNOWN_BUILDS:
            assert "build_id" in b
            assert "sha1" in b
            assert "fingerprint" in b

    def test_first_build_is_oldest(self):
        assert KNOWN_BUILDS[0]["build_id"] == "VVTA35.51-28-15"
        assert KNOWN_BUILDS[0]["sha1"] == "23d670d5d06f351"


class TestMakeCfgForBuild:
    def test_overrides_sha1_and_build(self, default_config: Config):
        build = KNOWN_BUILDS[0]
        cfg = _make_cfg_for_build(default_config, build)
        assert cfg.ota_source_sha1 == build["sha1"]
        assert cfg.build_id == build["build_id"]
        assert cfg.fingerprint == build["fingerprint"]
        # Rest should be unchanged
        assert cfg.serial_number == default_config.serial_number
        assert cfg.imei == default_config.imei


class TestScanUpdates:
    def test_scan_finds_update(self, default_config: Config, raw_check_response: Dict[str, Any]):
        """When the server returns proceed=True, scan collects the result."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = raw_check_response
        mock_resp.raise_for_status.return_value = None

        mock_session = MagicMock()
        mock_session.post.return_value = mock_resp

        builds = [KNOWN_BUILDS[0]]
        report = scan_updates(default_config, session=mock_session, builds=builds)
        assert report.builds_queried == 1
        assert len(report.results) == 1
        assert report.results[0].source_build == "VVTA35.51-28-15"
        assert report.results[0].target_build == "VVTA35.51-65-5"
        assert report.results[0].update_type == "MR"

    def test_scan_no_update(self, default_config: Config, raw_no_update: Dict[str, Any]):
        """When the server returns proceed=False, scan doesn't add a result."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = raw_no_update
        mock_resp.raise_for_status.return_value = None

        mock_session = MagicMock()
        mock_session.post.return_value = mock_resp

        builds = [KNOWN_BUILDS[0]]
        report = scan_updates(default_config, session=mock_session, builds=builds)
        assert report.builds_queried == 1
        assert len(report.results) == 0

    def test_scan_handles_error(self, default_config: Config):
        """When a request fails, it's recorded as an error, not a crash."""
        mock_session = MagicMock()
        mock_session.post.side_effect = Exception("network error")

        builds = [KNOWN_BUILDS[0]]
        report = scan_updates(default_config, session=mock_session, builds=builds)
        assert report.builds_queried == 1
        assert len(report.results) == 0
        assert len(report.errors) == 1
        assert "network error" in report.errors[0]

    def test_scan_multiple_builds(self, default_config: Config, raw_check_response: Dict[str, Any], raw_no_update: Dict[str, Any]):
        """Scan iterates through all provided builds."""
        resp_update = MagicMock()
        resp_update.json.return_value = raw_check_response
        resp_update.raise_for_status.return_value = None

        resp_no = MagicMock()
        resp_no.json.return_value = raw_no_update
        resp_no.raise_for_status.return_value = None

        mock_session = MagicMock()
        mock_session.post.side_effect = [resp_update, resp_no]

        builds = [KNOWN_BUILDS[0], KNOWN_BUILDS[1]]
        report = scan_updates(default_config, session=mock_session, builds=builds)
        assert report.builds_queried == 2
        assert len(report.results) == 1


# ── Output tests ──────────────────────────────────────────────────────


class TestPrintScanResults:
    def test_prints_header_and_rows(self, capsys):
        report = ScanReport(
            results=[
                ScanResult(
                    source_build="VVTA35.51-28-15",
                    source_sha1="23d670d5d06f351",
                    target_build="VVTA35.51-65-5",
                    target_sha1="a363e2a67728d8a",
                    size=354981143,
                    md5="e779db4c45f48461d4de52e569522e43",
                    update_type="MR",
                    package_id="test-pkg",
                    model="moto g15",
                    release_notes="",
                    check_response=CheckResponse(proceed=True),
                ),
            ],
            builds_queried=4,
        )
        print_scan_results(report)
        out = capsys.readouterr().out
        assert "Found 1 update(s)" in out
        assert "VVTA35.51-28-15" in out
        assert "VVTA35.51-65-5" in out
        assert "MR" in out


# ── CLI parser tests ──────────────────────────────────────────────────


class TestScanParser:
    def test_scan_subcommand(self):
        ap = build_parser()
        args = ap.parse_args(["scan"])
        assert args.command == "scan"

    def test_scan_no_interactive(self):
        ap = build_parser()
        args = ap.parse_args(["scan", "--no-interactive"])
        assert args.no_interactive is True

    def test_scan_with_serial(self):
        ap = build_parser()
        args = ap.parse_args(["scan", "--serial", "TEST123"])
        assert args.serial == "TEST123"

    def test_scan_with_output_dir(self, tmp_path):
        ap = build_parser()
        args = ap.parse_args(["scan", "-o", str(tmp_path)])
        assert str(args.output_dir) == str(tmp_path)

    def test_scan_configure_flag(self):
        ap = build_parser()
        args = ap.parse_args(["scan", "--configure"])
        assert args.configure is True

    def test_scan_triggered_by(self):
        ap = build_parser()
        args = ap.parse_args(["scan", "--triggered-by", "polling"])
        assert args.triggered_by == "polling"

    def test_scan_network_override(self):
        ap = build_parser()
        args = ap.parse_args(["scan", "--network", "cell5g"])
        assert args.network == "cell5g"

    def test_scan_bootloader_status(self):
        ap = build_parser()
        args = ap.parse_args(["scan", "--bootloader-status", "unlocked"])
        assert args.bootloader_status == "unlocked"

    def test_scan_build_type(self):
        ap = build_parser()
        args = ap.parse_args(["scan", "--build-type", "userdebug"])
        assert args.build_type == "userdebug"

    def test_scan_user_location(self):
        ap = build_parser()
        args = ap.parse_args(["scan", "--user-location", "CN"])
        assert args.user_location == "CN"

    def test_query_triggered_by(self):
        ap = build_parser()
        args = ap.parse_args(["query", "--triggered-by", "setup"])
        assert args.triggered_by == "setup"

    def test_query_network(self):
        ap = build_parser()
        args = ap.parse_args(["query", "--network", "cellular"])
        assert args.network == "cellular"


# ── Options module tests ──────────────────────────────────────────────


class TestOptions:
    def test_triggered_by_values(self):
        from motofw.src.config.options import TRIGGERED_BY_OPTIONS
        assert "user" in TRIGGERED_BY_OPTIONS
        assert "polling" in TRIGGERED_BY_OPTIONS
        assert "pairing" in TRIGGERED_BY_OPTIONS
        assert "setup" in TRIGGERED_BY_OPTIONS

    def test_network_values(self):
        from motofw.src.config.options import NETWORK_OPTIONS
        assert "wifi" in NETWORK_OPTIONS
        assert "cellular" in NETWORK_OPTIONS
        assert "cell5g" in NETWORK_OPTIONS

    def test_bootloader_values(self):
        from motofw.src.config.options import BOOTLOADER_STATUS_OPTIONS
        assert "locked" in BOOTLOADER_STATUS_OPTIONS
        assert "unlocked" in BOOTLOADER_STATUS_OPTIONS

    def test_build_type_values(self):
        from motofw.src.config.options import BUILD_TYPE_OPTIONS
        assert "user" in BUILD_TYPE_OPTIONS
        assert "userdebug" in BUILD_TYPE_OPTIONS
        assert "eng" in BUILD_TYPE_OPTIONS

    def test_update_type_values(self):
        from motofw.src.config.options import UPDATE_TYPE_OPTIONS
        assert "MR" in UPDATE_TYPE_OPTIONS
        assert "SMR" in UPDATE_TYPE_OPTIONS
        assert "OS" in UPDATE_TYPE_OPTIONS

    def test_configurable_params_structure(self):
        from motofw.src.config.options import CONFIGURABLE_PARAMS
        for key, info in CONFIGURABLE_PARAMS.items():
            assert "label" in info
            assert "options" in info
            assert "default" in info
            assert "description" in info
            assert info["default"] in info["options"]


# ── Apply overrides tests for new fields ─────────────────────────────


class TestApplyOverridesNew:
    def test_override_network(self, default_config: Config):
        from motofw.src.cli.commands import _apply_overrides
        c2 = _apply_overrides(default_config, network="cell5g")
        assert c2.network == "cell5g"

    def test_override_bootloader_status(self, default_config: Config):
        from motofw.src.cli.commands import _apply_overrides
        c2 = _apply_overrides(default_config, bootloader_status="unlocked")
        assert c2.bootloader_status == "unlocked"

    def test_override_build_type(self, default_config: Config):
        from motofw.src.cli.commands import _apply_overrides
        c2 = _apply_overrides(default_config, build_type="userdebug")
        assert c2.build_type == "userdebug"

    def test_override_user_location(self, default_config: Config):
        from motofw.src.cli.commands import _apply_overrides
        c2 = _apply_overrides(default_config, user_location="CN")
        assert c2.user_location == "CN"

    def test_scan_passes_triggered_by(self, default_config: Config, raw_check_response: Dict[str, Any]):
        """Scan passes triggered_by to check_body."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = raw_check_response
        mock_resp.raise_for_status.return_value = None

        mock_session = MagicMock()
        mock_session.post.return_value = mock_resp

        builds = [KNOWN_BUILDS[0]]
        report = scan_updates(default_config, session=mock_session, builds=builds, triggered_by="polling")
        assert report.builds_queried == 1
        # Verify the body sent to server has the correct triggered_by
        call_args = mock_session.post.call_args
        body = call_args.kwargs["json_body"]
        assert body["triggeredBy"] == "polling"
