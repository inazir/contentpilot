# shared/logging.py
"""
Structured logging for ContentPilot.

Usage:
    from shared.logging import configure_logging, get_logger
    configure_logging()
    logger = get_logger(__name__)
"""

import logging
import os
import sys
from datetime import datetime, timezone


class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        level = record.levelname
        name = record.name
        msg = record.getMessage()

        extras = {
            k: v for k, v in record.__dict__.items()
            if k not in {
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "message",
                "taskName",
            }
        }

        parts = [f"{ts} [{level}] {name}: {msg}"]
        if extras:
            kv = " ".join(f"{k}={v!r}" for k, v in sorted(extras.items()))
            parts.append(kv)

        if record.exc_info:
            parts.append(self.formatException(record.exc_info))

        return " | ".join(parts)


def configure_logging(level: str | None = None) -> None:
    if logging.root.handlers:
        return

    log_level = getattr(
        logging,
        (level or os.getenv("LOG_LEVEL", "INFO")).upper(),
        logging.INFO,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())

    logging.root.setLevel(log_level)
    logging.root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
