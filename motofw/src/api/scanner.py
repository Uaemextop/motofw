"""Scan the OTA server for all available firmware updates.

Queries the server using multiple known build SHA1 keys to discover
which OTA updates are available for download.  Follows the update chain
forward from the oldest known build, collecting every update the server
is willing to serve.
"""

from __future__ import annotations

import copy
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from motofw.src.api.body import check_body
from motofw.src.api.response import parse_check_response
from motofw.src.api.session import OTASession
from motofw.src.api.urls import check_url
from motofw.src.config.settings import Config
from motofw.src.utils.models import CheckResponse

logger = logging.getLogger(__name__)

# ── Known update chain for moto g05 (lamul_g / lamu) ──────────────
# Extracted from V1 release logs.

KNOWN_BUILDS: List[Dict[str, str]] = [
    {
        "build_id": "VVTA35.51-28-15",
        "sha1": "23d670d5d06f351",
        "fingerprint": "motorola/lamul_g/lamul:15/VVTA35.51-28-15/bd4d30:user/release-keys",
    },
    {
        "build_id": "VVTA35.51-65-5",
        "sha1": "a363e2a67728d8a",
        "fingerprint": "motorola/lamul_g/lamul:15/VVTA35.51-65-5/b608f4:user/release-keys",
    },
    {
        "build_id": "VVTA35.51-100",
        "sha1": "190325d96009ac5",
        "fingerprint": "motorola/lamul_g/lamul:15/VVTA35.51-100/e51bc9:user/release-keys",
    },
    {
        "build_id": "VVTAS35.51-100-3",
        "sha1": "96398c9adf48ac1",
        "fingerprint": "motorola/lamul_g/lamul:15/VVTAS35.51-100-3/96398c:user/release-keys",
    },
]


@dataclass
class ScanResult:
    """One available firmware update discovered during a scan."""

    source_build: str
    source_sha1: str
    target_build: str
    target_sha1: str
    size: int
    md5: str
    update_type: str
    package_id: str
    model: str
    release_notes: str
    check_response: CheckResponse


@dataclass
class ScanReport:
    """Full results of a scan across all known builds."""

    results: List[ScanResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    builds_queried: int = 0


def _make_cfg_for_build(cfg: Config, build: Dict[str, str]) -> Config:
    """Return a modified Config targeting *build*."""
    kw = {f.name: getattr(cfg, f.name) for f in cfg.__dataclass_fields__.values()}
    kw["ota_source_sha1"] = build["sha1"]
    kw["build_id"] = build["build_id"]
    kw["build_display_id"] = build["build_id"]
    kw["fingerprint"] = build["fingerprint"]
    return Config(**kw)


def scan_updates(
    cfg: Config,
    *,
    session: Optional[OTASession] = None,
    builds: Optional[List[Dict[str, str]]] = None,
) -> ScanReport:
    """Query the server for each known build and collect available updates.

    Parameters
    ----------
    cfg:
        Base configuration (device identity, server URL, etc.).
    session:
        Reuse an existing session, or one will be created.
    builds:
        Override the default list of builds to query.

    Returns
    -------
    ScanReport
        All discovered updates plus any errors.
    """
    target_builds = builds or KNOWN_BUILDS
    report = ScanReport()

    own = session is None
    if own:
        session = OTASession(cfg)

    try:
        for build in target_builds:
            report.builds_queried += 1
            build_cfg = _make_cfg_for_build(cfg, build)
            logger.info(
                "Scanning build %s (sha1=%s) …",
                build["build_id"],
                build["sha1"],
            )
            try:
                body = check_body(build_cfg)
                path = check_url(build_cfg)
                resp_http = session.post(path, json_body=body)
                raw: Dict[str, Any] = resp_http.json()
                resp = parse_check_response(raw)

                if resp.proceed and resp.content:
                    result = ScanResult(
                        source_build=build["build_id"],
                        source_sha1=build["sha1"],
                        target_build=resp.content.display_version or resp.content.version,
                        target_sha1=resp.content.ota_target_sha1,
                        size=resp.content.size,
                        md5=resp.content.md5_checksum,
                        update_type=resp.content.update_type,
                        package_id=resp.content.package_id,
                        model=resp.content.model,
                        release_notes=resp.content.release_notes,
                        check_response=resp,
                    )
                    report.results.append(result)
                    logger.info(
                        "  → Update found: %s → %s (%s, %d bytes)",
                        result.source_build,
                        result.target_build,
                        result.update_type,
                        result.size,
                    )
                else:
                    logger.info("  → No update available for %s", build["build_id"])

            except Exception as exc:
                msg = f"Error querying {build['build_id']}: {exc}"
                report.errors.append(msg)
                logger.warning(msg)

    finally:
        if own:
            session.close()

    return report
