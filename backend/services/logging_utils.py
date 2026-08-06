import logging
import time
import uuid
from contextvars import ContextVar

from fastapi import Request

request_id_context: ContextVar[str] = ContextVar(
    "request_id",
    default="no-request-id",
)


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_context.get()
        return True


def configure_logging(log_level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format=(
            "%(asctime)s level=%(levelname)s "
            "request_id=%(request_id)s "
            "logger=%(name)s message=%(message)s"
        ),
    )

    request_id_filter = RequestIdFilter()

    for handler in logging.getLogger().handlers:
        handler.addFilter(request_id_filter)


def get_request_id() -> str:
    return request_id_context.get()


async def request_id_middleware(request: Request, call_next):
    incoming_request_id = request.headers.get("X-Request-ID")
    request_id = incoming_request_id or str(uuid.uuid4())
    request_id_context.set(request_id)

    logger = logging.getLogger("backend.request")
    started_at = time.perf_counter()

    logger.info(
        "request_started method=%s path=%s",
        request.method,
        request.url.path,
    )

    try:
        response = await call_next(request)
    except Exception:
        duration_seconds = time.perf_counter() - started_at
        logger.exception(
            "request_failed method=%s path=%s duration_seconds=%.4f",
            request.method,
            request.url.path,
            duration_seconds,
        )
        raise

    duration_seconds = time.perf_counter() - started_at

    logger.info(
        "request_finished method=%s path=%s status_code=%s duration_seconds=%.4f",
        request.method,
        request.url.path,
        response.status_code,
        duration_seconds,
    )

    response.headers["X-Request-ID"] = request_id
    return response