# PROVIDA

PROVIDA is a local-first English desktop voice assistant for Windows. Release 1.1 adds persistent local conversation memory, an optional loopback-only Ollama provider, safe Codex app-server discovery, and a central permission-aware command service while preserving the verified Phase 1 voice pipeline.

## What it can do

- Explicitly enable local detection of “Wake up, JARVIS”, then answer “Hello, sir.” and listen for a command.
- Push to talk, stop listening, or use the always-available text box.
- Open YouTube or a validated HTTPS website in the default browser.
- Answer basic time/date/help requests and remember the last opened website.
- Remember recent conversation locally in SQLite and delete it only after explicit confirmation.
- Detect the installed Codex CLI/app-server without starting coding actions.
- Use an optional local Ollama model without sending prompts to a remote endpoint.
- Show sleeping, listening, thinking, speaking, and error states.

PROVIDA does not bundle a general-purpose language model and never pretends that it does. Unknown questions receive a clear limited-mode response unless the user explicitly enables a locally running Ollama model. It never executes arbitrary shell commands from speech.

## Optional local intelligence

Install Ollama separately from its official distribution, start it locally, and pull the model shown in the settings field (default `qwen2.5:3b`). Check **Use local Ollama** and select **Save AI settings**. PROVIDA only accepts `http://127.0.0.1:11434`; remote model endpoints and credentials are not supported in this release. Ollama calls run off the UI thread and failure returns a clear error without disabling text fallback.

Commands added in 1.1 include `Codex status`, `System status`, `What do you remember`, `Forget conversation`, and the explicit confirmation phrase shown by the assistant. Codex integration is discovery-only: it does not start a coding turn, alter files, or bypass Codex approvals.

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

The automated suite deliberately never starts a microphone. Hardware results and known limitations are recorded in `docs/FEATURE_MATRIX.md`. Design references and licensing decisions are recorded in `THIRD_PARTY_NOTICES.md`.
