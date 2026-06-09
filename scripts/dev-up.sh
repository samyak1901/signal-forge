#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$ROOT_DIR/.run"
LOG_DIR="$RUN_DIR/logs"
API_PID_FILE="$RUN_DIR/api.pid"
WEB_PID_FILE="$RUN_DIR/web.pid"

mkdir -p "$LOG_DIR"

cd "$ROOT_DIR"

# mise may activate a root .venv while uv uses per-project environments.
unset VIRTUAL_ENV

is_running() {
  local pid_file="$1"
  [[ -f "$pid_file" ]] && kill -0 "$(cat "$pid_file")" 2>/dev/null
}

wait_for_http() {
  local url="$1"
  local label="$2"
  local attempts=60

  for _ in $(seq 1 "$attempts"); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      printf '%s is ready\n' "$label"
      return 0
    fi
    sleep 1
  done

  printf '%s did not become ready at %s\n' "$label" "$url" >&2
  return 1
}

printf 'Starting SignalForge local infrastructure...\n'
docker compose -f infra/compose/docker-compose.yaml up -d

printf 'Installing dependencies...\n'
uv sync --project apps/api >/dev/null
npm install --prefix apps/web >/dev/null

printf 'Applying database migrations...\n'
uv run --project apps/api alembic -c apps/api/alembic.ini upgrade head

if is_running "$API_PID_FILE"; then
  printf 'API already running on PID %s\n' "$(cat "$API_PID_FILE")"
else
  printf 'Starting API on http://localhost:8000...\n'
  uv run --project apps/api uvicorn signal_forge_api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    >"$LOG_DIR/api.log" 2>&1 &
  printf '%s' "$!" >"$API_PID_FILE"
fi

wait_for_http "http://localhost:8000/health" "API"

if is_running "$WEB_PID_FILE"; then
  printf 'Web dashboard already running on PID %s\n' "$(cat "$WEB_PID_FILE")"
else
  printf 'Starting web dashboard on http://localhost:5173...\n'
  npm run dev --prefix apps/web >"$LOG_DIR/web.log" 2>&1 &
  printf '%s' "$!" >"$WEB_PID_FILE"
fi

wait_for_http "http://localhost:5173" "Web dashboard"

cat <<EOF

SignalForge is running.

Dashboard: http://localhost:5173
API docs:  http://localhost:8000/docs
Health:    http://localhost:8000/health

Logs:
  API: $LOG_DIR/api.log
  Web: $LOG_DIR/web.log

Stop everything with:
  mise run down
EOF
