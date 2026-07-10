# Azure Blob Static Web Editor

A Claude plugin for reading, writing, and managing static websites hosted in Azure Blob Storage (`$web` container). Includes AI image generation via DALL-E and automatic favicon creation.

## What it does

- **List files** — See everything currently on your website
- **Read files** — Inspect any HTML, CSS, JS, or other file
- **Write files** — Create or update pages, styles, scripts, and more
- **Generate images** — Use DALL-E to create images and upload them directly to your site
- **Create favicons** — Convert any image on your site into a `favicon.ico`
- **Backup & restore** — Snapshot the site to `backups/YYYYMMDD###/` and restore a named version on demand

## Architecture

The MCP server runs as a **local HTTP service** (Streamable HTTP transport). You start it once, then Claude connects over the network instead of spawning a subprocess.

```
Claude Desktop / Claude Code
        │
        ▼  HTTP (http://127.0.0.1:8000/mcp)
┌───────────────────────────┐
│  static-web-editor server │  ← uv + Python, reads .env
└───────────────────────────┘
        │
        ▼
  Azure Blob Storage ($web)
```

This model is easier to run in Docker and Azure Container Apps later — the same server binary, different host/port.

## Prerequisites

- **[uv](https://docs.astral.sh/uv/)** to resolve Python dependencies:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- An Azure Storage account with static website hosting enabled (`$web` container)
- An OpenAI API key, if you want image generation

macOS and Linux only for now.

## Quick start (local)

1. Copy the example env file and add your credentials:
   ```bash
   cd plugins/azure-static-web-editor
   cp .env.example .env
   # edit .env — at minimum set AZURE_STORAGE_CONNECTION_STRING
   ```

2. Start the server:
   ```bash
   ./server/run-server.sh
   ```
   Default endpoint: **http://127.0.0.1:8000/mcp**

3. Install the plugin in Claude (see below). The bundled `.mcp.json` already points at that URL.

4. Verify with the health check:
   ```bash
   curl http://127.0.0.1:8000/health
   ```

## Claude Desktop setup

**Do not use Customize → Connectors → Add custom connector** for this server. Custom connectors are for **remote** MCP servers on public **HTTPS** URLs — Anthropic's cloud calls that URL and cannot reach your machine.

For local development:

1. **Start the HTTP server** (keep this running):
   ```bash
   ./server/run-server.sh
   ```

2. **Install the plugin** via Customize → **Plugins** (not Connectors):
   - Add marketplace `Aon-Intelligence/claude-plugins`
   - Install **Azure Static Web Editor**

   The plugin uses `mcp-remote` to bridge Claude Desktop (stdio) to your local HTTP server at `http://127.0.0.1:8000/mcp`. Node.js is required for `npx`.

3. **Alternative — Developer config** (if not using the plugin):

   Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

   ```json
   {
     "mcpServers": {
       "static-web-editor": {
         "command": "npx",
         "args": [
           "-y",
           "mcp-remote@latest",
           "http://127.0.0.1:8000/mcp",
           "--allow-http"
         ]
       }
     }
   }
   ```

   Restart Claude Desktop completely after saving.

## Install the plugin

1. Open **Customize** in the Claude Desktop sidebar, then the **Plugins** tab.
2. Under **Personal plugins**, click **+** → **Add marketplace** → **Add from a repository**.
3. Enter `Aon-Intelligence/claude-plugins`.
4. Find **Azure Static Web Editor** and click **Install**.

The plugin bridges Claude Desktop to your local HTTP server via `mcp-remote`. **You must start the server yourself** (see Quick start) before using the plugin.

Secrets live in your local `.env` file (or container environment), not in Claude's plugin config.

## Usage

Claude loads the static web editor skill automatically when you mention your website:

- *"Show me all the files on the website"*
- *"Update the homepage hero text"*
- *"Add a new About page"*
- *"Generate a hero image of a modern office for the homepage"*
- *"Create a favicon from the logo image"*
- *"Back up the site"*
- *"List my backups"*
- *"Restore backup 20260710001"*

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `AZURE_STORAGE_CONNECTION_STRING` | — | Required. Azure Portal → storage account → Access keys |
| `AZURE_STORAGE_CONTAINER_NAME` | `$web` | Blob container for the static site |
| `OPENAI_API_KEY` | — | Required for DALL-E image generation |
| `MCP_HOST` | `127.0.0.1` | Bind address. Use `0.0.0.0` in Docker / Azure |
| `MCP_PORT` | `8000` | Listen port |
| `MCP_TRANSPORT` | `streamable-http` | `streamable-http` (recommended) or legacy `sse` |

### Legacy SSE transport

If your MCP client only supports the older SSE transport, set `MCP_TRANSPORT=sse` in `.env`. The SSE endpoint is `http://127.0.0.1:8000/sse` and requires a separate POST channel at `/messages/`. Streamable HTTP (`/mcp`) is preferred for new setups.

## Development

Dependencies are declared inline with [PEP 723](https://peps.python.org/pep-0723/) in `server/server.py` — no separate `requirements.txt`.

```bash
export AZURE_STORAGE_CONNECTION_STRING="..."
uv run --script server/server.py
```

Or use the [MCP Inspector](https://github.com/modelcontextprotocol/inspector) with transport **Streamable HTTP** and URL `http://127.0.0.1:8000/mcp`.
