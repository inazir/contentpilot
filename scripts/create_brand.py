#!/usr/bin/env python3
# scripts/create_brand.py
"""
Brand management CLI for ContentPilot.

Usage (non-interactive):
    python scripts/create_brand.py \
        --name "TechNewsHub" \
        --slug "technewshub" \
        --website "https://technewshub.com"

Usage (interactive — omit any flag to be prompted):
    python scripts/create_brand.py

Creates:
    - brand row
    - brand_profile row
    - default schedule (interval_hours=1)

Optional credential setup (prompted if --add-credentials flag given):
    - social_targets
    - wordpress
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, "/app")

from shared.brands.models import init_brand_db, seed_default_brand
from shared.brands.repository import (
    create_brand,
    get_brand_by_slug,
    upsert_profile,
    upsert_credential,
)
from shared.brands.validation import validate_name, validate_slug, validate_url
from shared.scheduler.models import init_scheduler_db, _connect as sched_connect
from datetime import datetime, timezone


def _prompt(label: str, default: str = "", required: bool = False) -> str:
    hint = f" [{default}]" if default else ""
    while True:
        val = input(f"{label}{hint}: ").strip() or default
        if required and not val:
            print("  This field is required.")
            continue
        return val


def _create_schedule(brand_id: int, interval_hours: int) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn = sched_connect()
    try:
        conn.execute(
            """
            INSERT INTO schedules
                (module_name, enabled, interval_hours, cron_expression, brand_id, created_at, updated_at)
            VALUES ('daily_news', 1, ?, NULL, ?, ?, ?)
            """,
            (interval_hours, brand_id, now, now),
        )
    except Exception:
        conn.execute(
            """
            INSERT INTO schedules
                (module_name, enabled, interval_hours, cron_expression, created_at, updated_at)
            VALUES ('daily_news', 1, ?, NULL, ?, ?)
            """,
            (interval_hours, now, now),
        )
    conn.commit()
    conn.close()
    print(f"  ✓ Default schedule created | module=daily_news | interval={interval_hours}h | brand_id={brand_id}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a new ContentPilot brand",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/create_brand.py --name "TechNewsHub" --website "https://technewshub.com"
  python scripts/create_brand.py  # fully interactive
        """,
    )
    parser.add_argument("--name",    type=str, help="Brand display name")
    parser.add_argument("--slug",    type=str, help="Brand slug (auto-derived from name if omitted)")
    parser.add_argument("--website", type=str, default="", help="Website URL")
    parser.add_argument("--logo",    type=str, default="", help="Path to logo file")
    parser.add_argument("--cta",     type=str, default="", help="Call-to-action text")
    parser.add_argument("--schedule-hours", type=int, default=1,
                        help="Default publishing interval in hours (default: 1)")
    parser.add_argument("--add-credentials", action="store_true",
                        help="Interactively add social/WP credentials after creation")
    args = parser.parse_args()

    print("\n ContentPilot — Create Brand")
    print("=" * 40)

    # Initialize DB
    init_brand_db()
    seed_default_brand()
    init_scheduler_db()

    # --- Name ---
    name = args.name
    if not name:
        name = _prompt("Brand name", required=True)
    try:
        name = validate_name(name)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # --- Slug ---
    default_slug = name.lower().replace(" ", "").replace("-", "")
    slug = args.slug or _prompt(f"Brand slug", default=default_slug)
    try:
        slug = validate_slug(slug)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Check slug uniqueness
    existing = get_brand_by_slug(slug)
    if existing:
        print(f"Error: Brand with slug '{slug}' already exists (id={existing.id}).")
        sys.exit(1)

    # --- Website ---
    website = args.website or _prompt("Website URL (optional)")
    try:
        website = validate_url(website)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    logo     = args.logo or _prompt("Logo path (optional)")
    cta      = args.cta  or _prompt("Brand CTA text (optional)")

    # --- Create ---
    print()
    print(f"Creating brand: {name!r} (slug={slug!r})")

    brand_id = create_brand(name=name, slug=slug)
    print(f"  ✓ Brand created | id={brand_id}")

    upsert_profile(
        brand_id        = brand_id,
        website_url     = website,
        logo_path       = logo,
        brand_name      = name,
        brand_cta       = cta,
        branding_layout = "",
    )
    print(f"  ✓ Profile created")

    _create_schedule(brand_id, args.schedule_hours)

    # --- Optional credentials ---
    if args.add_credentials:
        print("\n--- Social Targets ---")
        raw_targets = _prompt("Comma-separated social target keys (e.g. tn_facebook_main)")
        if raw_targets:
            targets = [t.strip() for t in raw_targets.split(",") if t.strip()]
            upsert_credential(brand_id, "social_targets", {"targets": targets})
            print(f"  ✓ Social targets saved: {targets}")

        print("\n--- WordPress Credentials ---")
        wp_url = _prompt("WordPress URL (leave blank to skip)")
        if wp_url:
            wp_user = _prompt("WordPress username", required=True)
            wp_pass = _prompt("WordPress app password", required=True)
            wp_status = _prompt("Default post status", default="draft")
            upsert_credential(brand_id, "wordpress", {
                "url":            wp_url,
                "user":           wp_user,
                "password":       wp_pass,
                "default_status": wp_status,
            })
            print("  ✓ WordPress credentials saved")

    print()
    print(f"Brand '{name}' created successfully.")
    print(f"  brand_id  = {brand_id}")
    print(f"  slug      = {slug}")
    print()
    print("To run this brand manually:")
    print(f"  python modules/daily_news/main.py --brand-slug {slug}")
    print()
    print("To schedule this brand, the scheduler will pick it up automatically")
    print("on next restart (schedule already created).")


if __name__ == "__main__":
    main()
