#!/usr/bin/env bash
set -euo pipefail

echo "[run_server] DUMMY=${DUMMY:-<unset>}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SERVICE_DIR="$ROOT_DIR/service"

cd "$SERVICE_DIR"

# миграции (на всякий случай)
python -m alembic -c alembic.ini upgrade head

# сервер
exec python -m uvicorn app.main:app --reload --port 8000

