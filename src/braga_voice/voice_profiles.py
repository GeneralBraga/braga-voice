from __future__ import annotations

import base64
import binascii
import json
import shutil
import subprocess
import wave
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable
from uuid import uuid4

from braga_voice.storage import slugify


MIN_REFERENCE_SECONDS = 30.0
MAX_REFERENCE_SECONDS = 180.0
MAX_RECORDING_BYTES = 30 * 1024 * 1024
ALLOWED_MIME_TYPES = {
    "audio/mp4": ".m4a",
    "audio/mpeg": ".mp3",
    "audio/ogg": ".ogg",
    "audio/wav": ".wav",
    "audio/webm": ".webm",
}


class VoiceProfileError(ValueError):
    """A safe validation error for locally recorded voice profiles."""


@dataclass(frozen=True)
class CreatedVoiceProfile:
    id: str
    name: str
    style: str
    duration_seconds: float


Converter = Callable[[Path, Path], None]


class VoiceProfileStore:
    def __init__(self, data_dir: Path, converter: Converter | None = None) -> None:
        self.voices_dir = data_dir / "voices"
        self.converter = converter or self._convert_audio

    def create(
        self,
        *,
        name: str,
        style: str,
        transcript: str,
        audio_base64: str,
        mime_type: str,
        owner_authorized: bool,
    ) -> CreatedVoiceProfile:
        clean_name = " ".join(name.split()).strip()
        clean_transcript = " ".join(transcript.split()).strip()
        clean_style = slugify(style)
        if not owner_authorized:
            raise VoiceProfileError("Confirme que a voz e sua ou que possui autorizacao.")
        if len(clean_name) < 2 or len(clean_name) > 80:
            raise VoiceProfileError("Informe um nome de voz entre 2 e 80 caracteres.")
        if len(clean_transcript) < 120 or len(clean_transcript) > 2_500:
            raise VoiceProfileError("Use o texto sugerido completo durante a gravacao.")
        if clean_style not in {"natural", "comercial", "institucional", "entusiasmado"}:
            raise VoiceProfileError("Perfil de interpretacao desconhecido.")
        suffix = ALLOWED_MIME_TYPES.get(mime_type.split(";", 1)[0].lower())
        if suffix is None:
            raise VoiceProfileError("Formato de gravacao nao suportado neste Mac.")
        try:
            audio = base64.b64decode(audio_base64, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise VoiceProfileError("A gravacao recebida esta corrompida.") from exc
        if not audio or len(audio) > MAX_RECORDING_BYTES:
            raise VoiceProfileError("A gravacao deve ter no maximo 30 MB.")

        self.voices_dir.mkdir(parents=True, exist_ok=True)
        self.voices_dir.chmod(0o700)
        profile_id = f"{slugify(clean_name)}-{clean_style}-{uuid4().hex[:6]}"
        final_dir = self.voices_dir / profile_id

        with TemporaryDirectory(prefix="braga-voice-") as temporary:
            temporary_dir = Path(temporary)
            source = temporary_dir / f"recording{suffix}"
            reference = temporary_dir / "reference.wav"
            source.write_bytes(audio)
            self.converter(source, reference)
            duration = self._wav_duration(reference)
            if duration < MIN_REFERENCE_SECONDS:
                raise VoiceProfileError("Grave pelo menos 30 segundos completos.")
            if duration > MAX_REFERENCE_SECONDS:
                raise VoiceProfileError("A gravacao deve ter no maximo 3 minutos.")

            staging = self.voices_dir / f".{profile_id}.tmp"
            staging.mkdir(mode=0o700)
            try:
                shutil.copy2(reference, staging / "reference.wav")
                (staging / "transcript.txt").write_text(
                    clean_transcript + "\n", encoding="utf-8"
                )
                created_at = datetime.now(timezone.utc).isoformat()
                self._write_json(
                    staging / "profile.json",
                    {
                        "id": profile_id,
                        "name": clean_name,
                        "style": clean_style,
                        "language": "pt-BR",
                        "source": "microphone-recording",
                        "duration_seconds": round(duration, 2),
                        "reference_audio": "reference.wav",
                        "reference_transcript": "transcript.txt",
                        "created_at": created_at,
                    },
                )
                self._write_json(
                    staging / "consent.json",
                    {
                        "status": "owner-declared-authorized",
                        "captured_at": created_at,
                        "purpose": "local-qwen-reference-voice",
                    },
                )
                for child in staging.iterdir():
                    child.chmod(0o600)
                staging.replace(final_dir)
            except Exception:
                shutil.rmtree(staging, ignore_errors=True)
                raise

        return CreatedVoiceProfile(profile_id, clean_name, clean_style, round(duration, 2))

    @staticmethod
    def _write_json(path: Path, value: dict[str, object]) -> None:
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def _wav_duration(path: Path) -> float:
        try:
            with wave.open(str(path), "rb") as recording:
                return recording.getnframes() / float(recording.getframerate())
        except (wave.Error, OSError, ZeroDivisionError) as exc:
            raise VoiceProfileError("Nao foi possivel validar a duracao da gravacao.") from exc

    @staticmethod
    def _convert_audio(source: Path, destination: Path) -> None:
        ffmpeg = shutil.which("ffmpeg")
        if ffmpeg:
            command = [
                ffmpeg,
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(source),
                "-ac",
                "1",
                "-ar",
                "24000",
                "-c:a",
                "pcm_s16le",
                str(destination),
            ]
        elif Path("/usr/bin/afconvert").is_file():
            command = [
                "/usr/bin/afconvert",
                "-f",
                "WAVE",
                "-d",
                "LEI16@24000",
                "-c",
                "1",
                str(source),
                str(destination),
            ]
        else:
            raise VoiceProfileError("Conversor de audio indisponivel neste computador.")
        try:
            subprocess.run(command, check=True, capture_output=True, timeout=90)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            raise VoiceProfileError("Nao foi possivel preparar esta gravacao.") from exc
        if not destination.is_file() or destination.stat().st_size == 0:
            raise VoiceProfileError("A conversao da gravacao nao produziu audio valido.")
