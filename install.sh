#!/usr/bin/env sh
# Thin wrapper: the real installer is install.py (works on Windows, macOS and Linux).
#   ./install.sh [--agent codex] [--link] [--with-claude-agents] ...   (same options as install.py)
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
PY="$(command -v python3 || command -v python)" || { echo "Python 3.9+ is required"; exit 1; }
exec "$PY" "$DIR/install.py" "$@"
