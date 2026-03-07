"""HTTP header construction for Motorola OTA requests.

Builds the exact ``Content-Type`` and ``Accept`` headers expected by the
Motorola CDS server.  Evidence from smali analysis shows no custom auth
headers — HTTPS alone provides transport security.
"""

from __future__ import annotations

from typing import Dict, Optional


# Default headers for every OTA API request (evidence: CDSUtils.smali).
DEFAULT_HEADERS: Dict[str, str] = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def build_request_headers(
    extra: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """Return the merged set of HTTP headers for an OTA request.

    Parameters
    ----------
    extra:
        Optional additional headers to merge on top of the defaults.

    Returns
    -------
    dict
        Combined header dict.
    """
    headers = dict(DEFAULT_HEADERS)
    if extra:
        headers.update(extra)
    return headers
