"""
Scheduler data models and access layer for ContentPilot.

Provides Schedule / JobRun dataclasses and all DB operations
needed by the scheduler service, retry manager, and tests.
"""

import logging
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = "/app/data/db/scheduler.db"


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

def _connect() -> sqlite3.Connection:
    """Open (or create) the scheduler database with Row factory."""
    path = os.getenv("SCHEDULER_DB_PATH", DB_PATH)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class Schedule:
    id: int
    module_name: str
    enabled: bool
    interval_hours: int | None
    cron_expression: str | None
    created_at: str
    updated_at: str

    @property
    def trigger_type(self) -> str:
        """Return 'interval' or 'cron' depending on which field is set."""
        if self.cron_expression:
            return "cron"
        return "interval"

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Schedule":
        return cls(
            id=row["id"],
            module_name=row["module_name"],
            enabled=bool(row["enabled"]),
            interval_hours=row["interval_hours"],
            cron_expression=row["cron_expression"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@dataclass
class JobRun:
    id: int
    schedule_id: int
    module_name: str
    status: str
    started_at: str
    completed_at: str | None
    duration_seconds: float | None
    retry_count: int
    error_traceback: str | None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "JobRun":
        return cls(
            id=row["id"],
            schedule_id=row["schedule_id"],
            module_name=row["module_name"],
            status=row["status"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            duration_seconds=row["duration_seconds"],
            retry_count=row["retry_count"],
            error_traceback=row["error_traceback"],
        )


# ---------------------------------------------------------------------------
# DB initialisation
# ---------------------------------------------------------------------------

def init_scheduler_db() -> None:
    """Create scheduler tables if they don't exist (idempotent)."""
    conn = _connect()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            module_name     TEXT    NOT NULL,
            enabled         INTEGER NOT NULL DEFAULT 1,
            interval_hours  INTEGER,
            cron_expression TEXT,
            created_at      TEXT    NOT NULL,
            updated_at      TEXT    NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS job_runs (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            schedule_id      INTEGER NOT NULL,
            module_name      TEXT    NOT NULL,
            status           TEXT    NOT NULL DEFAULT 'running',
            started_at       TEXT    NOT NULL,
            completed_at     TEXT,
            duration_seconds REAL,
            retry_count      INTEGER NOT NULL DEFAULT 0,
            error_traceback  TEXT
        )
    """)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Schedule CRUD
# ---------------------------------------------------------------------------

def load_enabled_schedules() -> list[Schedule]:
    """Return all schedules where enabled = 1."""
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM schedules WHERE enabled = 1"
    ).fetchall()
    conn.close()
    return [Schedule.from_row(r) for r in rows]


def seed_default_schedule() -> None:
    """Insert the default daily_news schedule if the table is empty."""
    conn = _connect()
    count = conn.execute("SELECT COUNT(*) FROM schedules").fetchone()[0]
    if count > 0:
        conn.close()
        return

    hours = int(os.getenv("DAILY_NEWS_SCHEDULE_HOURS", "1"))
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        INSERT INTO schedules
            (module_name, enabled, interval_hours, cron_expression, created_at, updated_at)
        VALUES (?, 1, ?, NULL, ?, ?)
        """,
        ("daily_news", hours, now, now),
    )
    conn.commit()
    conn.close()
    logger.info("Seeded default schedule: daily_news every %d hour(s)", hours)


# ---------------------------------------------------------------------------
# Job run lifecycle
# ---------------------------------------------------------------------------

def insert_job_run(schedule_id: int, module_name: str) -> int:
    """Insert a new job run row with status='running'. Returns the row id."""
    conn = _connect()
    now = datetime.now(timezone.utc).isoformat()
    cursor = conn.execute(
        """
        INSERT INTO job_runs
            (schedule_id, module_name, status, started_at, retry_count)
        VALUES (?, ?, 'running', ?, 0)
        """,
        (schedule_id, module_name, now),
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def update_job_run(
    run_id: int,
    status: str,
    duration_seconds: float | None = None,
    retry_count: int | None = None,
    error_traceback: str | None = None,
) -> None:
    """Update a job run after execution completes."""
    conn = _connect()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        UPDATE job_runs SET
            status = ?,
            completed_at = ?,
            duration_seconds = ?,
            retry_count = COALESCE(?, retry_count),
            error_traceback = ?
        WHERE id = ?
        """,
        (status, now, duration_seconds, retry_count, error_traceback, run_id),
    )
    conn.commit()
    conn.close()


def get_job_run(run_id: int) -> JobRun | None:
    """Fetch a single job run by id."""
    conn = _connect()
    row = conn.execute("SELECT * FROM job_runs WHERE id = ?", (run_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    return JobRun.from_row(row)


def count_retries_for_schedule(schedule_id: int) -> int:
    """Return the maximum retry_count across all runs for a schedule."""
    conn = _connect()
    row = conn.execute(
        "SELECT COALESCE(MAX(retry_count), 0) AS cnt FROM job_runs WHERE schedule_id = ?",
        (schedule_id,),
    ).fetchone()
    conn.close()
    return row["cnt"] if row else 0