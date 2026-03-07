<div align="center">

# 🛠️ Motofw

**A Python tool for querying and downloading OTA firmware updates from Motorola's update servers.**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/Uaemextop/motofw)](LICENSE)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/Uaemextop/motofw/actions)

</div>

---

## 📖 Overview

**Motofw** interfaces directly with Motorola's OTA infrastructure to let you:

- 🔍 **Query** available firmware updates for any Motorola / Lenovo device
- 📡 **Scan** the entire update chain from oldest to newest build
- ⬇️ **Download** full OTA packages with MD5 verification
- ⚙️ **Auto-configure** device settings via ADB (USB or wireless)
- 🎛️ **Customise** API request parameters (trigger type, network, bootloader status, etc.)

This tool is intended for **security researchers**, **firmware developers**, and **Android enthusiasts** who need programmatic access to Motorola firmware artifacts.

---

## ✨ Features

| Feature | Description |
|---|---|
| OTA Query | Fetches update metadata (version, URL, checksum) from Motorola servers |
| Build Scan | Queries all known builds from oldest to newest, shows interactive selection menu |
| Firmware Download | Streams large OTA packages with progress reporting and MD5 integrity verification |
| ADB Auto-Settings | Extracts serial number, IMEI, and all device properties via ADB to generate `device.ini` |
| Configurable Parameters | Override `triggeredBy`, `network`, `bootloaderStatus`, `buildType`, `userLocation` per smali analysis |
| Cross-platform | Works on **Windows** and **Linux** |
| Automation-ready | `--no-interactive` mode for scripting and CI/CD pipelines |

---

## 🚀 Installation

### Prerequisites

- **Python 3.11** or later
- **pip** (included with Python)
- **ADB** (optional, for auto-settings) — [Android SDK Platform-Tools](https://developer.android.com/tools/releases/platform-tools)

### Linux

```bash
# Clone the repository
git clone https://github.com/Uaemextop/motofw.git
cd motofw

# Install as a package (recommended)
pip install -e .

# Or with development dependencies (pytest, coverage)
pip install -e '.[dev]'

# Verify installation
motofw --help
```

### Windows

```powershell
# Clone the repository
git clone https://github.com/Uaemextop/motofw.git
cd motofw

# Install as a package
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"

# Verify installation
motofw --help
```

> **Note for Windows users:**
> - Use `pip install -e ".[dev]"` (double quotes) instead of single quotes.
> - If `motofw` is not found after install, make sure Python's `Scripts` folder is
>   in your `PATH`. You can find it with: `python -c "import sysconfig; print(sysconfig.get_path('scripts'))"`.
> - For ADB features, download [Platform-Tools for Windows](https://developer.android.com/tools/releases/platform-tools)
>   and add the extracted folder to your `PATH`.

---

## 📋 Usage

### 1. Auto-configure device settings via ADB

Connect your Motorola device via USB (with USB debugging enabled) or ADB wireless,
and let motofw extract all required device properties automatically:

```bash
motofw settings auto-settings-adb
```

This generates a `device.ini` file with serial number, IMEI, build fingerprint,
OTA SHA1, and all other fields needed for server queries.

The extraction replicates exactly what the Motorola OTA APK does:
- **Serial**: `Build.getSerial()` → `ro.serialno`
- **IMEI**: `TelephonyManager.getImei()` → `service call iphonesubinfo` (Parcel parse)
- **Bootloader**: `ro.boot.verifiedbootstate` (green = locked, orange = unlocked)
- **Build props**: `ro.build.fingerprint`, `ro.mot.build.guid`, `ro.build.display.id`, etc.

### 2. Query for updates

```bash
# Basic query (uses device.ini)
motofw query

# Show the full raw server response
motofw query --raw

# Print the request body and equivalent curl command
motofw query --dump-request

# Query a specific build by SHA1
motofw query --ota-source-sha1 23d670d5d06f351
```

### 3. Scan all builds

```bash
# Interactive mode — scan and choose which update to download
motofw scan

# List-only mode (no download prompt)
motofw scan --no-interactive

# Configure API parameters interactively before scanning
motofw scan --configure

# Override specific parameters
motofw scan --triggered-by polling --network cellular --bootloader-status unlocked
```

### 4. Download firmware

```bash
# Download the available update
motofw download

# Save to a specific directory
motofw download -o ./firmware/

# Skip MD5 verification
motofw download --no-verify
```

### 5. Verbosity

```bash
motofw -v query     # INFO-level logging
motofw -vv query    # DEBUG-level logging (full HTTP details)
```

---

## ⚙️ Configuration

### `device.ini`

Device-specific settings (IMEI, serial, build fingerprint). Generate it automatically
with `motofw settings auto-settings-adb`, or copy from the example:

```bash
cp device.ini.example device.ini
# Edit with your device values
```

> **Security:** `device.ini` is git-ignored and must never be committed.

### `config.ini`

Server and download settings. Copy from the example:

```bash
cp config.ini.example config.ini
```

### Configurable API Parameters

Override request parameters via CLI flags (values from Motorola OTA APK smali analysis):

| Flag | Values | Source |
|---|---|---|
| `--triggered-by` | `user`, `polling`, `pairing`, `setup` | PublicUtilityMethods$TRIGGER_BY.smali |
| `--network` | `wifi`, `cellular`, `cell3g`, `cell4g`, `cell5g`, `roaming`, `unknown` | NetworkUtils$networkType.smali |
| `--bootloader-status` | `locked`, `unlocked` | BuildPropReader.smali |
| `--build-type` | `user`, `userdebug`, `eng` | BuildPropReader.smali |
| `--user-location` | `Non-CN`, `CN` | LocationUtils.smali |

---

## 📁 Repository Layout

```
motofw/
├── motofw/
│   ├── src/
│   │   ├── api/          # OTA server communication (check, resources, scan)
│   │   ├── cli/          # CLI commands, parser, output formatting
│   │   ├── config/       # Settings loader, defaults, configurable options
│   │   ├── crypto/       # SHA-1 hashing for context keys
│   │   ├── device/       # Device properties, ADB integration, builders
│   │   ├── download/     # Streaming download, checksum, filename sanitisation
│   │   └── utils/        # Data models (CheckResponse, ContentInfo, etc.)
│   ├── __init__.py
│   └── __main__.py
├── tests/                # pytest test suite (132 tests)
├── docs/                 # Generated documentation and analysis
├── source_code/          # ← gitignored; Motorola OTA APK smali for analysis
├── config.ini.example
├── device.ini.example
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## 🧪 Running Tests

```bash
# Install dev dependencies
pip install -e '.[dev]'    # Linux/macOS
pip install -e ".[dev]"    # Windows

# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=motofw --cov-report=term-missing
```

---

## 🤝 Contributing

1. Fork the repository and create a feature branch.
2. Ensure all tests pass: `python -m pytest tests/ -v`
3. Open a Pull Request with a clear description of your changes.

Please read the [Copilot instructions](.github/copilot-instructions.md) for code style and architecture guidelines.

---

## ⚠️ Disclaimer

This tool is provided **for educational and research purposes only**. Always comply with Motorola's Terms of Service and applicable laws when using it. The authors are not responsible for any misuse.

---

## 📄 License

Distributed under the terms of the repository's license. See [`LICENSE`](LICENSE) for details.
