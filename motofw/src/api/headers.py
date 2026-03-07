"""Construct HTTP headers for OTA API requests.

Evidence from smali: no custom auth headers — HTTPS alone provides
transport security.  Content-Type and Accept are always JSON.
"""

from __future__ import annotations

from typing import Dict, Optional

DEFAULT_HEADERS: Dict[str, str] = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def build_headers(extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """Return merged headers for an OTA request."""
    merged = dict(DEFAULT_HEADERS)
    if extra:
        merged.update(extra)
    return merged
