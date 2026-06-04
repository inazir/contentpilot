# shared/scheduler/models.py
"""
Data models and schema definitions for the ContentPilot scheduler.

Phase 13B additions:
  - schedules.brand_id (migration applied by init_brand_db in shared/brands/models.py)
  - job_runs.brand_id  (migration applied by init_brand_db)
  - Schedule dataclass gains brand_id field
  - JobRun dataclass gains brand_id field

The actual ALTER TABLE migrations are handled by shared.brands.models.init_brand_db()
to keep all schema evolution in one place.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import logging
import os

logger = logging.getLogger(__name__)

_DEFAULT_DB_PATH = "/app/data/db/contentpilot.db"


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def _get_db_path() -> str:
    return os.getenv("STORE_DB_PATH", _DEFAULT_DB_PATH)


def _connect() -> sqlite3.Connection:
    db_path = _get_db_path()
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=10.0, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Schema init (base tables only — brand columns added by init_brand_db)
# ---------------------------------------------------------------------------

def init_scheduler_db() -> None:
    """
    Create base scheduler tables if they don't exist.
    Safe to call on every startup — idempotent.

    Phase 13B: adds brand_id columns to both tables via migration
    (in case the tables existed before the multi-brand upgrade).
    """
    conn = _connect()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            module_name      TEXT    NOT NULL,
            enabled          INTEGER NOT NULL DEFAULT 1,
            interval_hours   INTEGER,
            cron_expression  TEXT,
            created_at       TEXT    NOT NULL,
            updated_at       TEXT    NOT NULL,
            CHECK (
                (interval_hours IS NOT NULL AND cron_expression IS NULL)
                OR
                (interval_hours IS NULL AND cron_expression IS NOT NULL)
            )
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS job_runs (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            schedule_id      INTEGER,
            module_name      TEXT    NOT NULL,
            status           TEXT    NOT NULL,
            started_at       TEXT    NOT NULL,
            completed_at     TEXT,
            duration_seconds REAL,
            retry_count      INTEGER DEFAULT 0,
            error_traceback  TEXT,
            FOREIGN KEY (schedule_id) REFERENCES schedules(id)
        )
    """)
    conn.commit()

    # Phase 13B: add brand_id columns if the tables existed before migration
    cols = {r[1] for r in conn.execute("PRAGMA table_info(schedules)").fetchall()}
    if "brand_id" not in cols:
        conn.execute("ALTER TABLE schedules ADD COLUMN brand_id INTEGER NOT NULL DEFAULT 1")
    cols = {r[1] for r in conn.execute("PRAGMA table_info(job_runs)").fetchall()}
    if "brand_id" not in cols:
        conn.execute("ALTER TABLE job_runs ADD COLUMN brand_id INTEGER")
    conn.commit()

    conn.close()
    logger.debug("Scheduler DB initialized | path=%s", _get_db_path())


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class Schedule:
    id: int
    module_name: str
    enabled: bool
    interval_hours: Optional[int]
    cron_expression: Optional[str]
    created_at: str
    updated_at: str
    brand_id: int = 1  # Phase 13B: defaults to GermanySupport

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Schedule":
        # brand_id may be absent from older rows (before migration)
        brand_id = 1
        try:
            brand_id = row["brand_id"] or 1
        except (IndexError, KeyError):
            pass
        return cls(
            id=row["id"],
            module_name=row["module_name"],
            enabled=bool(row["enabled"]),
            interval_hours=row["interval_hours"],
            cron_expression=row["cron_expression"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            brand_id=brand_id,
        )

    @property
    def trigger_type(self) -> str:
        return "interval" if self.interval_hours is not None else "cron"


@dataclass
class JobRun:
    id: int
    schedule_id: Optional[int]
    module_name: str
    status: str  # running | completed | failed | retrying | locked
    started_at: str
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    retry_count: int = 0
    error_traceback: Optional[str] = None
    brand_id: Optional[int] = None  # Phase 13B addition

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "JobRun":
        brand_id = None
        try:
            brand_id = row["brand_id"]
        except (IndexError, KeyError):
            pass
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
            brand_id=brand_id,
        )


# ---------------------------------------------------------------------------
# DB operations (each opens its own connection — thread-safe)
# ---------------------------------------------------------------------------

def load_enabled_schedules() -> list[Schedule]:
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM schedules WHERE enabled = 1"
    ).fetchall()
    conn.close()
    return [Schedule.from_row(r) for r in rows]


def seed_default_schedule(module_name: str = "daily_news", interval_hours: int = 1) -> None:
    """
    Insert a default schedule (brand_id=1) if schedules table is empty.
    """
    hours = int(os.getenv("DAILY_NEWS_SCHEDULE_HOURS", str(interval_hours)))
    now = datetime.now(timezone.utc).isoformat()
    conn = _connect()
    count = conn.execute("SELECT COUNT(*) FROM schedules").fetchone()[0]
    if count == 0:
        # Insert with brand_id=1 if column exists, else without
        try:
            conn.execute(
                """
                INSERT INTO schedules
                    (module_name, enabled, interval_hours, cron_expression, brand_id, created_at, updated_at)
                VALUES (?, 1, ?, NULL, 1, ?, ?)
                """,
                (module_name, hours, now, now),
            )
        except Exception:
            # brand_id column may not exist yet if migration hasn't run
            conn.execute(
                """
                INSERT INTO schedules
                    (module_name, enabled, interval_hours, cron_expression, created_at, updated_at)
                VALUES (?, 1, ?, NULL, ?, ?)
                """,
                (module_name, hours, now, now),
            )
        conn.commit()
        logger.info(
            "scheduler_seed | module=%s | interval_hours=%d | brand_id=1",
            module_name, hours,
        )
    conn.close()


def insert_job_run(
    schedule_id: Optional[int],
    module_name: str,
    brand_id: Optional[int] = None,
) -> int:
    """Write a 'running' record. Returns the new row id."""
    now = datetime.now(timezone.utc).isoformat()
    conn = _connect()
    try:
        cursor = conn.execute(
            """
            INSERT INTO job_runs
                (schedule_id, module_name, status, started_at, brand_id)
            VALUES (?, ?, 'running', ?, ?)
            """,
            (schedule_id, module_name, now, brand_id),
        )
    except Exception:
        # brand_id column may not exist yet
        cursor = conn.execute(
            """
            INSERT INTO job_runs (schedule_id, module_name, status, started_at)
            VALUES (?, ?, 'running', ?)
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
    duration_seconds: float,
    retry_count: int = 0,
    error_traceback: Optional[str] = None,
) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn = _connect()
    conn.execute(
        """
        UPDATE job_runs SET
            status           = ?,
            completed_at     = ?,
            duration_seconds = ?,
            retry_count      = ?,
            error_traceback  = ?
        WHERE id = ?
        """,
        (status, now, round(duration_seconds, 2), retry_count, error_traceback, run_id),
    )
    conn.commit()
    conn.close()


def get_job_run(run_id: int) -> Optional[JobRun]:
    conn = _connect()
    row = conn.execute(
        "SELECT * FROM job_runs WHERE id = ?", (run_id,)
    ).fetchone()
    conn.close()
    return JobRun.from_row(row) if row else None


def count_retries_for_schedule(schedule_id: int) -> int:
    conn = _connect()
    row = conn.execute(
        """
        SELECT retry_count FROM job_runs
        WHERE schedule_id = ?
        ORDER BY id DESC LIMIT 1
        """,
        (schedule_id,),
    ).fetchone()
    conn.close()
    return row["retry_count"] if row else 0
