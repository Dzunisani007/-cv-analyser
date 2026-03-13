#!/usr/bin/env bash
set -euo pipefail

docker-compose up -d postgres

echo "Waiting for Postgres..."
sleep 2

alembic upgrade head

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
