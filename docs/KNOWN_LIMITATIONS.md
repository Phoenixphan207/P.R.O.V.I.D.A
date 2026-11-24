# Known limitations

- Conversation is rule-based limited mode unless the user installs and enables Ollama; no model is bundled.
- Wake accuracy depends on the microphone, room noise, and the installed Vosk model.
- Wake mode listens locally until stopped; it must be enabled explicitly each launch.
- Speech output uses the English-capable Windows voice selected by the operating system.
- Phase 1 opens only HTTPS websites and does not submit forms, post content, purchase, delete files, or change accounts.
- Codex support currently verifies the CLI/app-server capability only. Starting/steering coding sessions and approval forwarding are intentionally deferred until a reviewed protocol client and explicit approval UI are implemented.
- Local memory stores recent transcript text in the configured PROVIDA data directory. Use `Forget conversation` and confirm when you want it deleted.
