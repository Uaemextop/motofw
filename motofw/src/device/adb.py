"""ADB interface for extracting device properties.

Replicates the property-reading logic from the Motorola OTA APK smali code:

- Serial number: ``Build.getSerial()`` → ``ro.serialno`` via ADB
- IMEI: ``TelephonyManager.getImei()`` → ``service call iphonesubinfo`` via ADB
- IMEI2: same as IMEI but for second SIM slot
- MCC-MNC: ``TelephonyManager.getSimOperator()`` → ``gsm.sim.operator.numeric``
- Build props: ``getprop ro.build.*``, ``ro.mot.*``, ``ro.product.*``, etc.

Supports both USB and wireless (TCP/IP) ADB connections and works on
Windows and Linux.

References
----------
- BuildPropReader.smali:1190-1238 (getIdentityInfoAsJsonObject)
- BuildPropReader.smali:1240-1364 (getImeiValues)
- BuildPropertyUtils.smali:216-246 (getId / Build.getSerial)
"""

from __future__ import annotations

import logging
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# IMEI validation regex from BuildPropReader.smali:1327
_IMEI_RE = re.compile(r"^[0-9a-fA-F]{14,50}$")

# Mapping: device.ini key → Android property name(s)
# Derived from BuildPropReader.smali getExtraInfoAsJsonObject() lines 671-1163
_PROP_MAP: dict[str, list[str]] = {
    # deviceInfo
    "manufacturer": ["ro.product.manufacturer"],
    "hardware": ["ro.hardware"],
    "brand": ["ro.product.brand"],
    "model": ["ro.product.model", "ro.vendor.product.display"],
    "product": ["ro.product.name"],
    "os_version": ["ro.build.version.release"],
    "country": ["ro.product.locale.region", "persist.sys.country"],
    "language": ["ro.product.locale"],
    # extraInfo
    "fingerprint": ["ro.build.fingerprint"],
    "build_tags": ["ro.build.tags"],
    "build_type": ["ro.build.type"],
    "build_device": ["ro.mot.build.device", "ro.product.device"],
    "build_id": ["ro.build.display.id", "ro.build.id"],
    "build_display_id": ["ro.build.display.id"],
    "release_version": ["ro.build.version.release"],
    "ota_source_sha1": ["ro.mot.build.guid"],
    "device_chipset": ["ro.boot.hardware.chipset", "ro.hardware.chipname"],
    "bootloader_version": ["ro.bootloader"],
    "radio_version": ["gsm.version.baseband"],
    "build_incremental_version": ["ro.build.version.incremental"],
    # identity
    "serial_number": ["ro.serialno", "ro.boot.serialno"],
    # SIM operator codes
    "mccmnc": ["gsm.sim.operator.numeric"],
}


class ADBError(Exception):
    """Raised when an ADB command fails."""


def find_adb() -> str:
    """Locate the ``adb`` binary on the system PATH.

    Returns the full path to the adb executable.

    Raises
    ------
    ADBError
        If adb is not found on the system PATH.
    """
    adb = shutil.which("adb")
    if adb is None:
        raise ADBError(
            "adb not found on PATH. Install Android SDK Platform-Tools:\n"
            "  https://developer.android.com/tools/releases/platform-tools"
        )
    logger.debug("Found adb: %s", adb)
    return adb


def run_adb(
    args: list[str],
    *,
    adb_path: Optional[str] = None,
    timeout: int = 30,
) -> str:
    """Run an ADB command and return its stdout.

    Parameters
    ----------
    args:
        Arguments to pass to adb (e.g. ``["shell", "getprop"]``).
    adb_path:
        Explicit path to the adb binary; auto-detected if *None*.
    timeout:
        Maximum seconds to wait for the command.

    Raises
    ------
    ADBError
        On non-zero exit code or timeout.
    """
    adb = adb_path or find_adb()
    cmd = [adb, *args]
    logger.debug("Running: %s", " ".join(cmd))

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise ADBError(f"ADB command timed out after {timeout}s: {' '.join(cmd)}") from exc
    except FileNotFoundError as exc:
        raise ADBError(f"adb binary not found: {adb}") from exc

    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise ADBError(f"ADB error (exit {result.returncode}): {stderr or result.stdout.strip()}")

    return result.stdout


def wait_for_device(*, adb_path: Optional[str] = None, timeout: int = 60) -> None:
    """Block until a USB-attached device is detected.

    Raises
    ------
    ADBError
        If no device is found within *timeout* seconds.
    """
    sys.stdout.write("Waiting for USB device … (connect device with USB debugging enabled)\n")
    sys.stdout.flush()
    try:
        run_adb(["wait-for-usb-device"], adb_path=adb_path, timeout=timeout)
    except ADBError:
        raise ADBError(
            f"No USB device detected within {timeout}s.\n"
            "Make sure USB debugging is enabled in Developer Options."
        )


def connect_wireless(
    ip: str,
    port: int = 5555,
    *,
    adb_path: Optional[str] = None,
) -> None:
    """Connect to a device over TCP/IP (ADB wireless).

    Parameters
    ----------
    ip:
        Device IP address.
    port:
        ADB port (default 5555).

    Raises
    ------
    ADBError
        If the connection fails.
    """
    target = f"{ip}:{port}"
    sys.stdout.write(f"Connecting to {target} …\n")
    sys.stdout.flush()
    out = run_adb(["connect", target], adb_path=adb_path)
    if "connected" not in out.lower():
        raise ADBError(f"Failed to connect to {target}: {out.strip()}")
    sys.stdout.write(f"Connected to {target}\n")


def pair_wireless(
    ip: str,
    port: int,
    code: str,
    *,
    adb_path: Optional[str] = None,
) -> None:
    """Pair with a device for ADB wireless debugging (Android 11+).

    Parameters
    ----------
    ip:
        Device IP address.
    port:
        Pairing port shown on the device.
    code:
        Six-digit pairing code shown on the device.

    Raises
    ------
    ADBError
        If pairing fails.
    """
    target = f"{ip}:{port}"
    sys.stdout.write(f"Pairing with {target} …\n")
    sys.stdout.flush()
    out = run_adb(["pair", target, code], adb_path=adb_path, timeout=30)
    if "successfully" not in out.lower():
        raise ADBError(f"Pairing failed for {target}: {out.strip()}")
    sys.stdout.write(f"Paired successfully with {target}\n")


def get_all_properties(*, adb_path: Optional[str] = None) -> dict[str, str]:
    """Run ``adb shell getprop`` and return all properties as a dict.

    This mirrors how BuildPropReader.smali reads system properties.
    """
    raw = run_adb(["shell", "getprop"], adb_path=adb_path)
    props: dict[str, str] = {}
    for line in raw.splitlines():
        line = line.strip()
        # Format: [key]: [value]
        m = re.match(r"\[(.+?)]\s*:\s*\[(.*)]\s*$", line)
        if m:
            props[m.group(1)] = m.group(2)
    logger.info("Read %d properties from device", len(props))
    return props


def _resolve_prop(props: dict[str, str], candidates: list[str]) -> str:
    """Return the first non-empty property value from *candidates*."""
    for key in candidates:
        val = props.get(key, "").strip()
        if val:
            return val
    return ""


def _parse_parcel_string(raw: str) -> str:
    """Parse a Parcel hex dump from ``service call`` into a string.

    The Parcel format from ``adb shell service call iphonesubinfo`` looks like::

        Result: Parcel(
          0x00000000: 00000000 0000000f 00330035 00340039 '........5.3.9.4.'
          0x00000010: 00380038 00350033 00390037 00360033 '8.8.3.5.7.9.6.3.'
          0x00000020: 00300032 00330030 00000000          '2.0.3.0....')

    The readable characters between single quotes on each line form the string
    (with dots replacing non-printable characters).
    """
    # Strategy: extract characters between single quotes on each data line
    chars: list[str] = []
    for line in raw.splitlines():
        m = re.search(r"'(.+?)'", line)
        if m:
            segment = m.group(1)
            # Each char is UTF-16LE: ASCII chars separated by dots
            for ch in segment:
                if ch != "." and ch.isprintable():
                    chars.append(ch)
    result = "".join(chars)
    # Remove null padding
    result = result.replace("\x00", "").strip()
    return result


def get_serial(*, adb_path: Optional[str] = None) -> str:
    """Get the device serial number.

    Mirrors ``BuildPropertyUtils.getId()`` (BuildPropertyUtils.smali:216-246)
    which calls ``Build.getSerial()``.  Via ADB the equivalent is
    ``adb get-serialno`` or reading ``ro.serialno``.
    """
    try:
        sn = run_adb(["get-serialno"], adb_path=adb_path).strip()
        if sn and sn.lower() != "unknown":
            return sn
    except ADBError:
        pass

    # Fallback: read property directly
    try:
        sn = run_adb(["shell", "getprop", "ro.serialno"], adb_path=adb_path).strip()
        if sn:
            return sn
    except ADBError:
        pass

    return ""


def get_imei(slot: int = 0, *, adb_path: Optional[str] = None) -> str:
    """Get the IMEI for the given SIM *slot* (0 or 1).

    Mirrors ``BuildPropReader.getImeiValues()`` (BuildPropReader.smali:1240-1364)
    which calls ``TelephonyManager.getImei()`` per subscription.

    Via ADB, we call ``service call iphonesubinfo`` and parse the Parcel response.
    Multiple calling conventions are attempted for compatibility across Android versions.
    """
    # Try modern Android (12+) with package name
    commands = [
        ["shell", "service", "call", "iphonesubinfo", "1", "i32", str(slot + 2),
         "s16", "com.android.shell"],
        ["shell", "service", "call", "iphonesubinfo", "1", "i32", str(slot + 2)],
        ["shell", "service", "call", "iphonesubinfo", "1"],
    ]

    for cmd in commands:
        try:
            raw = run_adb(cmd, adb_path=adb_path)
            imei = _parse_parcel_string(raw)
            if imei and _IMEI_RE.match(imei):
                logger.info("IMEI slot %d: %s (via %s)", slot, imei, " ".join(cmd[1:]))
                return imei
        except ADBError:
            continue

    # Fallback: try getprop (some custom ROMs)
    try:
        raw = run_adb(["shell", "getprop", "persist.radio.imei"], adb_path=adb_path).strip()
        if raw and _IMEI_RE.match(raw):
            return raw
    except ADBError:
        pass

    return ""


def _detect_bootloader_status(props: dict[str, str]) -> str:
    """Detect bootloader status from system properties.

    Mirrors BuildPropReader.smali which reads ``ro.boot.verifiedbootstate``
    and ``ro.boot.secure_hardware`` to determine lock state.
    """
    vb_state = props.get("ro.boot.verifiedbootstate", "")
    secure_hw = props.get("ro.boot.secure_hardware", "")

    # verifiedbootstate: "green" = locked, "orange" = unlocked
    if vb_state == "orange":
        return "unlocked"
    if vb_state == "green":
        return "locked"

    # Fallback: check sys.oem_unlock_allowed
    oem_unlock = props.get("sys.oem_unlock_allowed", "")
    if oem_unlock == "1":
        return "unlocked"

    return "locked"


def _detect_user_location(props: dict[str, str]) -> str:
    """Detect CN vs Non-CN from system properties.

    Mirrors BuildPropReader.smali / LocationUtils.smali which checks
    ``ro.lenovo.region`` and ``ro.mot.build.customerid`` for China detection.
    """
    region = props.get("ro.lenovo.region", "")
    customer_id = props.get("ro.mot.build.customerid", "")
    if "cn" in region.lower() or "cn" in customer_id.lower():
        return "CN"
    return "Non-CN"


def _detect_is_4gb_ram(props: dict[str, str]) -> bool:
    """Detect if device has ≤4 GB RAM.

    Mirrors BuildPropReader.smali which reads ``ro.vendor.hw.ram``.
    """
    raw = props.get("ro.vendor.hw.ram", "")
    if raw:
        try:
            ram_mb = int(raw)
            return ram_mb <= 4096
        except ValueError:
            pass
    return False


def _detect_device_rooted(props: dict[str, str]) -> str:
    """Detect if device is rooted.

    Mirrors BuildPropReader.smali which reads ``persist.qe``.
    """
    qe = props.get("persist.qe", "")
    if qe == "1":
        return "true"
    return "false"


def _derive_country_language(props: dict[str, str]) -> tuple[str, str, str]:
    """Extract country, language, and user_language from locale properties.

    Returns (country, language, user_language).
    """
    locale = props.get("ro.product.locale", props.get("persist.sys.locale", ""))
    region = props.get("ro.product.locale.region", "")
    language = ""
    country = region

    if locale:
        # Locale format: "es_MX" or "es-MX" or just "es"
        parts = re.split(r"[_\-]", locale, maxsplit=1)
        language = parts[0] if parts else ""
        if len(parts) > 1 and not country:
            country = parts[1]

    user_language = f"{language}_{country}" if language and country else locale
    return country or "US", language or "en", user_language or "en_US"


def extract_device_info(*, adb_path: Optional[str] = None) -> dict[str, str]:
    """Extract all device properties needed for ``device.ini``.

    Reads system properties and calls service commands to replicate the
    exact data extraction performed by the Motorola OTA APK (see smali
    references in module docstring).

    Returns a flat dict matching the ``device.ini`` key names.
    """
    props = get_all_properties(adb_path=adb_path)

    info: dict[str, str] = {}

    # Map properties from _PROP_MAP
    for ini_key, candidates in _PROP_MAP.items():
        info[ini_key] = _resolve_prop(props, candidates)

    # Fixed values
    info["os"] = "Android"
    info["client_identity"] = "motorola-ota-client-app"
    info["carrier"] = props.get("ro.carrier", "")
    info["network"] = "wifi"
    info["apk_version"] = "3500094"
    info["provisioned_time"] = "0"
    info["incremental_version"] = "0"
    info["additional_info"] = ""
    info["id_type"] = "serialNumber"

    # Derived values (matching smali logic)
    country, language, user_language = _derive_country_language(props)
    info["country"] = country
    info["region"] = country
    info["language"] = language
    info["user_language"] = user_language
    info["bootloader_status"] = _detect_bootloader_status(props)
    info["user_location"] = _detect_user_location(props)
    info["is_4gb_ram"] = str(_detect_is_4gb_ram(props)).lower()
    info["device_rooted"] = _detect_device_rooted(props)

    # Serial number — Build.getSerial() (BuildPropertyUtils.smali:232)
    sn = info.get("serial_number", "")
    if not sn:
        sn = get_serial(adb_path=adb_path)
        info["serial_number"] = sn

    # IMEI — TelephonyManager.getImei() (BuildPropReader.smali:1321)
    imei = get_imei(slot=0, adb_path=adb_path)
    info["imei"] = imei

    # IMEI2 — second SIM slot (BuildPropReader.smali:989)
    imei2 = get_imei(slot=1, adb_path=adb_path)
    info["imei2"] = imei2

    # MCC-MNC for second SIM
    info["mccmnc2"] = props.get("gsm.sim.operator.numeric.2", "")

    return info


def write_device_ini(info: dict[str, str], dest: Path) -> Path:
    """Write a ``device.ini`` file from extracted device properties.

    Parameters
    ----------
    info:
        Flat dict of device properties (from :func:`extract_device_info`).
    dest:
        Path to the output ``device.ini`` file.

    Returns
    -------
    Path
        The absolute path of the written file.
    """
    lines = [
        "# =============================================================================",
        "# motofw device configuration — auto-generated from ADB",
        "# =============================================================================",
        f"# Device: {info.get('brand', '')} {info.get('model', '')}",
        f"# Serial: {info.get('serial_number', '')}",
        f"# Generated by: motofw settings auto-settings-adb",
        "#",
        "# SECURITY: device.ini is git-ignored and must NEVER be committed.",
        "",
        "[device]",
        f"manufacturer = {info.get('manufacturer', 'motorola')}",
        f"hardware = {info.get('hardware', '')}",
        f"brand = {info.get('brand', 'motorola')}",
        f"model = {info.get('model', '')}",
        f"product = {info.get('product', '')}",
        f"os = {info.get('os', 'Android')}",
        f"os_version = {info.get('os_version', '')}",
        f"country = {info.get('country', '')}",
        f"region = {info.get('region', '')}",
        f"language = {info.get('language', '')}",
        f"user_language = {info.get('user_language', '')}",
        f"client_identity = {info.get('client_identity', 'motorola-ota-client-app')}",
        f"carrier = {info.get('carrier', '')}",
        f"bootloader_version = {info.get('bootloader_version', '')}",
        f"fingerprint = {info.get('fingerprint', '')}",
        f"radio_version = {info.get('radio_version', '')}",
        f"build_tags = {info.get('build_tags', '')}",
        f"build_type = {info.get('build_type', 'user')}",
        f"build_device = {info.get('build_device', '')}",
        f"build_id = {info.get('build_id', '')}",
        f"build_display_id = {info.get('build_display_id', '')}",
        f"build_incremental_version = {info.get('build_incremental_version', '')}",
        f"release_version = {info.get('release_version', '')}",
        f"ota_source_sha1 = {info.get('ota_source_sha1', '')}",
        f"network = {info.get('network', 'wifi')}",
        f"apk_version = {info.get('apk_version', '3500094')}",
        f"provisioned_time = {info.get('provisioned_time', '0')}",
        f"incremental_version = {info.get('incremental_version', '0')}",
        f"additional_info = {info.get('additional_info', '')}",
        f"user_location = {info.get('user_location', 'Non-CN')}",
        f"bootloader_status = {info.get('bootloader_status', 'locked')}",
        f"device_rooted = {info.get('device_rooted', 'false')}",
        f"is_4gb_ram = {info.get('is_4gb_ram', 'false')}",
        f"device_chipset = {info.get('device_chipset', '')}",
        "",
        "[identity]",
        f"serial_number = {info.get('serial_number', '')}",
        f"imei = {info.get('imei', '')}",
        f"imei2 = {info.get('imei2', '')}",
        f"mccmnc = {info.get('mccmnc', '')}",
        f"mccmnc2 = {info.get('mccmnc2', '')}",
        f"id_type = {info.get('id_type', 'serialNumber')}",
        "",
    ]

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote device.ini to %s", dest)
    return dest.resolve()
