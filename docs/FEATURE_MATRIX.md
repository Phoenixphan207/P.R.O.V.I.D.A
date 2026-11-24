# Phase 1 feature matrix

Measured on Windows 11 x64, 2026-11-24.

| Feature | Status | Measured evidence |
|---|---|---|
| Desktop launch and responsive controls | Verified | Native source and packaged smoke; real clicks for help, wake text, YouTube, unsafe URL, sleep; screenshots inspected |
| English text conversation | Verified | Domain/UI tests and native smoke |
| Explicit microphone enable/stop | Verified | Physical Microphone Array opened for 1.25 s and released without error |
| Wake phrase recognizer/grammar | Verified with generated audio | Windows English WAV recognized exactly as `wake up jarvis` by bundled Vosk model |
| Live human wake phrase | Not measured | Speaker-to-mic loopback was blocked by echo cancellation; requires a person to say the phrase |
| English speech output | Verified | Windows System.Speech completed audible acceptance sentence without error |
| Open YouTube | Verified | Real UI Send click opened `https://www.youtube.com` in the system browser; packaged smoke also asserted URL |
| Safe HTTPS URL validation | Verified | Unit/UI/smoke tests reject HTTP and malformed input |
| Packaged model | Verified | Release contains Vosk model configuration and packaged app exits smoke with code 0 |
| Clean shutdown | Verified | Hardware acceptance released microphone; source and packaged smoke exited cleanly |
| General LLM conversation | Not included | Honest limited local mode |

Automated tests never enable or capture microphone audio. Hardware checks are separate manual acceptance scripts.
