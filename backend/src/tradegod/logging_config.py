import logging
import sys
import structlog
from structlog.typing import Processor

from .settings import LogFormat, LogLevel, get_settings


def setup_logging() -> None:
    log_level: LogLevel = get_settings().log_level
    log_format: LogFormat = get_settings().log_format

    # Log processors json or regular console text
    log_processor: Processor = (
        structlog.processors.JSONRenderer()
        if log_format == LogFormat.JSON
        else structlog.dev.ConsoleRenderer(colors=True)
    )

    # Enrichment adds the following elements to every log_event
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Configure logger with handler and formatter
    handler = logging.StreamHandler(sys.stdout)
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=log_processor, foreign_pre_chain=shared_processors
    )
    handler.setFormatter(formatter)

    # Configure root logger
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(log_level)

    # Configure structlog to route through stdlib
    structlog.configure(
        processors=shared_processors
        + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Tune noisy library loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
