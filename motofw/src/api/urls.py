"""Build endpoint URL paths from configuration values."""

from __future__ import annotations

from motofw.src.config.settings import Config


def check_url(cfg: Config) -> str:
    """Return the relative path for the ``/check`` endpoint."""
    return f"/{cfg.check_path}/ctx/{cfg.context}/key/{cfg.ota_source_sha1}"


def resources_url(cfg: Config, tracking_id: str) -> str:
    """Return the relative path for the ``/resources`` endpoint."""
    return (
        f"/{cfg.resources_path}/t/{tracking_id}"
        f"/ctx/{cfg.context}/key/{cfg.ota_source_sha1}"
    )


def state_url(cfg: Config) -> str:
    """Return the relative path for the ``/state`` endpoint."""
    return f"/{cfg.state_path}/ctx/{cfg.context}/key/{cfg.ota_source_sha1}"
