import json

import pytest

from braga_voice.storage import GenerationStore, slugify


def test_slugify_project_name() -> None:
    assert slugify("Projeto Exemplo 2026") == "projeto-exemplo-2026"


def test_store_keeps_audio_and_metadata_outside_repo(tmp_path) -> None:
    store = GenerationStore(tmp_path)
    result = store.save(
        audio=b"fake-mp3",
        extension="mp3",
        project="Projeto Exemplo",
        metadata={"provider": "elevenlabs", "text": "Teste autorizado."},
    )
    assert result.audio_path.read_bytes() == b"fake-mp3"
    record = json.loads(result.metadata_path.read_text(encoding="utf-8"))
    assert record["provider"] == "elevenlabs"
    assert store.audio_for(result.id) == result.audio_path


def test_store_rejects_invalid_generation_id(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        GenerationStore(tmp_path).audio_for("../../segredo")
