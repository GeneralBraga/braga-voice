import pytest

from braga_voice.presets import PRESETS, get_preset


def test_expected_presets_exist() -> None:
    assert {"natural", "comercial", "institucional", "urgente", "rapido"} <= PRESETS.keys()


def test_fast_preset_uses_flash_model() -> None:
    assert get_preset("rapido").model_id == "eleven_flash_v2_5"


def test_natural_preset_uses_v4_without_style_exaggeration() -> None:
    preset = get_preset("natural")
    assert preset.model_id == "eleven_v4"
    assert preset.style == 0
    assert preset.speed == 1.0
    assert preset.supports_style is False
    assert preset.supports_speed is False


def test_unknown_preset_is_rejected() -> None:
    with pytest.raises(ValueError, match="Preset desconhecido"):
        get_preset("pesado")

