from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf
from mlx_audio.tts.utils import load_model


def main() -> None:
    payload = json.loads(sys.stdin.read())
    model_path = Path(payload["model_path"])
    reference_audio = Path(payload["reference_audio"])
    transcript_path = Path(payload["transcript_path"])
    output_path = Path(payload["output_path"])
    text = str(payload["text"]).strip()
    if not text:
        raise ValueError("empty synthesis text")
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required for MP3 output")

    reference_text = transcript_path.read_text(encoding="utf-8").strip()
    started = time.perf_counter()
    model = load_model(str(model_path))
    loaded = time.perf_counter()
    results = list(
        model.generate(
            text=text,
            ref_audio=str(reference_audio),
            ref_text=reference_text,
            lang_code="portuguese",
            temperature=0.7,
            top_p=0.8,
            repetition_penalty=1.05,
            verbose=False,
        )
    )
    generated = time.perf_counter()
    chunks = [np.asarray(item.audio).reshape(-1) for item in results if item.audio.size > 0]
    if not chunks:
        raise RuntimeError("Qwen returned no audio")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_wav = output_path.with_suffix(".wav")
    sf.write(temporary_wav, np.concatenate(chunks), model.sample_rate, subtype="PCM_16")
    subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(temporary_wav),
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-ac",
            "1",
            "-ar",
            "44100",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "128k",
            str(output_path),
        ],
        check=True,
    )
    temporary_wav.unlink(missing_ok=True)
    print(
        json.dumps(
            {
                "load_seconds": round(loaded - started, 2),
                "generation_seconds": round(generated - loaded, 2),
                "format": "mp3_44100_128",
            }
        )
    )


if __name__ == "__main__":
    main()
