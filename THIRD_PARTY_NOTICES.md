# Third-party notices and design references

PROVIDA Phase 2 does not copy source code or assets from the reference assistants. The implementation uses native Python/Qt modules and the dependencies listed in `pyproject.toml`.

Architectural ideas reviewed:

- **Ari VoiceCommand** (MIT): provider abstraction, plugins/MCP boundaries, local decision routing.
- **psycoks/Jarvis**: separate wake/STT/TTS, cognition, memory and action layers. Its heavy Whisper/Kokoro/Chroma stack was not imported.
- **Nox**: optional Ollama local-model provider, explicit model status, SQLite conversation storage and offline-first fallback. Its Electron/FastAPI implementation was not imported.
- **OpenAI Codex** (Apache-2.0): app-server is the future integration boundary. Phase 2 performs read-only CLI discovery only; it does not embed or copy Codex code and never starts coding actions without explicit approval.
- Browser-use, agent-desktop, browse and asAgent informed the permission boundary: PROVIDA Phase 2 only opens validated HTTPS pages. It does not expose arbitrary browser or desktop actions.

Runtime libraries retain their own licenses: PySide6 (LGPL/commercial), Vosk (Apache-2.0), sounddevice (MIT), and their transitive components. The optional external Ollama and Codex executables are not redistributed by this repository.
