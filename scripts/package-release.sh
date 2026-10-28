#!/bin/zsh
set -euo pipefail

ROOT_DIR="${0:A:h:h}"
VERSION="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' "$ROOT_DIR/packaging/Info.plist")"
ARCH="${BRAGA_VOICE_ARCH:-$(uname -m)}"
APP_DIR="$ROOT_DIR/dist/BRAGA VOICE.app"
RELEASE_DIR="$ROOT_DIR/release"
ARCHIVE="$RELEASE_DIR/BRAGA-VOICE-${VERSION}-macOS-${ARCH}.zip"

BRAGA_VOICE_ARCH="$ARCH" "$ROOT_DIR/scripts/build-macos-app.sh"
mkdir -p "$RELEASE_DIR"
rm -f -- "$ARCHIVE" "$ARCHIVE.sha256"
/usr/bin/ditto -c -k --keepParent "$APP_DIR" "$ARCHIVE"
(
  cd "$RELEASE_DIR"
  /usr/bin/shasum -a 256 "${ARCHIVE:t}" > "${ARCHIVE:t}.sha256"
)

echo "Pacote criado: $ARCHIVE"
echo "Checksum: $ARCHIVE.sha256"
