from braga_voice.presets import get_preset
from braga_voice.providers.elevenlabs import ElevenLabsProvider


def test_v4_request_uses_portuguese_normalization_without_unsupported_controls() -> None:
    body = ElevenLabsProvider._synthesis_body(
        text="Uma fala natural.",
        preset=get_preset("natural"),
    )

    assert body["model_id"] == "eleven_v4"
    assert body["language_code"] == "pt"
    assert body["apply_text_normalization"] == "auto"
    assert body["voice_settings"] == {
        "stability": 0.50,
        "similarity_boost": 0.75,
    }


def test_flash_request_keeps_supported_controls() -> None:
    body = ElevenLabsProvider._synthesis_body(
        text="Teste rápido.",
        preset=get_preset("rapido"),
    )

    assert body["voice_settings"]["style"] == 0.0
    assert body["voice_settings"]["use_speaker_boost"] is False
