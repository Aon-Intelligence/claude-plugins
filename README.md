# Aon Intelligence — Claude Plugins

A Claude plugin marketplace maintained by Aon Intelligence.

## Install a plugin

In **Claude Desktop**:

1. Open **Customize** in the left sidebar, then the **Plugins** tab.
2. Under **Personal plugins**, click **+** → **Add marketplace** → **Add from a repository**.
3. Enter `Aon-Intelligence/claude-plugins`.
4. Browse the plugins and click **Install** on the one you want.

In **Claude Code** (terminal), the equivalent is:

```bash
/plugin marketplace add Aon-Intelligence/claude-plugins
/plugin install azure-static-web-editor@aon-intelligence
```

See each plugin's README for prerequisites.

## Available plugins

| Plugin | Description |
|--------|-------------|
| [azure-static-web-editor](./plugins/azure-static-web-editor) | Read, write, and manage static websites hosted in Azure Blob Storage. Includes DALL-E image generation and favicon creation. |

## Adding a new plugin

Create a directory under `plugins/` with a `.claude-plugin/plugin.json`, then add an entry to `.claude-plugin/marketplace.json`. Follow `azure-static-web-editor` as a template.

Plugins that bundle an MCP server should not assume a Python interpreter or preinstalled packages exist on the user's machine. Declare dependencies inline with [PEP 723](https://peps.python.org/pep-0723/) and launch through `uv`, as `azure-static-web-editor` does. HTTP-based servers (Streamable HTTP or SSE) are preferred over stdio when you plan to run in Docker or a cloud container — the client connects via URL instead of spawning a subprocess. Note that GUI-launched apps on macOS receive a minimal `PATH` that excludes Homebrew, so resolve tool locations explicitly rather than relying on the ambient `PATH`.

## Validate before publishing

```bash
claude plugin validate ./plugins/<name>
```

Bump the version in both `plugins/<name>/.claude-plugin/plugin.json` and the marketplace entry, then push to `main`. Users pick up changes via **Customize → Plugins**, or `/plugin marketplace update aon-intelligence` in Claude Code.
