from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import httpx

from braga_voice.presets import VoicePreset


class ProviderError(RuntimeError):
    """Erro seguro do provedor, sem expor chave ou corpo sensivel."""


@dataclass(frozen=True)
class Voice:
    id: str
    name: str
    category: str | None
    labels: dict[str, str]


class ElevenLabsProvider:
    BASE_URL = "https://api.elevenlabs.io"

    def __init__(self, api_key: str, timeout: float = 90.0) -> None:
        if not api_key.strip():
            raise ValueError("Chave da ElevenLabs nao configurada")
        self._headers = {"xi-api-key": api_key.strip()}
        self._timeout = timeout

    async def list_voices(self) -> list[Voice]:
        params = {"page_size": 100, "include_total_count": "false"}
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(
                f"{self.BASE_URL}/v2/voices",
                headers=self._headers,
                params=params,
            )
        self._raise_for_status(response)
        payload = response.json()
        return [
            Voice(
                id=item["voice_id"],
                name=item.get("name") or "Voz sem nome",
                category=item.get("category"),
                labels=item.get("labels") or {},
            )
            for item in payload.get("voices", [])
        ]

    async def synthesize(
        self,
        *,
        text: str,
        voice_id: str,
        preset: VoicePreset,
        output_format: str,
    ) -> bytes:
        voice_path = quote(voice_id, safe="")
        url = f"{self.BASE_URL}/v1/text-to-speech/{voice_path}"
        body: dict[str, Any] = {
            "text": text,
            "model_id": preset.model_id,
            "voice_settings": {
                "stability": preset.stability,
                "similarity_boost": preset.similarity_boost,
                "style": preset.style,
                "speed": preset.speed,
                "use_speaker_boost": preset.use_speaker_boost,
            },
        }
        headers = {**self._headers, "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                url,
                headers=headers,
                params={"output_format": output_format},
                json=body,
            )
        self._raise_for_status(response)
        return response.content

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        if response.is_success:
            return
        request_id = response.headers.get("request-id") or response.headers.get("x-request-id")
        detail = ""
        try:
            data = response.json()
            raw_detail = data.get("detail", data)
            if isinstance(raw_detail, dict):
                detail = str(raw_detail.get("message") or raw_detail.get("status") or "")
            elif isinstance(raw_detail, str):
                detail = raw_detail
        except ValueError:
            pass
        suffix = f" Request ID: {request_id}." if request_id else ""
        message = detail[:240] if detail else "Falha na requisicao ao provedor."
        raise ProviderError(f"ElevenLabs HTTP {response.status_code}: {message}.{suffix}")

