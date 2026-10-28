from __future__ import annotations

import re
import unicodedata


_FENCED_CODE = re.compile(r"```.*?```", re.DOTALL)
_MARKDOWN_LINK = re.compile(r"\[([^\]]+)]\([^)]*\)")
_HTML_TAG = re.compile(r"<[^>]+>")
_LEADING_MARKER = re.compile(r"(?m)^[ \t]*(?:[-+*>#]+|\d+[.)])[ \t]+")
_MULTI_SPACE = re.compile(r"[ \t]+")
_ELLIPSIS = re.compile(r"(?:\.{2,}|…+)")
_SPOKEN_END = re.compile(r"[.!?;:,][\"')\]]*$")
_PARAGRAPH_BREAK = re.compile(r"\n[ \t]*\n+")


def _drop_emoji_and_symbols(text: str) -> str:
    kept: list[str] = []
    for char in text:
        category = unicodedata.category(char)
        if char in {"\ufe0f", "\u200d"}:
            continue
        # So inclui a maioria dos emojis e pictogramas. Mantemos moeda (Sc)
        # e pontuacao normal para preservar valores e ritmo de locucao.
        if category == "So":
            continue
        kept.append(char)
    return "".join(kept)


def sanitize_for_speech(text: str) -> str:
    """Remove formatacao visual que nao deve ser pronunciada pelo TTS."""
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = _FENCED_CODE.sub(" ", cleaned)
    cleaned = _MARKDOWN_LINK.sub(r"\1", cleaned)
    cleaned = _HTML_TAG.sub(" ", cleaned)
    # Marcadores viram limites de frase. Quebras simples continuam sendo apenas
    # quebra visual, evitando pausas artificiais em texto colado do editor.
    cleaned = _LEADING_MARKER.sub("\n", cleaned)
    cleaned = cleaned.replace("**", "").replace("__", "")
    cleaned = cleaned.replace("`", "").replace("*", "").replace("_", " ")
    cleaned = _drop_emoji_and_symbols(cleaned)
    cleaned = _ELLIPSIS.sub(".", cleaned)

    spoken_paragraphs: list[str] = []
    for raw_paragraph in _PARAGRAPH_BREAK.split(cleaned):
        paragraph = " ".join(
            _MULTI_SPACE.sub(" ", line).strip()
            for line in raw_paragraph.splitlines()
            if line.strip()
        )
        if not paragraph:
            continue
        if not _SPOKEN_END.search(paragraph):
            paragraph += "."
        spoken_paragraphs.append(paragraph)
    return " ".join(spoken_paragraphs)

