"""CLI command implementations and entry point."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Optional, Sequence

from motofw.src.api.body import check_body
from motofw.src.api.headers import DEFAULT_HEADERS
from motofw.src.api.orchestrator import check_update, download_firmware, get_resources
from motofw.src.api.response import parse_check_response, parse_content_resources
from motofw.src.api.scanner import ScanReport, ScanResult, scan_updates
from motofw.src.api.session import OTASession
from motofw.src.api.urls import check_url
from motofw.src.cli.log import setup_logging
from motofw.src.cli.output import (
    print_downloaded,
    print_error,
    print_no_update,
    print_query_result,
    print_scan_results,
    print_update_info,
)
from motofw.src.cli.parser import build_parser
from motofw.src.config.options import CONFIGURABLE_PARAMS, SERVER_OPTIONS
from motofw.src.config.settings import Config, load_config
from motofw.src.device.adb import (
    ADBError,
    connect_wireless,
    extract_device_info,
    find_adb,
    pair_wireless,
    wait_for_device,
    write_device_ini,
)
from motofw.src.download.manager import download_update

logger = logging.getLogger("motofw")


def _apply_overrides(
    cfg: Config,
    *,
    ota_source_sha1: Optional[str] = None,
    serial: Optional[str] = None,
    output_dir: Optional[Path] = None,
    no_verify: bool = False,
    triggered_by: Optional[str] = None,
    network: Optional[str] = None,
    bootloader_status: Optional[str] = None,
    build_type: Optional[str] = None,
    user_location: Optional[str] = None,
    server: Optional[str] = None,
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
    if network is not None:
        kw["network"] = network
    if bootloader_status is not None:
        kw["bootloader_status"] = bootloader_status
    if build_type is not None:
        kw["build_type"] = build_type
    if user_location is not None:
        kw["user_location"] = user_location
    if server is not None:
        kw["server_url"] = SERVER_OPTIONS[server]
    return Config(**kw)


def _build_base_url(cfg: Config) -> str:
    """Build the full HTTPS base URL from Config."""
    return f"https://{cfg.server_url}"


def _dump_curl(cfg: Config, body: dict[str, Any]) -> None:
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


def _cmd_query(cfg: Config, *, dump_request: bool = False, raw: bool = False, triggered_by: str = "user") -> int:
    """Execute the ``query`` sub-command."""
    logger.info("Query: build_id=%s sha1=%s serial=%s", cfg.build_id, cfg.ota_source_sha1, cfg.serial_number)

    body = check_body(cfg, triggered_by=triggered_by)

    if dump_request:
        _dump_curl(cfg, body)

    with OTASession(cfg) as ses:
        resp_http = ses.post(check_url(cfg), json_body=body)
        raw_json: dict[str, Any] = resp_http.json()

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


def _choose_option(label: str, options: list[str], current: str) -> str:
    """Present a numbered menu for a single parameter and return the chosen value."""
    sys.stdout.write(f"\n{label} (current: {current}):\n")
    for idx, opt in enumerate(options, 1):
        marker = " *" if opt == current else ""
        sys.stdout.write(f"  [{idx}] {opt}{marker}\n")
    sys.stdout.write(f"  [0] Keep current ({current})\n")

    while True:
        try:
            sys.stdout.write("  Choice: ")
            sys.stdout.flush()
            raw = input().strip()
        except (EOFError, KeyboardInterrupt):
            return current
        if not raw or raw == "0":
            return current
        try:
            choice = int(raw)
        except ValueError:
            sys.stdout.write("  Please enter a number.\n")
            continue
        if 1 <= choice <= len(options):
            return options[choice - 1]
        sys.stdout.write(f"  Please enter 0–{len(options)}.\n")


def _interactive_configure(cfg: Config, triggered_by: str) -> tuple[Config, str]:
    """Let the user interactively select API request parameters.

    Returns the updated Config and triggered_by value.
    """
    sys.stdout.write("\n── Configure API request parameters ──\n")
    sys.stdout.write("(Values from Motorola OTA APK smali analysis)\n")

    overrides: dict[str, Any] = {}

    for key, info in CONFIGURABLE_PARAMS.items():
        if key == "triggered_by":
            triggered_by = _choose_option(info["label"], info["options"], triggered_by)
        elif key == "server":
            # Map current server_url back to server name for display
            current_name = "production"
            for name, host in SERVER_OPTIONS.items():
                if host == cfg.server_url:
                    current_name = name
                    break
            chosen = _choose_option(info["label"], info["options"], current_name)
            if chosen != current_name:
                overrides["server"] = chosen
        else:
            current = getattr(cfg, key, info["default"])
            chosen = _choose_option(info["label"], info["options"], current)
            if chosen != current:
                overrides[key] = chosen

    if overrides:
        cfg = _apply_overrides(cfg, **overrides)

    sys.stdout.write("\n── Configuration complete ──\n")
    return cfg, triggered_by


def _cmd_scan(cfg: Config, *, no_interactive: bool = False, configure: bool = False, triggered_by: str = "user", discover: bool = False) -> int:
    """Execute the ``scan`` sub-command — find all available OTAs and let user choose."""
    if configure:
        cfg, triggered_by = _interactive_configure(cfg, triggered_by)

    if discover:
        return _cmd_discover(cfg, triggered_by=triggered_by, no_interactive=no_interactive)

    sys.stdout.write("Scanning all known builds for available updates …\n")
    sys.stdout.write(f"Device: {cfg.model} ({cfg.product}/{cfg.hardware})\n")
    sys.stdout.write(f"Serial: {cfg.serial_number}  IMEI: {cfg.imei}\n")
    sys.stdout.write(f"Server: {cfg.server_url}\n")
    sys.stdout.write(
        f"Network: {cfg.network}  Bootloader: {cfg.bootloader_status}  "
        f"Build type: {cfg.build_type}  Trigger: {triggered_by}\n\n"
    )

    with OTASession(cfg) as ses:
        report = scan_updates(cfg, session=ses, triggered_by=triggered_by)

    if report.errors:
        for err in report.errors:
            sys.stderr.write(f"Warning: {err}\n")

    if not report.results:
        sys.stdout.write(
            f"No updates found across {report.builds_queried} builds queried.\n"
            "The server may not be serving updates for this device/serial.\n"
        )
        return 0

    print_scan_results(report)

    if no_interactive:
        return 0

    # Interactive menu
    return _interactive_download(cfg, report)


def _cmd_discover(cfg: Config, *, triggered_by: str = "user", no_interactive: bool = False) -> int:
    """Multi-server discovery: query all Motorola servers for available OTAs.

    Searches production, QA, dev, staging, China production, and China staging
    servers.  Each server is queried with every known build SHA1 to find all
    available firmware updates.

    Server endpoints discovered from smali analysis (UpgradeUtils.smali):
      production     = moto-cds.appspot.com
      china          = moto-cds.svcmot.cn
      qa             = moto-cds-qa.appspot.com       (may return 503)
      dev            = moto-cds-dev.appspot.com
      staging        = moto-cds-staging.appspot.com
      china-staging  = ota-cn-sdc.blurdev.com
    """
    from motofw.src.api.scanner import scan_updates

    sys.stdout.write("\n── Multi-server OTA Discovery ──\n")
    sys.stdout.write(f"Device: {cfg.model} ({cfg.product}/{cfg.hardware})\n")
    sys.stdout.write(f"Serial: {cfg.serial_number}  IMEI: {cfg.imei}\n")
    sys.stdout.write(f"Trigger: {triggered_by}\n")
    sys.stdout.write(f"Servers: {len(SERVER_OPTIONS)}\n\n")

    all_results: list[ScanResult] = []
    all_errors: list[str] = []
    total_queried = 0
    servers_ok = 0
    servers_fail = 0

    for name, host in SERVER_OPTIONS.items():
        sys.stdout.write(f"  [{name}] {host} … ")
        sys.stdout.flush()

        # Use shorter retries for discovery (2s, 5s) since we query 6 servers.
        # WebServiceThread.smali backoff starts at 2s — we use the first two.
        srv_cfg = _apply_overrides(cfg, server=name)
        srv_kw = {f.name: getattr(srv_cfg, f.name) for f in srv_cfg.__dataclass_fields__.values()}
        srv_kw["retry_delays_ms"] = [2000, 5000]
        srv_cfg = Config(**srv_kw)

        try:
            with OTASession(srv_cfg) as ses:
                report = scan_updates(srv_cfg, session=ses, triggered_by=triggered_by)
        except Exception as exc:
            servers_fail += 1
            msg = f"{name} ({host}): {exc}"
            all_errors.append(msg)
            sys.stdout.write(f"✗ error ({type(exc).__name__})\n")
            continue

        servers_ok += 1
        total_queried += report.builds_queried

        if report.results:
            for r in report.results:
                r.server_name = name
            all_results.extend(report.results)
            sys.stdout.write(f"✓ {len(report.results)} update(s)\n")
        else:
            sys.stdout.write(f"– no updates ({report.builds_queried} builds checked)\n")

        for err in report.errors:
            all_errors.append(f"{name}: {err}")

    sys.stdout.write(f"\n── Discovery Summary ──\n")
    sys.stdout.write(
        f"Servers OK: {servers_ok}/{len(SERVER_OPTIONS)}  "
        f"Builds checked: {total_queried}  "
        f"Updates found: {len(all_results)}\n"
    )

    if all_errors:
        sys.stdout.write(f"\nWarnings ({len(all_errors)}):\n")
        for err in all_errors:
            sys.stderr.write(f"  • {err}\n")

    if not all_results:
        sys.stdout.write(
            "\nNo updates found across any server.\n"
            "The server may not be serving updates for this device/serial combination.\n"
            "Tip: Try a different serial number with --serial to check rollout status.\n"
        )
        return 0

    # Print results with server column
    sys.stdout.write(f"\nFound {len(all_results)} update(s):\n\n")
    sys.stdout.write(
        f"{'#':>3}  {'Server':<16} {'Source Build':<22} {'Target Build':<22} {'Type':<6} {'Size':>12}\n"
    )
    sys.stdout.write(f"{'─' * 3}  {'─' * 16} {'─' * 22} {'─' * 22} {'─' * 6} {'─' * 12}\n")
    for idx, r in enumerate(all_results, 1):
        size_mb = f"{r.size / (1024 * 1024):.1f} MB"
        sys.stdout.write(
            f"{idx:>3}  {r.server_name:<16} {r.source_build:<22} {r.target_build:<22} "
            f"{r.update_type:<6} {size_mb:>12}\n"
        )
    sys.stdout.write("\n")

    if no_interactive:
        return 0

    # Build a combined report for the interactive download menu
    combined = ScanReport(results=all_results, errors=all_errors, builds_queried=total_queried)
    return _interactive_download(cfg, combined)


def _interactive_download(cfg: Config, report: ScanReport) -> int:
    """Present an interactive menu for choosing which update to download."""
    results = report.results
    sys.stdout.write("\n── Choose an update to download ──\n")
    for idx, r in enumerate(results, 1):
        size_mb = r.size / (1024 * 1024)
        sys.stdout.write(
            f"  [{idx}] {r.source_build} → {r.target_build}"
            f"  ({r.update_type}, {size_mb:.1f} MB)\n"
        )
    sys.stdout.write(f"  [0] Exit without downloading\n\n")

    while True:
        try:
            sys.stdout.write("Enter choice: ")
            sys.stdout.flush()
            raw_input = input().strip()
        except (EOFError, KeyboardInterrupt):
            sys.stdout.write("\nCancelled.\n")
            return 0

        if not raw_input:
            continue
        try:
            choice = int(raw_input)
        except ValueError:
            sys.stdout.write("Please enter a number.\n")
            continue

        if choice == 0:
            sys.stdout.write("Exiting.\n")
            return 0
        if 1 <= choice <= len(results):
            break
        sys.stdout.write(f"Please enter a number between 0 and {len(results)}.\n")

    selected = results[choice - 1]
    sys.stdout.write(
        f"\nDownloading: {selected.source_build} → {selected.target_build}\n"
    )

    # Use the check_response from the scan which already has content info
    resp = selected.check_response

    if resp.content:
        print_update_info(
            resp.content.source_display_version,
            resp.content.display_version,
            resp.content.size,
            resp.content.md5_checksum,
            resp.content.update_type,
        )

    # Need to get resources if not already present
    with OTASession(cfg) as ses:
        resp = download_firmware(cfg, resp, session=ses)

        if not resp.content_resources:
            print_error("Update found but no download URL available.")
            return 1

        dest = download_update(cfg, resp, session=ses)
        print_downloaded(str(dest))
        return 0


def _validate_device_config(cfg: Config) -> bool:
    """Check that essential device fields are configured.

    Returns True if the config looks valid; False if required fields are
    missing (empty).  Prints a helpful message when validation fails.
    """
    required = {
        "fingerprint": cfg.fingerprint,
        "serial_number": cfg.serial_number,
        "product": cfg.product,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        sys.stderr.write(
            "\n⚠  Device not configured — the following required fields are empty:\n"
        )
        for k in missing:
            sys.stderr.write(f"   • {k}\n")
        sys.stderr.write(
            "\nSetup options:\n"
            "  1. Connect your device via USB and run:\n"
            "       motofw settings auto-settings-adb\n"
            "  2. Copy and edit the example file:\n"
            "       cp device.ini.example device.ini\n\n"
        )
        return False
    return True


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
    # New configurable parameter overrides
    if hasattr(args, "network") and args.network:
        overrides["network"] = args.network
    if hasattr(args, "bootloader_status") and args.bootloader_status:
        overrides["bootloader_status"] = args.bootloader_status
    if hasattr(args, "build_type") and args.build_type:
        overrides["build_type"] = args.build_type
    if hasattr(args, "user_location") and args.user_location:
        overrides["user_location"] = args.user_location
    if hasattr(args, "server") and args.server:
        overrides["server"] = args.server
    if overrides:
        cfg = _apply_overrides(cfg, **overrides)

    triggered_by = getattr(args, "triggered_by", None) or "user"

    if args.command == "query":
        if not _validate_device_config(cfg):
            return 1
        return _cmd_query(
            cfg,
            dump_request=getattr(args, "dump_request", False),
            raw=getattr(args, "raw", False),
            triggered_by=triggered_by,
        )
    if args.command == "download":
        if not _validate_device_config(cfg):
            return 1
        return _cmd_download(cfg, dump_request=getattr(args, "dump_request", False))
    if args.command == "scan":
        if not _validate_device_config(cfg):
            return 1
        return _cmd_scan(
            cfg,
            no_interactive=getattr(args, "no_interactive", False),
            configure=getattr(args, "configure", False),
            triggered_by=triggered_by,
            discover=getattr(args, "discover", False),
        )
    if args.command == "settings":
        return _cmd_settings(args)
    ap.print_help()
    return 1


def _cmd_settings(args: Any) -> int:
    """Execute the ``settings`` sub-command."""
    settings_cmd = getattr(args, "settings_command", None)
    if settings_cmd == "auto-settings-adb":
        return _cmd_auto_settings_adb(output=args.output)
    sys.stdout.write("Usage: motofw settings auto-settings-adb [-o device.ini]\n")
    return 1


def _cmd_auto_settings_adb(*, output: Path) -> int:
    """Extract device properties via ADB and write device.ini.

    Presents an interactive menu to choose USB or wireless ADB.
    """
    sys.stdout.write("\n── Auto Settings via ADB ──\n")
    sys.stdout.write("Extract device properties and generate device.ini.\n\n")

    try:
        adb_path = find_adb()
    except ADBError as exc:
        print_error(str(exc))
        return 1

    sys.stdout.write(f"ADB found: {adb_path}\n\n")
    sys.stdout.write("Connection method:\n")
    sys.stdout.write("  [1] USB (device connected via USB cable)\n")
    sys.stdout.write("  [2] Wireless (ADB over Wi-Fi / TCP)\n")
    sys.stdout.write("  [0] Cancel\n\n")

    while True:
        try:
            sys.stdout.write("Choice: ")
            sys.stdout.flush()
            raw = input().strip()
        except (EOFError, KeyboardInterrupt):
            sys.stdout.write("\nCancelled.\n")
            return 0

        if raw == "0":
            sys.stdout.write("Cancelled.\n")
            return 0
        if raw in ("1", "2"):
            break
        sys.stdout.write("Please enter 0, 1, or 2.\n")

    try:
        if raw == "1":
            # USB connection
            wait_for_device(adb_path=adb_path)
        else:
            # Wireless connection
            _setup_wireless_adb(adb_path=adb_path)

        sys.stdout.write("\nExtracting device properties …\n")
        info = extract_device_info(adb_path=adb_path)

        # Display extracted info
        sys.stdout.write(f"\n── Extracted Device Info ──\n")
        sys.stdout.write(f"  Model:        {info.get('brand', '')} {info.get('model', '')}\n")
        sys.stdout.write(f"  Product:      {info.get('product', '')}\n")
        sys.stdout.write(f"  Fingerprint:  {info.get('fingerprint', '')}\n")
        sys.stdout.write(f"  Build ID:     {info.get('build_id', '')}\n")
        sys.stdout.write(f"  OTA SHA1:     {info.get('ota_source_sha1', '')}\n")
        sys.stdout.write(f"  Serial:       {info.get('serial_number', '')}\n")
        sys.stdout.write(f"  IMEI:         {info.get('imei', '')}\n")
        if info.get("imei2"):
            sys.stdout.write(f"  IMEI2:        {info.get('imei2', '')}\n")
        sys.stdout.write(f"  Bootloader:   {info.get('bootloader_status', '')}\n")
        sys.stdout.write(f"  Android:      {info.get('os_version', '')}\n")

        dest = write_device_ini(info, output)
        sys.stdout.write(f"\n✓ device.ini written to: {dest}\n")
        return 0

    except ADBError as exc:
        print_error(str(exc))
        return 1


def _setup_wireless_adb(*, adb_path: str) -> None:
    """Interactive wireless ADB setup with optional pairing."""
    sys.stdout.write("\n── Wireless ADB Setup ──\n")
    sys.stdout.write("On your device: Settings → Developer Options → Wireless debugging\n\n")
    sys.stdout.write("Is the device already paired with this computer?\n")
    sys.stdout.write("  [1] Yes — just connect\n")
    sys.stdout.write("  [2] No — pair first\n\n")

    while True:
        try:
            sys.stdout.write("Choice: ")
            sys.stdout.flush()
            raw = input().strip()
        except (EOFError, KeyboardInterrupt):
            raise ADBError("Cancelled by user.")
        if raw in ("1", "2"):
            break
        sys.stdout.write("Please enter 1 or 2.\n")

    if raw == "2":
        # Pairing flow
        sys.stdout.write("\nOn device: tap 'Pair device with pairing code'\n")
        try:
            sys.stdout.write("Pairing IP address: ")
            sys.stdout.flush()
            pair_ip = input().strip()
            sys.stdout.write("Pairing port: ")
            sys.stdout.flush()
            pair_port = int(input().strip())
            sys.stdout.write("Pairing code (6 digits): ")
            sys.stdout.flush()
            pair_code = input().strip()
        except (EOFError, KeyboardInterrupt):
            raise ADBError("Cancelled by user.")
        except ValueError:
            raise ADBError("Invalid port number.")

        pair_wireless(pair_ip, pair_port, pair_code, adb_path=adb_path)

    # Connect to device
    sys.stdout.write("\nDevice IP and port for ADB connection:\n")
    sys.stdout.write("(Shown under 'Wireless debugging' on the device)\n")
    try:
        sys.stdout.write("Device IP address: ")
        sys.stdout.flush()
        ip = input().strip()
        sys.stdout.write("Device port (default 5555): ")
        sys.stdout.flush()
        port_raw = input().strip()
        port = int(port_raw) if port_raw else 5555
    except (EOFError, KeyboardInterrupt):
        raise ADBError("Cancelled by user.")
    except ValueError:
        raise ADBError("Invalid port number.")

    connect_wireless(ip, port, adb_path=adb_path)
