from braga_voice.sanitizer import prepare_for_speech, sanitize_for_speech


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


def test_directs_messy_copy_for_natural_speech() -> None:
    source = (
        "  **SEGURANÇA NÃO ESPERA**...\n\n"
        "Quando o assunto é proteger o que importa,cada segundo faz diferença!!!\n\n"
        "- resposta rápida\n- tecnologia & confiança\n\n"
        "Fale com o Sr. João hoje , sem compromisso."
    )
    preparation = prepare_for_speech(source)

    assert preparation.text == (
        "Segurança não espera. Quando o assunto é proteger o que importa, "
        "cada segundo faz diferença! Resposta rápida. Tecnologia e confiança. "
        "Fale com o senhor João hoje, sem compromisso."
    )
    assert preparation.total_adjustments >= 10
    assert {item.code for item in preparation.adjustments} >= {
        "visual_formatting",
        "spacing",
        "punctuation",
        "pauses",
        "abbreviations",
    }


def test_splits_only_very_long_phrase_at_existing_pause() -> None:
    source = (
        "A Malupe oferece monitoramento inteligente, profissionais preparados "
        "para agir com rapidez, tecnologia integrada para antecipar riscos, "
        "atendimento próximo em todos os momentos, supervisão contínua das "
        "operações, protocolos claros para cada ocorrência, comunicação "
        "eficiente com o cliente e acompanhamento completo para proteger o que "
        "realmente importa em sua empresa."
    )
    preparation = prepare_for_speech(source)

    assert ". Supervisão contínua" in preparation.text
    assert any(item.code == "long_phrases" for item in preparation.adjustments)


def test_prepares_currency_and_url_for_speech() -> None:
    source = "Investimento de R$ 1.500,00. Acesse https://malupe.com.br"
    assert sanitize_for_speech(source) == (
        "Investimento de 1.500,00 reais. Acesse malupe ponto com ponto br."
    )


def test_prepares_date_clock_percentage_and_number_for_speech() -> None:
    source = "Reunião em 13/11/2026, às 14:30, na sala nº 2. Meta: 25%."
    assert sanitize_for_speech(source) == (
        "Reunião em 13 de novembro de 2026, às 14 horas e 30 minutos, "
        "na sala número 2. Meta: 25 por cento."
    )


def test_prepares_email_and_social_markers_without_losing_content() -> None:
    source = "Escreva para contato@malupe.com.br ou siga #Malupe."
    assert sanitize_for_speech(source) == (
        "Escreva para contato arroba malupe ponto com ponto br ou siga Malupe."
    )


def test_closes_text_that_ends_with_soft_punctuation() -> None:
    assert sanitize_for_speech("Uma mensagem incompleta,") == (
        "Uma mensagem incompleta."
    )
    assert sanitize_for_speech("ATENÇÃO:\nConfira os dados") == (
        "ATENÇÃO. Confira os dados."
    )

