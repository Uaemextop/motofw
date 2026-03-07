"""Argument parser construction for the motofw CLI."""

from __future__ import annotations

import argparse
from pathlib import Path


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

    # download
    dp = sub.add_parser("download", help="Download an available OTA update.")
    dp.add_argument("-o", "--output-dir", type=Path, default=None, help="Save directory.")
    dp.add_argument("--ota-source-sha1", default=None, help="Override otaSourceSha1.")
    dp.add_argument("--serial", default=None, help="Override serial number.")
    dp.add_argument("--no-verify", action="store_true", default=False, help="Skip MD5 check.")
    dp.add_argument("--dump-request", action="store_true", default=False, help="Print the request body and equivalent curl command.")

    return parser
