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
    supports_style: bool = True
    supports_speaker_boost: bool = True
    supports_speed: bool = True

    def public_dict(self) -> dict[str, object]:
        return asdict(self)


PRESETS: dict[str, VoicePreset] = {
    "natural": VoicePreset(
        id="natural",
        label="Natural",
        description="Próximo, leve e conversado.",
        model_id="eleven_v4",
        stability=0.50,
        similarity_boost=0.75,
        style=0.0,
        speed=1.0,
        use_speaker_boost=False,
        supports_style=False,
        supports_speaker_boost=False,
        supports_speed=False,
    ),
    "comercial": VoicePreset(
        id="comercial",
        label="Comercial",
        description="Energia controlada e chamada clara para ação.",
        model_id="eleven_v4",
        stability=0.46,
        similarity_boost=0.77,
        style=0.0,
        speed=1.0,
        use_speaker_boost=False,
        supports_style=False,
        supports_speaker_boost=False,
        supports_speed=False,
    ),
    "institucional": VoicePreset(
        id="institucional",
        label="Institucional",
        description="Seguro e profissional sem ficar pesado.",
        model_id="eleven_v4",
        stability=0.55,
        similarity_boost=0.78,
        style=0.0,
        speed=1.0,
        use_speaker_boost=False,
        supports_style=False,
        supports_speaker_boost=False,
        supports_speed=False,
    ),
    "urgente": VoicePreset(
        id="urgente",
        label="Urgente",
        description="Direto e ágil, sem gritar.",
        model_id="eleven_v4_turbo",
        stability=0.44,
        similarity_boost=0.75,
        style=0.0,
        speed=1.0,
        use_speaker_boost=False,
        supports_style=False,
        supports_speaker_boost=False,
        supports_speed=False,
    ),
    "rapido": VoicePreset(
        id="rapido",
        label="Teste rápido",
        description="Menor latência para aprovar texto e pronúncia.",
        model_id="eleven_flash_v2_5",
        stability=0.50,
        similarity_boost=0.75,
        style=0.0,
        speed=1.0,
        use_speaker_boost=False,
    ),
}


def get_preset(preset_id: str) -> VoicePreset:
    try:
        return PRESETS[preset_id]
    except KeyError as exc:
        raise ValueError(f"Preset desconhecido: {preset_id}") from exc

