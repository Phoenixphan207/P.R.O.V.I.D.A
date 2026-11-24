"""Structured local logging without audio or secret contents."""

import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path


class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps(
            {
                "time": datetime.now(UTC).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }
        )


def configure_logging():
    data_dir = Path(
        os.environ.get("PROVIDA_DATA_DIR", Path.home() / "AppData" / "Local" / "PROVIDA")
    )
    data_dir.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(data_dir / "provida.log", encoding="utf-8")
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    return data_dir
