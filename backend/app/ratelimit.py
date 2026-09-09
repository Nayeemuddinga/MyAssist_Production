import time
from collections import defaultdict, deque
from fastapi import Request
from .errors import ApiError

_attempts: dict[str, deque[float]] = defaultdict(deque)
WINDOW_SECONDS = 300
MAX_ATTEMPTS = 10


def rate_limit_auth(request: Request) -> None:
    key = f"auth:{request.client.host if request.client else 'unknown'}"
    now = time.monotonic()
    bucket = _attempts[key]
    while bucket and now - bucket[0] > WINDOW_SECONDS:
        bucket.popleft()
    if len(bucket) >= MAX_ATTEMPTS:
        raise ApiError(429, "RATE_LIMITED", "Too many attempts. Try again in a few minutes.")
    bucket.append(now)
