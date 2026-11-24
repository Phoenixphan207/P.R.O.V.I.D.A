"""English Phase 1 desktop assistant interface."""

import html
import logging
from pathlib import Path
from typing import ClassVar

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from provida.domain.assistant import LocalAssistant
from provida.infrastructure.browser import BrowserService
from provida.infrastructure.voice_input import VoiceInput
from provida.infrastructure.windows import Speech

LOGGER = logging.getLogger(__name__)


class Orb(QWidget):
    COLORS: ClassVar = {
        "sleeping": "#526178",
        "listening": "#36d5f2",
        "thinking": "#a78bfa",
        "speaking": "#4ade80",
        "error": "#fb7185",
    }

    def __init__(self):
        super().__init__()
        self.state = "sleeping"
        self.setFixedSize(150, 150)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(self.COLORS[self.state])
        painter.setPen(Qt.PenStyle.NoPen)
        color.setAlpha(45)
        painter.setBrush(color)
        painter.drawEllipse(5, 5, 140, 140)
        color.setAlpha(210)
        painter.setBrush(color)
        painter.drawEllipse(32, 32, 86, 86)


class AssistantWindow(QMainWindow):
    def __init__(
        self,
        engine=None,
        browser=None,
        speech=None,
        voice_input=None,
        speak_responses=True,
    ):
        super().__init__()
        self.engine = engine or LocalAssistant()
        self.browser = browser or BrowserService()
        self.speech = speech or Speech()
        self.voice = voice_input or VoiceInput()
        self.speak_responses = speak_responses
        self.pending_command_after_wake = False
        self.setWindowTitle("PROVIDA — Desktop Voice Assistant")
        self.resize(1050, 760)
        self.setMinimumSize(820, 620)
        self.setStyleSheet("""
            QWidget { background:#080f1d; color:#e6f2ff; font:14px 'Segoe UI'; }
            QFrame#panel { background:#101c31; border:1px solid #223451; border-radius:16px; }
            QPushButton { background:#183153; border:1px solid #2e527d; border-radius:9px; padding:10px 16px; }
            QPushButton:hover { background:#21466f; }
            QPushButton:disabled { color:#64748b; background:#111d2e; }
            QLineEdit, QTextEdit, QSpinBox { background:#0c1728; border:1px solid #29425f; border-radius:9px; padding:10px; }
        """)
        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(24, 20, 24, 20)
        top = QHBoxLayout()
        identity = QVBoxLayout()
        title = QLabel("PROVIDA")
        title.setStyleSheet("font-size:30px;font-weight:700;letter-spacing:4px;color:#79e6ff")
        identity.addWidget(title)
        identity.addWidget(QLabel("Private, local-first desktop voice assistant"))
        top.addLayout(identity)
        top.addStretch()
        self.mode_label = QLabel("LIMITED LOCAL MODE")
        self.mode_label.setStyleSheet(
            "background:#362d59;color:#d8c8ff;padding:8px 12px;border-radius:10px"
        )
        top.addWidget(self.mode_label)
        outer.addLayout(top)

        content = QHBoxLayout()
        state_panel = QFrame()
        state_panel.setObjectName("panel")
        state_layout = QVBoxLayout(state_panel)
        state_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.orb = Orb()
        state_layout.addWidget(self.orb, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.state_label = QLabel("SLEEPING")
        self.state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.state_label.setStyleSheet("font-size:20px;font-weight:700;color:#91a5c2")
        state_layout.addWidget(self.state_label)
        self.status_detail = QLabel("Microphone is off. Text input is ready.")
        self.status_detail.setWordWrap(True)
        self.status_detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        state_layout.addWidget(self.status_detail)
        self.privacy_label = QLabel("● MIC OFF — no audio is being captured")
        self.privacy_label.setStyleSheet("color:#93a4bc")
        self.privacy_label.setWordWrap(True)
        state_layout.addWidget(self.privacy_label)

        self.wake_button = QPushButton("Enable ‘Wake up, JARVIS’")
        self.wake_button.setObjectName("enable_wake")
        self.wake_button.clicked.connect(self.enable_wake_word)
        state_layout.addWidget(self.wake_button)
        self.talk_button = QPushButton("Push to Talk")
        self.talk_button.setObjectName("push_to_talk")
        self.talk_button.clicked.connect(self.push_to_talk)
        state_layout.addWidget(self.talk_button)
        self.stop_button = QPushButton("Stop Listening")
        self.stop_button.setObjectName("stop_listening")
        self.stop_button.clicked.connect(self.stop_listening)
        self.stop_button.setEnabled(False)
        state_layout.addWidget(self.stop_button)
        self.sleep_button = QPushButton("Sleep")
        self.sleep_button.setObjectName("sleep")
        self.sleep_button.clicked.connect(lambda: self.submit_text("sleep", show_user=True))
        state_layout.addWidget(self.sleep_button)
        state_layout.addStretch()
        content.addWidget(state_panel, 1)

        conversation_panel = QFrame()
        conversation_panel.setObjectName("panel")
        conversation_layout = QVBoxLayout(conversation_panel)
        transcript_title = QLabel("Conversation")
        transcript_title.setStyleSheet("font-size:18px;font-weight:600")
        conversation_layout.addWidget(transcript_title)
        self.transcript = QTextEdit()
        self.transcript.setReadOnly(True)
        self.transcript.setAccessibleName("Conversation transcript")
        conversation_layout.addWidget(self.transcript, 1)
        input_row = QHBoxLayout()
        self.text_input = QLineEdit()
        self.text_input.setObjectName("text_input")
        self.text_input.setPlaceholderText("Type in English — e.g. Open YouTube")
        self.text_input.returnPressed.connect(self.send_text)
        input_row.addWidget(self.text_input, 1)
        self.send_button = QPushButton("Send")
        self.send_button.setObjectName("send")
        self.send_button.clicked.connect(self.send_text)
        input_row.addWidget(self.send_button)
        conversation_layout.addLayout(input_row)
        self.help_label = QLabel(
            "Try: “Wake up, JARVIS” · “Open YouTube” · “Open example.com” · “What time is it?” · “Sleep”"
        )
        self.help_label.setWordWrap(True)
        self.help_label.setStyleSheet("color:#8da3bf")
        conversation_layout.addWidget(self.help_label)
        content.addWidget(conversation_panel, 2)
        outer.addLayout(content, 1)

        settings = QFrame()
        settings.setObjectName("panel")
        settings_layout = QHBoxLayout(settings)
        self.voice_toggle = QCheckBox("Speak English responses")
        self.voice_toggle.setChecked(speak_responses)
        self.voice_toggle.toggled.connect(lambda value: setattr(self, "speak_responses", value))
        settings_layout.addWidget(self.voice_toggle)
        self.volume = QSpinBox()
        self.volume.setRange(0, 100)
        self.volume.setValue(80)
        self.volume.setPrefix("Volume ")
        settings_layout.addWidget(self.volume)
        self.model_label = QLabel(
            "Speech model: " + (str(self.voice.model_path) if self.voice.available else "not found")
        )
        self.model_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        settings_layout.addWidget(self.model_label, 1)
        model_button = QPushButton("Select Vosk model…")
        model_button.clicked.connect(self.select_model)
        settings_layout.addWidget(model_button)
        outer.addWidget(settings)

        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.poll_workers)
        self.poll_timer.start(100)
        self.append_assistant(
            "Ready in limited local mode. Text input always works. Enable the "
            "microphone only when you want local speech recognition."
        )
        self.set_state("sleeping", "Microphone is off. Text input is ready.")

    def set_state(self, state, detail):
        self.orb.state = state
        self.orb.update()
        self.state_label.setText(state.upper())
        self.state_label.setStyleSheet(f"font-size:20px;font-weight:700;color:{Orb.COLORS[state]}")
        self.status_detail.setText(detail)
        listening = self.voice.running
        self.privacy_label.setText(
            "● MIC ON — audio stays on this device"
            if listening
            else "● MIC OFF — no audio is being captured"
        )
        self.privacy_label.setStyleSheet("color:#4ade80" if listening else "color:#93a4bc")
        self.stop_button.setEnabled(listening)

    def append_user(self, text):
        self.transcript.append(f'<p><b style="color:#79e6ff">You</b><br>{html.escape(text)}</p>')

    def append_assistant(self, text):
        self.transcript.append(
            f'<p><b style="color:#86efac">PROVIDA</b><br>{html.escape(text)}</p>'
        )

    def send_text(self):
        text = self.text_input.text().strip()
        if not text:
            self.set_state("error", "Type a command before pressing Send.")
            return
        self.text_input.clear()
        self.submit_text(text, show_user=True)

    def submit_text(self, text, show_user=True):
        if show_user:
            self.append_user(text)
        self.set_state("thinking", "Processing locally…")
        try:
            reply = self.engine.handle(text)
            self.append_assistant(reply.text)
            if reply.url and not self.browser.open(reply.url):
                raise RuntimeError("The default browser did not accept the request.")
            if self.speak_responses:
                self.speech.speak(reply.text, self.volume.value())
                self.set_state("speaking", "Speaking an English response…")
            else:
                self.set_state(reply.state, reply.text)
        except Exception as exc:
            LOGGER.exception("Assistant request failed")
            self.append_assistant(f"I could not complete that request: {exc}")
            self.set_state("error", str(exc))

    def enable_wake_word(self):
        try:
            self.voice.stop()
            self.voice.start_wake()
            self.wake_button.setText("Wake word enabled")
            self.set_state("listening", "Say “Wake up, JARVIS.”")
        except Exception as exc:  # noqa: BLE001 - hardware boundary
            self.append_assistant(str(exc))
            self.set_state("error", str(exc))

    def push_to_talk(self):
        try:
            self.voice.stop()
            self.voice.start_command()
            self.set_state("listening", "Listening for one English command…")
        except Exception as exc:  # noqa: BLE001 - hardware boundary
            self.append_assistant(str(exc))
            self.set_state("error", str(exc))

    def stop_listening(self):
        self.voice.stop()
        self.pending_command_after_wake = False
        self.wake_button.setText("Enable ‘Wake up, JARVIS’")
        self.set_state("sleeping", "Microphone stopped. Text input remains available.")

    def poll_workers(self):
        while not self.voice.results.empty():
            result = self.voice.results.get_nowait()
            if result["kind"] == "error":
                self.append_assistant(result["text"])
                self.set_state("error", result["text"])
            elif result["kind"] == "warning":
                self.status_detail.setText(result["text"])
            elif result["kind"] == "wake":
                self.voice.stop()
                self.submit_text("Wake up, JARVIS", show_user=False)
                self.pending_command_after_wake = True
            elif result["kind"] == "command":
                self.voice.stop()
                self.submit_text(result["text"], show_user=True)
        if (
            self.pending_command_after_wake
            and (not self.speech.pending or self.speech.pending.done())
            and not self.voice.running
        ):
            self.pending_command_after_wake = False
            try:
                self.voice.start_command()
                self.set_state("listening", "Hello, sir. What can I do for you?")
            except Exception as exc:  # noqa: BLE001
                self.append_assistant(str(exc))
                self.set_state("error", str(exc))
        elif (
            self.state_label.text() == "SPEAKING"
            and self.speech.pending
            and self.speech.pending.done()
        ):
            if self.speech.pending.exception():
                self.append_assistant("Speech output is unavailable. You can continue with text.")
                self.set_state("error", "Speech output is unavailable; text mode still works.")
                return
            self.set_state(
                "listening" if self.engine.active else "sleeping",
                "Ready for your next command." if self.engine.active else "Text input is ready.",
            )

    def select_model(self):
        path = QFileDialog.getExistingDirectory(self, "Select an English Vosk model")
        if path and (Path(path) / "conf").is_dir():
            self.voice.stop()
            self.voice = VoiceInput(path)
            self.model_label.setText("Speech model: " + path)
            self.set_state("sleeping", "Local speech model selected.")
        elif path:
            self.set_state("error", "That folder is not a valid Vosk model.")

    def show_dashboard(self):
        self.showNormal()

    def closeEvent(self, event):
        self.poll_timer.stop()
        self.voice.stop()
        self.speech.close()
        event.accept()
