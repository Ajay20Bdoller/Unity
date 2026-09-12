from pydantic import BaseModel, field_validator

from app.core.config import get_settings

settings = get_settings()

_MAX_HISTORY_TURNS = 6  # short history only — no unlimited conversation memory


class AIChatRequest(BaseModel):
    message: str
    history: list[dict[str, str]] | None = None

    @field_validator("message")
    @classmethod
    def message_not_empty_and_not_too_long(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Message cannot be empty")
        if len(stripped) > settings.AI_MAX_MESSAGE_LENGTH:
            raise ValueError(
                f"Message is too long (max {settings.AI_MAX_MESSAGE_LENGTH} characters)"
            )
        return stripped

    @field_validator("history")
    @classmethod
    def history_is_short(cls, value: list[dict[str, str]] | None) -> list[dict[str, str]] | None:
        if value is not None and len(value) > _MAX_HISTORY_TURNS:
            raise ValueError(f"History is limited to {_MAX_HISTORY_TURNS} turns")
        return value


class AIChatResponse(BaseModel):
    answer: str
    provider: str = "grok"
