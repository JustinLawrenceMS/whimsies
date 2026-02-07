#!/usr/bin/env bash
set -euo pipefail

# Usage: ./send_once.sh [project_dir] [python_bin]
# If project_dir omitted, uses script directory. If python_bin omitted, uses .venv/bin/python or system python3.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${1:-$SCRIPT_DIR}"
PYTHON_BIN="${2:-}" 

if [ -z "$PYTHON_BIN" ]; then
  if [ -x "$PROJECT_DIR/.venv/bin/python" ]; then
    PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"
  else
    PYTHON_BIN="$(command -v python3 || true)"
  fi
fi

if [ -z "$PYTHON_BIN" ]; then
  echo "Python binary not found. Pass one as second arg or create a .venv in the project dir." >&2
  exit 2
fi

# The Python script `whimsy.py` loads `.env` using python-dotenv, so we don't source it here.

echo "Running one-shot send using $PYTHON_BIN and project $PROJECT_DIR"
"$PYTHON_BIN" "$PROJECT_DIR/whimsy.py" --send-now
