#!/usr/bin/env python3
"""
Daily News module entrypoint — Phase 13B update.

Supports three execution modes:

1. Scheduler (brand-injected):
       main(brand_context=ctx)

2. CLI without brand flag (defaults to brand_id=1):
       python -m modules.daily_news.main

3. CLI with brand flag:
       python -m modules.daily_news.main --brand-slug technewshub
       python -m modules.daily_news.main --brand-id 2

Brand resolution priority:
    explicit argument > CLI --brand-slug/--brand-id > brand_id=1 (GermanySupport)

BrandContext is passed into runner.main() so all downstream pipeline steps
(WordPress, social, asset storage) receive brand-aware configuration.
"""

import os
import sys
from typing import Optional

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, "/app")

from shared.logging import configure_logging, get_logger
from shared.models import ExecutionSummary
from shared.runtime import managed_run
from shared.notify import notify_failure

configure_logging(module_name="daily_news")
logger = get_logger("daily_news.main")


def _resolve_brand_context(brand_id: Optional[int] = None, brand_slug: Optional[str] = None):
    """
    Resolve a BrandContext.

    Falls back gracefully to None if shared.brands is not yet initialized —
    this preserves backward compatibility with the Phase 12 env-driven path.
    """
    try:
        from shared.brands.service import (
            get_brand_context,
            get_brand_context_by_slug,
            get_default_brand_context,
        )
        from shared.brands.models import init_brand_db, seed_default_brand

        init_brand_db()
        seed_default_brand()

        if brand_slug:
            return get_brand_context_by_slug(brand_slug)
        if brand_id:
            return get_brand_context(brand_id)
        return get_default_brand_context()

    except Exception as exc:
        logger.warning(
            "brand_resolution_failed | error=%s — running without BrandContext (env fallback)",
            exc,
        )
        return None


def main(brand_context=None) -> ExecutionSummary:
    """
    Run the daily_news module.

    Args:
        brand_context: Optional BrandContext injected by scheduler.
                       When None, resolved from CLI args or defaults to brand_id=1.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Daily News Post Generator")
    parser.add_argument("--dry-run", action="store_true",
                        help="Skip AI generation and publishing")
    parser.add_argument("--topic", type=str, default=None,
                        help="Force a specific topic (bypasses RSS)")
    parser.add_argument("--brand-slug", type=str, default=None,
                        help="Brand slug to execute for (default: germanysupport)")
    parser.add_argument("--brand-id", type=int, default=None,
                        help="Brand ID to execute for (alternative to --brand-slug)")
    args = parser.parse_args()

    # Resolve brand context: injected > CLI > default
    if brand_context is None:
        brand_context = _resolve_brand_context(
            brand_id   = args.brand_id,
            brand_slug = args.brand_slug,
        )

    brand_id   = brand_context.brand_id   if brand_context else 1
    brand_slug = brand_context.brand_slug if brand_context else "germanysupport"

    logger.info(
        "daily_news_main_start | brand_id=%d | brand_slug=%s | dry_run=%s",
        brand_id, brand_slug, args.dry_run,
    )

    try:
        with managed_run("daily_news") as ctx:
            import runner
            summary = runner.main(brand_context=brand_context)

            if summary is None:
                summary = ExecutionSummary(module="daily_news")

            ctx.publish_count = getattr(summary, "social_posts_published", 0)
            summary.log_summary(logger)

    except SystemExit as exc:
        code = int(exc.code) if exc.code is not None else 1
        if code != 0:
            notify_failure("daily_news", f"exit code {code} | brand={brand_slug}")
        sys.exit(code)

    return summary


if __name__ == "__main__":
    main()
