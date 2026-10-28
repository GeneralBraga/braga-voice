from fastapi.testclient import TestClient

import braga_voice.api as api_module
from braga_voice.providers.elevenlabs import Voice


def test_config_endpoint_validates_without_echoing_key(monkeypatch, tmp_path) -> None:
    key = "sk_" + "abcdefghijklmnopqrstuvwxyz"
    saved: dict[str, str] = {}

    async def fake_list_voices(_provider) -> list[Voice]:
        return [Voice(id="voice_example", name="Minha voz", category="cloned", labels={})]

    def fake_save(api_key: str) -> None:
        saved["key"] = api_key

    monkeypatch.setattr(api_module.ElevenLabsProvider, "list_voices", fake_list_voices)
    monkeypatch.setattr(api_module, "save_local_provider_config", fake_save)

    response = TestClient(api_module.app).post("/api/config", json={"api_key": key})

    assert response.status_code == 200
    assert response.json() == {
        "provider": "elevenlabs",
        "ready": True,
        "voices_available": 1,
    }
    assert key not in response.text
    assert saved["key"] == key
