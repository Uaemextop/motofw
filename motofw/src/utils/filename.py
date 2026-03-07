"""Filename sanitisation for server-supplied filenames.

Ensures that filenames from server responses are safe to write to the
local filesystem (no directory traversal, no unsafe characters).
"""

from __future__ import annotations

import re
from pathlib import Path

# Maximum sane filename length (most filesystems cap at 255).
_MAX_FILENAME_LEN = 200

# Characters allowed in sanitised filenames.
_SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._\-]")


def sanitize_filename(raw: str) -> str:
    """Sanitise a server-supplied filename for safe local storage.

    - Strips directory traversal components.
    - Replaces unsafe characters with ``_``.
    - Truncates to :data:`_MAX_FILENAME_LEN` characters.

    Parameters
    ----------
    raw:
        The original filename string (e.g. from ``packageID``).

    Returns
    -------
    str
        A filesystem-safe filename.
    """
    name = Path(raw).name
    name = _SAFE_FILENAME_RE.sub("_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    if len(name) > _MAX_FILENAME_LEN:
        name = name[:_MAX_FILENAME_LEN]
    return name or "firmware.zip"
