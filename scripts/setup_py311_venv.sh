#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "== Checking for Python 3.11 =="
if command -v python3.11 >/dev/null 2>&1; then
  PY=python3.11
else
  echo "python3.11 not found. If you have Homebrew:"
  echo "  brew install pyenv && pyenv install 3.11.9"
  echo "Then re-run this script."
  exit 1
fi

echo "== Creating venv (.venv) =="
$PY -m venv .venv
source .venv/bin/activate
python -V

echo "== Upgrading pip/setuptools/wheel =="
pip install --upgrade pip setuptools wheel

echo "== Installing backend requirements (this may take a few minutes) =="
pip install -r backend/requirements.txt

echo "\nDone. Activate with:"
echo "  source .venv/bin/activate"
echo "\nRun backend:"
echo "  ENABLE_TEST_CHAT=true PYTHONPATH=backend uvicorn backend.main:app --host 0.0.0.0 --port 8000"
echo "\nRun frontend:"
echo "  cd frontend && python3 -m http.server 5173"
echo "\nOpen: http://localhost:5173/chat.html?api=http://localhost:8000"

