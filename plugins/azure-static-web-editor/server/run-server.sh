#!/bin/sh
# Start the static-web-editor MCP server over HTTP.
#
# Resolves uv across macOS PATH quirks, loads .env from the plugin root if
# present, then runs server.py (Streamable HTTP on port 8000 by default).
set -eu

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

find_uv() {
    if command -v uv >/dev/null 2>&1; then
        command -v uv
        return 0
    fi
    for candidate in \
        "$HOME/.local/bin/uv" \
        "$HOME/.cargo/bin/uv" \
        /opt/homebrew/bin/uv \
        /usr/local/bin/uv
    do
        if [ -x "$candidate" ]; then
            echo "$candidate"
            return 0
        fi
    done
    return 1
}

if ! UV="$(find_uv)"; then
    echo "azure-static-web-editor: could not find 'uv'." >&2
    echo "Install it with:  curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
    exit 127
fi

if [ -f "$PLUGIN_ROOT/.env" ]; then
    set -a
    set +u  # .env values may contain $ (e.g. Azure static site container "$web")
    # shellcheck disable=SC1091
    . "$PLUGIN_ROOT/.env"
    set -u
    set +a
fi

if [ -z "${AZURE_STORAGE_CONTAINER_NAME:-}" ]; then
    AZURE_STORAGE_CONTAINER_NAME='$web'
    export AZURE_STORAGE_CONTAINER_NAME
fi

if [ -z "${AZURE_STORAGE_CONNECTION_STRING:-}" ]; then
    echo "azure-static-web-editor: AZURE_STORAGE_CONNECTION_STRING is not set." >&2
    echo "Copy .env.example to .env and fill in your Azure credentials." >&2
    exit 1
fi

case "$AZURE_STORAGE_CONNECTION_STRING" in
    *AccountName=*AccountKey=*)
        ;;
    *)
        echo "azure-static-web-editor: AZURE_STORAGE_CONNECTION_STRING looks truncated." >&2
        echo "Wrap the entire value in single quotes in .env — semicolons break shell sourcing." >&2
        exit 1
        ;;
esac

export MCP_HOST="${MCP_HOST:-127.0.0.1}"
export MCP_PORT="${MCP_PORT:-8000}"
export MCP_TRANSPORT="${MCP_TRANSPORT:-streamable-http}"

exec "$UV" run --quiet --script "$(dirname "$0")/server.py"
