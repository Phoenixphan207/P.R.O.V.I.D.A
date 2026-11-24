"""Application composition root and acceptance smoke mode."""

import argparse
import json
import sys
from pathlib import Path

from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from provida.infrastructure.logging_setup import configure_logging
from provida.presentation.assistant_window import AssistantWindow


class SmokeSpeech:
    pending = None

    def speak(self, text, volume=80):  # pragma: no cover
        return None

    def close(self):
        return None


class SmokeVoice:
    model_path = "Bundled English model (audio disabled during smoke test)"
    available = True
    running = False

    def __init__(self):
        import queue

        self.results = queue.Queue()

    def stop(self):
        self.running = False


def run_smoke(window, screenshot: Path):
    QTest.qWaitForWindowExposed(window, 5_000)
    QTest.qWait(500)
    opened = []
    window.browser._opener = lambda url, **_kwargs: opened.append(url) or True
    checks = []
    for command, expected in [
        ("help", "limited local conversation mode"),
        ("Wake up, JARVIS", "Hello, sir."),
        ("Open YouTube", "Opening YouTube."),
        ("open http://example.com", "Only HTTPS websites"),
        ("sleep", "Going to sleep"),
    ]:
        window.text_input.setText(command)
        window.send_button.click()
        QTest.qWait(50)
        checks.append(expected in window.transcript.toPlainText())
    screenshot.parent.mkdir(parents=True, exist_ok=True)
    window.repaint()
    QTest.qWait(250)
    window.grab().save(str(screenshot))
    result = {
        "all_checks_passed": all(checks),
        "checks": checks,
        "opened": opened,
        "final_state": window.state_label.text(),
        "screenshot": str(screenshot),
    }
    print(json.dumps(result))
    return 0 if result["all_checks_passed"] and opened == ["https://www.youtube.com"] else 2


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test", action="store_true")
    parser.add_argument("--screenshot", default="artifacts/smoke.png")
    args = parser.parse_args(argv)
    configure_logging()
    app = QApplication.instance() or QApplication(sys.argv)
    if args.smoke_test:
        window = AssistantWindow(
            speech=SmokeSpeech(), voice_input=SmokeVoice(), speak_responses=False
        )
        window.show()
        code = run_smoke(window, Path(args.screenshot).resolve())
        window.close()
        return code
    window = AssistantWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
