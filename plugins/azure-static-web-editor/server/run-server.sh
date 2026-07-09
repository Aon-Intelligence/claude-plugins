#!/bin/sh
# Launch the MCP server via uv, which resolves the PEP 723 dependencies
# declared in server.py.
#
# GUI-launched apps on macOS get a minimal PATH that omits the usual uv install
# locations, so probe for it rather than relying on `command -v` alone.
set -eu

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
    echo "then restart Claude." >&2
    exit 127
fi

exec "$UV" run --quiet --script "$(dirname "$0")/server.py"
