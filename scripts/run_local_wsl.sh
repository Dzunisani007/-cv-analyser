#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# Ensure .env exists
if [ ! -f .env ] && [ -f .env.example ]; then
  cp .env.example .env
  echo "Created .env from .env.example (please review/edit)."
fi

# Load .env into this shell (export all vars)
if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

if [ ! -d .venv ]; then
  echo "No .venv found. Run ./scripts/setup_venv.sh first." >&2
  exit 1
fi

# shellcheck disable=SC1091
source .venv/bin/activate

HOST="${SERVICE_HOST:-0.0.0.0}"
PORT="${SERVICE_PORT:-8000}"

exec uvicorn app.main:app --reload --host "${HOST}" --port "${PORT}"
