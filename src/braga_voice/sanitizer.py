from __future__ import annotations

import re
import unicodedata


_FENCED_CODE = re.compile(r"```.*?```", re.DOTALL)
_MARKDOWN_LINK = re.compile(r"\[([^\]]+)]\([^)]*\)")
_HTML_TAG = re.compile(r"<[^>]+>")
_LEADING_MARKER = re.compile(r"(?m)^[ \t]*(?:[-+*>#]+|\d+[.)])[ \t]+")
_MULTI_SPACE = re.compile(r"[ \t]+")
_TOO_MANY_BREAKS = re.compile(r"\n{3,}")


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
    cleaned = _LEADING_MARKER.sub("", cleaned)
    cleaned = cleaned.replace("**", "").replace("__", "")
    cleaned = cleaned.replace("`", "").replace("*", "").replace("_", " ")
    cleaned = _drop_emoji_and_symbols(cleaned)
    cleaned = "\n".join(_MULTI_SPACE.sub(" ", line).strip() for line in cleaned.splitlines())
    cleaned = _TOO_MANY_BREAKS.sub("\n\n", cleaned)
    return cleaned.strip()

