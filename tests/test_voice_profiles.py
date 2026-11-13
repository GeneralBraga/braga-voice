import base64
import json
import wave
from pathlib import Path

import pytest

from braga_voice.voice_profiles import VoiceProfileError, VoiceProfileStore


TRANSCRIPT = (
    "Esta e uma leitura completa para registrar uma identidade vocal com clareza, "
    "ritmo e naturalidade. A gravacao preserva a intencao escolhida e permanece "
    "somente neste computador, protegida para uso local autorizado."
)


def write_reference(path: Path, seconds: int) -> None:
    with wave.open(str(path), "wb") as recording:
        recording.setnchannels(1)
        recording.setsampwidth(2)
        recording.setframerate(8_000)
        recording.writeframes(b"\0\0" * 8_000 * seconds)


def test_create_authorized_local_voice_profile(tmp_path: Path) -> None:
    def converter(_source: Path, destination: Path) -> None:
        write_reference(destination, 31)

    store = VoiceProfileStore(tmp_path, converter=converter)
    result = store.create(
        name="Minha Voz",
        style="comercial",
        transcript=TRANSCRIPT,
        audio_base64=base64.b64encode(b"recording").decode(),
        mime_type="audio/mp4",
        owner_authorized=True,
    )

    profile_dir = tmp_path / "voices" / result.id
    profile = json.loads((profile_dir / "profile.json").read_text(encoding="utf-8"))
    consent = json.loads((profile_dir / "consent.json").read_text(encoding="utf-8"))
    assert result.duration_seconds == 31
    assert profile["style"] == "comercial"
    assert profile["source"] == "microphone-recording"
    assert consent["status"] == "owner-declared-authorized"
    assert (profile_dir / "reference.wav").is_file()
    assert not any(path.name.startswith(".minha-voz") for path in (tmp_path / "voices").iterdir())


def test_rejects_recording_shorter_than_thirty_seconds(tmp_path: Path) -> None:
    def converter(_source: Path, destination: Path) -> None:
        write_reference(destination, 29)

    store = VoiceProfileStore(tmp_path, converter=converter)
    with pytest.raises(VoiceProfileError, match="30 segundos"):
        store.create(
            name="Minha Voz",
            style="natural",
            transcript=TRANSCRIPT,
            audio_base64=base64.b64encode(b"recording").decode(),
            mime_type="audio/mp4",
            owner_authorized=True,
        )


def test_requires_owner_authorization(tmp_path: Path) -> None:
    store = VoiceProfileStore(tmp_path, converter=lambda _source, _destination: None)
    with pytest.raises(VoiceProfileError, match="autorizacao"):
        store.create(
            name="Minha Voz",
            style="natural",
            transcript=TRANSCRIPT,
            audio_base64=base64.b64encode(b"recording").decode(),
            mime_type="audio/mp4",
            owner_authorized=False,
        )
