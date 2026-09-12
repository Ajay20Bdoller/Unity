import time
import uuid
from collections import defaultdict
from threading import Lock

from fastapi import HTTPException, status


class InMemoryRateLimiter:
    """Fixed-window limiter, one counter per user.

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
        self._hits: dict[uuid.UUID, list[float]] = defaultdict(list)
        self._lock = Lock()

    def check(self, key: uuid.UUID) -> None:
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
