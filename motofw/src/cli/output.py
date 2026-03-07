"""User-facing output formatting for the CLI."""

from __future__ import annotations

import json
import sys
from typing import Any, Dict

from motofw.src.utils.models import CheckResponse


def print_json(data: Dict[str, Any]) -> None:
    """Write *data* as pretty-printed JSON to stdout."""
    sys.stdout.write(json.dumps(data, indent=2) + "\n")


def print_query_result(resp: CheckResponse) -> None:
    """Print a human-readable summary of a check response."""
    out: Dict[str, Any] = {
        "proceed": resp.proceed,
        "context": resp.context,
        "contextKey": resp.context_key,
        "trackingId": resp.tracking_id,
        "pollAfterSeconds": resp.poll_after_seconds,
    }
    if resp.content:
        out["content"] = {
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
        out["downloadUrls"] = [r.url for r in resp.content_resources]
    print_json(out)


def print_no_update(build_id: str, context_key: str, poll_seconds: int) -> None:
    """Print a message when no update is available."""
    sys.stdout.write(
        f"No update available for build {build_id} "
        f"(contextKey={context_key}).\n"
        f"Server says poll again in {poll_seconds} seconds.\n"
    )


def print_update_info(
    source: str, target: str, size: int, md5: str, update_type: str,
) -> None:
    """Print a summary of the available update."""
    sys.stdout.write(
        f"Update available: {source} → {target}\n"
        f"Size: {size:,} bytes  MD5: {md5}\n"
        f"Type: {update_type}\n"
    )


def print_downloaded(path: str) -> None:
    """Print the path of the downloaded file."""
    sys.stdout.write(f"Downloaded: {path}\n")


def print_error(msg: str) -> None:
    """Print an error message to stderr."""
    sys.stderr.write(f"Error: {msg}\n")
