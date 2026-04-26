"""Centralized exception handlers wired onto the FastAPI app.

Every error response uses the same envelope: `{"code": "<error_code>", ...}`.
Optional fields (e.g. `errors` on validation failures) may appear per error type.
"""

import structlog
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_422_UNPROCESSABLE_CONTENT, HTTP_500_INTERNAL_SERVER_ERROR
from structlog.stdlib import BoundLogger

from tradegod.core.exceptions import AppError, ErrorCode
from tradegod.core.settings import Environment, get_settings

logger: BoundLogger = structlog.get_logger(__name__)

# Maps HTTP status codes raised by FastAPI/Starlette HTTPException to our ErrorCode.
# Anything not listed falls back to INTERNAL_ERROR.
_HTTP_STATUS_TO_CODE: dict[int, ErrorCode] = {
    401: ErrorCode.UNAUTHENTICATED,
    404: ErrorCode.NOT_FOUND,
    405: ErrorCode.METHOD_NOT_ALLOWED,
}


async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"code": exc.code})


async def request_validation_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    """Translate Pydantic validation failures into the standard {code, errors} shape.

    In non-dev environments, strips the `input` field from each error so
    raw submitted values (e.g. passwords) never leak back to the client.
    """
    exclude: set[str] = set() if get_settings().environment == Environment.DEV else {"input"}
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "code": ErrorCode.VALIDATION_FAILED,
            "errors": jsonable_encoder(exc.errors(), exclude=exclude),
        },
    )


async def http_exception_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Map FastAPI/Starlette HTTPExceptions (404 unknown route, 405 wrong method, etc.) to our envelope."""
    code = _HTTP_STATUS_TO_CODE.get(exc.status_code, ErrorCode.INTERNAL_ERROR)
    return JSONResponse(status_code=exc.status_code, content={"code": code})


async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unhandled exceptions. Logs the traceback, returns a generic 500."""
    logger.exception("unhandled.exception", exc_info=exc)
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"code": ErrorCode.INTERNAL_ERROR},
    )
