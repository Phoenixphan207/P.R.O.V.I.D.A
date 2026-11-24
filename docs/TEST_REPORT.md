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
