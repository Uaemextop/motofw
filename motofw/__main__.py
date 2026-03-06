"""
Command-line interface for Motofw.

Provides commands for querying, downloading, and analyzing Motorola OTA firmware.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from . import __version__
from .client import OTAClient
from .config import Config
from .device_info import DeviceInfo
from .downloader import FirmwareDownloader
from .parser import ResponseParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def cmd_query(args: argparse.Namespace) -> int:
    """
    Query command: Check for available firmware updates.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Create device info
        device_info = DeviceInfo(
            serial_number=args.serial,
            model=args.model,
            product=args.product,
            build_id=args.build_id,
            build_device=args.build_device,
            carrier=args.carrier,
            color_id=args.color,
            is_prc=args.prc,
            user_language=args.language,
        )

        # Create config and client
        config_path = Path(args.config) if args.config else None
        config = Config(config_path)

        with OTAClient(device_info, config, use_staging=args.staging) as client:
            # Check for updates
            logger.info("Checking for firmware updates...")
            response = client.check_for_update(upgrade_source=args.upgrade_source)

            # Parse response
            parser = ResponseParser()
            result = parser.parse_check_update_response(response)

            if result["update_available"]:
                print("\n✓ Update available!")
                print(f"  Tracking ID: {result['tracking_id']}")
                print(f"  Timestamp: {result['context_timestamp']}")

                # Get download descriptor if requested
                if args.get_url:
                    logger.info("Fetching download URLs...")
                    descriptor = client.get_download_descriptor(
                        result["tracking_id"],
                        result["context_timestamp"]
                    )

                    desc_result = parser.parse_download_descriptor_response(descriptor)

                    if desc_result["resources"]:
                        print("\nDownload URLs:")
                        for i, resource in enumerate(desc_result["resources"], 1):
                            print(f"\n  Resource {i}:")
                            print(f"    URL: {resource['url']}")
                            print(f"    Tags: {', '.join(resource['tags'])}")
                            if resource['headers']:
                                print(f"    Headers: {resource['headers']}")
                    else:
                        print("\n⚠ No download resources found")
                        return 1
            else:
                print("\n✗ No update available")
                if "message" in result:
                    print(f"  Message: {result['message']}")

        return 0

    except Exception as e:
        logger.error(f"Query failed: {e}", exc_info=args.debug)
        return 1


def cmd_download(args: argparse.Namespace) -> int:
    """
    Download command: Download OTA firmware package.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Create device info
        device_info = DeviceInfo(
            serial_number=args.serial,
            model=args.model,
            product=args.product,
            build_id=args.build_id,
            build_device=args.build_device,
            carrier=args.carrier,
            color_id=args.color,
            is_prc=args.prc,
            user_language=args.language,
        )

        # Create config and client
        config_path = Path(args.config) if args.config else None
        config = Config(config_path)

        with OTAClient(device_info, config, use_staging=args.staging) as client:
            # Check for updates
            logger.info("Checking for firmware updates...")
            response = client.check_for_update(upgrade_source=args.upgrade_source)

            # Parse response
            parser = ResponseParser()
            result = parser.parse_check_update_response(response)

            if not result["update_available"]:
                print("✗ No update available")
                return 1

            print("✓ Update found, fetching download URLs...")

            # Get download descriptor
            descriptor = client.get_download_descriptor(
                result["tracking_id"],
                result["context_timestamp"]
            )

            desc_result = parser.parse_download_descriptor_response(descriptor)

            if not desc_result["resources"]:
                print("✗ No download resources found")
                return 1

            # Select resource based on network type
            resource = parser.get_download_url_for_network(
                desc_result["resources"],
                args.network_type
            )

            if not resource:
                print(f"✗ No resource found for network type: {args.network_type}")
                return 1

            print(f"\nDownloading from: {resource['url']}")

            # Download firmware
            output_path = Path(args.output)
            downloader = FirmwareDownloader(client.session)

            success = downloader.download_with_progress_bar(
                url=resource['url'],
                output_path=output_path,
                headers=resource.get('headers'),
                expected_checksum=args.checksum,
                checksum_algorithm=args.checksum_algorithm,
            )

            if success:
                print(f"\n✓ Download complete: {output_path}")
                return 0
            else:
                print("\n✗ Download failed")
                return 1

    except Exception as e:
        logger.error(f"Download failed: {e}", exc_info=args.debug)
        return 1


def cmd_analyze(args: argparse.Namespace) -> int:
    """
    Analyze command: Analyze downloaded firmware package.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Placeholder for future implementation
    print("Analyze command is not yet implemented")
    print(f"Would analyze: {args.package}")
    return 0


def main() -> int:
    """
    Main entry point for CLI.

    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="Motofw - Motorola OTA Firmware Downloader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"motofw {__version__}",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Query command
    query_parser = subparsers.add_parser(
        "query",
        help="Query available firmware updates",
    )
    add_device_args(query_parser)
    add_common_args(query_parser)
    query_parser.add_argument(
        "--get-url",
        action="store_true",
        help="Also fetch download URLs",
    )

    # Download command
    download_parser = subparsers.add_parser(
        "download",
        help="Download firmware update",
    )
    add_device_args(download_parser)
    add_common_args(download_parser)
    download_parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output file path for downloaded firmware",
    )
    download_parser.add_argument(
        "--network-type",
        default="WIFI",
        choices=["WIFI", "CELL", "ADMIN_APN"],
        help="Network type for download (default: WIFI)",
    )
    download_parser.add_argument(
        "--checksum",
        help="Expected checksum for verification",
    )
    download_parser.add_argument(
        "--checksum-algorithm",
        default="sha1",
        choices=["sha1", "sha256", "md5"],
        help="Checksum algorithm (default: sha1)",
    )

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze firmware package (not yet implemented)",
    )
    analyze_parser.add_argument(
        "package",
        help="Path to firmware package",
    )

    args = parser.parse_args()

    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Execute command
    if args.command == "query":
        return cmd_query(args)
    elif args.command == "download":
        return cmd_download(args)
    elif args.command == "analyze":
        return cmd_analyze(args)
    else:
        parser.print_help()
        return 1


def add_device_args(parser: argparse.ArgumentParser) -> None:
    """Add device-related arguments to parser."""
    device_group = parser.add_argument_group("device information")

    device_group.add_argument(
        "-s", "--serial",
        required=True,
        help="Device serial number",
    )
    device_group.add_argument(
        "-m", "--model",
        required=True,
        help="Device model identifier",
    )
    device_group.add_argument(
        "-p", "--product",
        required=True,
        help="Product name",
    )
    device_group.add_argument(
        "-b", "--build-id",
        required=True,
        help="Current firmware build ID",
    )
    device_group.add_argument(
        "--build-device",
        help="Internal device name (defaults to model)",
    )
    device_group.add_argument(
        "--carrier",
        help="Telecom carrier identifier",
    )
    device_group.add_argument(
        "--color",
        help="Device color variant",
    )
    device_group.add_argument(
        "--prc",
        action="store_true",
        help="Device is in PRC (China) region",
    )
    device_group.add_argument(
        "--language",
        default="en-US",
        help="User language/locale (default: en-US)",
    )


def add_common_args(parser: argparse.ArgumentParser) -> None:
    """Add common arguments to parser."""
    common_group = parser.add_argument_group("common options")

    common_group.add_argument(
        "-c", "--config",
        help="Path to config.ini file",
    )
    common_group.add_argument(
        "--staging",
        action="store_true",
        help="Use staging environment",
    )
    common_group.add_argument(
        "--upgrade-source",
        default="UPGRADED_VIA_PULL",
        choices=[
            "UPGRADED_VIA_PULL",
            "UPGRADED_VIA_PAIR",
            "UPGRADED_VIA_INTIAL_SETUP",
            "UPGRADED_VIA_UNKNOWN_METHOD",
        ],
        help="Update trigger source (default: UPGRADED_VIA_PULL)",
    )


if __name__ == "__main__":
    sys.exit(main())
