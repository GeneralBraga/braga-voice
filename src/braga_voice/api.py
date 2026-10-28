from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from braga_voice import __version__
from braga_voice.config import get_settings, save_local_provider_config
from braga_voice.presets import PRESETS, get_preset
from braga_voice.providers import ElevenLabsProvider, ProviderError
from braga_voice.sanitizer import prepare_for_speech
from braga_voice.storage import GenerationStore


PACKAGE_DIR = Path(__file__).resolve().parent
SOURCE_WEB_DIR = PACKAGE_DIR.parents[1] / "web"
WEB_DIR = SOURCE_WEB_DIR if SOURCE_WEB_DIR.exists() else PACKAGE_DIR / "web"

app = FastAPI(title="BRAGA VOICE", version=__version__)
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


class PreviewRequest(BaseModel):
    text: str = Field(min_length=1, max_length=40_000)
    preset: str = "natural"


class GenerateRequest(PreviewRequest):
    voice_id: str | None = None
    project: str = Field(default="geral", max_length=80)
    output_format: str = "mp3_44100_128"


class ProviderConfigRequest(BaseModel):
    api_key: str = Field(min_length=20, max_length=300)


@app.get("/", include_in_schema=False)
async def home() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> Response:
    return Response(status_code=204)


@app.get("/health")
async def health() -> dict[str, object]:
    settings = get_settings()
    return {
        "status": "ok",
        "version": __version__,
        "provider": "elevenlabs",
        "provider_ready": settings.elevenlabs_ready,
    }


@app.get("/api/config/status")
async def config_status() -> dict[str, object]:
    settings = get_settings()
    return {
        "provider": "elevenlabs",
        "ready": settings.elevenlabs_ready,
        "default_voice_configured": bool(settings.elevenlabs_voice_id),
        "data_dir": str(settings.data_dir),
    }


@app.post("/api/config")
async def configure_provider(request: ProviderConfigRequest) -> dict[str, object]:
    """Validate and store a user's own ElevenLabs key on this Mac only."""
    try:
        voices = await ElevenLabsProvider(request.api_key).list_voices()
        save_local_provider_config(request.api_key)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {
        "provider": "elevenlabs",
        "ready": True,
        "voices_available": len(voices),
    }


@app.get("/api/presets")
async def presets() -> list[dict[str, object]]:
    return [preset.public_dict() for preset in PRESETS.values()]


@app.post("/api/preview")
async def preview(request: PreviewRequest) -> dict[str, object]:
    try:
        preset = get_preset(request.preset)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    preparation = prepare_for_speech(request.text)
    clean_text = preparation.text
    if not clean_text:
        raise HTTPException(status_code=422, detail="O texto ficou vazio apos a limpeza.")
    return {
        "text": clean_text,
        "characters": len(clean_text),
        "removed_characters": len(request.text) - len(clean_text),
        "total_adjustments": preparation.total_adjustments,
        "adjustments": [
            adjustment.public_dict() for adjustment in preparation.adjustments
        ],
        "preset": preset.public_dict(),
    }


@app.get("/api/voices")
async def voices() -> list[dict[str, object]]:
    settings = get_settings()
    if not settings.elevenlabs_ready:
        raise HTTPException(status_code=503, detail="ElevenLabs ainda nao configurada.")
    try:
        items = await ElevenLabsProvider(settings.elevenlabs_api_key).list_voices()
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return [
        {
            "id": item.id,
            "name": item.name,
            "category": item.category,
            "labels": item.labels,
            "is_default": item.id == settings.elevenlabs_voice_id,
        }
        for item in items
    ]


@app.post("/api/generate")
async def generate(request: GenerateRequest) -> dict[str, object]:
    settings = get_settings()
    if not settings.elevenlabs_ready:
        raise HTTPException(status_code=503, detail="Configure a chave da ElevenLabs primeiro.")
    voice_id = request.voice_id or settings.elevenlabs_voice_id
    if not voice_id:
        raise HTTPException(status_code=422, detail="Selecione uma voz.")
    try:
        preset = get_preset(request.preset)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    preparation = prepare_for_speech(request.text)
    clean_text = preparation.text
    if not clean_text:
        raise HTTPException(status_code=422, detail="O texto ficou vazio apos a limpeza.")
    if request.output_format != "mp3_44100_128":
        raise HTTPException(status_code=422, detail="Formato ainda nao habilitado no MVP.")

    provider = ElevenLabsProvider(settings.elevenlabs_api_key)
    try:
        audio = await provider.synthesize(
            text=clean_text,
            voice_id=voice_id,
            preset=preset,
            output_format=request.output_format,
        )
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    store = GenerationStore(settings.data_dir)
    saved = store.save(
        audio=audio,
        extension="mp3",
        project=request.project,
        metadata={
            "provider": "elevenlabs",
            "voice_id": voice_id,
            "project": request.project,
            "preset": preset.id,
            "model_id": preset.model_id,
            "characters": len(clean_text),
            "text": clean_text,
            "speech_adjustments": [
                adjustment.public_dict()
                for adjustment in preparation.adjustments
            ],
        },
    )
    return {
        "id": saved.id,
        "characters": len(clean_text),
        "model_id": preset.model_id,
        "filename": saved.audio_path.name,
        "audio_url": f"/api/audio/{saved.id}",
        "download_url": f"/api/audio/{saved.id}/download",
    }


@app.get("/api/audio/{generation_id}")
async def audio(generation_id: str) -> FileResponse:
    store = GenerationStore(get_settings().data_dir)
    try:
        audio_path = store.audio_for(generation_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Audio nao encontrado.") from exc
    return FileResponse(
        audio_path,
        media_type="audio/mpeg",
        filename=audio_path.name,
        content_disposition_type="inline",
    )


@app.get("/api/audio/{generation_id}/download")
async def download_audio(generation_id: str) -> FileResponse:
    store = GenerationStore(get_settings().data_dir)
    try:
        audio_path = store.audio_for(generation_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Audio nao encontrado.") from exc
    return FileResponse(
        audio_path,
        media_type="audio/mpeg",
        filename=audio_path.name,
        content_disposition_type="attachment",
    )

