# MCP Repository Settings

## What this file is

`mcp-repository-settings.json` contains the JSON that must be pasted into:

> **Repository Settings → Copilot → Coding agent → MCP configuration**

It configures the six MCP servers that are declared in
`.github/agents/motofw-architect.agent.md`, making them available
to any Copilot coding agent session in this repository.

---

## How to apply it

1. Go to **Settings → Copilot → Coding agent** in this repository.
2. Open `docs/mcp-repository-settings.json`.
3. Copy the entire file contents.
4. Paste into the **MCP configuration** text box and click **Save**.

GitHub will validate the JSON syntax before saving.

---

## Servers

| Name | Runtime | Package | npm / PyPI version | Purpose |
|---|---|---|---|---|
| `fetch` | Python | `mcp-server-fetch` (PyPI) | 2025.4.7 | Fetches URLs and converts HTML to Markdown |
| `filesystem` | Node / npx | `@modelcontextprotocol/server-filesystem` | 2026.1.14 | Read/write access to the workspace |
| `memory` | Node / npx | `@modelcontextprotocol/server-memory` | 2026.1.26 | Persistent knowledge-graph across sessions |
| `sequential-thinking` | Node / npx | `@modelcontextprotocol/server-sequential-thinking` | 2025.12.18 | Structured step-by-step reasoning |
| `github` | Node / npx | `@modelcontextprotocol/server-github` | 2025.4.8 | GitHub API — download release ZIPs, read issues/PRs |
| `git` | Python | `mcp-server-git` (PyPI) | 2026.1.14 | Git operations on the workspace (status, log, diff, commit) |

---

## Prerequisites

### Python MCP servers

`mcp-server-fetch` and `mcp-server-git` must be installed in the Copilot
coding agent environment. This is handled by step **12b** in
`.github/workflows/copilot-setup-steps.yml`:

```yaml
- name: Install MCP Python servers
  run: pip install mcp-server-fetch mcp-server-git
```

`npx` is provided by the Node.js step (`actions/setup-node@v4`) and does not
require a separate install step.

### Secret required for the `github` server

The `github` server needs a GitHub personal access token. Add it to the
repository's **Copilot environment** (Settings → Environments → copilot)
as a secret named exactly:

```
COPILOT_MCP_GITHUB_PERSONAL_ACCESS_TOKEN
```

Use a fine-grained PAT scoped to this repository with **read-only** access
to Contents, Issues, and Pull Requests.

---

## Note on the filesystem and git paths

Both the `filesystem` and `git` servers are configured with the absolute path
`/home/runner/work/motofw/motofw`. This is the value of `$GITHUB_WORKSPACE`
on every GitHub Actions runner for this repository, and is the directory
Copilot coding agent always checks out the code into.

**If you run this configuration locally** (e.g. in VS Code with the MCP
extension), replace that path with your local repository root:

```json
"args": ["-y", "@modelcontextprotocol/server-filesystem", "/your/local/path/to/motofw"]
```

```json
"args": ["-m", "mcp_server_git", "--repository", "/your/local/path/to/motofw"]
```
