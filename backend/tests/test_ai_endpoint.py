import uuid
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.api.routes.ai import get_ai_service
from app.main import app
from app.models.user import UserRole
from app.services.ai.base import AIProvider, AIProviderError
from app.services.ai.service import AIService


class FakeProvider(AIProvider):
    def __init__(self, reply: str | None = "A software engineer designs and builds software.", error=None):
        self.reply = reply
        self.error = error

    def complete(self, messages, max_tokens, temperature, timeout):
        if self.error:
            raise AIProviderError(self.error)
        return self.reply


def _fake_user(role: UserRole):
    return SimpleNamespace(id=uuid.uuid4(), role=role, is_active=True)


def _client_as(role: UserRole | None, provider_error: str | None = None) -> TestClient:
    client = TestClient(app)
    if role is not None:
        app.dependency_overrides[get_current_user] = lambda: _fake_user(role)
    app.dependency_overrides[get_ai_service] = lambda: AIService(
        provider=FakeProvider(error=provider_error), max_tokens=500, temperature=0.4, timeout=20
    )
    return client


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.clear()


def test_unauthenticated_request_rejected():
    client = TestClient(app)
    app.dependency_overrides[get_ai_service] = lambda: AIService(
        provider=FakeProvider(), max_tokens=500, temperature=0.4, timeout=20
    )
    response = client.post("/ai/chat", json={"message": "What is an AI engineer?"})
    assert response.status_code == 401


@pytest.mark.parametrize(
    "role",
    [UserRole.STUDENT, UserRole.PARENT, UserRole.MENTOR, UserRole.SCHOOL_ADMIN, UserRole.ADMIN],
)
def test_every_role_is_accepted(role):
    client = _client_as(role)
    response = client.post("/ai/chat", json={"message": "What is an AI engineer?"})
    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "grok"
    assert body["answer"]


def test_empty_message_rejected():
    client = _client_as(UserRole.STUDENT)
    response = client.post("/ai/chat", json={"message": "   "})
    assert response.status_code == 422


def test_oversized_message_rejected():
    client = _client_as(UserRole.STUDENT)
    response = client.post("/ai/chat", json={"message": "a" * 3000})
    assert response.status_code == 422


def test_provider_failure_returns_friendly_503_not_a_stack_trace():
    client = _client_as(UserRole.STUDENT, provider_error="timeout")
    response = client.post("/ai/chat", json={"message": "What is an AI engineer?"})
    assert response.status_code == 503
    detail = response.json()["detail"]
    assert "temporarily unavailable" in detail.lower()
    assert "timeout" not in detail.lower()  # internal reason never leaks to the client


def test_missing_api_key_handled_safely():
    client = _client_as(UserRole.STUDENT, provider_error="missing_api_key")
    response = client.post("/ai/chat", json={"message": "What is an AI engineer?"})
    assert response.status_code == 503
    assert "api" not in response.json()["detail"].lower()
