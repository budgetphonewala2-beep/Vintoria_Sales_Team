#!/usr/bin/env sh
# Thin wrapper: python install.py --uninstall
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
PY="$(command -v python3 || command -v python)" || { echo "Python 3.9+ is required"; exit 1; }
exec "$PY" "$DIR/install.py" --uninstall "$@"
