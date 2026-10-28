from fastapi.testclient import TestClient

import braga_voice.api as api_module
from braga_voice.config import Settings
from braga_voice.storage import GenerationStore


def test_preview_reports_narration_adjustments() -> None:
    client = TestClient(api_module.app)

    response = client.post(
        "/api/preview",
        json={"text": "Teste local", "preset": "natural"},
    )

    assert response.status_code == 200
    assert response.json()["text"] == "Teste local."
    assert response.json()["total_adjustments"] == 1
    assert response.json()["adjustments"][0]["code"] == "punctuation"


def test_player_is_inline_and_download_is_attachment(monkeypatch, tmp_path) -> None:
    settings = Settings(
        elevenlabs_api_key="",
        elevenlabs_voice_id=None,
        data_dir=tmp_path,
        host="127.0.0.1",
        port=8765,
    )
    monkeypatch.setattr(api_module, "get_settings", lambda: settings)
    saved = GenerationStore(tmp_path).save(
        audio=b"fake-mp3",
        extension="mp3",
        project="teste",
        metadata={"text": "Teste."},
    )
    client = TestClient(api_module.app)

    player = client.get(f"/api/audio/{saved.id}")
    download = client.get(f"/api/audio/{saved.id}/download")

    assert player.status_code == 200
    assert player.headers["content-disposition"].startswith("inline;")
    assert download.status_code == 200
    assert download.headers["content-disposition"].startswith("attachment;")
    assert download.content == b"fake-mp3"
