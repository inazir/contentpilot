# shared/scheduler/schedule_config.py
"""
Phase 13D-Ext: Converts dashboard schedule config (from brand_content_config)
into APScheduler-compatible cron expressions, and writes/updates the
schedules table so the running scheduler picks up dashboard changes.

Why cron_expression (not interval_hours):
    interval_hours can only express "every N hours" — it cannot encode
    "post at 09:00 and 17:00 on Mon-Fri only". cron_expression handles
    all cases the dashboard supports.

Multiple posting times per day:
    APScheduler does not support multiple times in one cron job. Solution:
    one row in schedules per posting time. So "twice_daily at 09:00 and
    17:00" creates/updates two rows:
        daily_news | brand_id=1 | cron=0 9 * * 0,1,2,3,4
        daily_news | brand_id=1 | cron=0 17 * * 0,1,2,3,4
    The scheduler_service.py picks them both up as separate jobs.
"""
from __future__ import annotations

import logging
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_DEFAULT_DB_PATH = "/app/data/db/contentpilot.db"


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


def schedule_config_to_cron_expressions(schedule: dict) -> list[str]:
    """
    Convert a dashboard schedule dict to one or more cron expressions.

    Args:
        schedule: {
            "frequency": "daily" | "twice_daily" | "weekly",
            "times": ["09:00", "17:00"],
            "active_days": [0, 1, 2, 3, 4],   # 0=Mon, 6=Sun
            "max_posts_per_day": 2
        }

    Returns:
        List of cron expression strings, one per posting time.
        e.g. ["0 9 * * 1,2,3,4,5", "0 17 * * 1,2,3,4,5"]

    Note: APScheduler cron uses 1=Mon...7=Sun (ISO), not 0=Sun like
    standard Unix cron. We convert accordingly.
    """
    times = schedule.get("times") or ["09:00"]
    active_days = schedule.get("active_days") or [0, 1, 2, 3, 4]

    # Convert dashboard day numbers (0=Mon) to APScheduler day names
    # APScheduler accepts: mon,tue,wed,thu,fri,sat,sun
    _DAY_NAMES = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    day_str = ",".join(_DAY_NAMES[d] for d in sorted(active_days) if 0 <= d <= 6)
    if not day_str:
        day_str = "mon"  # safe fallback

    expressions = []
    for t in times:
        parts = t.strip().split(":")
        if len(parts) != 2:
            continue
        try:
            hour, minute = int(parts[0]), int(parts[1])
        except ValueError:
            continue
        # APScheduler cron format: minute hour day month day_of_week
        expressions.append(f"{minute} {hour} * * {day_str}")

    return expressions or ["0 9 * * mon,tue,wed,thu,fri"]  # safe fallback


def sync_schedule_to_db(
    brand_id: int,
    module_name: str,
    schedule: dict,
) -> list[int]:
    """
    Write dashboard schedule config to the schedules table.

    Replaces any existing schedule rows for this (brand_id, module_name)
    pair with new rows derived from the dashboard config. Returns the
    list of new schedule row IDs created.

    Safe to call repeatedly — idempotent per (brand_id, module_name).
    The scheduler service picks up changes on next restart; a live
    reload trigger is a future enhancement.
    """
    cron_exprs = schedule_config_to_cron_expressions(schedule)
    now = datetime.now(timezone.utc).isoformat()
    conn = _connect()

    # Disable (not delete) existing schedule rows for this brand+module
    # so job_runs history foreign keys remain intact.
    conn.execute(
        """
        UPDATE schedules SET enabled = 0, updated_at = ?
        WHERE brand_id = ? AND module_name = ?
        """,
        (now, brand_id, module_name),
    )

    new_ids: list[int] = []
    for expr in cron_exprs:
        cursor = conn.execute(
            """
            INSERT INTO schedules
                (module_name, enabled, interval_hours, cron_expression,
                 brand_id, created_at, updated_at)
            VALUES (?, 1, NULL, ?, ?, ?, ?)
            """,
            (module_name, expr, brand_id, now, now),
        )
        new_ids.append(cursor.lastrowid)
        logger.info(
            "schedule_synced | brand_id=%d | module=%s | cron=%r | row_id=%d",
            brand_id, module_name, expr, cursor.lastrowid,
        )

    conn.commit()
    conn.close()
    return new_ids


def get_active_schedules_for_brand(
    brand_id: int, module_name: str
) -> list[dict]:
    """
    Fetch the currently enabled schedule rows for a brand+module,
    for display in the dashboard.
    """
    conn = _connect()
    rows = conn.execute(
        """
        SELECT id, cron_expression, enabled, created_at
        FROM schedules
        WHERE brand_id = ? AND module_name = ? AND enabled = 1
        ORDER BY id
        """,
        (brand_id, module_name),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def disable_schedules_for_brand(brand_id: int, module_name: str) -> None:
    """Pause all schedules for a brand+module without deleting history."""
    now = datetime.now(timezone.utc).isoformat()
    conn = _connect()
    conn.execute(
        "UPDATE schedules SET enabled = 0, updated_at = ? WHERE brand_id = ? AND module_name = ?",
        (now, brand_id, module_name),
    )
    conn.commit()
    conn.close()
    logger.info("schedules_disabled | brand_id=%d | module=%s", brand_id, module_name)
