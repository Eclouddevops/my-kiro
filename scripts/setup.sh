#!/usr/bin/env bash
#
# setup.sh — one-time developer setup for macOS and Linux.
#
# Creates the backend virtualenv + installs deps, installs frontend deps, and
# copies the example env files if real ones do not exist yet.
#
# Usage:  ./scripts/setup.sh
set -euo pipefail

# Resolve the repo root regardless of where the script is invoked from.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

info()  { printf '\033[0;34m==>\033[0m %s\n' "$1"; }
warn()  { printf '\033[0;33mwarn:\033[0m %s\n' "$1"; }
die()   { printf '\033[0;31merror:\033[0m %s\n' "$1" >&2; exit 1; }

# ---- Prerequisite checks -------------------------------------------------
command -v python3 >/dev/null 2>&1 || die "python3 is required (install Python 3.11+)."
command -v node    >/dev/null 2>&1 || warn "node not found — frontend setup will be skipped."

PY_VER="$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
info "Using Python $PY_VER"

# ---- Backend -------------------------------------------------------------
info "Setting up backend (backend/.venv)"
cd "$ROOT_DIR/backend"

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip >/dev/null
pip install -e ".[dev]"
deactivate

if [ ! -f .env ]; then
  cp .env.example .env
  info "Created backend/.env from example — edit it with your AWS + DB settings."
fi

# ---- Frontend ------------------------------------------------------------
cd "$ROOT_DIR/frontend"
if command -v npm >/dev/null 2>&1; then
  info "Installing frontend dependencies"
  npm install
  if [ ! -f .env ]; then
    cp .env.example .env
    info "Created frontend/.env from example."
  fi
else
  warn "Skipping frontend install (npm not available). Install Node.js 20+ and run 'npm install' in frontend/."
fi

cd "$ROOT_DIR"
info "Setup complete. Next: ./scripts/dev.sh to run both services."
