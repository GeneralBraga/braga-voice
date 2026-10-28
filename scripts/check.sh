#!/bin/zsh
set -euo pipefail

ROOT_DIR="${0:A:h:h}"
cd "$ROOT_DIR"

"$ROOT_DIR/.venv/bin/python" -m pytest -q
"$ROOT_DIR/.venv/bin/python" -m compileall -q src
"$ROOT_DIR/.venv/bin/python" scripts/privacy-check.py
git diff --check

