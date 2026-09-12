import pytest

from app.services.ai.base import AIProvider, AIProviderError
from app.services.ai.service import AIService


class FakeProvider(AIProvider):
    def __init__(self, reply: str | None = None, error: str | None = None):
        self.reply = reply
        self.error = error
        self.last_messages: list[dict[str, str]] | None = None

    def complete(self, messages, max_tokens, temperature, timeout):
        self.last_messages = messages
        if self.error:
            raise AIProviderError(self.error)
        return self.reply


def _service(provider: AIProvider) -> AIService:
    return AIService(provider=provider, max_tokens=500, temperature=0.4, timeout=20)


def test_ask_returns_provider_reply():
    provider = FakeProvider(reply="An AI engineer builds and deploys ML systems.")
    service = _service(provider)
    assert service.ask("What is an AI engineer?") == "An AI engineer builds and deploys ML systems."


def test_ask_includes_system_prompt_first():
    provider = FakeProvider(reply="ok")
    service = _service(provider)
    service.ask("hello")
    assert provider.last_messages[0]["role"] == "system"
    assert provider.last_messages[-1] == {"role": "user", "content": "hello"}


def test_ask_includes_history_between_system_and_new_message():
    provider = FakeProvider(reply="ok")
    service = _service(provider)
    history = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello!"}]
    service.ask("next question", history=history)
    assert provider.last_messages[1:3] == history
    assert provider.last_messages[-1] == {"role": "user", "content": "next question"}


def test_ask_propagates_provider_error():
    provider = FakeProvider(error="timeout")
    service = _service(provider)
    with pytest.raises(AIProviderError):
        service.ask("hello")


def test_salary_guidance_is_in_the_system_prompt():
    # Regression guard for the product rule: never a single confident
    # salary number. Cheap to check the instruction is actually present.
    provider = FakeProvider(reply="ok")
    service = _service(provider)
    assert "salary" in service.system_prompt.lower()
    assert "never give a single number" in service.system_prompt.lower()
