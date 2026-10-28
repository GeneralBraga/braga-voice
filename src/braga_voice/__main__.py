from __future__ import annotations

import uvicorn

from braga_voice.api import app
from braga_voice.config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(app, host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()

