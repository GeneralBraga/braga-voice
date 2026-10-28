#!/usr/bin/env python3
"""Cliente sem dependências para a API local do BRAGA VOICE."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def request_json(base: str, path: str, payload: dict[str, object] | None = None) -> object:
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        urllib.parse.urljoin(base.rstrip("/") + "/", path.lstrip("/")),
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
        method="POST" if data else "GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        try:
            detail = json.load(exc).get("detail", str(exc))
        except Exception:
            detail = str(exc)
        raise SystemExit(f"BRAGA VOICE: {detail}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit("BRAGA VOICE não está disponível em 127.0.0.1:8765.") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8765")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("health")
    subparsers.add_parser("voices")

    preview = subparsers.add_parser("preview")
    preview.add_argument("--text", required=True)
    preview.add_argument("--preset", default="natural")

    generate = subparsers.add_parser("generate")
    generate.add_argument("--text", required=True)
    generate.add_argument("--voice-id", required=True)
    generate.add_argument("--preset", default="natural")
    generate.add_argument("--project", default="geral")
    generate.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    parsed = urllib.parse.urlparse(args.base_url)
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit("Por segurança, o cliente aceita somente uma API local.")

    if args.command == "health":
        result = request_json(args.base_url, "/health")
    elif args.command == "voices":
        result = request_json(args.base_url, "/api/voices")
    elif args.command == "preview":
        result = request_json(args.base_url, "/api/preview", {"text": args.text, "preset": args.preset})
    else:
        result = request_json(
            args.base_url,
            "/api/generate",
            {"text": args.text, "voice_id": args.voice_id, "preset": args.preset, "project": args.project},
        )
        download_url = result["download_url"]
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(urllib.parse.urljoin(args.base_url, download_url), timeout=120) as response:
            args.output.write_bytes(response.read())
        result = {**result, "saved_to": str(args.output.resolve())}

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
