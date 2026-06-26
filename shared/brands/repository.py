# shared/brands/repository.py
"""
Brand persistence layer.

RULE: Only this module and shared/brands/service.py may query brand tables.
No module may import from here directly.

All functions open their own DB connection (thread-safe for APScheduler workers).
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Optional

from .models import (
    Brand,
    BrandCredential,
    BrandProfile,
    ContentConfig,
    _connect,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Brands
# ---------------------------------------------------------------------------

def get_brand_by_id(brand_id: int) -> Optional[Brand]:
    conn = _connect()
    row = conn.execute(
        "SELECT * FROM brands WHERE id = ?", (brand_id,)
    ).fetchone()
    conn.close()
    return Brand.from_row(row) if row else None


def get_brand_by_slug(slug: str) -> Optional[Brand]:
    conn = _connect()
    row = conn.execute(
        "SELECT * FROM brands WHERE slug = ?", (slug.lower(),)
    ).fetchone()
    conn.close()
    return Brand.from_row(row) if row else None


def get_all_enabled_brands() -> list[Brand]:
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM brands WHERE enabled = 1 ORDER BY id"
    ).fetchall()
    conn.close()
    return [Brand.from_row(r) for r in rows]


def create_brand(name: str, slug: str) -> int:
    """Insert a brand row. Returns the new brand_id."""
    now = datetime.now(timezone.utc).isoformat()
    conn = _connect()
    cursor = conn.execute(
        """
        INSERT INTO brands (name, slug, enabled, created_at, updated_at)
        VALUES (?, ?, 1, ?, ?)
        """,
        (name, slug.lower(), now, now),
    )
    conn.commit()
    brand_id = cursor.lastrowid
    conn.close()
    logger.info("brand_created | id=%d | name=%s | slug=%s", brand_id, name, slug)
    return brand_id


def update_brand_timestamp(brand_id: int) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn = _connect()
    conn.execute(
        "UPDATE brands SET updated_at = ? WHERE id = ?", (now, brand_id)
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Brand Profiles
# ---------------------------------------------------------------------------

def get_profile(brand_id: int) -> Optional[BrandProfile]:
    conn = _connect()
    row = conn.execute(
        "SELECT * FROM brand_profiles WHERE brand_id = ?", (brand_id,)
    ).fetchone()
    conn.close()
    return BrandProfile.from_row(row) if row else None


def upsert_profile(
    brand_id: int,
    website_url: str = "",
    logo_path: str = "",
    brand_name: str = "",
    brand_cta: str = "",
    branding_layout: str = "",
) -> None:
    conn = _connect()
    existing = conn.execute(
        "SELECT id FROM brand_profiles WHERE brand_id = ?", (brand_id,)
    ).fetchone()

    if existing:
        conn.execute(
            """
            UPDATE brand_profiles SET
                website_url     = ?,
                logo_path       = ?,
                brand_name      = ?,
                brand_cta       = ?,
                branding_layout = ?
            WHERE brand_id = ?
            """,
            (website_url, logo_path, brand_name, brand_cta, branding_layout, brand_id),
        )
    else:
        conn.execute(
            """
            INSERT INTO brand_profiles
                (brand_id, website_url, logo_path, brand_name, brand_cta, branding_layout)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (brand_id, website_url, logo_path, brand_name, brand_cta, branding_layout),
        )

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Brand Credentials
# ---------------------------------------------------------------------------

def get_credentials(brand_id: int, credential_type: str) -> Optional[BrandCredential]:
    conn = _connect()
    row = conn.execute(
        """
        SELECT * FROM brand_credentials
        WHERE brand_id = ? AND credential_type = ?
        ORDER BY id DESC LIMIT 1
        """,
        (brand_id, credential_type),
    ).fetchone()
    conn.close()
    return BrandCredential.from_row(row) if row else None


def get_all_credentials(brand_id: int) -> list[BrandCredential]:
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM brand_credentials WHERE brand_id = ? ORDER BY credential_type",
        (brand_id,),
    ).fetchall()
    conn.close()
    return [BrandCredential.from_row(r) for r in rows]


def upsert_credential(brand_id: int, credential_type: str, data: dict) -> None:
    """
    Store credentials as a JSON blob.
    Phase 13B stores plaintext — future phases may encrypt.
    """
    now = datetime.now(timezone.utc).isoformat()
    credential_json = json.dumps(data)
    conn = _connect()

    existing = conn.execute(
        """
        SELECT id FROM brand_credentials
        WHERE brand_id = ? AND credential_type = ?
        """,
        (brand_id, credential_type),
    ).fetchone()

    if existing:
        conn.execute(
            """
            UPDATE brand_credentials
            SET credential_json = ?, created_at = ?
            WHERE id = ?
            """,
            (credential_json, now, existing["id"]),
        )
    else:
        conn.execute(
            """
            INSERT INTO brand_credentials (brand_id, credential_type, credential_json, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (brand_id, credential_type, credential_json, now),
        )

    conn.commit()
    conn.close()
    logger.info(
        "credential_upserted | brand_id=%d | type=%s", brand_id, credential_type
    )


# ---------------------------------------------------------------------------
# Brand Content Config (Phase 13C — dashboard)
# ---------------------------------------------------------------------------

def get_content_config(brand_id: int, platform: str) -> Optional[ContentConfig]:
    """Fetch content strategy config for one brand+platform. None if unset."""
    conn = _connect()
    row = conn.execute(
        """
        SELECT * FROM brand_content_config
        WHERE brand_id = ? AND platform = ?
        """,
        (brand_id, platform),
    ).fetchone()
    conn.close()
    return ContentConfig.from_row(row) if row else None


def get_all_content_config(brand_id: int) -> list[ContentConfig]:
    """Fetch content config for every platform configured for this brand."""
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM brand_content_config WHERE brand_id = ? ORDER BY platform",
        (brand_id,),
    ).fetchall()
    conn.close()
    return [ContentConfig.from_row(r) for r in rows]


def upsert_content_config(brand_id: int, platform: str, data: dict) -> None:
    """
    Store content strategy config (topics, hashtags, CTA text, image
    overlay text, first comment template, etc.) as a JSON blob.

    Caller (dashboard layer) owns field validation — this function only
    persists whatever dict it's given.
    """
    now = datetime.now(timezone.utc).isoformat()
    config_json = json.dumps(data)
    conn = _connect()

    existing = conn.execute(
        """
        SELECT id FROM brand_content_config
        WHERE brand_id = ? AND platform = ?
        """,
        (brand_id, platform),
    ).fetchone()

    if existing:
        conn.execute(
            """
            UPDATE brand_content_config
            SET config_json = ?, updated_at = ?
            WHERE id = ?
            """,
            (config_json, now, existing["id"]),
        )
    else:
        conn.execute(
            """
            INSERT INTO brand_content_config (brand_id, platform, config_json, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (brand_id, platform, config_json, now),
        )

    conn.commit()
    conn.close()
    logger.info(
        "content_config_upserted | brand_id=%d | platform=%s", brand_id, platform
    )


# ---------------------------------------------------------------------------
# Scheduler brand tracking
# ---------------------------------------------------------------------------

def record_job_run_brand(run_id: int, brand_id: int) -> None:
    """Update a job_runs row with its brand_id after execution."""
    conn = _connect()
    conn.execute(
        "UPDATE job_runs SET brand_id = ? WHERE id = ?", (brand_id, run_id)
    )
    conn.commit()
    conn.close()
