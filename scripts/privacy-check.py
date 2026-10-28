#!/usr/bin/env python3
"""Fail when publishable files contain common credentials or local private data."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_TRACKED = {".env"}
FORBIDDEN_SUFFIXES = {".mp3", ".wav", ".m4a", ".aiff", ".flac"}
PATTERNS = {
    "absolute macOS user path": re.compile(r"/Users/[^/\s]+/"),
    "ElevenLabs secret": re.compile(r"\bsk_[A-Za-z0-9_-]{20,}\b"),
}


def tracked_files() -> list[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
    )
    return [ROOT / item.decode() for item in output.split(b"\0") if item]


def main() -> int:
    findings: list[str] = []
    for path in tracked_files():
        relative = path.relative_to(ROOT)
        if str(relative) in FORBIDDEN_TRACKED or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            findings.append(f"arquivo privado publicável: {relative}")
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if path.name.startswith(".env"):
            for line in content.splitlines():
                if line.startswith("ELEVENLABS_API_KEY="):
                    value = line.partition("=")[2].strip()
                    if value and value != "sua_chave_local":
                        findings.append(f"filled API key: {relative}")
        if relative == Path("scripts/privacy-check.py"):
            continue
        for label, pattern in PATTERNS.items():
            if pattern.search(content):
                findings.append(f"{label}: {relative}")

    if findings:
        print("Verificação de privacidade falhou:")
        for finding in sorted(set(findings)):
            print(f"- {finding}")
        return 1
    print("Privacidade: nenhum segredo, áudio ou caminho pessoal publicável encontrado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
