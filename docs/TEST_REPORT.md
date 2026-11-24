# Phase 1 test report

Date: 2026-11-24

- `scripts/test.ps1`: 14 passed.
- `scripts/lint.ps1`: Ruff passed; Python compilation passed.
- Native source smoke: all five button flows passed; YouTube adapter received the exact HTTPS URL.
- Hardware acceptance: bundled model found; Microphone Array started/stopped; English SAPI output completed.
- Wake model acceptance: generated English WAV decoded exactly as `wake up jarvis`.
- Speaker-to-microphone wake attempt: no detection; resources released cleanly. This does not substitute for a human live wake test.
- Browser acceptance: the real UI command opened YouTube using the system default browser.
- Release: `dist/release-1.0.0/PROVIDA/PROVIDA.exe`, bundled model present, packaged smoke exit code 0, rendered screenshot inspected.

## Release 1.1.0 integration

- `scripts/test.ps1`: 19 passed.
- `scripts/lint.ps1`: Ruff and Python compilation passed.
- Native and packaged smoke: nine flows passed, including Codex status, memory recall, deletion prompt and explicit deletion confirmation.
- Packaged executable exit code: 0; bundled Vosk model and SQLite database verified; screenshot visually inspected.
- Optional Ollama: fake-provider response and asynchronous unavailable/error recovery passed. Ollama is not installed on this machine, so no real model inference is claimed.
- Codex: installed CLI version and `app-server` capability detected read-only. No coding action or approval bypass was attempted.

## Release 1.1.1 Ollama verification

- Ollama 0.40.17 detected with installed models `qwen3.5:4b` and `ministral-3:8b`.
- Direct `/api/chat` inference returned the exact requested readiness phrase.
- PROVIDA `Service.command` inference with `qwen3.5:4b` returned a grounded English description of PROVIDA.
- A real 30-second timeout was reproduced with conversation memory, then fixed using background execution, `think: false`, a 120-second provider timeout and a fixed identity/safety system message.
- Final automated result after the fix: 19 passed; Ruff and compilation passed.
