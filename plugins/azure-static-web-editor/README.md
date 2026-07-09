# Azure Blob Static Web Editor

A Claude plugin for reading, writing, and managing static websites hosted in Azure Blob Storage (`$web` container). Includes AI image generation via DALL-E and automatic favicon creation.

## What it does

- **List files** — See everything currently on your website
- **Read files** — Inspect any HTML, CSS, JS, or other file
- **Write files** — Create or update pages, styles, scripts, and more
- **Generate images** — Use DALL-E to create images and upload them directly to your site
- **Create favicons** — Convert any image on your site into a `favicon.ico`

## Prerequisites

- **Claude Desktop.** This plugin runs a local MCP server, which works in the Desktop app's Chat tab and in Cowork. It does not run in browser chat at claude.ai.
- **[uv](https://docs.astral.sh/uv/)**, which manages the server's Python dependencies for you. Install it with:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
  You do not need to set up Python or install packages yourself.
- An Azure Storage account with static website hosting enabled (`$web` container)
- An OpenAI API key, if you want image generation

macOS and Linux only for now — the server launches through a shell script.

## Install

1. Open **Customize** in the Claude Desktop sidebar, then the **Plugins** tab.
2. Under **Personal plugins**, click **+** → **Add marketplace** → **Add from a repository**.
3. Enter `Aon-Intelligence/claude-plugins`.
4. Find **Azure Static Web Editor** and click **Install**.

Claude prompts you for three values at install time. They are stored by Claude — the two secrets go to your system's secure storage, and nothing is written into this repo.

| Value | Where to find it |
|-------|------------------|
| Azure Storage connection string | Azure Portal → your storage account → Security + networking → Access keys |
| OpenAI API key | platform.openai.com/api-keys |
| Container name | Defaults to `$web`; change only if your site lives elsewhere |

## Usage

Claude loads the static web editor skill automatically when you mention your website:

- *"Show me all the files on the website"*
- *"Update the homepage hero text"*
- *"Add a new About page"*
- *"Generate a hero image of a modern office for the homepage"*
- *"Create a favicon from the logo image"*

## Development

The server declares its dependencies inline with [PEP 723](https://peps.python.org/pep-0723/) in `server/server.py`, so there is no `requirements.txt` to keep in sync. Run it directly with:

```bash
uv run --script server/server.py
```

It expects `AZURE_STORAGE_CONNECTION_STRING` and, for image generation, `OPENAI_API_KEY` in the environment.
