import time
from collections import defaultdict
from threading import Lock

from fastapi import HTTPException, Request, status


def get_client_ip(request: Request) -> str:
    """Behind a reverse proxy (Railway, Render, Vercel, etc.) the real
    client IP is in X-Forwarded-For, not request.client — that header
    can hold a comma-separated chain if there are multiple proxies, so
    take the first entry (the original client)."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class InMemoryRateLimiter:
    """Fixed-window limiter, one counter per key (a user id, an IP
    address, a mobile number — whatever the caller wants to throttle).

    KNOWN LIMITATION (documented, not accidental): this state lives in
    process memory. It resets on restart and does not share state across
    multiple server workers/instances — fine for a single-process MVP,
    not correct once the app scales horizontally. Swap for a Redis-backed
    limiter with the same `check()` interface at that point; nothing
    calling this needs to change.
    """

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def check(self, key: str) -> None:
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            hits = [t for t in self._hits[key] if t > cutoff]
            if len(hits) >= self.max_requests:
                self._hits[key] = hits
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please wait a moment and try again.",
                )
            hits.append(now)
            self._hits[key] = hits

    def reset(self) -> None:
        """For tests only — this limiter's state is otherwise process-
        lifetime, which is correct in production but means every test in
        the same pytest run would otherwise share one budget and start
        failing each other with 429s partway through the suite."""
        with self._lock:
            self._hits.clear()
