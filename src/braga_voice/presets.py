from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class VoicePreset:
    id: str
    label: str
    description: str
    model_id: str
    stability: float
    similarity_boost: float
    style: float
    speed: float
    use_speaker_boost: bool = True

    def public_dict(self) -> dict[str, object]:
        return asdict(self)


PRESETS: dict[str, VoicePreset] = {
    "natural": VoicePreset(
        id="natural",
        label="Natural",
        description="Próximo, leve e conversado.",
        model_id="eleven_multilingual_v2",
        stability=0.42,
        similarity_boost=0.78,
        style=0.22,
        speed=1.03,
    ),
    "comercial": VoicePreset(
        id="comercial",
        label="Comercial",
        description="Energia controlada e chamada clara para ação.",
        model_id="eleven_multilingual_v2",
        stability=0.36,
        similarity_boost=0.82,
        style=0.42,
        speed=1.05,
    ),
    "institucional": VoicePreset(
        id="institucional",
        label="Institucional",
        description="Seguro e profissional sem ficar pesado.",
        model_id="eleven_multilingual_v2",
        stability=0.56,
        similarity_boost=0.80,
        style=0.18,
        speed=1.01,
    ),
    "urgente": VoicePreset(
        id="urgente",
        label="Urgente",
        description="Direto e ágil, sem gritar.",
        model_id="eleven_multilingual_v2",
        stability=0.31,
        similarity_boost=0.78,
        style=0.48,
        speed=1.08,
    ),
    "rapido": VoicePreset(
        id="rapido",
        label="Teste rápido",
        description="Menor latência para aprovar texto e pronúncia.",
        model_id="eleven_flash_v2_5",
        stability=0.44,
        similarity_boost=0.76,
        style=0.18,
        speed=1.04,
    ),
}


def get_preset(preset_id: str) -> VoicePreset:
    try:
        return PRESETS[preset_id]
    except KeyError as exc:
        raise ValueError(f"Preset desconhecido: {preset_id}") from exc

