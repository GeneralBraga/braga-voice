from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


MODEL_ID = "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit"
ENGINE_ID = "qwen-local"


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
