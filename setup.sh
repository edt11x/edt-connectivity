#!/usr/bin/env bash
# setup.sh — Create and populate the Python venv (Linux / macOS)

set -euo pipefail

VENV_DIR=".venv"
PYTHON="${PYTHON:-python3}"

echo "=== EDT Connectivity Checker — Environment Setup ==="

# Verify Python is available
if ! command -v "$PYTHON" &>/dev/null; then
    echo "ERROR: '$PYTHON' not found. Install Python 3.10+ and try again." >&2
    exit 1
fi

PY_VERSION=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "  Python  : $("$PYTHON" --version)"

# Create venv if it does not already exist
if [ ! -d "$VENV_DIR" ]; then
    echo "  Creating venv in $VENV_DIR/ ..."
    "$PYTHON" -m venv "$VENV_DIR"
else
    echo "  Venv already exists at $VENV_DIR/ — skipping creation."
fi

# Activate and install dependencies
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "  Upgrading pip ..."
pip install --quiet --upgrade pip

echo "  Installing dependencies from requirements.txt ..."
pip install --quiet -r requirements.txt

echo ""
echo "Setup complete. To run the checker:"
echo "  source $VENV_DIR/bin/activate"
echo "  python check_connectivity.py"
echo ""
