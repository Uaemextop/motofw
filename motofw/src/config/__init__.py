"""Config subpackage — tool-level settings from ``config.ini``.

Modules
-------
settings
    ``Config`` dataclass and ``load_config`` loader.
"""

from motofw.src.config.settings import Config, load_config

__all__ = ["Config", "load_config"]
