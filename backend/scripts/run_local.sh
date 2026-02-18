#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON_BIN="${PYTHON_BIN:-python}"

# Django 6.x requires Python 3.12+
"$PYTHON_BIN" -c "import sys; raise SystemExit(\"Python 3.12+ required for Django 6.x. Your version: %s\" % sys.version.split()[0]) if sys.version_info < (3,12) else None"

# Create venv if missing
if [ ! -d ".venv" ]; then
  "$PYTHON_BIN" -m venv .venv
fi

# Activate venv
# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python manage.py migrate
python manage.py runserver 127.0.0.1:8000