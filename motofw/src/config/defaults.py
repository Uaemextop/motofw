"""Default values for motofw configuration.

Server and protocol constants come from the Motorola OTA APK smali analysis.
Device-specific values are intentionally empty — they MUST be provided via
``device.ini`` (or auto-generated with ``motofw settings auto-settings-adb``).
"""

SERVER_DEFAULTS: dict[str, str] = {
    "url": "moto-cds.appspot.com",
    "check_path": "cds/upgrade/1/check",
    "resources_path": "cds/upgrade/1/resources",
    "state_path": "cds/upgrade/1/state",
    "context": "ota",
    "timeout": "60",
    # WebServiceThread.smali backOffValues: "2000,5000,15000,30000,60000,..."
    # Using the first 4 for CLI (full 9-value chain is too aggressive).
    "retry_delays_ms": "2000,5000,15000,30000",
}

DOWNLOAD_DEFAULTS: dict[str, str] = {
    "output_dir": "output",
    "verify_checksum": "true",
}

# Device-specific values are empty by default.  Users MUST configure them
# via device.ini or by running ``motofw settings auto-settings-adb``.
DEVICE_DEFAULTS: dict[str, str] = {
    "manufacturer": "",
    "hardware": "",
    "brand": "",
    "model": "",
    "product": "",
    "os": "Android",
    "os_version": "",
    "country": "",
    "region": "",
    "language": "",
    "user_language": "",
    "client_identity": "motorola-ota-client-app",
    "carrier": "",
    "bootloader_version": "",
    "fingerprint": "",
    "radio_version": "",
    "build_tags": "",
    "build_type": "user",
    "build_device": "",
    "build_id": "",
    "build_display_id": "",
    "build_incremental_version": "",
    "release_version": "",
    "ota_source_sha1": "",
    "network": "wifi",
    "apk_version": "3500094",
    "provisioned_time": "0",
    "incremental_version": "0",
    "additional_info": "",
    "user_location": "Non-CN",
    "bootloader_status": "locked",
    "device_rooted": "false",
    "is_4gb_ram": "false",
    "device_chipset": "",
}

IDENTITY_DEFAULTS: dict[str, str] = {
    "serial_number": "",
    "imei": "",
    "imei2": "",
    "mccmnc": "",
    "mccmnc2": "",
    "id_type": "serialNumber",
}
