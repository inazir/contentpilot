"""
Runtime execution tracking and locking for ContentPilot.

Responsibilities:
- module-level file-based locking (prevents overlapping runs)
- execution metadata tracking (persisted to SQLite)
- stale lock detection and cleanup

All data lands in /app/data/ which is bind-mounted from the host.
"""

import logging
import os
import sqlite3
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from shared.config import get_db_path

logger = logging.getLogger(__name__)

_LOCK_DIR = "/app/data/locks"
_STALE_LOCK_SECONDS = 3600   # 1 hour — a job running longer than this is assumed dead


# ---------------------------------------------------------------------------
# Metadata store
# ---------------------------------------------------------------------------

def _runtime_db_path() -> str:
    return os.getenv("RUNTIME_DB_PATH", get_db_path())


def _connect() -> sqlite3.Connection:
    db_path = _runtime_db_path()
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn


def init_runtime_db() -> None:
    """Create runtime_executions table if it doesn't exist."""
    conn = _connect()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS runtime_executions (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            module_name      TEXT    NOT NULL,
            started_at       TEXT    NOT NULL,
            completed_at     TEXT,
            duration_seconds REAL,
            success          INTEGER,
            exit_code        INTEGER,
            publish_count    INTEGER DEFAULT 0,
            retry_count      INTEGER DEFAULT 0,
            error_message    TEXT,
            run_id           TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def record_run_start(module_name: str, run_id: str) -> int:
    """Insert a new execution record. Returns the row id."""
    conn = _connect()
    cursor = conn.execute(
        """
        INSERT INTO runtime_executions
            (module_name, started_at, run_id)
        VALUES (?, ?, ?)
        """,
        (module_name, datetime.now(timezone.utc).isoformat(), run_id),
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def record_run_end(
    row_id:        int,
    success:       bool,
    exit_code:     int,
    duration:      float,
    publish_count: int = 0,
    retry_count:   int = 0,
    error_message: str | None = None,
) -> None:
    conn = _connect()
    conn.execute(
        """
        UPDATE runtime_executions SET
            completed_at     = ?,
            duration_seconds = ?,
            success          = ?,
            exit_code        = ?,
            publish_count    = ?,
            retry_count      = ?,
            error_message    = ?
        WHERE id = ?
        """,
        (
            datetime.now(timezone.utc).isoformat(),
            round(duration, 2),
            1 if success else 0,
            exit_code,
            publish_count,
            retry_count,
            error_message,
            row_id,
        ),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# File-based locking
# ---------------------------------------------------------------------------

def _lock_path(module_name: str) -> Path:
    Path(_LOCK_DIR).mkdir(parents=True, exist_ok=True)
    return Path(_LOCK_DIR) / f"{module_name}.lock"


def _is_stale(lock_file: Path) -> bool:
    """A lock older than _STALE_LOCK_SECONDS is considered stale."""
    try:
        age = time.time() - lock_file.stat().st_mtime
        return age > _STALE_LOCK_SECONDS
    except FileNotFoundError:
        return True


def _acquire_lock(module_name: str) -> bool:
    """
    Try to acquire a lock for module_name.
    Returns True if acquired, False if another run is active.
    """
    lock_file = _lock_path(module_name)

    if lock_file.exists():
        if _is_stale(lock_file):
            logger.warning(
                "Stale lock found for %s (older than %ds) — removing",
                module_name, _STALE_LOCK_SECONDS,
            )
            lock_file.unlink(missing_ok=True)
        else:
            logger.warning(
                "Lock held for %s — another run is active, skipping",
                module_name,
            )
            return False

    lock_file.write_text(str(os.getpid()))
    logger.debug("Lock acquired for %s (pid=%d)", module_name, os.getpid())
    return True


def _release_lock(module_name: str) -> None:
    lock_file = _lock_path(module_name)
    lock_file.unlink(missing_ok=True)
    logger.debug("Lock released for %s", module_name)


# ---------------------------------------------------------------------------
# Context manager: full execution lifecycle
# ---------------------------------------------------------------------------

@dataclass
class RunContext:
    """Passed into module main() so it can report publish count etc."""
    module_name:   str
    run_id:        str
    publish_count: int = 0
    retry_count:   int = 0


@contextmanager
def managed_run(module_name: str):
    """
    Context manager that handles the full job lifecycle:
    - lock acquisition
    - metadata recording (start + end)
    - duration tracking
    - structured logging
    - lock release (always, even on failure)

    Usage:
        with managed_run("daily_news") as ctx:
            ctx.publish_count = run_module()

    Yields a RunContext. Raises SystemExit(1) if lock cannot be acquired.
    """
    import uuid
    run_id = uuid.uuid4().hex[:12]

    init_runtime_db()

    if not _acquire_lock(module_name):
        logger.error(
            "job_skipped | module=%s | reason=lock_held | run_id=%s",
            module_name, run_id,
        )
        raise SystemExit(0)

    start_time = time.monotonic()
    row_id = record_run_start(module_name, run_id)

    logger.info(
        "job_start | module=%s | run_id=%s | pid=%d",
        module_name, run_id, os.getpid(),
    )

    ctx = RunContext(module_name=module_name, run_id=run_id)
    success = False
    exit_code = 1
    error_message = None

    try:
        yield ctx
        success = True
        exit_code = 0

    except SystemExit as exc:
        exit_code = int(exc.code) if exc.code is not None else 1
        success = exit_code == 0
        if not success:
            error_message = f"SystemExit({exit_code})"
        raise

    except Exception as exc:
        error_message = str(exc)
        logger.exception(
            "job_error | module=%s | run_id=%s | error=%s",
            module_name, run_id, exc,
        )
        raise SystemExit(1) from exc

    finally:
        duration = time.monotonic() - start_time

        record_run_end(
            row_id=row_id,
            success=success,
            exit_code=exit_code,
            duration=duration,
            publish_count=ctx.publish_count,
            retry_count=ctx.retry_count,
            error_message=error_message,
        )

        _release_lock(module_name)

        logger.info(
            "job_end | module=%s | run_id=%s | success=%s | duration=%.2fs | published=%d",
            module_name, run_id, success, duration, ctx.publish_count,
        )
