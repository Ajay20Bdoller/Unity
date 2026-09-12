from abc import ABC, abstractmethod


class AIProviderError(Exception):
    """Any provider failure — timeout, unavailable, missing key, malformed
    response. The route layer catches this and returns one generic
    friendly message; it never leaks which case occurred to the client.
    """


class AIProvider(ABC):
    @abstractmethod
    def complete(
        self,
        messages: list[dict[str, str]],
        max_tokens: int,
        temperature: float,
        timeout: float,
    ) -> str:
        """Return the assistant's reply text, or raise AIProviderError."""
        raise NotImplementedError
