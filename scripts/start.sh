#!/bin/zsh
set -euo pipefail

ROOT_DIR="${0:A:h:h}"
PYTHON_BIN="${BRAGA_VOICE_PYTHON:-}"

if [[ -z "$PYTHON_BIN" ]]; then
  for candidate in python3.13 python3.12 python3.11 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
      PYTHON_BIN="$(command -v "$candidate")"
      break
    fi
  done
fi

if [[ -z "$PYTHON_BIN" || ! -x "$PYTHON_BIN" ]]; then
  echo "Python 3.11 ou superior não encontrado." >&2
  exit 1
fi

if ! "$PYTHON_BIN" -c 'import sys; raise SystemExit(sys.version_info < (3, 11))'; then
  echo "O BRAGA VOICE requer Python 3.11 ou superior." >&2
  exit 1
fi

if [[ ! -x "$ROOT_DIR/.venv/bin/braga-voice" ]]; then
  "$PYTHON_BIN" -m venv "$ROOT_DIR/.venv"
  "$ROOT_DIR/.venv/bin/python" -m pip install --upgrade pip
  "$ROOT_DIR/.venv/bin/python" -m pip install -e "$ROOT_DIR"
fi

cd "$ROOT_DIR"
exec "$ROOT_DIR/.venv/bin/braga-voice"

