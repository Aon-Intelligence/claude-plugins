#!/bin/sh
# Stop the static-web-editor MCP server listening on MCP_PORT (default 8000).
set -eu

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [ -f "$PLUGIN_ROOT/.env" ]; then
    set -a
    set +u
    # shellcheck disable=SC1091
    . "$PLUGIN_ROOT/.env"
    set -u
    set +a
fi

PORT="${MCP_PORT:-8000}"

pids="$(lsof -t -iTCP:"$PORT" -sTCP:LISTEN 2>/dev/null || true)"
if [ -z "$pids" ]; then
    echo "No server listening on port $PORT."
    exit 0
fi

echo "Stopping server on port $PORT (PIDs: $pids)"
kill $pids 2>/dev/null || true

# Give uvicorn a moment to shut down gracefully.
sleep 1

still="$(lsof -t -iTCP:"$PORT" -sTCP:LISTEN 2>/dev/null || true)"
if [ -n "$still" ]; then
    echo "Force stopping remaining PIDs: $still"
    kill -9 $still 2>/dev/null || true
fi

if lsof -t -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "Failed to free port $PORT." >&2
    exit 1
fi

echo "Port $PORT is free."
