"""Logging configuration for the motofw CLI."""

from __future__ import annotations

import logging
import sys


def setup_logging(verbosity: int) -> None:
    """Configure the ``motofw`` logger hierarchy.

    Parameters
    ----------
    verbosity:
        0 → WARNING, 1 → INFO, 2+ → DEBUG.
    """
    level = logging.WARNING
    if verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"),
    )

    root = logging.getLogger("motofw")
    root.setLevel(level)
    if not root.handlers:
        root.addHandler(handler)
