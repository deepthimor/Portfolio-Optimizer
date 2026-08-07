import os
import time
from collections import defaultdict, deque

from fastapi import Request
from fastapi.responses import JSONResponse

from backend.services.logging_utils import get_request_id

RATE_LIMIT_WINDOW_SECONDS = 60

_request_timestamps: dict[str, deque[float]] = defaultdict(deque)


def get_rate_limit_per_minute() -> int:
    raw_limit = os.getenv("RATE_LIMIT_PER_MINUTE", "60")

    try:
        return int(raw_limit)
    except ValueError:
        return 60


def get_rate_limit_key(request: Request) -> str:
    client_host = request.client.host if request.client else "unknown-client"
    return f"{client_host}:{request.url.path}"


def reset_rate_limit_state() -> None:
    _request_timestamps.clear()


async def rate_limit_middleware(request: Request, call_next):
    limit = get_rate_limit_per_minute()

    if limit <= 0:
        return await call_next(request)

    now = time.time()
    key = get_rate_limit_key(request)
    timestamps = _request_timestamps[key]

    while timestamps and now - timestamps[0] > RATE_LIMIT_WINDOW_SECONDS:
        timestamps.popleft()

    if len(timestamps) >= limit:
        return JSONResponse(
            status_code=429,
            content={
                "error": "rate_limit_exceeded",
                "message": "Too many requests. Please wait before trying again.",
                "request_id": get_request_id(),
            },
            headers={
                "Retry-After": str(RATE_LIMIT_WINDOW_SECONDS),
                "X-Request-ID": get_request_id(),
            },
        )

    timestamps.append(now)

    return await call_next(request)