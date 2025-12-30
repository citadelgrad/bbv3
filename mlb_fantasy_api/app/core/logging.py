import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor

from app.config import settings

# Fields to redact from logs
SENSITIVE_FIELDS = frozenset(
    {
        "password",
        "passwd",
        "pwd",
        "token",
        "access_token",
        "refresh_token",
        "secret",
        "api_key",
        "authorization",
        "ssn",
        "credit_card",
        "cvv",
    }
)


def redact_sensitive_data(
    _logger: logging.Logger, _method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Processor that redacts sensitive fields from log events."""
    for key in list(event_dict.keys()):
        if key.lower() in SENSITIVE_FIELDS:
            event_dict[key] = "[REDACTED]"
        elif isinstance(event_dict[key], dict):
            event_dict[key] = _redact_dict(event_dict[key])
    return event_dict


def _redact_dict(d: dict[str, Any]) -> dict[str, Any]:
    """Recursively redact sensitive fields from a dictionary."""
    result = {}
    for key, value in d.items():
        if key.lower() in SENSITIVE_FIELDS:
            result[key] = "[REDACTED]"
        elif isinstance(value, dict):
            result[key] = _redact_dict(value)
        else:
            result[key] = value
    return result


def setup_logging() -> None:
    """Configure structlog for the application."""
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        redact_sensitive_data,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.log_format == "json":
        renderer: Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(settings.log_level)

    # Reduce noise from third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a logger instance for the given name."""
    return structlog.get_logger(name)


class LogService:
    """Centralized logging service for the application."""

    def __init__(self, name: str = "mlb_fantasy_api") -> None:
        self._logger = get_logger(name)

    def bind(self, **kwargs: Any) -> "LogService":
        """Bind additional context to the logger."""
        new_service = LogService.__new__(LogService)
        new_service._logger = self._logger.bind(**kwargs)
        return new_service

    def info(self, message: str, **kwargs: Any) -> None:
        """Log at INFO level."""
        self._logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log at WARNING level."""
        self._logger.warning(message, **kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs: Any) -> None:
        """Log at ERROR level with optional exception info."""
        self._logger.error(message, exc_info=exc_info, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log at DEBUG level."""
        self._logger.debug(message, **kwargs)

    def audit(self, action: str, resource: str, **kwargs: Any) -> None:
        """Log security/audit events."""
        self._logger.info(
            "audit_event",
            audit_action=action,
            audit_resource=resource,
            **kwargs,
        )


# Global logger instance
logger = LogService()
