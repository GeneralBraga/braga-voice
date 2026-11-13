from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient

import braga_voice.api as api_module
from braga_voice.providers.qwen_local import QwenLocalProvider


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
