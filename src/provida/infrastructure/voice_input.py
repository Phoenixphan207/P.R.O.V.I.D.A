"""Local Vosk microphone input. Audio is processed in memory and never stored."""

import json
import os
import queue
import sys
import threading
import time
from pathlib import Path


def find_model_path() -> Path | None:
    configured = os.environ.get("PROVIDA_VOSK_MODEL")
    candidates = []
    if configured:
        candidates.append(Path(configured))
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys._MEIPASS) / "models" / "vosk-model-small-en-us-0.15")
    candidates.append(
        Path(__file__).resolve().parents[3] / "models" / "vosk-model-small-en-us-0.15"
    )
    return next((path for path in candidates if (path / "conf").is_dir()), None)


class VoiceInput:
    def __init__(self, model_path=None):
        self.model_path = Path(model_path) if model_path else find_model_path()
        self.results = queue.Queue(maxsize=4)
        self.stop_event = threading.Event()
        self.thread = None
        self._model = None

    @property
    def available(self):
        return bool(self.model_path and (self.model_path / "conf").is_dir())

    @property
    def running(self):
        return bool(self.thread and self.thread.is_alive())

    def start_wake(self):
        self._start("wake")

    def start_command(self):
        self._start("command")

    def _start(self, mode):
        if self.running:
            raise RuntimeError("Microphone is already listening.")
        if not self.available:
            raise RuntimeError(
                "The local English speech model is missing. Select a Vosk model "
                "or use the text input."
            )
        self.stop_event.clear()
        self.thread = threading.Thread(
            target=self._run, args=(mode,), daemon=True, name=f"provida-{mode}"
        )
        self.thread.start()

    def _load_model(self):
        if self._model is None:
            import vosk

            self._model = vosk.Model(str(self.model_path))
        return self._model

    def _run(self, mode):
        try:
            import sounddevice
            import vosk

            grammar = None
            if mode == "wake":
                grammar = json.dumps(["wake up jarvis", "[unk]"])
            recognizer = (
                vosk.KaldiRecognizer(self._load_model(), 16_000, grammar)
                if grammar
                else vosk.KaldiRecognizer(self._load_model(), 16_000)
            )
            deadline = None if mode == "wake" else time.monotonic() + 8
            with sounddevice.RawInputStream(
                samplerate=16_000,
                blocksize=2_000,
                dtype="int16",
                channels=1,
            ) as stream:
                while not self.stop_event.is_set() and (
                    deadline is None or time.monotonic() < deadline
                ):
                    data, overflow = stream.read(2_000)
                    if overflow:
                        self._put({"kind": "warning", "text": "Microphone overflow."})
                    if recognizer.AcceptWaveform(bytes(data)):
                        text = json.loads(recognizer.Result()).get("text", "").strip()
                        if text and (mode != "wake" or text == "wake up jarvis"):
                            self._put({"kind": mode, "text": text})
                            return
            text = json.loads(recognizer.FinalResult()).get("text", "").strip()
            if text and (mode != "wake" or text == "wake up jarvis"):
                self._put({"kind": mode, "text": text})
            elif mode == "command" and not self.stop_event.is_set():
                self._put({"kind": "error", "text": "I did not hear a clear command."})
        except Exception as exc:  # noqa: BLE001 - worker reports device/model failures
            self._put({"kind": "error", "text": f"Speech recognition is unavailable: {exc}"})

    def _put(self, result):
        try:
            self.results.put_nowait(result)
        except queue.Full:
            pass

    def stop(self):
        self.stop_event.set()
        thread = self.thread
        if thread and thread.is_alive() and thread is not threading.current_thread():
            thread.join(timeout=2)
        self.thread = None
