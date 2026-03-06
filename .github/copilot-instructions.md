# Copilot Instructions — Motofw

## Project Overview

**Motofw** is a Python tool designed to query and download OTA (Over-The-Air) firmware updates directly from Motorola's update servers. It allows researchers, developers, and enthusiasts to retrieve firmware packages, analyze their contents, and inspect Motorola-specific update mechanisms.

---

## Language & Runtime

- **Primary language:** Python 3.x
- Use `pip` for dependency management (`requirements.txt` is the source of truth).
- All scripts must be compatible with Python 3.9+.

---

## Code Style & Conventions

- Follow [PEP 8](https://peps.python.org/pep-0008/) for formatting and naming.
- Use type hints on all function signatures.
- Prefer `pathlib.Path` over `os.path` for file operations.
- Use f-strings for string formatting (avoid `%` or `.format()`).
- All public functions and classes must have docstrings.
- Keep functions small and focused (single responsibility).

---

## Architecture Guidelines

- Network requests must go through a shared HTTP client module so that proxy and timeout settings are centralised.
- Firmware metadata parsing should be kept separate from download logic.
- Avoid hardcoding URLs or API endpoints — store them in a configuration file or constants module.
- Logging must use the standard `logging` module; do **not** use plain `print()` for diagnostics.

---

## Security

- Never log or store credentials, tokens, or device-specific identifiers in plain text.
- Validate and sanitise all filenames derived from server responses before writing to disk.
- Use `hashlib` to verify firmware checksums after download.

---

## Testing

- Unit tests live in `tests/` and use `pytest`.
- Mock all outbound HTTP calls in tests using `pytest-httpserver` or `responses`.
- Aim for ≥ 80 % coverage on core modules.

---

## Tools Available in the Development Environment

The Copilot setup steps provision the following tools; use them as needed:

| Category | Tool |
|---|---|
| Package manager | `pip`, `apt` |
| Network | `curl`, `wget` |
| JavaScript runtime | Node.js (LTS) |
| JDK | Eclipse Temurin 21 |
| APK / DEX disassembly | `apktool`, `baksmali` |
| Smali analysis | `smali`, `smali-cfr` |
| Deobfuscation | `simplify` |
| Java decompiler | `jadx` |
| Binary analysis | `binutils` (aarch64-linux-gnu), `file`, `readelf`, `objdump` |
| Disassembly framework | `capstone` (Python bindings) |
| Source code | `source_code/` directory (cloned from Motorola CCC OTA repo) |

---

## Custom Agents

This repository ships a specialised Copilot agent for the main development
workflow. Select it from the Copilot agent dropdown before starting a task:

| Agent file | Purpose |
|---|---|
| `.github/agents/motofw-architect.agent.md` | End-to-end project designer: analyzes the Motorola OTA APK (smali + .so), deobfuscates, reverse-engineers the OTA HTTP API, downloads release ZIP logs, and scaffolds the complete Python application with `config.ini` support. |

---

## Directory Structure

```
motofw/
├── .github/
│   ├── copilot-instructions.md       ← this file
│   ├── agents/
│   │   └── motofw-architect.agent.md ← Copilot custom agent
│   └── workflows/
│       └── copilot-setup-steps.yml
│
├── motofw/                       ← main Python package (scaffolded by agent)
│   ├── __init__.py
│   ├── __main__.py               ← CLI entry point
│   ├── config.py                 ← configparser wrapper
│   ├── cli.py                    ← argparse commands
│   ├── http/                     ← shared HTTP client + models
│   ├── ota/                      ← OTA query, parser, downloader
│   ├── apk/                      ← smali analysis, .so analysis, deobfuscation
│   ├── logs/                     ← GitHub release asset fetcher + log parser
│   └── report/                   ← Markdown + JSON report generator
│
├── docs/
│   └── api-reverse-engineering.md ← reverse-engineered OTA API documentation
│
├── tests/                        ← pytest test suite
├── config.ini                    ← gitignored; fill in your real values
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

> **Note:** `source_code/`, `config.ini`, and `output/` are excluded from
> version control via `.gitignore`.
