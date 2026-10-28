#!/bin/zsh
set -euo pipefail

ROOT_DIR="${0:A:h:h}"
PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
BUILD_DIR="$ROOT_DIR/build/macos"
PYINSTALLER_DIR="$ROOT_DIR/build/pyinstaller"
APP_DIR="$ROOT_DIR/dist/BRAGA VOICE.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"
ICONSET_DIR="$BUILD_DIR/AppIcon.iconset"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Ambiente Python não encontrado. Execute ./scripts/start.sh primeiro." >&2
  exit 1
fi

"$PYTHON_BIN" -m pip install -e "${ROOT_DIR}[dev,mac]"

rm -rf -- "$BUILD_DIR" "$PYINSTALLER_DIR" "$APP_DIR"
mkdir -p "$BUILD_DIR" "$PYINSTALLER_DIR/dist" "$PYINSTALLER_DIR/work" \
  "$MACOS_DIR" "$RESOURCES_DIR/backend" "$ICONSET_DIR"

"$PYTHON_BIN" -m PyInstaller \
  --noconfirm \
  --clean \
  --distpath "$PYINSTALLER_DIR/dist" \
  --workpath "$PYINSTALLER_DIR/work" \
  "$ROOT_DIR/packaging/braga_voice_backend.spec"

/usr/bin/swiftc \
  -parse-as-library \
  -target arm64-apple-macos14.0 \
  -O \
  -framework AppKit \
  -framework Foundation \
  -framework WebKit \
  "$ROOT_DIR/packaging/BragaVoice.swift" \
  -o "$MACOS_DIR/BragaVoice"

/usr/bin/ditto "$PYINSTALLER_DIR/dist/braga-voice-backend" "$RESOURCES_DIR/backend/braga-voice-backend"
cp "$ROOT_DIR/packaging/Info.plist" "$CONTENTS_DIR/Info.plist"

for spec in \
  "16:icon_16x16.png" \
  "32:icon_16x16@2x.png" \
  "32:icon_32x32.png" \
  "64:icon_32x32@2x.png" \
  "128:icon_128x128.png" \
  "256:icon_128x128@2x.png" \
  "256:icon_256x256.png" \
  "512:icon_256x256@2x.png" \
  "512:icon_512x512.png" \
  "1024:icon_512x512@2x.png"; do
  size="${spec%%:*}"
  filename="${spec#*:}"
  /usr/bin/sips -z "$size" "$size" "$ROOT_DIR/assets/braga-voice-icon-v3.png" \
    --out "$ICONSET_DIR/$filename" >/dev/null
done

/usr/bin/iconutil -c icns "$ICONSET_DIR" -o "$RESOURCES_DIR/AppIcon.icns"
chmod 755 "$MACOS_DIR/BragaVoice" "$RESOURCES_DIR/backend/braga-voice-backend/braga-voice-backend"
/usr/bin/codesign --force --deep --sign - "$APP_DIR"
/usr/bin/codesign --verify --deep --strict "$APP_DIR"

echo "Aplicativo criado em: $APP_DIR"
