"""Command-line interface for motofw.

Provides two sub-commands:

``query``
    Check the Motorola OTA server for available firmware updates and
    print the result as JSON.

``download``
    Query for an update and, if one is available, stream-download the
    firmware package with MD5 verification.

Entry point: ``motofw.cli:main`` (registered in ``pyproject.toml``).
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

from motofw.api import check_update, get_resources
from motofw.client import OTAClient
from motofw.config import Config, load_config
from motofw.downloader import download_update

logger = logging.getLogger("motofw")


def _configure_logging(verbosity: int) -> None:
    """Set up the root ``motofw`` logger based on ``-v`` count."""
    level = logging.WARNING
    if verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    root = logging.getLogger("motofw")
    root.setLevel(level)
    root.addHandler(handler)


def _build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser."""
    parser = argparse.ArgumentParser(
        prog="motofw",
        description="Query and download Motorola OTA firmware updates.",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=None,
        help="Path to config.ini (default: auto-detect).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v info, -vv debug).",
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # --- query ---
    query_p = sub.add_parser("query", help="Check for an available OTA update.")
    query_p.add_argument(
        "--ota-source-sha1",
        default=None,
        help="Override the device's otaSourceSha1 context key.",
    )
    query_p.add_argument(
        "--serial",
        default=None,
        help="Override the device serial number.",
    )

    # --- download ---
    dl_p = sub.add_parser("download", help="Download an available OTA update.")
    dl_p.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help="Directory to save the firmware file (default: from config).",
    )
    dl_p.add_argument(
        "--ota-source-sha1",
        default=None,
        help="Override the device's otaSourceSha1 context key.",
    )
    dl_p.add_argument(
        "--serial",
        default=None,
        help="Override the device serial number.",
    )
    dl_p.add_argument(
        "--no-verify",
        action="store_true",
        default=False,
        help="Skip MD5 checksum verification after download.",
    )

    return parser


def _apply_overrides(
    cfg: Config,
    *,
    ota_source_sha1: Optional[str] = None,
    serial: Optional[str] = None,
    output_dir: Optional[Path] = None,
    no_verify: bool = False,
) -> Config:
    """Return a new Config with CLI overrides applied."""
    # dataclass is frozen so we rebuild it via __init__ kwargs
    kw = {f.name: getattr(cfg, f.name) for f in cfg.__dataclass_fields__.values()}
    if ota_source_sha1 is not None:
        kw["ota_source_sha1"] = ota_source_sha1
    if serial is not None:
        kw["serial_number"] = serial
    if output_dir is not None:
        kw["output_dir"] = output_dir
    if no_verify:
        kw["verify_checksum"] = False
    return Config(**kw)


def _cmd_query(cfg: Config) -> int:
    """Execute the ``query`` sub-command."""
    with OTAClient(cfg) as client:
        resp = check_update(cfg, client=client)

    # Build a human-readable JSON summary
    output: dict = {
        "proceed": resp.proceed,
        "context": resp.context,
        "contextKey": resp.context_key,
        "trackingId": resp.tracking_id,
        "pollAfterSeconds": resp.poll_after_seconds,
    }
    if resp.content:
        output["content"] = {
            "packageID": resp.content.package_id,
            "version": resp.content.version,
            "sourceVersion": resp.content.source_display_version,
            "displayVersion": resp.content.display_version,
            "size": resp.content.size,
            "md5": resp.content.md5_checksum,
            "updateType": resp.content.update_type,
            "model": resp.content.model,
        }
    if resp.content_resources:
        output["downloadUrls"] = [r.url for r in resp.content_resources]

    sys.stdout.write(json.dumps(output, indent=2) + "\n")
    return 0


def _cmd_download(cfg: Config) -> int:
    """Execute the ``download`` sub-command."""
    with OTAClient(cfg) as client:
        logger.info("Querying for available update …")
        resp = check_update(cfg, client=client)

        if not resp.proceed:
            logger.info("No update available.")
            sys.stdout.write("No update available.\n")
            return 0

        if not resp.content_resources:
            # Try the resources endpoint to get download URLs
            logger.info("No resources in check response; fetching via /resources …")
            if resp.tracking_id:
                get_resources(
                    cfg,
                    tracking_id=resp.tracking_id,
                    client=client,
                )
            else:
                logger.warning("No tracking ID — cannot fetch resources")
                sys.stdout.write("Update found but no download URL available.\n")
                return 1

        dest = download_update(cfg, resp, client=client)
        sys.stdout.write(f"Downloaded: {dest}\n")
        return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI entry point.

    Parameters
    ----------
    argv:
        Command-line arguments.  Defaults to ``sys.argv[1:]``.

    Returns
    -------
    int
        Exit code (``0`` on success).
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    _configure_logging(args.verbose)

    if args.command is None:
        parser.print_help()
        return 1

    cfg = load_config(args.config)

    # Apply any CLI overrides
    override_kwargs: dict = {}
    if hasattr(args, "ota_source_sha1") and args.ota_source_sha1:
        override_kwargs["ota_source_sha1"] = args.ota_source_sha1
    if hasattr(args, "serial") and args.serial:
        override_kwargs["serial"] = args.serial
    if hasattr(args, "output_dir") and args.output_dir:
        override_kwargs["output_dir"] = args.output_dir
    if hasattr(args, "no_verify") and args.no_verify:
        override_kwargs["no_verify"] = True

    if override_kwargs:
        cfg = _apply_overrides(cfg, **override_kwargs)

    if args.command == "query":
        return _cmd_query(cfg)
    elif args.command == "download":
        return _cmd_download(cfg)
    else:
        parser.print_help()
        return 1
