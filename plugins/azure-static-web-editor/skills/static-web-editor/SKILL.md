---
name: "static-web-editor"
description: "Manages static websites hosted in Azure Blob Storage. Load when the user wants to update their website, edit HTML/CSS/JS files, add or modify pages, list what's on the site, upload or generate images, create a favicon, or do anything related to their static web presence."
---

# Azure Static Web Editor

You have access to tools for reading, writing, and managing a static website hosted in Azure Blob Storage (`$web` container).

## Available Tools

| Tool | Purpose |
|------|---------|
| `get_all_files()` | List every file on the website with name, size, type, and last modified date |
| `get_file(file_name)` | Read the current contents of any file |
| `save_file(file_name, content)` | Write or overwrite a text file (HTML, CSS, JS, etc.) |
| `generate_image(prompt, file_name, size)` | Generate an image via DALL-E and upload it to `images/` |
| `generate_favicon(filename)` | Convert an existing site image into a `favicon.ico` at the root |
| `create_backup()` | Snapshot all live site files into `backups/YYYYMMDD###/` |
| `list_backups()` | List available backup versions with file counts |
| `restore_backup(backup_id)` | Replace the live site with a named backup (e.g. `20260710001`) |

## Core Workflow

**Always start by listing files.** Call `get_all_files()` at the beginning of any editing session to understand the site's current structure before making changes.

**Always read before writing.** Call `get_file(file_name)` before editing any existing file. Never rewrite a file from scratch when you can get the current version and make targeted changes.

**Write complete file content.** `save_file` overwrites the entire file. Always pass the full updated content, not just the changed section.

## File Conventions

- HTML pages: lowercase, kebab-case (e.g., `about.html`, `contact-us.html`)
- Stylesheets: `styles.css` or `css/styles.css`
- Scripts: `scripts.js` or `js/scripts.js`
- Images: always in the `images/` folder (e.g., `images/hero.jpeg`, `images/logo.jpeg`)
- Favicon: always `favicon.ico` at the root (use `generate_favicon` to create it)

## Image Generation

Write rich, specific DALL-E prompts. Include style, mood, color palette, composition, and intended use. Vague prompts produce generic results.

Good: `"A clean, professional hero image with a soft blue-to-white gradient background, subtle geometric line art, and an abstract representation of data flowing between connected nodes. Modern, minimal, corporate style."`

Poor: `"A nice image for a website"`

Always use the `images/` prefix for generated image filenames.

## Favicon Workflow

1. Ensure a source image exists on the site (generate one or confirm with `get_all_files`)
2. Call `generate_favicon("images/logo.jpeg")` (or whichever image)
3. `favicon.ico` is automatically placed at the site root

## Content Type Handling

Use `save_file` for text-based content only: HTML, CSS, JavaScript, JSON, plain text, SVG.

Use `generate_image` or `generate_favicon` for all binary/image content. Do not attempt to write image data via `save_file`.

## Backups

Backups live under `backups/` in blob storage. Each backup is a folder named `YYYYMMDD###` (date plus a 3-digit sequence for that day).

- **Before large edits**: Offer or run `create_backup()` when making structural changes, deleting pages, or rewriting major sections.
- **List versions**: Use `list_backups()` when the user asks what backups exist.
- **Restore**: Use `restore_backup("YYYYMMDD###")` when the user names a version (e.g. "restore 20260703001"). Restore **replaces the entire live site** — all current site files are removed and replaced with the backup. The `backups/` folder is never modified. Confirm with the user before restoring unless they gave an explicit version to restore.

`get_all_files()` lists live site files only; backup blobs are excluded.

## When to Ask vs. Act

- **Ask first**: Adding a new page (confirm whether to update navigation on existing pages), deleting files, making large structural changes, **restoring a backup**
- **Act directly**: Fixing typos, updating copy, adding CSS rules, generating images the user described, **creating a backup when asked**
