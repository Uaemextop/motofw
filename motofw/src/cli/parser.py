"""Argument parser construction for the motofw CLI."""

from __future__ import annotations

import argparse
from pathlib import Path

from motofw.src.config.options import (
    BOOTLOADER_STATUS_OPTIONS,
    BUILD_TYPE_OPTIONS,
    NETWORK_OPTIONS,
    SERVER_NAMES,
    TRIGGERED_BY_OPTIONS,
    USER_LOCATION_OPTIONS,
)


def _add_request_overrides(p: argparse.ArgumentParser) -> None:
    """Add shared --triggered-by / --network / --server / etc. flags to *p*."""
    p.add_argument(
        "--server",
        choices=SERVER_NAMES,
        default=None,
        help="Server environment (production/china/qa/dev/staging/china-staging).",
    )
    p.add_argument(
        "--triggered-by",
        choices=TRIGGERED_BY_OPTIONS,
        default=None,
        help="Override triggeredBy (user/polling/pairing/setup).",
    )
    p.add_argument(
        "--network",
        choices=NETWORK_OPTIONS,
        default=None,
        help="Override network type (wifi/cellular/cell3g/cell4g/cell5g/roaming/unknown).",
    )
    p.add_argument(
        "--bootloader-status",
        choices=BOOTLOADER_STATUS_OPTIONS,
        default=None,
        help="Override bootloader status (locked/unlocked).",
    )
    p.add_argument(
        "--build-type",
        choices=BUILD_TYPE_OPTIONS,
        default=None,
        help="Override Android build type (user/userdebug/eng).",
    )
    p.add_argument(
        "--user-location",
        choices=USER_LOCATION_OPTIONS,
        default=None,
        help="Override user location (Non-CN/CN).",
    )


def build_parser() -> argparse.ArgumentParser:
    """Return the top-level argument parser with sub-commands."""
    parser = argparse.ArgumentParser(
        prog="motofw",
        description="Query and download Motorola OTA firmware updates.",
    )
    parser.add_argument("-c", "--config", type=Path, default=None, help="Path to config.ini.")
    parser.add_argument("-d", "--device", type=Path, default=None, help="Path to device.ini.")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="-v info, -vv debug.")

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # query
    qp = sub.add_parser("query", help="Check for an available OTA update.")
    qp.add_argument("--ota-source-sha1", default=None, help="Override otaSourceSha1.")
    qp.add_argument("--serial", default=None, help="Override serial number.")
    qp.add_argument("--dump-request", action="store_true", default=False, help="Print the request body and equivalent curl command.")
    qp.add_argument("--raw", action="store_true", default=False, help="Print the full raw server response JSON.")
    _add_request_overrides(qp)

    # download
    dp = sub.add_parser("download", help="Download an available OTA update.")
    dp.add_argument("-o", "--output-dir", type=Path, default=None, help="Save directory.")
    dp.add_argument("--ota-source-sha1", default=None, help="Override otaSourceSha1.")
    dp.add_argument("--serial", default=None, help="Override serial number.")
    dp.add_argument("--no-verify", action="store_true", default=False, help="Skip MD5 check.")
    dp.add_argument("--dump-request", action="store_true", default=False, help="Print the request body and equivalent curl command.")
    _add_request_overrides(dp)

    # scan
    sp = sub.add_parser("scan", help="Scan all known builds for available OTA updates and choose which to download.")
    sp.add_argument("--serial", default=None, help="Override serial number.")
    sp.add_argument("-o", "--output-dir", type=Path, default=None, help="Save directory for downloads.")
    sp.add_argument("--no-verify", action="store_true", default=False, help="Skip MD5 check.")
    sp.add_argument("--no-interactive", action="store_true", default=False, help="Skip interactive menu, just list results.")
    sp.add_argument("--configure", action="store_true", default=False, help="Interactively configure API request parameters before scanning.")
    sp.add_argument(
        "--discover", action="store_true", default=False,
        help="Multi-server discovery: query all 6 Motorola servers (production, QA, dev, staging, China) to find OTAs.",
    )
    _add_request_overrides(sp)

    # settings
    stp = sub.add_parser("settings", help="Configure motofw settings.")
    stp_sub = stp.add_subparsers(dest="settings_command", help="Settings commands")
    adb_p = stp_sub.add_parser(
        "auto-settings-adb",
        help="Auto-detect device settings via ADB (USB or wireless) and generate device.ini.",
    )
    adb_p.add_argument(
        "--output", "-o", type=Path, default=Path("device.ini"),
        help="Path to write device.ini (default: ./device.ini).",
    )

    return parser
