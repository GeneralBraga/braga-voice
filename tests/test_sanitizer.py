from braga_voice.sanitizer import sanitize_for_speech


def test_removes_markdown_and_emoji_without_losing_words() -> None:
    source = "**MINHA EMPRESA.** 📲\n\n- Proteção 24 horas\n- [Fale conosco](https://example.com)"
    assert sanitize_for_speech(source) == (
        "MINHA EMPRESA.\n\nProteção 24 horas\nFale conosco"
    )


def test_collapses_visual_spacing() -> None:
    source = "  Segurança    com   tecnologia.\n\n\n\n  Resposta rápida.  "
    assert sanitize_for_speech(source) == "Segurança com tecnologia.\n\nResposta rápida."


def test_empty_visual_input_becomes_empty() -> None:
    assert sanitize_for_speech("** 📲 **") == ""

