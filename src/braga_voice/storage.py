from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


_SAFE_SLUG = re.compile(r"[^a-z0-9-]+")


def slugify(value: str) -> str:
    slug = _SAFE_SLUG.sub("-", value.lower().strip().replace("_", "-")).strip("-")
    return slug or "geral"


@dataclass(frozen=True)
class StoredGeneration:
    id: str
    audio_path: Path
    metadata_path: Path


class GenerationStore:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.audio_dir = data_dir / "audio"
        self.history_dir = data_dir / "history"

    def save(
        self,
        *,
        audio: bytes,
        extension: str,
        project: str,
        metadata: dict[str, object],
    ) -> StoredGeneration:
        generation_id = uuid4().hex
        project_slug = slugify(project)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        audio_folder = self.audio_dir / project_slug
        audio_folder.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)

        audio_path = audio_folder / f"{timestamp}-{generation_id}.{extension}"
        metadata_path = self.history_dir / f"{generation_id}.json"

        temporary_audio = audio_path.with_suffix(audio_path.suffix + ".tmp")
        temporary_audio.write_bytes(audio)
        temporary_audio.replace(audio_path)

        record = {
            **metadata,
            "id": generation_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "audio_path": str(audio_path),
        }
        temporary_metadata = metadata_path.with_suffix(".json.tmp")
        temporary_metadata.write_text(
            json.dumps(record, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary_metadata.replace(metadata_path)
        return StoredGeneration(generation_id, audio_path, metadata_path)

    def audio_for(self, generation_id: str) -> Path:
        if not re.fullmatch(r"[0-9a-f]{32}", generation_id):
            raise FileNotFoundError(generation_id)
        metadata_path = self.history_dir / f"{generation_id}.json"
        if not metadata_path.exists():
            raise FileNotFoundError(generation_id)
        record = json.loads(metadata_path.read_text(encoding="utf-8"))
        audio_path = Path(record["audio_path"])
        if not audio_path.exists():
            raise FileNotFoundError(generation_id)
        return audio_path

