import queue

from PySide6.QtCore import Qt

from provida.presentation.assistant_window import AssistantWindow


class FakeSpeech:
    pending = None

    def __init__(self):
        self.spoken = []

    def speak(self, text, volume):
        self.spoken.append(text)

    def close(self):
        pass


class FakeVoice:
    model_path = "fake-model"
    available = True
    running = False

    def __init__(self):
        self.results = queue.Queue()
        self.calls = []

    def start_wake(self):
        self.running = True
        self.calls.append("wake")

    def start_command(self):
        self.running = True
        self.calls.append("command")

    def stop(self):
        self.running = False
        self.calls.append("stop")


class FakeBrowser:
    def __init__(self):
        self.opened = []

    def open(self, url):
        self.opened.append(url)
        return True


def make_window(qtbot):
    speech, voice, browser = FakeSpeech(), FakeVoice(), FakeBrowser()
    window = AssistantWindow(browser=browser, speech=speech, voice_input=voice)
    qtbot.addWidget(window)
    window.show()
    return window, speech, voice, browser


def send(qtbot, window, command):
    window.text_input.setText(command)
    qtbot.mouseClick(window.send_button, Qt.MouseButton.LeftButton)


def test_real_button_flows(qtbot):
    window, speech, _voice, browser = make_window(qtbot)
    assert window.state_label.text() == "SLEEPING"
    send(qtbot, window, "Wake up, JARVIS")
    assert "Hello, sir." in window.transcript.toPlainText()
    assert speech.spoken[-1] == "Hello, sir."
    send(qtbot, window, "Open YouTube")
    assert browser.opened == ["https://www.youtube.com"]
    send(qtbot, window, "open http://example.com")
    assert "Only HTTPS websites" in window.transcript.toPlainText()
    assert browser.opened == ["https://www.youtube.com"]
    qtbot.mouseClick(window.sleep_button, Qt.MouseButton.LeftButton)
    assert "Going to sleep" in window.transcript.toPlainText()


def test_microphone_controls_are_explicit(qtbot):
    window, _, voice, _ = make_window(qtbot)
    assert not voice.running
    qtbot.mouseClick(window.wake_button, Qt.MouseButton.LeftButton)
    assert voice.calls[-1] == "wake"
    assert window.state_label.text() == "LISTENING"
    qtbot.mouseClick(window.stop_button, Qt.MouseButton.LeftButton)
    assert not voice.running
    assert window.state_label.text() == "SLEEPING"
