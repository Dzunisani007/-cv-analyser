#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_DIR="${SCRIPT_DIR}/.."

cd "${SERVICE_DIR}"

PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "Python not found (${PYTHON_BIN}). Install python3.11+ in WSL." >&2
  exit 1
fi

"${PYTHON_BIN}" --version

if [ ! -d .venv ]; then
  echo "Creating .venv..."
  "${PYTHON_BIN}" -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Done. To run locally:" 
echo "  source .venv/bin/activate"
echo "  ./scripts/test.sh"
echo "  ./scripts/run_local_wsl.sh"
