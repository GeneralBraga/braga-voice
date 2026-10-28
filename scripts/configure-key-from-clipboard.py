#!/usr/bin/env python3
"""Grava a chave ElevenLabs do clipboard no .env sem imprimi-la."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"


def read_clipboard() -> str:
    key = subprocess.check_output(["pbpaste"], text=True).strip()
    if not key.startswith("sk_") or len(key) < 20:
        raise SystemExit("O clipboard não contém uma chave ElevenLabs válida.")
    if "\n" in key or "\r" in key:
        raise SystemExit("A chave no clipboard contém múltiplas linhas.")
    return key


def update_env(key: str, voice_id: str | None = None) -> None:
    existing = ENV_PATH.read_text(encoding="utf-8").splitlines() if ENV_PATH.exists() else []
    output: list[str] = []
    key_replaced = False
    voice_replaced = False

    for line in existing:
        if line.startswith("ELEVENLABS_API_KEY="):
            output.append(f"ELEVENLABS_API_KEY={key}")
            key_replaced = True
        elif voice_id and line.startswith("ELEVENLABS_VOICE_ID="):
            output.append(f"ELEVENLABS_VOICE_ID={voice_id}")
            voice_replaced = True
        else:
            output.append(line)

    if not key_replaced:
        if output and output[-1]:
            output.append("")
        output.append(f"ELEVENLABS_API_KEY={key}")
    if voice_id and not voice_replaced:
        output.append(f"ELEVENLABS_VOICE_ID={voice_id}")

    temporary = ENV_PATH.with_suffix(".env.tmp")
    temporary.write_text("\n".join(output) + "\n", encoding="utf-8")
    os.chmod(temporary, 0o600)
    temporary.replace(ENV_PATH)
    os.chmod(ENV_PATH, 0o600)


if __name__ == "__main__":
    selected_voice_id = sys.argv[1] if len(sys.argv) > 1 else None
    update_env(read_clipboard(), selected_voice_id)
    print("Chave ElevenLabs configurada localmente em .env (modo 600).")
