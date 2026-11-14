#!/usr/bin/env bash
set -euo pipefail

# JARVIS Linux / Linux Mint Startup Script
# Developer: Shadow

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

echo "============================================"
echo "  JARVIS - Advanced Discord Management Bot  "
echo "============================================"

if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

echo "Running Alembic database migrations..."
alembic upgrade head

echo "Starting JARVIS..."
exec python bot.py
