"""Evidence-based default values extracted from smali analysis and device logs.

Every constant originates from decompiled Motorola OTA APK bytecode
or captured request/response logs.  Nothing is invented.
"""

SERVER_DEFAULTS: dict[str, str] = {
    "url": "moto-cds.appspot.com",
    "check_path": "cds/upgrade/1/check",
    "resources_path": "cds/upgrade/1/resources",
    "state_path": "cds/upgrade/1/state",
    "context": "ota",
    "timeout": "60",
    "retry_delays_ms": "5000,15000,30000",
}

DOWNLOAD_DEFAULTS: dict[str, str] = {
    "output_dir": "output",
    "verify_checksum": "true",
}

DEVICE_DEFAULTS: dict[str, str] = {
    "manufacturer": "motorola",
    "hardware": "lamu",
    "brand": "motorola",
    "model": "moto g05",
    "product": "lamul_g",
    "os": "Android",
    "os_version": "15",
    "country": "MX",
    "region": "MX",
    "language": "es",
    "user_language": "es_MX",
    "client_identity": "motorola-ota-client-app",
    "carrier": "",
    "bootloader_version": "",
    "fingerprint": "motorola/lamul_g/lamul:15/VVTAS35.51-100-3/bb8ed4:user/release-keys",
    "radio_version": "",
    "build_tags": "release-keys",
    "build_type": "user",
    "build_device": "lamul",
    "build_id": "VVTAS35.51-100-3",
    "build_display_id": "VVTAS35.51-100-3",
    "build_incremental_version": "",
    "release_version": "15",
    "ota_source_sha1": "96398c9adf48ac1",
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
    "serial_number": "ZY32LNRW97",
    "imei": "359488357396203",
    "imei2": "",
    "mccmnc": "",
    "mccmnc2": "",
    "id_type": "serialNumber",
}
