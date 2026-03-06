# MCP Repository Settings

## What this file is

`mcp-repository-settings.json` contains the JSON that must be pasted into:

> **Repository Settings → Copilot → Coding agent → MCP configuration**

It configures the same four MCP servers that are declared in
`.github/agents/motofw-architect.agent.md`, making them available
to any Copilot coding agent session in this repository (not just when
the named agent is selected).

---

## How to apply it

1. Go to **Settings → Copilot → Coding agent** in this repository.
2. Open `docs/mcp-repository-settings.json`.
3. Copy the entire file contents.
4. Paste into the **MCP configuration** text box and click **Save**.

GitHub will validate the JSON syntax before saving.

---

## Servers

| Name | Runtime | Package / module | Purpose |
|---|---|---|---|
| `fetch` | Python | `mcp-server-fetch` (PyPI) | Fetches URLs and converts HTML to Markdown |
| `filesystem` | Node / npx | `@modelcontextprotocol/server-filesystem` | Read/write access to the workspace |
| `memory` | Node / npx | `@modelcontextprotocol/server-memory` | Persistent knowledge-graph across sessions |
| `sequential-thinking` | Node / npx | `@modelcontextprotocol/server-sequential-thinking` | Structured step-by-step reasoning |

---

## Prerequisites

`mcp-server-fetch` must be installed in the Copilot coding agent environment
before the `fetch` server can start. This is handled by step **12b** in
`.github/workflows/copilot-setup-steps.yml`:

```yaml
- name: Install mcp-server-fetch
  run: pip install mcp-server-fetch
```

`npx` is provided by the Node.js step (`actions/setup-node@v4`) and does not
require a separate install step.

---

## Note on the filesystem path

The `filesystem` server is configured with the absolute path
`/home/runner/work/motofw/motofw`.  This is the value of `$GITHUB_WORKSPACE`
on every GitHub Actions runner for this repository, and is the directory
Copilot coding agent always checks out the code into.

**If you run this configuration locally** (e.g. in VS Code with the MCP
extension), replace that path with your local repository root, for example:

```json
"args": ["-y", "@modelcontextprotocol/server-filesystem", "/your/local/path/to/motofw"]
```
