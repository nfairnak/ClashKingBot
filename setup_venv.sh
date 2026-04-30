#!/usr/bin/env bash
set -euo pipefail

PYTHON=python3
if command -v python3.13 >/dev/null 2>&1; then
  PYTHON=python3.13
fi

if ! "$PYTHON" -c 'import sys; sys.exit(0 if sys.version_info >= (3,13) else 1)'; then
  echo "ERROR: Python 3.13 or newer is required."
  echo "Install Python 3.13+ and rerun this script."
  exit 1
fi

if [ ! -d .venv ]; then
  "$PYTHON" -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Environment ready. Activate with: source .venv/bin/activate"
