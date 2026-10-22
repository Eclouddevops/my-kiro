#!/usr/bin/env bash
#
# dev.sh — run the backend and frontend dev servers together (macOS / Linux).
#
# Starts FastAPI (uvicorn --reload) on :8000 and the Vite dev server on :5173.
# Both run in the background; Ctrl+C stops both cleanly.
#
# Usage:  ./scripts/dev.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

info() { printf '\033[0;34m==>\033[0m %s\n' "$1"; }
die()  { printf '\033[0;31merror:\033[0m %s\n' "$1" >&2; exit 1; }

[ -d "$ROOT_DIR/backend/.venv" ] || die "backend/.venv missing. Run ./scripts/setup.sh first."

pids=()
cleanup() {
  info "Stopping dev servers..."
  for pid in "${pids[@]}"; do
    kill "$pid" 2>/dev/null || true
  done
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# ---- Backend -------------------------------------------------------------
info "Starting backend on http://localhost:8000"
(
  cd "$ROOT_DIR/backend"
  # shellcheck disable=SC1091
  source .venv/bin/activate
  exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
) &
pids+=($!)

# ---- Frontend ------------------------------------------------------------
if command -v npm >/dev/null 2>&1; then
  info "Starting frontend on http://localhost:5173"
  (
    cd "$ROOT_DIR/frontend"
    exec npm run dev
  ) &
  pids+=($!)
else
  info "npm not found — running backend only."
fi

info "Press Ctrl+C to stop."
wait
