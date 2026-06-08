# shared/logging.py
"""
Structured logging for ContentPilot.

Writes to:
  - stdout (always)
  - data/logs/<module>.log (rotating, when LOG_FILE_ENABLED=true)

Usage:
    from shared.logging import configure_logging, get_logger
    configure_logging(module_name="daily_news")
    logger = get_logger(__name__)
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


_LOG_DIR = "/app/data/logs"
_MAX_BYTES = 5 * 1024 * 1024
_BACKUP_COUNT = 5


class StructuredFormatter(logging.Formatter):
    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        timestamp = datetime.fromtimestamp(record.created, timezone.utc)
        return timestamp.strftime(datefmt or "%Y-%m-%dT%H:%M:%SZ")

    def format(self, record: logging.LogRecord) -> str:
        ts = self.formatTime(record, "%Y-%m-%dT%H:%M:%SZ")
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


def configure_logging(
    module_name: str | None = None,
    level: str | None = None,
) -> None:
    if logging.root.handlers:
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

    log_level = getattr(
        logging,
        (level or os.getenv("LOG_LEVEL", "INFO")).upper(),
        logging.INFO,
    )

    formatter = StructuredFormatter()

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    handlers = [stdout_handler]

    file_enabled = os.getenv("LOG_FILE_ENABLED", "true").strip().lower() in {"1", "true", "yes"}
    if file_enabled and module_name:
        log_dir = Path(os.getenv("LOG_DIR", _LOG_DIR))
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            log_path = log_dir / f"{module_name}.log"
            file_handler = logging.handlers.RotatingFileHandler(
                filename=str(log_path),
                maxBytes=_MAX_BYTES,
                backupCount=_BACKUP_COUNT,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)
        except Exception as exc:
            print(
                f"WARNING: Could not configure file logging to {log_dir}: {exc}",
                file=sys.stderr,
            )

    logging.root.setLevel(log_level)
    for handler in handlers:
        logging.root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
