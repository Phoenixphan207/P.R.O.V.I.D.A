"""Safe local JSON settings; no credentials are stored."""

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path


def data_dir() -> Path:
    return Path(os.environ.get("PROVIDA_DATA_DIR", Path.home() / "AppData" / "Local" / "PROVIDA"))


@dataclass
class AppConfig:
    ollama_enabled: bool = False
    ollama_endpoint: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen2.5:3b"
    memory_enabled: bool = True


class ConfigStore:
    def __init__(self, path=None):
        self.path = Path(path) if path else data_dir() / "settings.json"

    def load(self) -> AppConfig:
        try:
            values = json.loads(self.path.read_text(encoding="utf-8"))
            allowed = {key: values[key] for key in asdict(AppConfig()) if key in values}
            config = AppConfig(**allowed)
            if config.ollama_endpoint != "http://127.0.0.1:11434":
                config.ollama_enabled = False
            return config
        except (FileNotFoundError, ValueError, TypeError, json.JSONDecodeError):
            return AppConfig()

    def save(self, config: AppConfig):
        if config.ollama_endpoint != "http://127.0.0.1:11434":
            raise ValueError("Phase 2 only permits the local Ollama endpoint.")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(asdict(config), indent=2), encoding="utf-8")
