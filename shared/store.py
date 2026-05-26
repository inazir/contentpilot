# shared/store.py
"""
SQLite-backed publish history store.

Provides duplicate detection and publish record tracking.
All data lives in /app/data/db/contentpilot.db which is bind-mounted from the host.
"""

import hashlib
import logging
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

_DEFAULT_DB_PATH = "/app/data/db/contentpilot.db"


def _get_db_path() -> str:
    return os.getenv("STORE_DB_PATH", _DEFAULT_DB_PATH)


def _connect() -> sqlite3.Connection:
    db_path = _get_db_path()
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _connect()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS publish_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_hash TEXT NOT NULL,
            platform TEXT NOT NULL,
            module_name TEXT NOT NULL,
            status TEXT NOT NULL,
            external_post_id TEXT,
            error_message TEXT,
            published_at TEXT NOT NULL,
            UNIQUE(content_hash, platform)
        )
        """
    )
    conn.commit()
    conn.close()
    logger.debug("Database initialized at %s", _get_db_path())


def compute_content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def already_published(content_hash: str, platform: str) -> bool:
    conn = _connect()
    row = conn.execute(
        """
        SELECT id FROM publish_history
        WHERE content_hash = ? AND platform = ? AND status = 'success'
        LIMIT 1
        """,
        (content_hash, platform),
    ).fetchone()
    conn.close()
    return row is not None


def record_publish(
    content_hash: str,
    platform: str,
    module_name: str,
    status: str,
    external_post_id: str | None = None,
    error_message: str | None = None,
) -> None:
    conn = _connect()
    conn.execute(
        """
        INSERT OR REPLACE INTO publish_history
            (content_hash, platform, module_name, status, external_post_id, error_message, published_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            content_hash,
            platform,
            module_name,
            status,
            external_post_id,
            error_message,
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    conn.close()
