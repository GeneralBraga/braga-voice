from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4


MODEL_ID = "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit"
ENGINE_ID = "qwen-local"
_GENERATION_LOCK = asyncio.Lock()


class LocalProviderError(RuntimeError):
    """Safe local-engine error that does not expose private paths or text."""


@dataclass(frozen=True)
class LocalVoice:
    id: str
    name: str
    language: str
    reference_audio: Path
    transcript_path: Path


@dataclass(frozen=True)
class LocalSynthesis:
    audio: bytes
    model_id: str
    generation_seconds: float | None


@dataclass(frozen=True)
class LocalEnginePaths:
    root: Path
    python: Path
    model: Path
    voices: Path

    @classmethod
    def under(cls, data_dir: Path) -> "LocalEnginePaths":
        return cls(
            root=data_dir / "local-engine",
            python=data_dir / "local-engine" / ".venv" / "bin" / "python",
            model=data_dir / "models" / "qwen3-tts-1.7b-base-8bit",
            voices=data_dir / "voices",
        )


class QwenLocalProvider:
    """Detect the private MLX runtime without importing it into the web process."""

    def __init__(self, data_dir: Path) -> None:
        self.paths = LocalEnginePaths.under(data_dir)

    @property
    def runtime_ready(self) -> bool:
        return self.paths.python.is_file()

    @property
    def model_ready(self) -> bool:
        required = (
            self.paths.model / "config.json",
            self.paths.model / "model.safetensors",
            self.paths.model / "speech_tokenizer" / "config.json",
        )
        return all(path.is_file() and path.stat().st_size > 0 for path in required)

    @property
    def ready(self) -> bool:
        return self.runtime_ready and self.model_ready

    def public_status(self) -> dict[str, object]:
        return {
            "id": ENGINE_ID,
            "name": "Qwen3-TTS local",
            "provider": "local",
            "model_id": MODEL_ID,
            "runtime_ready": self.runtime_ready,
            "model_ready": self.model_ready,
            "ready": self.ready,
            "uses_credits": False,
            "requires_internet_after_install": False,
        }

    def list_voices(self) -> list[LocalVoice]:
        if not self.paths.voices.is_dir():
            return []
        voices: list[LocalVoice] = []
        for folder in sorted(self.paths.voices.iterdir()):
            if not folder.is_dir():
                continue
            try:
                profile = json.loads((folder / "profile.json").read_text(encoding="utf-8"))
                consent = json.loads((folder / "consent.json").read_text(encoding="utf-8"))
                reference = self._private_child(folder, profile["reference_audio"])
                transcript = self._private_child(folder, profile["reference_transcript"])
                voice_id = str(profile["id"])
                name = str(profile["name"])
                language = str(profile.get("language") or "pt-BR")
                consent_status = str(consent.get("status") or "")
            except (FileNotFoundError, KeyError, TypeError, ValueError, json.JSONDecodeError):
                continue
            if voice_id != folder.name or not consent_status.endswith("authorized"):
                continue
            if not reference.is_file() or not transcript.is_file():
                continue
            if not transcript.read_text(encoding="utf-8").strip():
                continue
            voices.append(LocalVoice(voice_id, name, language, reference, transcript))
        return voices

    async def synthesize(self, *, text: str, voice_id: str) -> LocalSynthesis:
        if not self.ready:
            raise LocalProviderError("O motor Qwen local ainda nao esta pronto.")
        voice = next((item for item in self.list_voices() if item.id == voice_id), None)
        if voice is None:
            raise LocalProviderError("A identidade vocal local nao foi encontrada.")

        temporary_dir = self.paths.root / "tmp"
        temporary_dir.mkdir(parents=True, exist_ok=True)
        temporary_dir.chmod(0o700)
        output_path = temporary_dir / f"{uuid4().hex}.mp3"
        worker_path = Path(__file__).resolve().parents[1] / "local_worker.py"
        payload = {
            "model_path": str(self.paths.model),
            "reference_audio": str(voice.reference_audio),
            "transcript_path": str(voice.transcript_path),
            "text": text,
            "output_path": str(output_path),
        }

        async with _GENERATION_LOCK:
            process = await asyncio.create_subprocess_exec(
                str(self.paths.python),
                str(worker_path),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, _stderr = await asyncio.wait_for(
                    process.communicate(json.dumps(payload).encode("utf-8")),
                    timeout=360,
                )
            except TimeoutError as exc:
                process.kill()
                await process.wait()
                raise LocalProviderError("A sintese local excedeu o tempo limite.") from exc

        if process.returncode != 0 or not output_path.is_file():
            raise LocalProviderError("O motor Qwen local nao conseguiu gerar o audio.")
        try:
            result = json.loads(stdout.decode("utf-8").strip().splitlines()[-1])
            generation_seconds = float(result["generation_seconds"])
        except (IndexError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            generation_seconds = None
        audio = output_path.read_bytes()
        output_path.unlink(missing_ok=True)
        return LocalSynthesis(audio, MODEL_ID, generation_seconds)

    @staticmethod
    def _private_child(folder: Path, relative_name: object) -> Path:
        if not isinstance(relative_name, str) or not relative_name.strip():
            raise ValueError("invalid private filename")
        root = folder.resolve()
        child = (root / relative_name).resolve()
        if not child.is_relative_to(root):
            raise ValueError("private filename escaped profile")
        return child
