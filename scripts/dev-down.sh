#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$ROOT_DIR/.run"
API_PID_FILE="$RUN_DIR/api.pid"
WEB_PID_FILE="$RUN_DIR/web.pid"

cd "$ROOT_DIR"

# mise may activate a root .venv while uv uses per-project environments.
unset VIRTUAL_ENV

stop_pid_file() {
  local pid_file="$1"
  local label="$2"

  if [[ ! -f "$pid_file" ]]; then
    printf '%s is not running\n' "$label"
    return 0
  fi

  local pid
  pid="$(cat "$pid_file")"

  if kill -0 "$pid" 2>/dev/null; then
    printf 'Stopping %s on PID %s...\n' "$label" "$pid"
    kill "$pid" 2>/dev/null || true

    for _ in $(seq 1 20); do
      if ! kill -0 "$pid" 2>/dev/null; then
        break
      fi
      sleep 0.25
    done

    if kill -0 "$pid" 2>/dev/null; then
      printf 'Force stopping %s on PID %s...\n' "$label" "$pid"
      kill -9 "$pid" 2>/dev/null || true
    fi
  else
    printf '%s PID file was stale\n' "$label"
  fi

  rm -f "$pid_file"
}

stop_pid_file "$WEB_PID_FILE" "web dashboard"
stop_pid_file "$API_PID_FILE" "API"

printf 'Stopping SignalForge local infrastructure...\n'
docker compose -f infra/compose/docker-compose.yaml down

printf 'SignalForge is stopped. Logs remain under .run/logs/.\n'
