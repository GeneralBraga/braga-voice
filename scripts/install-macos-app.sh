#!/bin/zsh
set -euo pipefail

ROOT_DIR="${0:A:h:h}"
SOURCE_APP="$ROOT_DIR/dist/BRAGA VOICE.app"
TARGET_APP="/Applications/BRAGA VOICE.app"
SUPPORT_DIR="$HOME/Library/Application Support/BRAGA VOICE"

if [[ ! -d "$SOURCE_APP" ]]; then
  echo "Aplicativo ainda não foi compilado. Execute ./scripts/build-macos-app.sh." >&2
  exit 1
fi

if [[ -e "$TARGET_APP" ]]; then
  if [[ "${1:-}" != "--replace" ]]; then
    echo "Já existe um BRAGA VOICE em Aplicativos. Use --replace para atualizar." >&2
    exit 1
  fi
  rm -rf -- "$TARGET_APP"
fi

mkdir -p "$SUPPORT_DIR"
if [[ -f "$ROOT_DIR/.env" ]]; then
  /usr/bin/install -m 600 "$ROOT_DIR/.env" "$SUPPORT_DIR/.env"
fi

/usr/bin/ditto "$SOURCE_APP" "$TARGET_APP"
/usr/bin/codesign --verify --deep --strict "$TARGET_APP"

echo "BRAGA VOICE instalado em: $TARGET_APP"
