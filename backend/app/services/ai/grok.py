import httpx

from app.services.ai.base import AIProvider, AIProviderError


class GrokProvider(AIProvider):
    """Talks to x.ai's Grok API. Nothing outside this class knows Grok's
    request/response shape — swapping providers later means writing a
    new class with the same `complete()` signature, not touching the
    route or AIService."""

    def __init__(self, api_key: str, model: str, base_url: str = "https://api.x.ai/v1"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

    def complete(
        self,
        messages: list[dict[str, str]],
        max_tokens: int,
        temperature: float,
        timeout: float,
    ) -> str:
        if not self.api_key:
            raise AIProviderError("missing_api_key")

        try:
            response = httpx.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
                timeout=timeout,
            )
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise AIProviderError("timeout") from exc
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429:
                raise AIProviderError("provider_rate_limited") from exc
            raise AIProviderError(f"provider_http_{exc.response.status_code}") from exc
        except httpx.HTTPError as exc:
            raise AIProviderError("provider_unavailable") from exc

        try:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError) as exc:
            raise AIProviderError("invalid_provider_response") from exc
