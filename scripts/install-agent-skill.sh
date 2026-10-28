#!/bin/zsh
set -euo pipefail

ROOT_DIR="${0:A:h:h}"
SOURCE_DIR="$ROOT_DIR/skills/braga-voice"
REPLACE="${1:-}"
DESTINATIONS=(
  "$HOME/.codex/skills/braga-voice"
  "$HOME/.claude/skills/braga-voice"
)

for destination in "${DESTINATIONS[@]}"; do
  if [[ -e "$destination" ]]; then
    if [[ "$REPLACE" != "--replace" ]]; then
      echo "A skill já existe em $destination. Use --replace para atualizar." >&2
      exit 1
    fi
    rm -rf -- "$destination"
  fi
  mkdir -p "${destination:h}"
  /usr/bin/ditto "$SOURCE_DIR" "$destination"
  echo "Skill instalada em: $destination"
done
