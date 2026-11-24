"""End-to-end speaker-to-microphone wake check; not an automated test."""

import json
import time

from provida.infrastructure.voice_input import VoiceInput
from provida.infrastructure.windows import Speech


def main():
    voice = VoiceInput()
    speech = Speech()
    result = None
    try:
        voice.start_wake()
        time.sleep(3)
        speech.speak("Wake up, JARVIS.", 100).result(timeout=30)
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline and result is None:
            if not voice.results.empty():
                result = voice.results.get_nowait()
            time.sleep(0.1)
    finally:
        voice.stop()
        speech.close()
    print(json.dumps({"result": result, "stopped": not voice.running}))
    return 0 if result and result.get("kind") == "wake" else 1


if __name__ == "__main__":
    raise SystemExit(main())
