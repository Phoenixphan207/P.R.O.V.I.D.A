"""Manual hardware acceptance. This is never called by the automated test suite."""

import json
import time

import sounddevice

from provida.infrastructure.voice_input import VoiceInput, find_model_path
from provida.infrastructure.windows import Speech


def main():
    result = {
        "model": str(find_model_path()) if find_model_path() else None,
        "input_device": None,
        "microphone_start_stop": False,
        "speech_output": False,
        "errors": [],
    }
    try:
        default_input = sounddevice.default.device[0]
        result["input_device"] = sounddevice.query_devices(default_input)["name"]
        voice = VoiceInput()
        voice.start_command()
        time.sleep(1.25)
        voice.stop()
        result["microphone_start_stop"] = not voice.running
    except Exception as exc:
        result["errors"].append(f"microphone: {exc}")
    try:
        speech = Speech()
        future = speech.speak("Hello, sir. PROVIDA speech output is working.", 80)
        future.result(timeout=30)
        result["speech_output"] = True
        speech.close()
    except Exception as exc:
        result["errors"].append(f"speech: {exc}")
    print(json.dumps(result))
    return 0 if result["microphone_start_stop"] and result["speech_output"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
