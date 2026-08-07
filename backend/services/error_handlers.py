import logging

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.services.logging_utils import get_request_id

logger = logging.getLogger(__name__)


async def validation_exception_handler(
    request: Request,
    error: RequestValidationError,
):
    error_details = error.errors()

    logger.info(
        "request_id=%s validation_error path=%s error_count=%s",
        get_request_id(),
        request.url.path,
        len(error_details),
    )

    return JSONResponse(
        status_code=422,
        content={
            "detail": error_details,
            "details": error_details,
            "error": "invalid_request",
            "message": "Please check your request fields and try again.",
            "request_id": get_request_id(),
        },
    )


async def http_exception_handler(request: Request, error: HTTPException):
    logger.info(
        "request_id=%s http_error path=%s status_code=%s",
        get_request_id(),
        request.url.path,
        error.status_code,
    )

    return JSONResponse(
        status_code=error.status_code,
        content={
            "detail": error.detail,
            "error": "http_error",
            "message": error.detail,
            "request_id": get_request_id(),
        },
    )


async def unhandled_exception_handler(request: Request, error: Exception):
    logger.exception(
        "request_id=%s unhandled_error path=%s error_type=%s",
        get_request_id(),
        request.url.path,
        type(error).__name__,
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Something went wrong while processing the request.",
            "error": "internal_server_error",
            "message": "Something went wrong while processing the request.",
            "request_id": get_request_id(),
        },
    )