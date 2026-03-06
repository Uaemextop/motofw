<div align="center">

# 🛠️ Motofw

**A Python tool for querying and downloading OTA firmware updates from Motorola's update servers.**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/Uaemextop/motofw)](LICENSE)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/Uaemextop/motofw/actions)

</div>

---

## 📖 Overview

**Motofw** interfaces directly with Motorola's OTA infrastructure to let you:

- 🔍 **Query** available firmware updates for any Motorola / Lenovo device
- ⬇️ **Download** full OTA packages without needing a physical device
- 🔬 **Analyze** the firmware contents — DEX bytecode, smali files, native ARM64 libraries, and more
- 🧩 **Deobfuscate** and decompile APKs bundled inside OTA packages using industry-standard tools (JADX, Apktool, Simplify)

This tool is intended for **security researchers**, **firmware developers**, and **Android enthusiasts** who need programmatic access to Motorola firmware artifacts.

---

## ✨ Features

| Feature | Description |
|---|---|
| OTA Query | Fetches update metadata (version, URL, checksum) from Motorola servers |
| Firmware Download | Streams large OTA packages with progress reporting and integrity verification |
| Smali Analysis | Integrates with baksmali / smali for DEX ↔ smali conversion |
| Java Decompilation | Runs JADX to produce readable Java/Kotlin source from APKs |
| Deobfuscation | Uses Simplify to resolve obfuscated smali bytecode |
| ARM64 Library Analysis | Leverages Capstone + LIEF + binutils for native `.so` inspection |
| Automation-ready | Fully scriptable; designed for CI/CD pipelines |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or later
- Java 21 (Eclipse Temurin recommended)
- See the [Copilot setup steps](.github/workflows/copilot-setup-steps.yml) for the full list of optional analysis tools

### Installation

```bash
# Clone the repository
git clone https://github.com/Uaemextop/motofw.git
cd motofw

# Install Python dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Query available OTA updates for a device
python -m motofw query --device <DEVICE_SKU>

# Download the latest OTA package
python -m motofw download --device <DEVICE_SKU> --output ./firmware/

# Analyze a downloaded OTA zip
python -m motofw analyze ./firmware/update.zip
```

---

## 🧰 Analysis Toolchain

Motofw ships a Copilot setup workflow that automatically provisions the full analysis environment:

| Tool | Purpose |
|---|---|
| **JADX** | Decompile APK/DEX to Java source |
| **Apktool** | Decode/rebuild APK resources and smali |
| **baksmali / smali** | Disassemble / assemble DEX bytecode |
| **Simplify** | Statically execute smali to deobfuscate |
| **Capstone** | Multi-arch disassembly (ARM, ARM64, x86 …) |
| **LIEF** | Parse and modify ELF, PE, DEX, and Android binaries |
| **pyelftools** | Pure-Python ELF parser |
| **Androguard** | Android APK / DEX analysis framework |
| **aarch64-linux-gnu binutils** | `readelf`, `objdump` for ARM64 native libraries |

---

## 📁 Repository Layout

```
motofw/
├── .github/
│   ├── copilot-instructions.md   # Copilot Coding Agent configuration
│   └── workflows/
│       └── copilot-setup-steps.yml  # Dev environment provisioning
├── motofw/                       # Main package source
│   ├── __init__.py
│   ├── client.py                 # HTTP client (OTA server communication)
│   ├── parser.py                 # Firmware metadata parser
│   └── downloader.py             # Streaming download + checksum verification
├── tests/                        # pytest test suite
├── source_code/                  # ← gitignored; cloned by setup steps
├── requirements.txt
└── README.md
```

---

## 🤝 Contributing

1. Fork the repository and create a feature branch.
2. Ensure all tests pass: `pytest -v`
3. Open a Pull Request with a clear description of your changes.

Please read the [Copilot instructions](.github/copilot-instructions.md) for code style and architecture guidelines.

---

## ⚠️ Disclaimer

This tool is provided **for educational and research purposes only**. Always comply with Motorola's Terms of Service and applicable laws when using it. The authors are not responsible for any misuse.

---

## 📄 License

Distributed under the terms of the repository's license. See [`LICENSE`](LICENSE) for details.
