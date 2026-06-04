# shared/brands/models.py
"""
Brand data models and SQLite schema for ContentPilot multi-brand support.

Tables managed here:
  brands            — one row per brand
  brand_profiles    — display/branding config per brand
  brand_credentials — per-brand service credentials (social, WP, etc.)

Migration functions are idempotent — safe to call on every startup.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

_DEFAULT_DB_PATH = "/app/data/db/contentpilot.db"


# ---------------------------------------------------------------------------
# DB helpers (thread-safe: each call opens its own connection)
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
# Schema migrations
# ---------------------------------------------------------------------------

def init_brand_db() -> None:
    """
    Create brand tables and apply migrations to existing scheduler tables.
    Idempotent — safe to call on every startup.
    """
    conn = _connect()

    # --- Core brand tables ---
    conn.execute("""
        CREATE TABLE IF NOT EXISTS brands (
            id         INTEGER PRIMARY KEY,
            name       TEXT    NOT NULL,
            slug       TEXT    UNIQUE NOT NULL,
            enabled    INTEGER NOT NULL DEFAULT 1,
            created_at TEXT    NOT NULL,
            updated_at TEXT    NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS brand_profiles (
            id               INTEGER PRIMARY KEY,
            brand_id         INTEGER NOT NULL,
            website_url      TEXT,
            logo_path        TEXT,
            brand_name       TEXT,
            brand_cta        TEXT,
            branding_layout  TEXT,
            FOREIGN KEY(brand_id) REFERENCES brands(id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS brand_credentials (
            id               INTEGER PRIMARY KEY,
            brand_id         INTEGER NOT NULL,
            credential_type  TEXT    NOT NULL,
            credential_json  TEXT    NOT NULL,
            created_at       TEXT    NOT NULL,
            FOREIGN KEY(brand_id) REFERENCES brands(id)
        )
    """)

    conn.commit()

    # --- Migrate schedules: add brand_id if missing ---
    _add_column_if_missing(conn, "schedules", "brand_id", "INTEGER NOT NULL DEFAULT 1")

    # --- Migrate job_runs: add brand_id if missing (nullable for historical rows) ---
    _add_column_if_missing(conn, "job_runs", "brand_id", "INTEGER")

    conn.close()
    logger.debug("Brand DB initialized | path=%s", _get_db_path())


def _add_column_if_missing(
    conn: sqlite3.Connection, table: str, column: str, definition: str
) -> None:
    """ALTER TABLE only if the column doesn't already exist. SQLite-safe."""
    try:
        cols = {
            row[1]
            for row in conn.execute(f"PRAGMA table_info({table})").fetchall()
        }
        if cols and column not in cols:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
            conn.commit()
            logger.info("DB migration: added %s.%s", table, column)
    except Exception as exc:
        # Table may not exist yet (scheduler tables created later) — that's fine
        logger.debug("Migration skipped for %s.%s: %s", table, column, exc)


def seed_default_brand() -> None:
    """
    Ensure brand_id=1 (GermanySupport) exists.
    Uses env vars for initial values — safe to call multiple times.
    No-op if the brand already exists.
    """
    now = datetime.now(timezone.utc).isoformat()
    conn = _connect()

    existing = conn.execute(
        "SELECT id FROM brands WHERE id = 1"
    ).fetchone()

    if existing:
        conn.close()
        return

    name = os.getenv("DEFAULT_BRAND_NAME", "GermanySupport")
    slug = os.getenv("DEFAULT_BRAND_SLUG", "germanysupport")
    website = os.getenv("DEFAULT_BRAND_WEBSITE", "")

    conn.execute(
        """
        INSERT INTO brands (id, name, slug, enabled, created_at, updated_at)
        VALUES (1, ?, ?, 1, ?, ?)
        """,
        (name, slug, now, now),
    )

    conn.execute(
        """
        INSERT INTO brand_profiles (brand_id, website_url, brand_name)
        VALUES (1, ?, ?)
        """,
        (website, name),
    )

    conn.commit()
    conn.close()
    logger.info(
        "Default brand seeded | id=1 | name=%s | slug=%s", name, slug
    )


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Brand:
    id: int
    name: str
    slug: str
    enabled: bool
    created_at: str
    updated_at: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Brand":
        return cls(
            id=row["id"],
            name=row["name"],
            slug=row["slug"],
            enabled=bool(row["enabled"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@dataclass
class BrandProfile:
    brand_id: int
    website_url: Optional[str] = None
    logo_path: Optional[str] = None
    brand_name: Optional[str] = None
    brand_cta: Optional[str] = None
    branding_layout: Optional[str] = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "BrandProfile":
        return cls(
            brand_id=row["brand_id"],
            website_url=row["website_url"],
            logo_path=row["logo_path"],
            brand_name=row["brand_name"],
            brand_cta=row["brand_cta"],
            branding_layout=row["branding_layout"],
        )


@dataclass
class BrandCredential:
    id: int
    brand_id: int
    credential_type: str
    credential_json: str
    created_at: str

    def as_dict(self) -> dict[str, Any]:
        return json.loads(self.credential_json)

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "BrandCredential":
        return cls(
            id=row["id"],
            brand_id=row["brand_id"],
            credential_type=row["credential_type"],
            credential_json=row["credential_json"],
            created_at=row["created_at"],
        )


@dataclass
class BrandContext:
    """
    The primary execution context for a brand.

    All module execution, publishing, and asset storage flows through this.
    Constructed by shared.brands.service and passed down — never built inside modules.

    Configuration priority:
        BrandContext fields  (highest)
        └── Database values
            └── Environment variables  (fallback for brand_id=1)
    """
    brand_id: int
    brand_slug: str
    brand_name: str
    website_url: str = ""
    logo_path: str = ""
    brand_cta: str = ""
    branding_layout: str = ""

    # Resolved publishing targets (list of target keys for social publisher)
    social_targets: list[str] = field(default_factory=list)

    # WordPress overrides — None means fall back to env
    wp_url: Optional[str] = None
    wp_user: Optional[str] = None
    wp_password: Optional[str] = None
    wp_default_status: str = "draft"

    # AI overrides — None means fall back to env / shared.ai.config
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None

    # Publish mode override — None means fall back to PUBLISH_MODE env
    publish_mode: Optional[str] = None

    def __repr__(self) -> str:
        return (
            f"BrandContext(id={self.brand_id}, slug={self.brand_slug!r}, "
            f"name={self.brand_name!r})"
        )

    @property
    def media_storage_root(self) -> str:
        """Brand-isolated media storage root."""
        base = os.getenv("MEDIA_STORAGE_DIR", "/app/data/media")
        return f"{base}/{self.brand_slug}"

    @property
    def log_fields(self) -> dict:
        """Standard log fields injected into every brand-aware log line."""
        return {"brand_id": self.brand_id, "brand_slug": self.brand_slug}
