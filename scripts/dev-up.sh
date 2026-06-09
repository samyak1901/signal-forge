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

stop_if_running() {
  local pid_file="$1"
  local label="$2"

  if ! is_running "$pid_file"; then
    rm -f "$pid_file"
    return 0
  fi

  local pid
  pid="$(cat "$pid_file")"
  printf 'Restarting %s on PID %s...\n' "$label" "$pid"
  kill "$pid" 2>/dev/null || true

  for _ in $(seq 1 20); do
    if ! kill -0 "$pid" 2>/dev/null; then
      break
    fi
    sleep 0.25
  done

  if kill -0 "$pid" 2>/dev/null; then
    kill -9 "$pid" 2>/dev/null || true
  fi

  rm -f "$pid_file"
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

stop_if_running "$API_PID_FILE" "API"
printf 'Starting API on http://localhost:8000...\n'
uv run --project apps/api uvicorn signal_forge_api.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  >"$LOG_DIR/api.log" 2>&1 &
printf '%s' "$!" >"$API_PID_FILE"

wait_for_http "http://localhost:8000/health" "API"

stop_if_running "$WEB_PID_FILE" "web dashboard"
printf 'Starting web dashboard on http://localhost:5173...\n'
npm run dev --prefix apps/web >"$LOG_DIR/web.log" 2>&1 &
printf '%s' "$!" >"$WEB_PID_FILE"

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
