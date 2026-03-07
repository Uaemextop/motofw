"""Tests for motofw.src.api.scanner and the scan CLI subcommand."""

from __future__ import annotations

from typing import Any, Dict
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
