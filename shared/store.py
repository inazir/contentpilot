# shared/store.py
"""
SQLite-backed persistence for ContentPilot.

Tables:
  publish_history  — social publishing deduplication (Phase 4)
  rss_articles     — RSS ingestion deduplication (Phase 7)

All tables use CREATE TABLE IF NOT EXISTS so adding new tables
never affects existing data.
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

def _migrate_db(conn: sqlite3.Connection) -> None:
    """
    Apply incremental schema migrations.
    Safe to run on every startup — each step is idempotent.
    """
    # Phase 5 migration: add target_key if publish_history exists without it
    cols = {
        row[1] for row in
        conn.execute("PRAGMA table_info(publish_history)").fetchall()
    }
    if cols and "target_key" not in cols:
        conn.execute(
            "ALTER TABLE publish_history ADD COLUMN target_key TEXT"
        )
        conn.execute(
            "UPDATE publish_history SET target_key = platform WHERE target_key IS NULL"
        )
        conn.commit()
        logger.info("DB migration: added target_key column to publish_history")

def init_db() -> None:
    """
    Create all tables if they don't exist.
    Safe to call on every startup — never drops or alters existing data.
    """
    conn = _connect()

    # Phase 4 — publish history
    conn.execute("""
        CREATE TABLE IF NOT EXISTS publish_history (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            content_hash     TEXT    NOT NULL,
            target_key       TEXT    NOT NULL,
            platform         TEXT    NOT NULL,
            module_name      TEXT    NOT NULL,
            status           TEXT    NOT NULL,
            external_post_id TEXT,
            error_message    TEXT,
            published_at     TEXT    NOT NULL,
            UNIQUE(content_hash, target_key)
        )
    """)

    # Phase 7 — RSS article deduplication
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rss_articles (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            fingerprint  TEXT    NOT NULL UNIQUE,
            title        TEXT    NOT NULL,
            link         TEXT    NOT NULL,
            source       TEXT    NOT NULL,
            published_at TEXT    NOT NULL,
            processed_at TEXT    NOT NULL
        )
    """)

    conn.commit()
    _migrate_db(conn)
    conn.close()
    logger.debug("Database initialized | path=%s", _get_db_path())


# ---------------------------------------------------------------------------
# Publish history (Phase 4 — unchanged)
# ---------------------------------------------------------------------------

def compute_content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def already_published(content_hash: str, target_key: str) -> bool:
    conn = _connect()
    row = conn.execute(
        """
        SELECT id FROM publish_history
        WHERE content_hash = ? AND target_key = ? AND status = 'success'
        LIMIT 1
        """,
        (content_hash, target_key),
    ).fetchone()
    conn.close()
    return row is not None


def record_publish(
    content_hash: str,
    target_key: str,
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
            (content_hash, target_key, platform, module_name, status, external_post_id, error_message, published_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            content_hash,
            target_key,
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


# ---------------------------------------------------------------------------
# RSS deduplication (Phase 7)
# ---------------------------------------------------------------------------

def is_article_processed(fingerprint: str) -> bool:
    """
    Returns True if this article fingerprint has already been processed.
    Check this BEFORE any AI call to avoid wasting tokens on duplicates.
    """
    conn = _connect()
    row = conn.execute(
        "SELECT id FROM rss_articles WHERE fingerprint = ? LIMIT 1",
        (fingerprint,),
    ).fetchone()
    conn.close()
    return row is not None


def mark_article_processed(article) -> None:
    """
    Record that an article has been processed.
    article must have: fingerprint(), title, link, source, published_at
    """
    conn = _connect()
    conn.execute(
        """
        INSERT OR IGNORE INTO rss_articles
            (fingerprint, title, link, source, published_at, processed_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            article.fingerprint(),
            article.title,
            article.link,
            article.source,
            article.published_at,
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    conn.close()
