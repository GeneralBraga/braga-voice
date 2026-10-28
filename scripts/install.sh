#!/bin/zsh
set -euo pipefail

ROOT_DIR="${0:A:h:h}"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "O aplicativo desktop atual requer macOS." >&2
  exit 1
fi

case "$(uname -m)" in
  arm64|x86_64) ;;
  *)
    echo "Este Mac usa uma arquitetura ainda não suportada: $(uname -m)." >&2
    exit 1
    ;;
esac

if ! /usr/bin/xcrun --find swiftc >/dev/null 2>&1; then
  echo "Instale o Xcode Command Line Tools com: xcode-select --install" >&2
  exit 1
fi

PYTHON_BIN="${BRAGA_VOICE_PYTHON:-}"
if [[ -z "$PYTHON_BIN" ]]; then
  for candidate in python3.13 python3.12 python3.11 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
      PYTHON_BIN="$(command -v "$candidate")"
      break
    fi
  done
fi

if [[ -z "$PYTHON_BIN" ]] || ! "$PYTHON_BIN" -c 'import sys; raise SystemExit(sys.version_info < (3, 11))'; then
  echo "Instale Python 3.11 ou superior antes de continuar." >&2
  exit 1
fi

if [[ ! -d "$ROOT_DIR/.venv" ]]; then
  "$PYTHON_BIN" -m venv "$ROOT_DIR/.venv"
fi
"$ROOT_DIR/.venv/bin/python" -m pip install --upgrade pip
"$ROOT_DIR/.venv/bin/python" -m pip install -e "${ROOT_DIR}[dev,mac]"
"$ROOT_DIR/scripts/check.sh"
"$ROOT_DIR/scripts/build-macos-app.sh"
"$ROOT_DIR/scripts/install-macos-app.sh" --replace

echo "BRAGA VOICE instalado. Abra-o pela pasta Aplicativos e conecte sua própria ElevenLabs."
