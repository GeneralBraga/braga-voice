from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient

import braga_voice.api as api_module
from braga_voice.config import Settings
from braga_voice.providers.qwen_local import LocalSynthesis, QwenLocalProvider


def test_qwen_local_is_not_ready_without_private_runtime(tmp_path: Path) -> None:
    provider = QwenLocalProvider(tmp_path)

    assert provider.runtime_ready is False
    assert provider.model_ready is False
    assert provider.ready is False
    assert provider.public_status()["uses_credits"] is False


def test_qwen_local_detects_runtime_and_complete_model(tmp_path: Path) -> None:
    provider = QwenLocalProvider(tmp_path)
    provider.paths.python.parent.mkdir(parents=True)
    provider.paths.python.write_text("python", encoding="utf-8")
    (provider.paths.model / "speech_tokenizer").mkdir(parents=True)
    for path in (
        provider.paths.model / "config.json",
        provider.paths.model / "model.safetensors",
        provider.paths.model / "speech_tokenizer" / "config.json",
    ):
        path.write_text("ready", encoding="utf-8")

    assert provider.runtime_ready is True
    assert provider.model_ready is True
    assert provider.ready is True


def test_qwen_local_lists_only_authorized_private_profiles(tmp_path: Path) -> None:
    provider = QwenLocalProvider(tmp_path)
    voice_dir = provider.paths.voices / "minha-voz"
    voice_dir.mkdir(parents=True)
    (voice_dir / "reference.wav").write_bytes(b"wav")
    (voice_dir / "transcript.txt").write_text("Minha referencia.", encoding="utf-8")
    (voice_dir / "profile.json").write_text(
        '{"id":"minha-voz","name":"Minha voz","language":"pt-BR",'
        '"reference_audio":"reference.wav","reference_transcript":"transcript.txt"}',
        encoding="utf-8",
    )
    (voice_dir / "consent.json").write_text(
        '{"status":"owner-declared-authorized"}',
        encoding="utf-8",
    )

    voices = provider.list_voices()

    assert [(voice.id, voice.name) for voice in voices] == [("minha-voz", "Minha voz")]


def test_engines_endpoint_does_not_require_or_return_elevenlabs_key(
    monkeypatch, tmp_path: Path
) -> None:
    settings = SimpleNamespace(
        data_dir=tmp_path,
        elevenlabs_ready=False,
    )
    monkeypatch.setattr(api_module, "get_settings", lambda: settings)

    response = TestClient(api_module.app).get("/api/engines")

    assert response.status_code == 200
    engines = response.json()
    assert engines[0]["id"] == "qwen-local"
    assert engines[0]["uses_credits"] is False
    assert engines[1]["id"] == "elevenlabs-cloud"
    assert "key" not in response.text.lower()


def test_generate_with_qwen_local_never_requires_elevenlabs(
    monkeypatch, tmp_path: Path
) -> None:
    settings = Settings(
        elevenlabs_api_key="",
        elevenlabs_voice_id=None,
        data_dir=tmp_path,
        host="127.0.0.1",
        port=8765,
    )

    async def fake_synthesize(_provider, *, text: str, voice_id: str) -> LocalSynthesis:
        assert text == "Teste totalmente local."
        assert voice_id == "minha-voz"
        return LocalSynthesis(b"local-mp3", "qwen-test", 1.25)

    monkeypatch.setattr(api_module, "get_settings", lambda: settings)
    monkeypatch.setattr(QwenLocalProvider, "synthesize", fake_synthesize)

    response = TestClient(api_module.app).post(
        "/api/generate",
        json={
            "engine": "qwen-local",
            "voice_id": "minha-voz",
            "text": "Teste totalmente local",
            "preset": "natural",
            "project": "teste",
            "output_format": "mp3_44100_128",
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["engine"] == "qwen-local"
    assert result["provider"] == "qwen-local"
    assert result["uses_credits"] is False
    assert result["model_id"] == "qwen-test"
