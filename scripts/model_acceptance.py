"""Feed a generated WAV to the same local wake grammar without using a microphone."""

import json
import sys
import wave

import vosk

from provida.infrastructure.voice_input import find_model_path


def main(wav_path):
    path = find_model_path()
    with wave.open(wav_path, "rb") as audio:
        recognizer = vosk.KaldiRecognizer(
            vosk.Model(str(path)), audio.getframerate(), '["wake up jarvis", "[unk]"]'
        )
        while chunk := audio.readframes(4000):
            recognizer.AcceptWaveform(chunk)
        text = json.loads(recognizer.FinalResult()).get("text", "")
    print(json.dumps({"recognized": text, "expected": "wake up jarvis"}))
    return 0 if text == "wake up jarvis" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
