# Aon Intelligence — Claude Plugins

Internal Claude Desktop plugin marketplace for Aon Intelligence.

## Onboarding (one-time setup per person)

### 1. Clone this repo

Clone it wherever you keep your repos:

```bash
git clone git@github.com:Aon-Intelligence/claude-plugins.git ~/dev/claude-plugins
```

### 2. Register the marketplace with Claude

Add this to `~/.claude/settings.json` (create the file if it doesn't exist):

```json
{
  "extraKnownMarketplaces": {
    "aon-intelligence": {
      "source": {
        "source": "local",
        "directory": "/Users/yourname/dev/claude-plugins"
      }
    }
  }
}
```

Replace `/Users/yourname/dev/claude-plugins` with the actual path where you cloned the repo.

### 3. Install a plugin

Open Claude Desktop and run:

```
/plugin install azure-static-web-editor@aon-intelligence
```

See each plugin's README for any additional setup steps (e.g., environment variables).

## Keeping plugins up to date

When plugins are updated, pull the latest and refresh:

```bash
cd ~/dev/claude-plugins && git pull
```

Then in Claude Desktop:

```
/plugin marketplace update
```

## Available Plugins

| Plugin | Description |
|--------|-------------|
| [azure-static-web-editor](./plugins/azure-static-web-editor) | Read, write, and manage static websites hosted in Azure Blob Storage. Includes DALL-E image generation and favicon creation. |

## Adding a new plugin

Create a new directory under `plugins/` following the same structure as `azure-static-web-editor`, then add an entry to `.claude-plugin/marketplace.json`.
