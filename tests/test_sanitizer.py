from braga_voice.sanitizer import sanitize_for_speech


def test_removes_markdown_and_emoji_without_losing_words() -> None:
    source = "**MINHA EMPRESA.** 📲\n\n- Proteção 24 horas\n- [Fale conosco](https://example.com)"
    assert sanitize_for_speech(source) == (
        "MINHA EMPRESA. Proteção 24 horas. Fale conosco."
    )


def test_collapses_visual_spacing() -> None:
    source = "  Segurança    com   tecnologia.\n\n\n\n  Resposta rápida.  "
    assert sanitize_for_speech(source) == "Segurança com tecnologia. Resposta rápida."


def test_removes_visual_breaks_and_long_ellipsis() -> None:
    source = "Hoje...\n\n\nVamos apresentar a solução\ncom naturalidade"
    assert sanitize_for_speech(source) == (
        "Hoje. Vamos apresentar a solução com naturalidade."
    )


def test_single_visual_line_break_does_not_create_a_pause() -> None:
    source = "A tecnologia está\npresente e funcionando"
    assert sanitize_for_speech(source) == "A tecnologia está presente e funcionando."


def test_empty_visual_input_becomes_empty() -> None:
    assert sanitize_for_speech("** 📲 **") == ""

