from provida.application.service import Service
from provida.infrastructure.config import AppConfig, ConfigStore
from provida.infrastructure.memory import ConversationMemory
from provida.infrastructure.ollama import OllamaClient


class FakeCodex:
    def status(self):
        return "Codex CLI is available: test. Coding actions require explicit approval."


class FakeLlm:
    enabled = True

    def chat(self, message, history):
        assert message == "explain recursion"
        assert history
        return "A function calls itself with a smaller problem."


def test_memory_and_confirmed_deletion(tmp_path):
    memory = ConversationMemory(tmp_path / "memory.db")
    service = Service(memory=memory)
    service.command("hello")
    assert any(text == "hello" for _, text in memory.recent())
    prompt = service.command("forget conversation")
    assert "confirm forget conversation" in prompt.text
    assert memory.recent()
    service.command("confirm forget conversation")
    assert memory.recent() == []


def test_optional_llm_and_codex_status(tmp_path):
    memory = ConversationMemory(tmp_path / "memory.db")
    service = Service(memory=memory, llm=FakeLlm(), codex=FakeCodex())
    assert "Codex CLI is available" in service.command("codex status").text
    reply = service.command("explain recursion")
    assert reply.source == "ollama"
    assert "smaller problem" in reply.text


def test_config_rejects_non_loopback_ollama(tmp_path):
    store = ConfigStore(tmp_path / "settings.json")
    config = AppConfig(ollama_enabled=True, ollama_model="qwen-test")
    store.save(config)
    assert store.load().ollama_model == "qwen-test"
    config.ollama_endpoint = "https://example.com"
    try:
        store.save(config)
    except ValueError as exc:
        assert "local Ollama" in str(exc)
    else:
        raise AssertionError("A remote model endpoint was accepted")


def test_ollama_disabled_by_default():
    assert not OllamaClient(AppConfig()).enabled
