"""Single command boundary used by every PROVIDA interface."""

from provida.domain.assistant import AssistantReply, LocalAssistant


class Service:
    def __init__(
        self, local=None, memory=None, llm=None, codex=None, config=None, config_store=None
    ):
        self.local = local or LocalAssistant()
        self.memory = memory
        self.llm = llm
        self.codex = codex
        self.config = config
        self.config_store = config_store
        self.pending_confirmation = None

    @property
    def active(self):
        return self.local.active

    def command(self, message: str) -> AssistantReply:
        normalized = " ".join(message.lower().split())
        if normalized == "codex status":
            reply = AssistantReply(self.codex.status() if self.codex else "Codex is not configured.")
        elif normalized == "system status":
            memory = "enabled" if self.memory else "disabled"
            llm = "enabled" if self.llm and self.llm.enabled else "not configured"
            codex = self.codex.status() if self.codex else "not configured"
            reply = AssistantReply(f"Memory is {memory}. Ollama is {llm}. {codex}")
        elif normalized == "what do you remember":
            items = self.memory.recent(6) if self.memory else []
            user_items = [text for role, text in items if role == "user"]
            text = "; ".join(user_items[-3:]) or "I do not have any saved conversation yet."
            reply = AssistantReply(f"Recent requests: {text}" if user_items else text)
        elif normalized == "forget conversation":
            self.pending_confirmation = "forget"
            reply = AssistantReply(
                "This will delete the local conversation history. Say or type “confirm forget conversation” to continue.",
                "listening",
            )
        elif normalized == "confirm forget conversation" and self.pending_confirmation == "forget":
            if self.memory:
                self.memory.clear()
            self.pending_confirmation = None
            return AssistantReply("The local conversation history has been deleted.")
        else:
            reply = self.local.handle(message)
            if reply.source == "limited" and self.llm and self.llm.enabled:
                history = self.memory.recent(10) if self.memory else []
                reply = AssistantReply(self.llm.chat(message, history), "speaking", source="ollama")
        if self.memory:
            self.memory.add("user", message)
            self.memory.add("assistant", reply.text)
        return reply
