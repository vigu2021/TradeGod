import time
from uuid import uuid4

import structlog.contextvars
from asgiref.typing import ASGI3Application, ASGIReceiveCallable, ASGISendCallable, ASGISendEvent, Scope
import structlog
from structlog.stdlib import BoundLogger

logger: BoundLogger = structlog.get_logger(__name__)


class RequestLoggingMiddleware:
    def __init__(self, app: ASGI3Application) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:

        # If not http, do nothing
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Start timer
        start_time = time.perf_counter()

        # Get the headers
        request_headers = dict(scope["headers"])

        # Get or generate correlation id (if not provided)
        raw_correlation_id = request_headers.get(b"x-correlation-id", None)
        correlation_id = raw_correlation_id.decode() if raw_correlation_id else str(uuid4())

        tokens = structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

        status_code = 500

        # Intercept for the status code to enhance logging
        async def send_wrapper(message: ASGISendEvent) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        # Run the downstream app, log outcome (success or failure) and enhance it with duration.
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.exception(
                "Request failed",
                status=status_code,
                duration_ms=round(duration_ms, 2),
                path=scope["path"],
                method=scope["method"],
            )
            raise
        else:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Request complete",
                status=status_code,
                duration_ms=round(duration_ms, 2),
                path=scope["path"],
                method=scope["method"],
            )
        # Cleanup context vars
        finally:
            structlog.contextvars.reset_contextvars(**tokens)
