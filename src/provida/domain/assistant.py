"""Pure English conversation and safe intent parsing for Phase 1."""

from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlparse

WAKE_PHRASES = {"wake up jarvis", "wake up jarvis.", "wake up, jarvis"}
SLEEP_PHRASES = {"sleep", "go to sleep", "stop listening", "goodbye"}


@dataclass(frozen=True)
class AssistantReply:
    text: str
    state: str = "sleeping"
    url: str | None = None


def normalize_url(value: str) -> str:
    candidate = value.strip()
    if not candidate or any(character.isspace() for character in candidate):
        raise ValueError("Enter a domain or HTTPS URL without spaces.")
    if "://" not in candidate:
        candidate = "https://" + candidate
    parsed = urlparse(candidate)
    if parsed.scheme.lower() != "https":
        raise ValueError("Only HTTPS websites can be opened.")
    hostname = parsed.hostname or ""
    if not hostname or "." not in hostname or hostname.startswith(".") or hostname.endswith("."):
        raise ValueError("That does not look like a valid website address.")
    if parsed.username or parsed.password:
        raise ValueError("Website addresses containing credentials are not allowed.")
    if parsed.port not in (None, 443):
        raise ValueError("Only the standard HTTPS port is allowed.")
    return candidate


class LocalAssistant:
    """Honest rule-based fallback used when no language model is configured."""

    def __init__(self, now=None):
        self.active = False
        self.now = now or datetime.now
        self.last_topic = None

    def handle(self, message: str) -> AssistantReply:
        text = " ".join(message.strip().lower().replace(",", "").split())
        if not text:
            return AssistantReply("Please type or say a command.", "error")
        if text in WAKE_PHRASES:
            self.active = True
            return AssistantReply("Hello, sir.", "listening")
        if text in SLEEP_PHRASES:
            self.active = False
            return AssistantReply("Going to sleep, sir.", "sleeping")
        if text == "open youtube":
            self.last_topic = "YouTube"
            return AssistantReply("Opening YouTube.", "thinking", "https://www.youtube.com")
        if text.startswith("open "):
            target = message.strip()[5:].strip()
            try:
                url = normalize_url(target)
            except ValueError as exc:
                return AssistantReply(str(exc), "error")
            self.last_topic = url
            return AssistantReply(f"Opening {url}.", "thinking", url)
        if text in {"what time is it", "what is the time", "time"}:
            return AssistantReply(
                f"It is {self.now().strftime('%I:%M %p').lstrip('0')}.", "speaking"
            )
        if text in {"what is the date", "what day is it", "date"}:
            return AssistantReply(f"Today is {self.now().strftime('%A, %B %d, %Y')}.", "speaking")
        if text in {"hello", "hi", "hey jarvis"}:
            return AssistantReply("Hello, sir. How can I help?", "speaking")
        if text in {"help", "what can you do"}:
            return AssistantReply(
                "I can open safe HTTPS websites, tell the time and date, and "
                "respond through text or English speech. I am currently using "
                "a limited local conversation mode.",
                "speaking",
            )
        if text in {"what did you open", "what was that"} and self.last_topic:
            return AssistantReply(f"The last website was {self.last_topic}.", "speaking")
        return AssistantReply(
            "I am running in limited local mode, so I cannot answer that yet. "
            "Try ‘help’, ‘open YouTube’, ‘open example.com’, ‘time’, or ‘date’.",
            "speaking",
        )
