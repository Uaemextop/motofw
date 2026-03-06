"""Tests for motofw.cli — command-line argument parsing.

Verifies CLI argument parsing and sub-command routing without making
any HTTP calls.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from motofw.cli import _apply_overrides, _build_parser, main
from motofw.config import Config
from motofw.models import CheckResponse
from tests.conftest import (
    EVIDENCE_OTA_SOURCE_SHA1,
    EVIDENCE_SERVER_URL,
)


class TestArgParser:
    """Verify argparse structure."""

    def test_no_args_returns_1(self) -> None:
        """No sub-command → exit code 1."""
        rc = main([])
        assert rc == 1

    def test_query_subcommand_parsed(self) -> None:
        parser = _build_parser()
        args = parser.parse_args(["query"])
        assert args.command == "query"

    def test_download_subcommand_parsed(self) -> None:
        parser = _build_parser()
        args = parser.parse_args(["download"])
        assert args.command == "download"

    def test_query_with_ota_override(self) -> None:
        parser = _build_parser()
        args = parser.parse_args(["query", "--ota-source-sha1", "abc123"])
        assert args.ota_source_sha1 == "abc123"

    def test_download_with_output_dir(self, tmp_path: Path) -> None:
        parser = _build_parser()
        args = parser.parse_args(
            ["download", "-o", str(tmp_path)]
        )
        assert args.output_dir == tmp_path

    def test_download_no_verify_flag(self) -> None:
        parser = _build_parser()
        args = parser.parse_args(["download", "--no-verify"])
        assert args.no_verify is True

    def test_verbose_count(self) -> None:
        parser = _build_parser()
        args = parser.parse_args(["-vv", "query"])
        assert args.verbose == 2

    def test_config_path_option(self, tmp_path: Path) -> None:
        parser = _build_parser()
        cfg_path = tmp_path / "my.ini"
        args = parser.parse_args(["-c", str(cfg_path), "query"])
        assert args.config == cfg_path


class TestApplyOverrides:
    """Verify CLI overrides are applied to Config."""

    def test_override_ota_source_sha1(self, default_config: Config) -> None:
        new_cfg = _apply_overrides(
            default_config, ota_source_sha1="custom_sha1"
        )
        assert new_cfg.ota_source_sha1 == "custom_sha1"
        # Other fields unchanged
        assert new_cfg.server_url == EVIDENCE_SERVER_URL

    def test_override_serial(self, default_config: Config) -> None:
        new_cfg = _apply_overrides(default_config, serial="MY_SERIAL")
        assert new_cfg.serial_number == "MY_SERIAL"

    def test_override_no_verify(self, default_config: Config) -> None:
        new_cfg = _apply_overrides(default_config, no_verify=True)
        assert new_cfg.verify_checksum is False

    def test_override_output_dir(
        self, default_config: Config, tmp_path: Path
    ) -> None:
        new_cfg = _apply_overrides(
            default_config, output_dir=tmp_path / "fw"
        )
        assert new_cfg.output_dir == tmp_path / "fw"


class TestQueryCommand:
    """Test the query sub-command with mocked API."""

    @patch("motofw.cli.OTAClient")
    @patch("motofw.cli.check_update")
    def test_query_no_update(
        self,
        mock_check: MagicMock,
        mock_client_cls: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        mock_client_cls.return_value.__enter__ = MagicMock(
            return_value=mock_client_cls.return_value
        )
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_check.return_value = CheckResponse(proceed=False)

        rc = main(["query"])
        assert rc == 0
        out = capsys.readouterr().out
        assert '"proceed": false' in out


class TestDownloadCommand:
    """Test the download sub-command with mocked API."""

    @patch("motofw.cli.download_update")
    @patch("motofw.cli.OTAClient")
    @patch("motofw.cli.check_update")
    def test_download_no_update(
        self,
        mock_check: MagicMock,
        mock_client_cls: MagicMock,
        mock_download: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        mock_client_cls.return_value.__enter__ = MagicMock(
            return_value=mock_client_cls.return_value
        )
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_check.return_value = CheckResponse(proceed=False)

        rc = main(["download"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "No update available" in out
        mock_download.assert_not_called()
