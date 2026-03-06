"""URL construction and request building for Motorola OTA endpoints.

Mirrors the Java classes:
- ``CheckUrlConstructor`` — builds the check-for-upgrade URL
- ``ResourcesUrlConstructor`` — builds the resources (download descriptor) URL
- ``StateUrlConstructor`` — builds the state-reporting URL
- ``CheckRequestBuilder`` — builds the JSON body for check requests
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any, Optional
from urllib.parse import quote

from motofw.config import Config

logger = logging.getLogger(__name__)

# Identity type used in all requests (from CDSUtils.IDTYPE).
_ID_TYPE = "serialNumber"

# Client identity string (from getExtraInfoAsJsonObject).
_CLIENT_IDENTITY = "motorola-ota-client-app"

# OtaLib version constant (0x30d44 = 200004 in decimal).
_OTA_LIB_VERSION = 200004


def build_check_url(config: Config) -> str:
    """Construct the check-for-upgrade URL.

    Replicates ``CheckUrlConstructor.constructUrl()`` from the smali source.
    The URL pattern is::

        https://<server_url>/<base_url>/ctx/<context>/key/<context_key>

    Parameters
    ----------
    config:
        Loaded configuration.

    Returns
    -------
    str
        The fully-qualified check URL.
    """
    scheme = "https" if config.is_secure else "http"
    server = _resolve_server(config)
    base = config.check_base_url
    context = config.ota_context
    context_key = quote(config.ota_source_sha1, safe="")

    url = f"{scheme}://{server}/{base}/ctx/{context}/key/{context_key}"
    logger.debug("Check URL: %s", url)
    return url


def build_resources_url(config: Config) -> str:
    """Construct the resources (download descriptor) URL.

    Parameters
    ----------
    config:
        Loaded configuration.

    Returns
    -------
    str
        The fully-qualified resources URL.
    """
    scheme = "https" if config.is_secure else "http"
    server = _resolve_server(config)
    base = config.resources_base_url
    context = config.ota_context
    context_key = quote(config.ota_source_sha1, safe="")

    url = f"{scheme}://{server}/{base}/ctx/{context}/key/{context_key}"
    logger.debug("Resources URL: %s", url)
    return url


def build_state_url(
    config: Config,
    tracking_id: str,
    state: str,
) -> str:
    """Construct the state-reporting URL.

    Parameters
    ----------
    config:
        Loaded configuration.
    tracking_id:
        Tracking identifier received in the check response.
    state:
        Current upgrade state string.

    Returns
    -------
    str
        The fully-qualified state URL.
    """
    scheme = "https" if config.is_secure else "http"
    server = _resolve_server(config)
    base = config.state_base_url
    context = config.ota_context
    context_key = quote(config.ota_source_sha1, safe="")

    url = f"{scheme}://{server}/{base}/ctx/{context}/key/{context_key}"
    logger.debug("State URL: %s", url)
    return url


def build_check_body(
    config: Config,
    *,
    content_timestamp: int = 0,
    apk_version: int = 0,
    apk_package_name: str = "com.motorola.ccc.ota",
    provision_time: str = "",
    network: str = "",
    user_language: str = "es_MX",
) -> dict[str, Any]:
    """Build the JSON body for a check-for-upgrade POST request.

    Replicates the ``CheckRequestBuilder.toJSONObject()`` structure
    from the smali source.  The resulting dict has these top-level keys:

    - ``id`` — SHA-1 of ``contextKey + serialNumber``
    - ``contentTimestamp``
    - ``deviceInfo`` — manufacturer, model, product, isPRC, carrier, userLanguage
    - ``extraInfo`` — clientIdentity, brand, buildDevice, buildId, …
    - ``identityInfo`` — ``{ "serialNumber": "…" }``
    - ``triggeredBy`` — user / polling / …
    - ``idType`` — ``"serialNumber"``

    Parameters
    ----------
    config:
        Loaded configuration.
    content_timestamp:
        Timestamp of the last known content version.
    apk_version:
        OTA APK version code.
    apk_package_name:
        OTA APK package name.
    provision_time:
        Device provisioning time string.
    network:
        Current network state string.
    user_language:
        Locale string such as ``es_MX``.

    Returns
    -------
    dict
        JSON-serialisable request body.
    """
    primary_key = _compute_primary_key(
        config.ota_source_sha1, config.serial_number
    )

    device_info = _build_device_info(config, user_language=user_language)
    extra_info = _build_extra_info(
        config,
        network=network,
        apk_version=apk_version,
        provision_time=provision_time,
        apk_package_name=apk_package_name,
    )
    identity_info = {"serialNumber": config.serial_number}

    body: dict[str, Any] = {
        "id": primary_key,
        "contentTimestamp": content_timestamp,
        "deviceInfo": device_info,
        "extraInfo": extra_info,
        "identityInfo": identity_info,
        "triggeredBy": config.triggered_by,
        "idType": _ID_TYPE,
    }
    logger.debug("Check request body built for contextKey=%s", config.ota_source_sha1)
    return body


def build_resources_body(
    config: Config,
    *,
    content_timestamp: int = 0,
    tracking_id: str = "",
) -> dict[str, Any]:
    """Build the JSON body for a resources POST request.

    Parameters
    ----------
    config:
        Loaded configuration.
    content_timestamp:
        Timestamp from the check response.
    tracking_id:
        Tracking identifier from the check response.

    Returns
    -------
    dict
        JSON-serialisable request body.
    """
    primary_key = _compute_primary_key(
        config.ota_source_sha1, config.serial_number
    )

    body: dict[str, Any] = {
        "id": primary_key,
        "contentTimestamp": content_timestamp,
        "deviceInfo": _build_device_info(config),
        "identityInfo": {"serialNumber": config.serial_number},
        "triggeredBy": config.triggered_by,
        "idType": _ID_TYPE,
    }
    logger.debug("Resources request body built")
    return body


def build_state_body(
    config: Config,
    *,
    tracking_id: str,
    state: str,
    status: str = "",
) -> dict[str, Any]:
    """Build the JSON body for a state POST request.

    Parameters
    ----------
    config:
        Loaded configuration.
    tracking_id:
        Tracking identifier from the check response.
    state:
        Current upgrade state string.
    status:
        Status code string.

    Returns
    -------
    dict
        JSON-serialisable request body.
    """
    primary_key = _compute_primary_key(
        config.ota_source_sha1, config.serial_number
    )

    body: dict[str, Any] = {
        "id": primary_key,
        "contentTimestamp": 0,
        "deviceInfo": _build_device_info(config),
        "identityInfo": {"serialNumber": config.serial_number},
        "triggeredBy": config.triggered_by,
        "idType": _ID_TYPE,
        "trackingId": tracking_id,
        "state": state,
        "status": status,
    }
    logger.debug("State request body built for state=%s", state)
    return body


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _resolve_server(config: Config) -> str:
    """Choose the correct server hostname based on device flags.

    Replicates ``getMasterCloud()`` from the smali source.
    """
    if config.is_prc_device:
        if config.is_production_device:
            return config.china_server_url
        return "ota-cn-sdc.blurdev.com"
    if config.is_production_device:
        return config.server_url
    return "moto-cds-staging.appspot.com"


def _compute_primary_key(context_key: str, serial_number: str) -> str:
    """Compute the primary key (SHA-1 of contextKey + serialNumber).

    Replicates ``CheckRequestObj.getPrimaryKey()`` from the smali source.

    Parameters
    ----------
    context_key:
        The OTA source SHA1 (contextKey).
    serial_number:
        Device serial number.

    Returns
    -------
    str
        Hex-encoded SHA-1 hash, or empty string if inputs are missing.
    """
    if not context_key or not serial_number:
        return ""
    raw = context_key + serial_number
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()  # noqa: S324


def _build_device_info(
    config: Config,
    *,
    user_language: str = "es_MX",
) -> dict[str, Any]:
    """Build the ``deviceInfo`` JSON object.

    Replicates ``getDeviceInfoAsJsonObject()`` from the smali source.
    """
    return {
        "manufacturer": config.manufacturer,
        "model": config.model_id,
        "product": config.product,
        "isPRC": config.is_prc_device,
        "carrier": config.carrier,
        "userLanguage": user_language,
    }


def _build_extra_info(
    config: Config,
    *,
    network: str = "",
    apk_version: int = 0,
    provision_time: str = "",
    apk_package_name: str = "com.motorola.ccc.ota",
) -> dict[str, Any]:
    """Build the ``extraInfo`` JSON object.

    Replicates ``getExtraInfoAsJsonObject()`` from the smali source.
    """
    build_display_id = f"{config.source_version}_{config.product}"
    return {
        "clientIdentity": _CLIENT_IDENTITY,
        "brand": config.color_id,
        "buildDevice": config.internal_name,
        "otaSourceSha1": config.ota_source_sha1,
        "buildId": config.source_version,
        "buildDisplayId": build_display_id,
        "network": network,
        "provisionedTime": provision_time or "0",
        "colorId": config.color_id,
        "apkPackageName": apk_package_name,
        "apkVersion": apk_version,
        "OtaLibVersion": _OTA_LIB_VERSION,
        "mobileModel": config.model_id,
    }
