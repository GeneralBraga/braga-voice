from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata


_FENCED_CODE = re.compile(r"```.*?```", re.DOTALL)
_MARKDOWN_LINK = re.compile(r"\[([^\]]+)]\([^)]*\)")
_HTML_TAG = re.compile(r"<[^>]+>")
_LEADING_MARKER = re.compile(
    r"(?m)^[ \t]*(?:[-+*>#•▪◦]+|\d+[.)])[ \t]+"
)
_MULTI_SPACE = re.compile(r"[ \t\u00a0]+")
_ELLIPSIS = re.compile(r"(?:\.{2,}|…+)")
_REPEATED_EMPHASIS = re.compile(r"([!?])\1+")
_REPEATED_SEPARATOR = re.compile(r"([,;:])(?:[ \t]*[,;:])+")
_SPACE_BEFORE_PUNCTUATION = re.compile(r"[ \t]+([,.;:!?])")
_MISSING_AFTER_PUNCTUATION = re.compile(r"([,;:!?])(?=[^\s\d/])")
_MISSING_AFTER_SENTENCE = re.compile(r"([.!?])(?=[A-ZÀ-Ü])")
_SPOKEN_END = re.compile(r"[.!?][\"')\]]*$")
_TRAILING_SOFT_PAUSE = re.compile(r"[,;:]+$")
_PARAGRAPH_BREAK = re.compile(r"\n[ \t]*\n+")
_SPACED_DASH = re.compile(r"[ \t]*[–—][ \t]*")
_PARENTHESES = re.compile(r"[()\[\]{}]")
_DOUBLE_QUOTE = re.compile(r"[\"“”«»]")
_PLAIN_URL = re.compile(r"\b(?:https?://|www\.)[^\s<>()]+", re.IGNORECASE)
_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_BRL = re.compile(r"R\$\s*([0-9][0-9.]*(?:,[0-9]{1,2})?)")
_PERCENT = re.compile(r"\b([0-9]+(?:[.,][0-9]+)?)\s*%")
_DATE = re.compile(r"\b(0?[1-9]|[12][0-9]|3[01])[/.-](0?[1-9]|1[0-2])[/.-]([0-9]{2,4})\b")
_CLOCK = re.compile(r"\b([01]?[0-9]|2[0-3]):([0-5][0-9])\b")
_HOURS = re.compile(r"\b([0-9]+)\s*h\b", re.IGNORECASE)
_NUMBER_SIGN = re.compile(r"\bn[.º°]\s*", re.IGNORECASE)
_SOCIAL_MARKER = re.compile(r"(?<!\w)[#@](?=[A-Za-zÀ-ÖØ-öø-ÿ0-9_])")
_ALL_CAPS_PHRASE = re.compile(
    r"\b(?:[A-ZÀ-ÖØ-Þ]{2,}\s+){2,}[A-ZÀ-ÖØ-Þ]{2,}\b"
)
_MONTHS = (
    "", "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
)
_COMMON_ABBREVIATIONS = (
    (re.compile(r"\bSr\.(?=\s)", re.IGNORECASE), "senhor"),
    (re.compile(r"\bSra\.(?=\s)", re.IGNORECASE), "senhora"),
    (re.compile(r"\bDr\.(?=\s)", re.IGNORECASE), "doutor"),
    (re.compile(r"\bDra\.(?=\s)", re.IGNORECASE), "doutora"),
    (re.compile(r"\bProf\.(?=\s)", re.IGNORECASE), "professor"),
    (re.compile(r"\bProfa\.(?=\s)", re.IGNORECASE), "professora"),
    (re.compile(r"\bAv\.(?=\s)", re.IGNORECASE), "avenida"),
    (re.compile(r"\bR\.(?=\s)", re.IGNORECASE), "rua"),
    (re.compile(r"\bTel\.(?=\s)", re.IGNORECASE), "telefone"),
    (re.compile(r"\bAprox\.(?=\s)", re.IGNORECASE), "aproximadamente"),
)


@dataclass(frozen=True)
class SpeechAdjustment:
    code: str
    label: str
    count: int

    def public_dict(self) -> dict[str, str | int]:
        return {"code": self.code, "label": self.label, "count": self.count}


@dataclass(frozen=True)
class SpeechPreparation:
    text: str
    adjustments: tuple[SpeechAdjustment, ...]
    source_characters: int

    @property
    def output_characters(self) -> int:
        return len(self.text)

    @property
    def total_adjustments(self) -> int:
        return sum(item.count for item in self.adjustments)


class _AdjustmentTracker:
    def __init__(self) -> None:
        self._counts: dict[str, int] = {}

    def add(self, code: str, count: int = 1) -> None:
        if count > 0:
            self._counts[code] = self._counts.get(code, 0) + count

    def replace(
        self,
        pattern: re.Pattern[str],
        replacement: str,
        text: str,
        code: str,
    ) -> str:
        result, count = pattern.subn(replacement, text)
        self.add(code, count)
        return result

    def finish(self) -> tuple[SpeechAdjustment, ...]:
        labels = {
            "visual_formatting": "formatação visual removida",
            "symbols": "símbolos que atrapalham a fala removidos",
            "spacing": "espaçamento corrigido",
            "punctuation": "pontuação ajustada",
            "pauses": "pausas artificiais reduzidas",
            "abbreviations": "abreviações preparadas para leitura",
            "long_phrases": "frases longas divididas para melhorar o ritmo",
            "spoken_notation": "datas, horas e valores convertidos para fala",
            "web_addresses": "endereços digitais preparados para leitura",
            "capitalization": "ênfase artificial de caixa alta suavizada",
        }
        return tuple(
            SpeechAdjustment(code=code, label=labels[code], count=count)
            for code, count in self._counts.items()
        )


def _drop_emoji_and_symbols(text: str) -> tuple[str, int]:
    kept: list[str] = []
    removed = 0
    for char in text:
        category = unicodedata.category(char)
        if char in {"\ufe0f", "\u200d"}:
            removed += 1
            continue
        if category == "So":
            removed += 1
            continue
        kept.append(char)
    return "".join(kept), removed


def _is_short_heading(line: str) -> bool:
    letters = [char for char in line if char.isalpha()]
    return (
        1 <= len(line.split()) <= 10
        and len(line) <= 90
        and bool(letters)
        and all(char.isupper() for char in letters)
    )


def _spoken_url(match: re.Match[str]) -> str:
    value = re.sub(r"^(?:https?://|www\.)", "", match.group(0), flags=re.IGNORECASE)
    value = value.rstrip(".,;:!?")
    return (
        value.replace("/", " barra ")
        .replace(".", " ponto ")
        .replace("-", " hífen ")
        .replace("_", " sublinhado ")
    )


def _spoken_email(match: re.Match[str]) -> str:
    local, domain = match.group(0).split("@", 1)
    return local.replace(".", " ponto ") + " arroba " + domain.replace(".", " ponto ")


def _spoken_date(match: re.Match[str]) -> str:
    day, month, year = match.groups()
    return f"{int(day)} de {_MONTHS[int(month)]} de {year}"


def _spoken_clock(match: re.Match[str]) -> str:
    hour, minute = (int(value) for value in match.groups())
    return f"{hour} horas" if minute == 0 else f"{hour} horas e {minute} minutos"


def _soften_all_caps(match: re.Match[str]) -> str:
    value = match.group(0).lower()
    return value[:1].upper() + value[1:]


def _join_visual_lines(paragraph: str, tracker: _AdjustmentTracker) -> str:
    lines = [
        _MULTI_SPACE.sub(" ", line).strip()
        for line in paragraph.splitlines()
        if line.strip()
    ]
    spoken: list[str] = []
    for line in lines:
        if _is_short_heading(line):
            if _TRAILING_SOFT_PAUSE.search(line):
                line = _TRAILING_SOFT_PAUSE.sub(".", line)
                tracker.add("punctuation")
            elif not _SPOKEN_END.search(line):
                line += "."
                tracker.add("punctuation")
        spoken.append(line)
    if len(spoken) > 1:
        tracker.add("spacing", len(spoken) - 1)
    return " ".join(spoken)


def _split_long_phrases(
    text: str,
    tracker: _AdjustmentTracker,
    target: int = 175,
    maximum: int = 230,
) -> str:
    """Quebra apenas frases muito longas, usando uma pausa ja escrita pelo autor."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    result: list[str] = []
    for sentence in sentences:
        remainder = sentence
        while len(remainder) > maximum:
            candidates = [
                match.start()
                for match in re.finditer(r"[,;:]", remainder[:maximum])
                if 95 <= match.start() <= maximum - 35
            ]
            if not candidates:
                break
            split_at = min(candidates, key=lambda position: abs(position - target))
            result.append(remainder[:split_at].rstrip() + ".")
            remainder = remainder[split_at + 1 :].lstrip()
            if remainder and remainder[0].isalpha():
                remainder = remainder[0].upper() + remainder[1:]
            tracker.add("long_phrases")
        if remainder:
            result.append(remainder)
    return " ".join(result)


def prepare_for_speech(text: str) -> SpeechPreparation:
    """Prepara texto escrito para narracao sem reescrever o seu significado."""
    tracker = _AdjustmentTracker()
    cleaned = unicodedata.normalize("NFC", text)
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = tracker.replace(_FENCED_CODE, " ", cleaned, "visual_formatting")
    cleaned = tracker.replace(
        _MARKDOWN_LINK, r"\1", cleaned, "visual_formatting"
    )
    cleaned = tracker.replace(_HTML_TAG, " ", cleaned, "visual_formatting")
    # Itens de lista viram blocos falados separados. Quebras simples continuam
    # sendo apenas visuais e nao criam pausas artificiais.
    cleaned = tracker.replace(
        _LEADING_MARKER, "\n\n", cleaned, "visual_formatting"
    )

    for marker in ("**", "__", "`", "*"):
        count = cleaned.count(marker)
        if count:
            cleaned = cleaned.replace(marker, "")
            tracker.add("visual_formatting", count)
    underscore_count = cleaned.count("_")
    if underscore_count:
        cleaned = cleaned.replace("_", " ")
        tracker.add("visual_formatting", underscore_count)

    # Converte notação visual em fala antes da limpeza de símbolos.
    cleaned = tracker.replace(_EMAIL, _spoken_email, cleaned, "web_addresses")
    cleaned = tracker.replace(_PLAIN_URL, _spoken_url, cleaned, "web_addresses")
    cleaned = tracker.replace(_BRL, r"\1 reais", cleaned, "spoken_notation")
    cleaned = tracker.replace(_PERCENT, r"\1 por cento", cleaned, "spoken_notation")
    cleaned = tracker.replace(_DATE, _spoken_date, cleaned, "spoken_notation")
    cleaned = tracker.replace(_CLOCK, _spoken_clock, cleaned, "spoken_notation")
    cleaned = tracker.replace(_HOURS, r"\1 horas", cleaned, "spoken_notation")
    cleaned = tracker.replace(_NUMBER_SIGN, "número ", cleaned, "spoken_notation")
    cleaned = tracker.replace(_SOCIAL_MARKER, "", cleaned, "symbols")
    cleaned = tracker.replace(
        _ALL_CAPS_PHRASE, _soften_all_caps, cleaned, "capitalization"
    )

    cleaned, removed_symbols = _drop_emoji_and_symbols(cleaned)
    tracker.add("symbols", removed_symbols)
    cleaned = tracker.replace(_DOUBLE_QUOTE, "", cleaned, "symbols")
    cleaned = tracker.replace(_PARENTHESES, " ", cleaned, "spacing")
    cleaned = tracker.replace(_SPACED_DASH, ", ", cleaned, "punctuation")
    if "&" in cleaned:
        count = cleaned.count("&")
        cleaned = cleaned.replace("&", " e ")
        tracker.add("symbols", count)

    cleaned = tracker.replace(_ELLIPSIS, ".", cleaned, "pauses")
    cleaned = tracker.replace(
        _REPEATED_EMPHASIS, r"\1", cleaned, "punctuation"
    )
    cleaned = tracker.replace(
        _REPEATED_SEPARATOR, r"\1", cleaned, "punctuation"
    )
    for pattern, replacement in _COMMON_ABBREVIATIONS:
        cleaned = tracker.replace(
            pattern, replacement, cleaned, "abbreviations"
        )

    spoken_paragraphs: list[str] = []
    for raw_paragraph in _PARAGRAPH_BREAK.split(cleaned):
        paragraph = _join_visual_lines(raw_paragraph, tracker)
        if not paragraph:
            continue
        paragraph = tracker.replace(
            _SPACE_BEFORE_PUNCTUATION, r"\1", paragraph, "spacing"
        )
        paragraph = tracker.replace(
            _MISSING_AFTER_PUNCTUATION, r"\1 ", paragraph, "spacing"
        )
        paragraph = tracker.replace(
            _MISSING_AFTER_SENTENCE, r"\1 ", paragraph, "spacing"
        )
        paragraph = _MULTI_SPACE.sub(" ", paragraph).strip()
        if paragraph and paragraph[0].islower():
            paragraph = paragraph[0].upper() + paragraph[1:]
            tracker.add("capitalization")
        if _TRAILING_SOFT_PAUSE.search(paragraph):
            paragraph = _TRAILING_SOFT_PAUSE.sub(".", paragraph)
            tracker.add("punctuation")
        elif not _SPOKEN_END.search(paragraph):
            paragraph += "."
            tracker.add("punctuation")
        spoken_paragraphs.append(paragraph)

    prepared = " ".join(spoken_paragraphs)
    prepared = _split_long_phrases(prepared, tracker)
    prepared = _MULTI_SPACE.sub(" ", prepared).strip()
    return SpeechPreparation(
        text=prepared,
        adjustments=tracker.finish(),
        source_characters=len(text),
    )


def sanitize_for_speech(text: str) -> str:
    """Compatibilidade: devolve somente o texto preparado para o TTS."""
    return prepare_for_speech(text).text
