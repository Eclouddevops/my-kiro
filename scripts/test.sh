#!/usr/bin/env bash
#
# test.sh — run backend and frontend test suites (macOS / Linux).
#
# Usage:
#   ./scripts/test.sh            # run both suites
#   ./scripts/test.sh backend    # backend only
#   ./scripts/test.sh frontend   # frontend only
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TARGET="${1:-all}"

info() { printf '\033[0;34m==>\033[0m %s\n' "$1"; }
die()  { printf '\033[0;31merror:\033[0m %s\n' "$1" >&2; exit 1; }

run_backend() {
  info "Running backend tests (pytest)"
  cd "$ROOT_DIR/backend"
  [ -d .venv ] || die "backend/.venv missing. Run ./scripts/setup.sh first."
  # shellcheck disable=SC1091
  source .venv/bin/activate
  pytest -q
  deactivate
}

run_frontend() {
  info "Running frontend tests (vitest)"
  cd "$ROOT_DIR/frontend"
  command -v npm >/dev/null 2>&1 || die "npm not found. Install Node.js 20+."
  npm test
}

case "$TARGET" in
  backend)  run_backend ;;
  frontend) run_frontend ;;
  all)      run_backend; run_frontend ;;
  *)        die "unknown target '$TARGET' (use: backend | frontend | all)" ;;
esac

info "Tests complete."
