"""CLI entry point for the motofw tool.

Can be invoked as::

    python -m motofw check   --config config.ini
    python -m motofw download --config config.ini
    motofw check
    motofw download
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

from motofw import __version__
from motofw.config import Config
from motofw.ota import check_update, download_update, get_resources, query_and_download
from motofw.client import OTAClient
from motofw.response_parser import get_download_url, get_firmware_metadata


def main(argv: Optional[list[str]] = None) -> None:
    """Parse arguments and dispatch to the appropriate sub-command."""
    parser = argparse.ArgumentParser(
        prog="motofw",
        description="Query and download Motorola OTA firmware updates.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to config.ini (default: ./config.ini)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v for INFO, -vv for DEBUG).",
    )

    subparsers = parser.add_subparsers(dest="command")

    # -- check ----------------------------------------------------------------
    check_parser = subparsers.add_parser(
        "check",
        help="Check for available OTA updates.",
    )

    # -- download -------------------------------------------------------------
    dl_parser = subparsers.add_parser(
        "download",
        help="Download the latest OTA firmware.",
    )
    dl_parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output directory for the firmware file.",
    )

    # -- full -----------------------------------------------------------------
    full_parser = subparsers.add_parser(
        "full",
        help="Check, get resources, and download in one step.",
    )
    full_parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output directory for the firmware file.",
    )

    args = parser.parse_args(argv)

    # Logging setup.
    level = logging.WARNING
    if args.verbose >= 2:
        level = logging.DEBUG
    elif args.verbose >= 1:
        level = logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    if not args.command:
        parser.print_help()
        sys.exit(0)

    config = Config(args.config)

    if args.command == "check":
        _cmd_check(config)
    elif args.command == "download":
        _cmd_download(config, output_dir=args.output)
    elif args.command == "full":
        _cmd_full(config, output_dir=args.output)


def _cmd_check(config: Config) -> None:
    """Execute the ``check`` sub-command."""
    client = OTAClient(config)
    try:
        response = check_update(config, client)
        result = {
            "proceed": response.proceed,
            "context": response.context,
            "contextKey": response.context_key,
            "trackingId": response.tracking_id,
            "pollAfterSeconds": response.poll_after_seconds,
        }
        metadata = get_firmware_metadata(response)
        if metadata:
            result["version"] = metadata.get("version", "")
            result["displayVersion"] = metadata.get("displayVersion", "")
            result["size"] = metadata.get("size", 0)
            result["md5_checksum"] = metadata.get("md5_checksum", "")
            result["updateType"] = metadata.get("updateType", "")
        print(json.dumps(result, indent=2))
    finally:
        client.close()


def _cmd_download(config: Config, *, output_dir: Optional[Path] = None) -> None:
    """Execute the ``download`` sub-command."""
    client = OTAClient(config)
    try:
        # First check for update.
        check_resp = check_update(config, client)
        if not check_resp.proceed:
            print(json.dumps({"update_available": False}))
            return

        # Then get resources.
        resources_resp = get_resources(config, client, check_resp)
        download_url = get_download_url(resources_resp)
        if not download_url:
            print(json.dumps({"error": "No download URL in resources response"}))
            return

        # Download the firmware.
        dest = output_dir or config.output_dir
        path = download_update(config, client, resources_resp, output_dir=dest)
        print(json.dumps({"downloaded": str(path)}))
    finally:
        client.close()


def _cmd_full(config: Config, *, output_dir: Optional[Path] = None) -> None:
    """Execute the ``full`` sub-command."""
    result = query_and_download(config, output_dir=output_dir)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
