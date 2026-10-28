from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_SUPPORT_DIR = Path.home() / "Library" / "Application Support" / "BRAGA VOICE"
LOCAL_ENV_PATH = APP_SUPPORT_DIR / ".env"
_VOICE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{4,128}$")


def _load_local_environment() -> None:
    configured_path = os.getenv("BRAGA_VOICE_ENV_FILE", "").strip()
    candidates = [
        Path(configured_path).expanduser() if configured_path else None,
        LOCAL_ENV_PATH,
        PROJECT_ROOT / ".env",
    ]
    for candidate in candidates:
        if candidate and candidate.is_file():
            load_dotenv(candidate, override=False)
            return


_load_local_environment()


@dataclass(frozen=True)
class Settings:
    elevenlabs_api_key: str
    elevenlabs_voice_id: str | None
    data_dir: Path
    host: str
    port: int

    @property
    def elevenlabs_ready(self) -> bool:
        return bool(self.elevenlabs_api_key.strip())


def get_settings() -> Settings:
    default_data = APP_SUPPORT_DIR
    return Settings(
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY", "").strip(),
        elevenlabs_voice_id=os.getenv("ELEVENLABS_VOICE_ID", "").strip() or None,
        data_dir=Path(os.getenv("BRAGA_VOICE_DATA_DIR", str(default_data))).expanduser(),
        host=os.getenv("BRAGA_VOICE_HOST", "127.0.0.1"),
        port=int(os.getenv("BRAGA_VOICE_PORT", "8765")),
    )


def save_local_provider_config(
    api_key: str,
    voice_id: str | None = None,
    *,
    env_path: Path = LOCAL_ENV_PATH,
) -> Path:
    """Persist provider credentials locally without returning or logging them."""
    normalized_key = api_key.strip()
    if not normalized_key.startswith("sk_") or len(normalized_key) < 20:
        raise ValueError("A chave ElevenLabs informada nao parece valida.")
    if any(character in normalized_key for character in "\r\n"):
        raise ValueError("A chave ElevenLabs deve ocupar uma unica linha.")

    normalized_voice = (voice_id or "").strip()
    if normalized_voice and not _VOICE_ID_PATTERN.fullmatch(normalized_voice):
        raise ValueError("O identificador da voz nao parece valido.")

    env_path.parent.mkdir(parents=True, exist_ok=True)
    existing = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    updates = {
        "ELEVENLABS_API_KEY": normalized_key,
        "ELEVENLABS_VOICE_ID": normalized_voice,
    }
    output: list[str] = []
    replaced: set[str] = set()
    for line in existing:
        name, separator, _ = line.partition("=")
        if separator and name in updates:
            output.append(f"{name}={updates[name]}")
            replaced.add(name)
        else:
            output.append(line)
    for name, value in updates.items():
        if name not in replaced:
            output.append(f"{name}={value}")

    temporary = env_path.with_name(f"{env_path.name}.tmp")
    temporary.write_text("\n".join(output).rstrip() + "\n", encoding="utf-8")
    os.chmod(temporary, 0o600)
    temporary.replace(env_path)
    os.chmod(env_path, 0o600)
    os.environ.update(updates)
    return env_path

