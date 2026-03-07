"""Valid parameter options extracted from Motorola OTA APK smali analysis.

Every value originates from decompiled bytecode of the Motorola OTA client APK.
These constants define which values the server accepts for each configurable field.
"""

from __future__ import annotations

# ── Server environments (UpgradeUtils.smali, CDSUtils.smali) ──────
# Production, QA, Dev, Staging, and China-specific servers discovered
# in smali analysis of the Motorola OTA APK.
SERVER_OPTIONS: dict[str, str] = {
    "production": "moto-cds.appspot.com",          # UpgradeUtils.smali:43 PRODUCTION_SERVER
    "china": "moto-cds.svcmot.cn",                 # UpgradeUtils.smali:19 CHINA_PRODUCTION_SERVER
    "qa": "moto-cds-qa.appspot.com",               # UpgradeUtils.smali:45
    "dev": "moto-cds-dev.appspot.com",              # UpgradeUtils.smali:39
    "staging": "moto-cds-staging.appspot.com",      # UpgradeUtils.smali:47
    "china-staging": "ota-cn-sdc.blurdev.com",      # UpgradeUtils.smali:21 CHINA_STAGING_SERVER
}

SERVER_NAMES: list[str] = list(SERVER_OPTIONS.keys())

# ── triggeredBy (PublicUtilityMethods$TRIGGER_BY.smali) ──
TRIGGERED_BY_OPTIONS: list[str] = ["user", "polling", "pairing", "setup"]

# ── network type (NetworkUtils$networkType.smali / extraInfo.network) ──
NETWORK_OPTIONS: list[str] = [
    "wifi",         # WiFi connection
    "cellular",     # Generic cellular
    "cell3g",       # 3G cellular
    "cell4g",       # 4G/LTE cellular
    "cell5g",       # 5G cellular
    "roaming",      # International roaming
    "unknown",      # Unknown type
]

# ── bootloaderStatus (BuildPropReader.smali) ──
BOOTLOADER_STATUS_OPTIONS: list[str] = ["locked", "unlocked"]

# ── buildType (BuildPropReader.smali) ──
BUILD_TYPE_OPTIONS: list[str] = ["user", "userdebug", "eng"]

# ── userLocation (LocationUtils.smali) ──
USER_LOCATION_OPTIONS: list[str] = ["Non-CN", "CN"]

# ── idType (CDSUtils.smali) ──
ID_TYPE_OPTIONS: list[str] = ["serialNumber"]

# ── context (Configs.smali) ──
CONTEXT_OPTIONS: list[str] = ["ota"]

# ── updateType — server response values (UpdateType$DIFFUpdateType.smali) ──
UPDATE_TYPE_OPTIONS: list[str] = ["MR", "SMR", "OS", "DEFAULT"]

# ── abInstallType (UpgradeUtils$AB_INSTALL_TYPE.smali) ──
AB_INSTALL_TYPE_OPTIONS: list[str] = [
    "streamingOnAb",  # Streaming A/B install (default for modern devices)
    "defaultAb",      # Default A/B install
    "classicOnAb",    # Classic install on A/B device
]

# ── Mapping of human labels to option lists (for interactive menus) ──
CONFIGURABLE_PARAMS: dict[str, dict] = {
    "server": {
        "label": "Server environment (UpgradeUtils.smali)",
        "options": SERVER_NAMES,
        "default": "production",
        "description": "Motorola CDS server to query",
    },
    "triggered_by": {
        "label": "Trigger type (triggeredBy)",
        "options": TRIGGERED_BY_OPTIONS,
        "default": "user",
        "description": "What triggered the update check",
    },
    "network": {
        "label": "Network type (extraInfo.network)",
        "options": NETWORK_OPTIONS,
        "default": "wifi",
        "description": "Current network connection type",
    },
    "bootloader_status": {
        "label": "Bootloader status",
        "options": BOOTLOADER_STATUS_OPTIONS,
        "default": "locked",
        "description": "Device bootloader lock state",
    },
    "build_type": {
        "label": "Build type",
        "options": BUILD_TYPE_OPTIONS,
        "default": "user",
        "description": "Android build variant",
    },
    "user_location": {
        "label": "User location",
        "options": USER_LOCATION_OPTIONS,
        "default": "Non-CN",
        "description": "China vs international region",
    },
}
