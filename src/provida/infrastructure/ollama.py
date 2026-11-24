"""Loopback-only Ollama chat adapter."""

import json
from urllib.error import URLError
from urllib.request import Request, urlopen


class OllamaClient:
    def __init__(self, config):
        self.config = config

    @property
    def enabled(self):
        return bool(
            self.config.ollama_enabled
            and self.config.ollama_endpoint == "http://127.0.0.1:11434"
        )

    def chat(self, message, history):
        messages = [
            {
                "role": "system",
                "content": (
                    "You are PROVIDA, a private local-first Windows desktop voice assistant. "
                    "Reply concisely in English. Never claim that you performed a tool action "
                    "unless the application reports it. Never provide or execute shell commands "
                    "as actions. Ask for confirmation before destructive or account-changing work."
                ),
            }
        ]
        messages.extend({"role": role, "content": text} for role, text in history)
        messages.append({"role": "user", "content": message})
        body = json.dumps(
            {
                "model": self.config.ollama_model,
                "messages": messages,
                "stream": False,
                "think": False,
            }
        ).encode()
        request = Request(
            self.config.ollama_endpoint + "/api/chat",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=120) as response:
                payload = json.load(response)
        except (OSError, URLError, ValueError) as exc:
            raise RuntimeError(
                "The local Ollama service is unavailable. Disable Ollama or start it locally."
            ) from exc
        text = payload.get("message", {}).get("content", "").strip()
        if not text:
            raise RuntimeError("The local Ollama model returned an empty response.")
        return text
