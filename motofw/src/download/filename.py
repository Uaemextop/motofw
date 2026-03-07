"""Filename sanitisation for server-supplied file names."""

from __future__ import annotations

import re
from pathlib import Path

_MAX_LEN = 200
_UNSAFE = re.compile(r"[^A-Za-z0-9._\-]")


def sanitize(raw: str) -> str:
    """Return a filesystem-safe version of *raw*.

    Strips directory components, replaces unsafe characters, and
    truncates to 200 characters.
    """
    name = Path(raw).name
    name = _UNSAFE.sub("_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    if len(name) > _MAX_LEN:
        name = name[:_MAX_LEN]
    return name or "firmware.zip"
