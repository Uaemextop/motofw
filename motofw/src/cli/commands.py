"""CLI command implementations and entry point."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

from motofw.src.api.body import check_body
from motofw.src.api.headers import DEFAULT_HEADERS
from motofw.src.api.orchestrator import check_update, download_firmware, get_resources
from motofw.src.api.response import parse_check_response, parse_content_resources
from motofw.src.api.session import OTASession
from motofw.src.api.urls import check_url
from motofw.src.cli.log import setup_logging
from motofw.src.cli.output import (
    print_downloaded,
    print_error,
    print_no_update,
    print_query_result,
    print_update_info,
)
from motofw.src.cli.parser import build_parser
from motofw.src.config.settings import Config, load_config
from motofw.src.download.manager import download_update

logger = logging.getLogger("motofw")


def _apply_overrides(
    cfg: Config,
    *,
    ota_source_sha1: Optional[str] = None,
    serial: Optional[str] = None,
    output_dir: Optional[Path] = None,
    no_verify: bool = False,
) -> Config:
    """Return a new frozen Config with selected fields replaced."""
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


def _build_base_url(cfg: Config) -> str:
    """Build the full HTTPS base URL from Config."""
    return f"https://{cfg.server_url}"


def _dump_curl(cfg: Config, body: Dict[str, Any]) -> None:
    """Print the request body and an equivalent curl command to stderr."""
    path = check_url(cfg).lstrip("/")
    url = f"{_build_base_url(cfg)}/{path}"
    body_json = json.dumps(body, indent=2)

    sys.stderr.write("\n── Request body ──\n")
    sys.stderr.write(body_json)
    sys.stderr.write("\n\n── Equivalent curl ──\n")
    sys.stderr.write(
        f"curl -s -X POST \\\n"
        f"  -H 'Content-Type: application/json' \\\n"
        f"  -H 'Accept: application/json' \\\n"
        f"  '{url}' \\\n"
        f"  -d '{json.dumps(body)}'\n\n"
    )


def _cmd_query(cfg: Config, *, dump_request: bool = False, raw: bool = False) -> int:
    """Execute the ``query`` sub-command."""
    logger.info("Query: build_id=%s sha1=%s serial=%s", cfg.build_id, cfg.ota_source_sha1, cfg.serial_number)

    body = check_body(cfg)

    if dump_request:
        _dump_curl(cfg, body)

    with OTASession(cfg) as ses:
        resp_http = ses.post(check_url(cfg), json_body=body)
        raw_json: Dict[str, Any] = resp_http.json()

    if raw:
        sys.stdout.write(json.dumps(raw_json, indent=2) + "\n")
        return 0

    resp = parse_check_response(raw_json)
    print_query_result(resp)
    return 0


def _cmd_download(cfg: Config, *, dump_request: bool = False) -> int:
    """Execute the ``download`` sub-command."""
    if dump_request:
        _dump_curl(cfg, check_body(cfg))

    with OTASession(cfg) as ses:
        logger.info("Check: build_id=%s sha1=%s", cfg.build_id, cfg.ota_source_sha1)
        resp = check_update(cfg, session=ses)

        if not resp.proceed:
            print_no_update(cfg.build_id, cfg.ota_source_sha1, resp.poll_after_seconds)
            return 0

        resp = download_firmware(cfg, resp, session=ses)

        if not resp.content_resources:
            print_error("Update found but no download URL available.")
            return 1

        if resp.content:
            print_update_info(
                resp.content.source_display_version,
                resp.content.display_version,
                resp.content.size,
                resp.content.md5_checksum,
                resp.content.update_type,
            )

        dest = download_update(cfg, resp, session=ses)
        print_downloaded(str(dest))
        return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI entry point (registered in pyproject.toml)."""
    ap = build_parser()
    args = ap.parse_args(argv)
    setup_logging(args.verbose)

    if args.command is None:
        ap.print_help()
        return 1

    cfg = load_config(args.config, device_path=args.device)

    overrides: dict = {}
    if hasattr(args, "ota_source_sha1") and args.ota_source_sha1:
        overrides["ota_source_sha1"] = args.ota_source_sha1
    if hasattr(args, "serial") and args.serial:
        overrides["serial"] = args.serial
    if hasattr(args, "output_dir") and args.output_dir:
        overrides["output_dir"] = args.output_dir
    if hasattr(args, "no_verify") and args.no_verify:
        overrides["no_verify"] = True
    if overrides:
        cfg = _apply_overrides(cfg, **overrides)

    if args.command == "query":
        return _cmd_query(
            cfg,
            dump_request=getattr(args, "dump_request", False),
            raw=getattr(args, "raw", False),
        )
    if args.command == "download":
        return _cmd_download(cfg, dump_request=getattr(args, "dump_request", False))
    ap.print_help()
    return 1
