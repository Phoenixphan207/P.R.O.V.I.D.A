"""Safe Windows speech output adapter."""

import base64
import subprocess
from concurrent.futures import ThreadPoolExecutor


class Speech:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="provida-speech")
        self.pending = None

    @staticmethod
    def _speak(text: str, volume: int):
        escaped = text.replace("'", "''")
        script = (
            "Add-Type -AssemblyName System.Speech;"
            "$voice=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
            f"$voice.Volume={max(0, min(100, int(volume)))};"
            "$voice.Rate=0;"
            f"$voice.Speak('{escaped}');$voice.Dispose()"
        )
        encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
            capture_output=True,
            timeout=30,
            check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if result.returncode:
            raise RuntimeError("Windows speech output is unavailable.")

    def speak(self, text: str, volume: int = 80):
        self.pending = self.executor.submit(self._speak, text, volume)
        return self.pending

    def close(self):
        self.executor.shutdown(wait=False, cancel_futures=True)
