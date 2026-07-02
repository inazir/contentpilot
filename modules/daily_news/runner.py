# modules/daily_news/runner.py
"""
Daily News runner — Phase 13B: BrandContext-aware pipeline.

All configuration now flows through BrandContext with env fallback for brand_id=1.

Changes from Phase 11B:
  - main() accepts optional brand_context parameter
  - _get_mode(), _get_publish_platforms(), _get_media_config(),
    _get_wordpress_config() all accept BrandContext and override env defaults
  - Asset storage uses brand-isolated paths via brand_context.media_storage_root
  - Every major log line includes brand_id and brand_slug
  - Fully backward-compatible: calling main() with no args uses brand_id=1 + env
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from typing import Optional, TYPE_CHECKING

sys.path.insert(0, "/app")

from shared.logging import configure_logging, get_logger
from shared.store import (
    init_db,
    is_article_processed,
    mark_article_processed,
    compute_content_hash,
    already_published,
    record_publish,
)
from shared.config import get_publish_mode, get_media_config
from shared.social import publish_post
from shared.models import ExecutionSummary
from shared.ingestion import fetch_feeds, get_feed_urls, get_max_articles, get_feed_timeout
from generator import generate_news_post, summarize_article
from shared.brands import get_content_config

if TYPE_CHECKING:
    from shared.brands.models import BrandContext

configure_logging(module_name="daily_news")
logger = get_logger("daily_news")

_FALLBACK_TOPICS = [
    "registering your address in Germany (Anmeldung) and why it matters",
    "opening a bank account in Germany as a foreigner",
    "health insurance options in Germany for expats",
    "public transport tips for newcomers in Germany",
    "filing taxes in Germany for the first time",
]


# ---------------------------------------------------------------------------
# Config resolution helpers (BrandContext → env fallback)
# ---------------------------------------------------------------------------

def _get_mode(brand_context: Optional["BrandContext"] = None) -> str:
    # BrandContext doesn't carry a mode override for "draft/publish" — use env
    return os.getenv("DAILY_NEWS_MODE", "draft").strip().lower()


def _get_publish_platforms(brand_context: Optional["BrandContext"] = None) -> list[str]:
    if brand_context and brand_context.social_targets:
        return brand_context.social_targets
    raw = os.getenv("DAILY_NEWS_TARGETS", "").strip()
    return [t.strip() for t in raw.split(",") if t.strip()] if raw else []


def _resolve_facebook_content_config(brand_context) -> dict | None:
    """
    Returns the brand's saved Facebook content config, or None if
    no brand_context is available or no config has been saved yet.
    None means generator.py falls back to its hardcoded defaults —
    this preserves exact existing behavior for any brand with no
    dashboard config saved.
    """
    if not brand_context:
        return None
    try:
        config = get_content_config(brand_context.brand_id, "facebook")
    except Exception as exc:
        logger.warning(
            "Could not load content config for brand %s: %s — "
            "falling back to default topics/prompt",
            brand_context.brand_id, exc,
        )
        return None
    return config.as_dict() if config else None


def _brand_log(brand_context: Optional["BrandContext"] = None) -> str:
    if brand_context:
        return f" | brand_id={brand_context.brand_id} | brand_slug={brand_context.brand_slug}"
    return ""


def _get_brand_media_config(brand_context: Optional["BrandContext"] = None):
    """
    Return media config, with brand storage root override if BrandContext is present.

    Since shared/content is not in scope, we return the existing media_cfg object
    and patch its storage_dir if the brand provides an override.
    """
    media_cfg = get_media_config()

    if brand_context:
        # Patch storage root to brand-isolated path
        # Uses a simple attribute override — works as long as get_media_config()
        # returns an object (dataclass/SimpleNamespace) with a storage_dir field.
        try:
            object.__setattr__(media_cfg, "storage_dir", brand_context.media_storage_root)
        except (AttributeError, TypeError):
            try:
                media_cfg.storage_dir = brand_context.media_storage_root
            except AttributeError:
                pass  # media_cfg may be frozen — best-effort

    return media_cfg


def _get_wordpress_config_for_brand(brand_context: Optional["BrandContext"] = None):
    """
    Return WordPress config, with BrandContext credential override.

    For brand_id=1: falls back to existing get_wordpress_config() (env-driven).
    For brand_id>1: builds WP config entirely from brand_context.
    """
    from shared.config import get_wordpress_config
    try:
        base_cfg = get_wordpress_config()
    except Exception:
        base_cfg = None

    if brand_context and (brand_context.wp_url or brand_context.wp_user):
        # Build a minimal WP config object from BrandContext
        # This follows whatever interface get_wordpress_config() returns
        try:
            from shared.config import WordPressConfig
            return WordPressConfig(
                url      = brand_context.wp_url or "",
                user     = brand_context.wp_user or "",
                password = brand_context.wp_password or "",
            )
        except (ImportError, TypeError):
            # WordPressConfig may have a different signature — return base
            pass

    return base_cfg


# ---------------------------------------------------------------------------
# Asset pipeline helpers (unchanged from Phase 11B, media_cfg now brand-aware)
# ---------------------------------------------------------------------------

def _build_asset_bundle(
    title: str,
    summary: str,
    article_body: str,
    keywords: list[str],
    media_cfg,
    summary_obj: ExecutionSummary,
    brand_context: Optional["BrandContext"] = None,
    content_config: dict | None = None,
):
    if not media_cfg.enabled:
        return None
    try:
        from shared.content import AssetBuilder
        from shared.content.storage import AssetStorage
        from pathlib import Path

        storage = AssetStorage(storage_root=Path(media_cfg.storage_dir))
        builder = AssetBuilder(storage=storage)

        logger.info(
            "asset_pipeline_start | title=%r | branding=%s | ads=%s%s",
            title, media_cfg.branding_enabled, media_cfg.ads_enabled,
            _brand_log(brand_context),
        )

        result = builder.build(
            title            = title,
            summary          = summary,
            article_body     = article_body,
            keywords         = keywords,
            branding_enabled = media_cfg.branding_enabled,
            ads_enabled      = media_cfg.ads_enabled,
        )

        if result.success and result.bundle:
            summary_obj.bundles_created += 1
            summary_obj.assets_generated += result.assets_written
            summary_obj.images_generated += sum(
                1 for k in result.bundle.assets
                if k not in {"metadata", "article"}
            )
            logger.info(
                "asset_bundle_stored | slug=%s | assets=%d | dir=%s%s",
                result.bundle.article_slug, result.assets_written,
                result.storage_dir, _brand_log(brand_context),
            )
        else:
            logger.warning(
                "asset_bundle_failed | title=%r | error=%s%s",
                title, result.error_message, _brand_log(brand_context),
            )

        return result

    except Exception as exc:
        logger.warning("asset_pipeline_error | title=%r | error=%s%s", title, exc, _brand_log(brand_context))
        return None


def _select_social_image(asset_result) -> tuple[bytes | None, str]:
    if asset_result is None or not asset_result.success:
        return None, ""
    bundle = asset_result.bundle
    if bundle is None:
        return None, ""
    for key, filename in [
        ("facebook_landscape", "facebook_landscape.jpg"),
        ("featured",           "featured.jpg"),
        ("facebook_square",    "facebook_square.jpg"),
    ]:
        asset = bundle.assets.get(key)
        if asset and asset.exists():
            try:
                return asset.path.read_bytes(), filename
            except Exception:
                pass
    return None, ""


def _upload_featured_image(
    asset_result,
    title: str,
    media_cfg,
    summary_obj: ExecutionSummary,
    brand_context: Optional["BrandContext"] = None,
    content_config: dict | None = None,
) -> int | None:
    if not media_cfg.enabled or not media_cfg.featured_images:
        return None
    if asset_result is None or not asset_result.success:
        return None
    bundle = asset_result.bundle
    if bundle is None or bundle.featured_image is None:
        return None
    try:
        wp_config = _get_wordpress_config_for_brand(brand_context)
        if wp_config is None:
            return None
        from shared.content.wordpress_media import WordPressMediaService
        svc = WordPressMediaService(wp_config)
        result = svc.upload_asset_file(
            asset_file=bundle.featured_image,
            alt_text=title,
            title=title,
        )
        if result.success:
            summary_obj.images_uploaded += 1
            logger.info(
                "wp_media_upload_success | media_id=%d | url=%s%s",
                result.media_id, result.url, _brand_log(brand_context),
            )
            return result.media_id
        else:
            summary_obj.wordpress_media_failures += 1
            return None
    except Exception as exc:
        logger.warning("wp_media_upload_error | title=%r | error=%s%s", title, exc, _brand_log(brand_context))
        return None


def _publish_to_wordpress(
    title: str,
    post_text: str,
    featured_media_id: int | None,
    summary_obj: ExecutionSummary,
    brand_context: Optional["BrandContext"] = None,
    content_config: dict | None = None,
) -> str | None:
    wp_enabled = os.getenv("DAILY_NEWS_ENABLE_WORDPRESS", "false").strip().lower()
    if wp_enabled not in {"1", "true", "yes"}:
        # Also check if brand has WP credentials
        if not (brand_context and brand_context.wp_url):
            return None

    try:
        from shared.wordpress.client import WordPressClient
        from shared.wordpress.models import PostRequest

        wp_config = _get_wordpress_config_for_brand(brand_context)
        if not wp_config:
            return None

        client = WordPressClient(wp_config)
        status = (
            brand_context.wp_default_status
            if brand_context and brand_context.wp_default_status
            else os.getenv("DAILY_NEWS_WORDPRESS_STATUS", "draft")
        )

        post_request = PostRequest(title=title, content=post_text, status=status)
        if featured_media_id is not None:
            post_request.featured_media = featured_media_id

        response = client.create_post(post_request)

        if response.success:
            summary_obj.wordpress_posts_created += 1
            if response.status == "publish":
                summary_obj.wordpress_posts_published += 1
            logger.info(
                "wordpress_publish_success | post_id=%s | status=%s%s",
                response.wordpress_post_id, response.status, _brand_log(brand_context),
            )
            return response.status
        return None

    except (ValueError, ImportError, AttributeError):
        return None
    except Exception as exc:
        logger.warning("wp_post_error | title=%r | error=%s%s", title, exc, _brand_log(brand_context))
        return None


# ---------------------------------------------------------------------------
# Main entry points
# ---------------------------------------------------------------------------

def main(brand_context: Optional["BrandContext"] = None) -> ExecutionSummary:
    """
    Run the daily_news pipeline.

    Args:
        brand_context: Optional BrandContext. When None, uses env variables
                       (backward-compatible with Phase 12).
    """
    parser = argparse.ArgumentParser(description="Daily News Post Generator")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--topic", type=str, default=None)
    # Brand args are consumed by main.py — ignored here if present
    parser.add_argument("--brand-slug", type=str, default=None)
    parser.add_argument("--brand-id", type=int, default=None)
    args = parser.parse_args()

    mode      = _get_mode(brand_context)
    media_cfg = _get_brand_media_config(brand_context)
    summary   = ExecutionSummary(module="daily_news", dry_run=args.dry_run)

    content_config = _resolve_facebook_content_config(brand_context)

    init_db()

    logger.info(
        "daily_news_start | mode=%s | dry_run=%s | publish_mode=%s%s",
        mode, args.dry_run,
        brand_context.publish_mode if brand_context else get_publish_mode(),
        _brand_log(brand_context),
    )

    if args.topic:
        return _run_single_topic(args.topic, summary, args.dry_run, mode, media_cfg, brand_context, content_config=content_config)

    feed_urls = get_feed_urls("DAILY_NEWS_RSS_FEEDS")
    if not feed_urls:
        import random
        return _run_single_topic(
            random.choice(_FALLBACK_TOPICS), summary, args.dry_run, mode, media_cfg, brand_context
        )

    articles = fetch_feeds(
        feed_urls    = feed_urls,
        max_articles = get_max_articles(),
        timeout      = get_feed_timeout(),
    )

    if not articles:
        logger.warning("No articles fetched from any feed%s", _brand_log(brand_context))
        summary.failures = 1
        return summary

    logger.info("Fetched %d articles from feeds%s", len(articles), _brand_log(brand_context))

    for article in articles:
        if args.dry_run:
            logger.info("dry_run: would process | title=%r%s", article.title, _brand_log(brand_context))
            summary.posts_generated += 1
            continue

        if is_article_processed(article.fingerprint()):
            summary.duplicates_skipped += 1
            continue

        try:
            post_text = summarize_article(article, content_config=content_config)
            summary.posts_generated += 1
        except Exception as exc:
            logger.error("summarization_failed | title=%r | error=%s%s", article.title, exc, _brand_log(brand_context))
            summary.failures += 1
            continue

        mark_article_processed(article)

        asset_result = _build_asset_bundle(
            title        = article.title,
            summary      = post_text[:300],
            article_body = post_text,
            keywords     = getattr(article, "tags", []) or [],
            media_cfg    = media_cfg,
            summary_obj  = summary,
            brand_context = brand_context,
        )

        if mode == "publish":
            featured_media_id = _upload_featured_image(asset_result, article.title, media_cfg, summary, brand_context)
            _publish_to_wordpress(article.title, post_text, featured_media_id, summary, brand_context)

            image_bytes, image_name = _select_social_image(asset_result)
            platforms = _get_publish_platforms(brand_context)

            pub_summary = publish_post(
                content={
                    "title":       article.title,
                    "text":        post_text,
                    "image_url":   None,
                    "image_bytes": image_bytes,
                    "image_name":  image_name,
                },
                targets       = platforms,
                module_name   = "daily_news",
                brand_context = brand_context,
            )

            for result in pub_summary.results:
                logger.info(str(result))
                if result.success and not result.metadata.get("duplicate"):
                    summary.social_posts_published += 1
                elif not result.success:
                    summary.failures += 1
        else:
            logger.info("draft_mode_publish_skipped | title=%r%s", article.title, _brand_log(brand_context))

    return summary


def _run_single_topic(
    topic: str,
    summary: ExecutionSummary,
    dry_run: bool,
    mode: str,
    media_cfg,
    brand_context: Optional["BrandContext"] = None,
    content_config: dict | None = None,
) -> ExecutionSummary:
    logger.info("single_topic_path | topic=%r%s", topic, _brand_log(brand_context))

    if dry_run:
        summary.posts_generated = 1
        return summary

    topic_hash = compute_content_hash(topic.strip().lower())
    platforms  = _get_publish_platforms(brand_context)

    if platforms and all(already_published(topic_hash, t) for t in platforms):
        summary.duplicates_skipped = 1
        return summary

    try:
        post_text = generate_news_post(topic, content_config=content_config)
        summary.posts_generated = 1
    except Exception as exc:
        logger.error("generation_failed | error=%s%s", exc, _brand_log(brand_context))
        summary.failures = 1
        return summary

    if mode != "publish":
        _build_asset_bundle(topic, post_text[:300], post_text, [], media_cfg, summary, brand_context)
        return summary

    asset_result = _build_asset_bundle(topic, post_text[:300], post_text, [], media_cfg, summary, brand_context)
    featured_media_id = _upload_featured_image(asset_result, topic, media_cfg, summary, brand_context)
    _publish_to_wordpress(topic, post_text, featured_media_id, summary, brand_context)

    image_bytes, image_name = _select_social_image(asset_result)

    pub_summary = publish_post(
        content={
            "title":       topic,
            "text":        post_text,
            "image_url":   None,
            "image_bytes": image_bytes,
            "image_name":  image_name,
        },
        targets       = platforms,
        module_name   = "daily_news",
        brand_context = brand_context,
    )

    for target_key, result in zip(platforms, pub_summary.results):
        logger.info(str(result))
        if result.success and not result.metadata.get("duplicate"):
            summary.social_posts_published += 1
            record_publish(
                content_hash     = topic_hash,
                target_key       = target_key,
                platform         = result.platform,
                module_name      = "daily_news",
                status           = "success",
                external_post_id = result.external_post_id,
            )
        elif not result.success:
            summary.failures += 1
            logger.warning("publish_failed | target=%s | error=%s%s", target_key, result.error_message, _brand_log(brand_context))

    logger.info(
        "daily_news_complete | posts=%d | published=%d%s",
        summary.posts_generated, summary.social_posts_published, _brand_log(brand_context),
    )
    return summary


if __name__ == "__main__":
    main()
