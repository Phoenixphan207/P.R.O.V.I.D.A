from datetime import datetime

import pytest

from provida.domain.assistant import LocalAssistant, normalize_url
from provida.infrastructure.browser import BrowserService


def test_wake_conversation_and_sleep():
    assistant = LocalAssistant(now=lambda: datetime(2026, 11, 24, 9, 5))
    assert assistant.handle("Wake up, JARVIS").text == "Hello, sir."
    assert assistant.active
    assert assistant.handle("time").text == "It is 9:05 AM."
    assert assistant.handle("date").text == "Today is Tuesday, November 24, 2026."
    assert assistant.handle("sleep").state == "sleeping"
    assert not assistant.active


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("example.com", "https://example.com"),
        ("https://openai.com/docs", "https://openai.com/docs"),
    ],
)
def test_safe_urls(raw, expected):
    assert normalize_url(raw) == expected


@pytest.mark.parametrize(
    "unsafe",
    [
        "",
        "hello world",
        "http://example.com",
        "file:///etc/passwd",
        "localhost",
        "https://user:pass@example.com",
    ],
)
def test_unsafe_urls_are_rejected(unsafe):
    with pytest.raises(ValueError):
        normalize_url(unsafe)


def test_youtube_and_browser_boundary():
    opened = []
    reply = LocalAssistant().handle("Open YouTube")
    assert reply.url == "https://www.youtube.com"
    assert BrowserService(lambda url, **kwargs: opened.append(url) or True).open(reply.url)
    assert opened == ["https://www.youtube.com"]


def test_unknown_request_is_honest():
    text = LocalAssistant().handle("write a novel").text
    assert "limited local mode" in text
