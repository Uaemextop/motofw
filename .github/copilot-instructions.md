# Copilot Instructions — Motofw

## Project Overview

**Motofw** is a Python tool that queries and downloads OTA (Over-The-Air)
firmware updates directly from Motorola's update servers. It targets
researchers, developers, and enthusiasts who want to retrieve firmware packages
and inspect Motorola's update mechanisms.

---

## Language & Runtime

- Primary language: Python 3.11+.
- Use `pip` for dependency management. `requirements.txt` is the source of
  truth for runtime dependencies; `requirements-dev.txt` for development
  dependencies.
- All code must be compatible with Python 3.11+.

---

## Code Style & Conventions

- Follow [PEP 8](https://peps.python.org/pep-0008/) for formatting and naming.
- Use type hints on all function signatures.
- Prefer `pathlib.Path` over `os.path` for all file operations.
- Use f-strings for string formatting. Avoid `%`-style or `.format()`.
- All public functions and classes must have docstrings.
- Keep functions small and focused on a single responsibility.

---

## Architecture Guidelines

- All outbound HTTP traffic must go through a single shared client so that
  proxy, timeout, retry, and header injection settings are centralised.
- Avoid hardcoding server URLs, endpoint paths, or API parameters. All such
  values belong in `config.ini`.
- Use the standard `logging` module for all diagnostic output. `print()` is
  not permitted for diagnostics.
- Separate concerns into modules whose boundaries reflect the actual structure
  of the problem, derived from analysis — not from a predetermined template.

---

## Security

- Never log or store credentials, tokens, or device-specific identifiers in
  plain text.
- Validate and sanitise all filenames derived from server responses before
  writing to disk.
- Verify file checksums with `hashlib` after every download.
- `config.ini` must be listed in `.gitignore` and never committed.

---

## Testing

- Unit tests live in `tests/` and use `pytest`.
- Mock all outbound HTTP calls in unit tests using `pytest-httpserver` or
  `responses`.
- Integration tests that make live server calls must be tagged separately and
  must skip automatically when the server is unreachable.
- Aim for ≥ 80 % coverage on core modules.
- Test values must come from real log evidence, not from invented placeholders.

---

## Tools Available in the Development Environment

The Copilot setup steps provision the following tools:

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

Select the agent from the Copilot agent dropdown before starting a task:

| Agent | Purpose |
|---|---|
| `motofw-architect` | Builds the Motofw Python tool. Extracts the OTA server communication protocol from release log evidence and implements a tool that replicates it faithfully. |
