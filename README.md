# PROVIDA

PROVIDA is a local-first English desktop voice assistant for Windows. Phase 1 provides an honest limited conversation mode, local Vosk speech recognition, Windows English speech output, safe website opening, and a text fallback that remains usable without audio hardware.

## What it can do

- Explicitly enable local detection of “Wake up, JARVIS”, then answer “Hello, sir.” and listen for a command.
- Push to talk, stop listening, or use the always-available text box.
- Open YouTube or a validated HTTPS website in the default browser.
- Answer basic time/date/help requests and remember the last opened website.
- Show sleeping, listening, thinking, speaking, and error states.

PROVIDA does not contain a general-purpose language model and never pretends that it does. Unknown questions receive a clear limited-mode response. It never executes shell commands from speech.

## Setup and run

Requirements: Windows 10/11 x64, Python 3.11 or 3.12, a microphone for voice features, and a default browser.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Download the official `vosk-model-small-en-us-0.15` English model from https://alphacephei.com/vosk/models and extract it as:

`models\vosk-model-small-en-us-0.15\conf\...`

Then run:

```powershell
.\scripts\run.ps1
```

The microphone starts **off**. Select **Enable “Wake up, JARVIS”** for wake-word mode or **Push to Talk** for one command. Audio is processed locally in memory and is not saved or transmitted. Set `PROVIDA_VOSK_MODEL` to another compatible English Vosk model if desired. Set `PROVIDA_DATA_DIR` to change the local log directory.

## Verification and packaging

```powershell
.\scripts\test.ps1
.\scripts\lint.ps1
python -m provida --smoke-test --screenshot artifacts\smoke.png
.\scripts\build.ps1
```

The automated suite deliberately never starts a microphone. Hardware results and known limitations are recorded in `docs/FEATURE_MATRIX.md`.
