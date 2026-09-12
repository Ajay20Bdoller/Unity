import logging
import time

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.models.user import User
from app.schemas.ai import AIChatRequest, AIChatResponse
from app.services.ai.base import AIProviderError
from app.services.ai.grok import GrokProvider
from app.services.ai.rate_limit import InMemoryRateLimiter
from app.services.ai.service import AIService

router = APIRouter(prefix="/ai", tags=["ai"])
settings = get_settings()
logger = logging.getLogger("app.ai")

_rate_limiter = InMemoryRateLimiter(
    max_requests=settings.AI_RATE_LIMIT_PER_MINUTE, window_seconds=60
)


def get_ai_service() -> AIService:
    """A dependency so tests can override this with a fake provider —
    see tests/test_ai_endpoint.py. Nothing about auth or rate limiting
    lives here; this only builds the provider-agnostic service."""
    provider = GrokProvider(
        api_key=settings.GROK_API_KEY,
        model=settings.GROK_MODEL,
        base_url=settings.GROK_BASE_URL,
    )
    return AIService(
        provider=provider,
        max_tokens=settings.AI_MAX_TOKENS,
        temperature=settings.AI_TEMPERATURE,
        timeout=settings.AI_REQUEST_TIMEOUT,
    )


@router.post("/chat", response_model=AIChatResponse)
def chat(
    payload: AIChatRequest,
    current_user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service),
) -> AIChatResponse:
    _rate_limiter.check(current_user.id)

    started = time.monotonic()
    try:
        answer = ai_service.ask(payload.message, payload.history)
    except AIProviderError as exc:
        latency_ms = round((time.monotonic() - started) * 1000)
        # Log operational info only — never the user's message content,
        # never the API key, never raw provider stack traces.
        logger.warning(
            "ai_chat_failed reason=%s latency_ms=%s role=%s", exc, latency_ms, current_user.role.value
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI is temporarily unavailable. Please try again.",
        ) from exc

    latency_ms = round((time.monotonic() - started) * 1000)
    logger.info("ai_chat_ok latency_ms=%s role=%s", latency_ms, current_user.role.value)
    return AIChatResponse(answer=answer, provider="grok")
