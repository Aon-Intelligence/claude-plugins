# Azure Blob Static Web Editor

A Claude Desktop plugin for reading, writing, and managing static websites hosted in Azure Blob Storage (`$web` container). Includes AI image generation via DALL-E and automatic favicon creation.

## What it does

- **List files** — See everything currently on your website
- **Read files** — Inspect any HTML, CSS, JS, or other file
- **Write files** — Create or update pages, styles, scripts, and more
- **Generate images** — Use DALL-E to create images and upload them directly to your site
- **Create favicons** — Convert any image on your site into a `favicon.ico`

## Prerequisites

- Python 3.10+
- An Azure Storage account with static website hosting enabled (`$web` container)
- An OpenAI API key (required for image generation)

## Setup

### 1. Install Python dependencies

From inside the `server/` directory:

```bash
pip install -r plugins/azure-static-web-editor/server/requirements.txt
```

Or with `uv`:

```bash
uv pip install -r plugins/azure-static-web-editor/server/requirements.txt
```

### 2. Set environment variables

Add these to your shell config (`~/.zshrc` on Mac):

```bash
export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net"
export AZURE_STORAGE_CONTAINER_NAME="$web"
export OPENAI_API_KEY="sk-..."
```

Then reload your shell:

```bash
source ~/.zshrc
```

Your Azure connection string can be found in the Azure Portal under:
**Storage account → Security + networking → Access keys**

`AZURE_STORAGE_CONTAINER_NAME` is typically `$web` for Azure static website hosting, but can be any container name.

### 3. Install the plugin

In Claude Desktop:

```
/plugin install azure-static-web-editor@aon-intelligence
```

## Usage

Once installed, Claude will automatically load the static web editor skill when you mention your website. For example:

- *"Show me all the files on the website"*
- *"Update the homepage hero text"*
- *"Add a new About page"*
- *"Generate a hero image of a modern office for the homepage"*
- *"Create a favicon from the logo image"*
