# modules/daily_news/runner.py
"""
Daily News runner — Phase 11B enriched workflow.

Pipeline:
    RSS → AI Generation → Asset Bundle → WordPress (with featured image) → Social

Feature flags (all default to safe backward-compatible values):
    ENABLE_MEDIA_ASSETS      — master switch for asset pipeline
    ENABLE_FEATURED_IMAGES   — upload featured image to WordPress
    ENABLE_SOCIAL_IMAGES     — generate social image variants
    MEDIA_BRANDING_ENABLED   — apply branding overlay
    MEDIA_ADS_ENABLED        — apply ads overlay

When all flags are false / unset the behaviour is identical to pre-Phase-11.
"""

import argparse
import logging
import os
import sys

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

configure_logging(module_name="daily_news")
logger = get_logger("daily_news")

# Fallback topics used when no RSS feeds are configured
_FALLBACK_TOPICS = [
    "registering your address in Germany (Anmeldung) and why it matters",
    "opening a bank account in Germany as a foreigner",
    "health insurance options in Germany for expats",
    "public transport tips for newcomers in Germany",
    "filing taxes in Germany for the first time",
]


def _get_mode() -> str:
    """
    DAILY_NEWS_MODE=draft   → full pipeline except publishing
    DAILY_NEWS_MODE=publish → complete pipeline including publishing
    """
    return os.getenv("DAILY_NEWS_MODE", "draft").strip().lower()


def _get_publish_platforms() -> list[str]:
    raw = os.getenv("DAILY_NEWS_TARGETS", "").strip()
    if raw:
        return [t.strip() for t in raw.split(",") if t.strip()]
    return []


# ---------------------------------------------------------------------------
# Asset pipeline helpers
# ---------------------------------------------------------------------------

def _build_asset_bundle(
    title: str,
    summary: str,
    article_body: str,
    keywords: list[str],
    media_cfg,
    summary_obj: ExecutionSummary,
):
    """
    Build and store a content asset bundle.

    Returns AssetStorageResult or None if disabled / failed.
    Always isolated — never raises upward.
    """
    if not media_cfg.enabled:
        return None

    try:
        from shared.content import AssetBuilder
        from shared.content.storage import AssetStorage
        from pathlib import Path

        storage = AssetStorage(storage_root=Path(media_cfg.storage_dir))
        builder = AssetBuilder(storage=storage)

        logger.info(
            "asset_pipeline_start | title=%r | branding=%s | ads=%s",
            title, media_cfg.branding_enabled, media_cfg.ads_enabled,
        )

        result = builder.build(
            title=title,
            summary=summary,
            article_body=article_body,
            keywords=keywords,
            branding_enabled=media_cfg.branding_enabled,
            ads_enabled=media_cfg.ads_enabled,
        )

        if result.success and result.bundle:
            summary_obj.bundles_created += 1
            summary_obj.assets_generated += result.assets_written
            # Count image assets (exclude metadata + article)
            summary_obj.images_generated += sum(
                1 for k in result.bundle.assets
                if k not in {"metadata", "article"}
            )
            logger.info(
                "asset_bundle_stored | slug=%s | assets=%d | dir=%s",
                result.bundle.article_slug,
                result.assets_written,
                result.storage_dir,
            )
        else:
            logger.warning(
                "asset_bundle_failed | title=%r | error=%s",
                title, result.error_message,
            )

        return result

    except Exception as exc:
        logger.warning(
            "asset_pipeline_error | title=%r | error=%s",
            title, exc,
        )
        return None


def _select_social_image(asset_result) -> tuple[bytes | None, str]:
    """
    Pick the best image from an asset bundle for social publishing.

    Preference order: facebook_landscape → featured → facebook_square

    Returns (image_bytes, filename) or (None, "").
    Never raises.
    """
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
                image_bytes = asset.path.read_bytes()
                logger.info(
                    "social_image_selected | key=%s | filename=%s | size=%d",
                    key, filename, len(image_bytes),
                )
                return image_bytes, filename
            except Exception as exc:
                logger.warning(
                    "social_image_read_failed | key=%s | error=%s", key, exc
                )

    return None, ""


def _upload_featured_image(
    asset_result,
    title: str,
    media_cfg,
    summary_obj: ExecutionSummary,
) -> int | None:
    """
    Upload featured image to WordPress media library.

    Returns WordPress media_id or None.
    Always isolated — never raises upward.
    """
    if not media_cfg.enabled or not media_cfg.featured_images:
        return None

    if asset_result is None or not asset_result.success:
        return None

    bundle = asset_result.bundle
    if bundle is None or bundle.featured_image is None:
        logger.debug("upload_featured_image_skip | reason=no_featured_asset")
        return None

    try:
        from shared.config import get_wordpress_config
        from shared.content.wordpress_media import WordPressMediaService

        wp_config = get_wordpress_config()
        svc = WordPressMediaService(wp_config)

        logger.info("wp_media_upload_start | title=%r", title)

        result = svc.upload_asset_file(
            asset_file=bundle.featured_image,
            alt_text=title,
            title=title,
        )

        if result.success:
            summary_obj.images_uploaded += 1
            logger.info(
                "wp_media_upload_success | media_id=%d | url=%s",
                result.media_id, result.url,
            )
            return result.media_id
        else:
            summary_obj.wordpress_media_failures += 1
            logger.warning(
                "wp_media_upload_failed | title=%r | error=%s | retryable=%s",
                title, result.error_message, result.retryable,
            )
            return None

    except ValueError as exc:
        # WordPress not configured — not an error, just skip
        logger.debug(
            "wp_media_upload_skip | reason=wordpress_not_configured | detail=%s", exc
        )
        return None

    except Exception as exc:
        summary_obj.wordpress_media_failures += 1
        logger.warning(
            "wp_media_upload_error | title=%r | error=%s", title, exc
        )
        return None


def _publish_to_wordpress(
    title: str,
    post_text: str,
    featured_media_id: int | None,
    summary_obj: ExecutionSummary,
) -> str | None:
    """
    Publish article to WordPress.

    Returns post status string ("draft" / "publish") on success, None on failure.
    Also updates summary_obj.wordpress_posts_created / wordpress_posts_published.
    Always isolated — never raises upward.
    """
    wp_enabled = os.getenv("DAILY_NEWS_ENABLE_WORDPRESS", "false").strip().lower()
    if wp_enabled not in {"1", "true", "yes"}:
        return None
    logger.info("wp_post_create_start | title=%r | featured_media_id=%s", title, featured_media_id)
    try:
        from shared.config import get_wordpress_config
        from shared.wordpress.client import WordPressClient
        from shared.wordpress.models import PostRequest

        wp_config   = get_wordpress_config()
        client      = WordPressClient(wp_config)
        status      = os.getenv("DAILY_NEWS_WORDPRESS_STATUS", "draft").strip().lower()

        post_request = PostRequest(
            title   = title,
            content = post_text,
            status  = status,
        )

        if featured_media_id is not None:
            post_request.featured_media = featured_media_id
            logger.info(
                "wp_post_with_featured_image | media_id=%d | title=%r",
                featured_media_id, title,
            )

        response = client.create_post(post_request)

        if response.success:
            summary_obj.wordpress_posts_created += 1
            if response.status == "publish":
                summary_obj.wordpress_posts_published += 1
            logger.info(
                "wordpress_post_result | post_id=%s | status=%s | url=%s",
                response.wordpress_post_id, response.status, response.url,
            )
            return response.status
        else:
            logger.warning(
                "wp_post_failed | title=%r | error=%s",
                title, response.error_message,
            )
            return None

    except ValueError as exc:
        logger.debug(
            "wp_post_skip | reason=wordpress_not_configured | detail=%s", exc
        )
        return None

    except Exception as exc:
        logger.warning("wp_post_error | title=%r | error=%s", title, exc)
        return None


# ---------------------------------------------------------------------------
# Main entry points
# ---------------------------------------------------------------------------

def main() -> ExecutionSummary:
    parser = argparse.ArgumentParser(description="Daily News Post Generator")
    parser.add_argument("--dry-run", action="store_true",
                        help="Skip AI generation and publishing entirely")
    parser.add_argument("--topic", type=str, default=None,
                        help="Force a specific topic (bypasses RSS)")
    args = parser.parse_args()

    mode      = _get_mode()
    media_cfg = get_media_config()
    summary   = ExecutionSummary(module="daily_news", dry_run=args.dry_run)

    init_db()

    logger.info(
        "daily_news_start | mode=%s | dry_run=%s | publish_mode=%s"
        " | media_enabled=%s | featured_images=%s | social_images=%s",
        mode, args.dry_run, get_publish_mode(),
        media_cfg.enabled, media_cfg.featured_images, media_cfg.social_images,
    )

    # ------------------------------------------------------------------
    # FORCED TOPIC (bypasses RSS, used for testing)
    # ------------------------------------------------------------------
    if args.topic:
        return _run_single_topic(args.topic, summary, args.dry_run, mode, media_cfg)

    # ------------------------------------------------------------------
    # RSS PIPELINE
    # ------------------------------------------------------------------
    feed_urls = get_feed_urls("DAILY_NEWS_RSS_FEEDS")

    if not feed_urls:
        logger.warning("DAILY_NEWS_RSS_FEEDS not set — falling back to static topic")
        import random
        return _run_single_topic(
            random.choice(_FALLBACK_TOPICS), summary, args.dry_run, mode, media_cfg
        )

    articles = fetch_feeds(
        feed_urls    = feed_urls,
        max_articles = get_max_articles(),
        timeout      = get_feed_timeout(),
    )

    if not articles:
        logger.warning("No articles fetched from any feed")
        summary.failures = 1
        return summary

    logger.info("Fetched %d articles from feeds", len(articles))

    for article in articles:
        if args.dry_run:
            logger.info(
                "dry_run: would process | title=%r | source=%s",
                article.title, article.source,
            )
            summary.posts_generated += 1
            continue

        if is_article_processed(article.fingerprint()):
            logger.info(
                "article_already_processed | title=%r | fingerprint=%s",
                article.title, article.fingerprint()[:12],
            )
            summary.duplicates_skipped += 1
            continue

        # --- Summarize ---
        try:
            post_text = summarize_article(article)
            summary.posts_generated += 1
        except Exception as exc:
            logger.error(
                "summarization_failed | title=%r | error=%s",
                article.title, exc,
            )
            summary.failures += 1
            continue

        logger.info("generated_post | title=%r", article.title)

        mark_article_processed(article)

        # --- Asset pipeline (isolated) ---
        asset_result = _build_asset_bundle(
            title        = article.title,
            summary      = post_text[:300],
            article_body = post_text,
            keywords     = getattr(article, "tags", []) or [],
            media_cfg    = media_cfg,
            summary_obj  = summary,
        )

        # --- WordPress publish ---
        if mode == "publish":
            featured_media_id = _upload_featured_image(
                asset_result, article.title, media_cfg, summary
            )

            _publish_to_wordpress(article.title, post_text, featured_media_id, summary)

            # --- Select social image from bundle ---
            image_bytes, image_name = _select_social_image(asset_result)

            pub_summary = publish_post(
                content={
                    "title":       article.title,
                    "text":        post_text,
                    "image_url":   None,
                    "image_bytes": image_bytes,
                    "image_name":  image_name,
                },
                targets     = _get_publish_platforms(),
                module_name = "daily_news",
            )

            for result in pub_summary.results:
                logger.info(str(result))
                if result.success and not result.metadata.get("duplicate"):
                    summary.social_posts_published += 1
                elif not result.success:
                    summary.failures += 1
        else:
            logger.info("draft_mode_publish_skipped | title=%r", article.title)

    logger.info(
        "daily_news_pipeline_complete | generated=%d | social_posts_published=%d"
        " | bundles=%d | images=%d | wp_media_failures=%d"
        " | wordpress_posts_created=%d | wordpress_posts_published=%d",
        summary.posts_generated, summary.social_posts_published,
        summary.bundles_created, summary.images_generated,
        summary.wordpress_media_failures,
        summary.wordpress_posts_created, summary.wordpress_posts_published,
    )

    return summary


def _run_single_topic(
    topic: str,
    summary: ExecutionSummary,
    dry_run: bool,
    mode: str,
    media_cfg,
) -> ExecutionSummary:
    logger.info("single_topic_path | topic=%r", topic)

    if dry_run:
        logger.info("dry_run: would generate for topic=%r", topic)
        summary.posts_generated = 1
        return summary

    topic_hash = compute_content_hash(topic.strip().lower())
    platforms  = _get_publish_platforms()

    if platforms and all(already_published(topic_hash, t) for t in platforms):
        logger.info(
            "topic_already_published | topic=%r | hash=%s",
            topic, topic_hash[:12],
        )
        summary.duplicates_skipped = 1
        return summary

    try:
        post_text = generate_news_post(topic)
        summary.posts_generated = 1
    except Exception as exc:
        logger.error("generation_failed | error=%s", exc)
        summary.failures = 1
        return summary

    logger.info("generated_post | topic=%r\n%s", topic, post_text)

    if mode != "publish":
        # Still build assets in draft mode — just skip publishing
        _build_asset_bundle(
            title        = topic,
            summary      = post_text[:300],
            article_body = post_text,
            keywords     = [],
            media_cfg    = media_cfg,
            summary_obj  = summary,
        )
        return summary

    # --- Asset pipeline ---
    asset_result = _build_asset_bundle(
        title        = topic,
        summary      = post_text[:300],
        article_body = post_text,
        keywords     = [],
        media_cfg    = media_cfg,
        summary_obj  = summary,
    )

    # --- WordPress ---
    featured_media_id = _upload_featured_image(
        asset_result, topic, media_cfg, summary
    )
    _publish_to_wordpress(topic, post_text, featured_media_id, summary)

    # --- Select social image from bundle ---
    image_bytes, image_name = _select_social_image(asset_result)

    # --- Social ---
    pub_summary = publish_post(
        content={
            "title":       topic,
            "text":        post_text,
            "image_url":   None,
            "image_bytes": image_bytes,
            "image_name":  image_name,
        },
        targets     = platforms,
        module_name = "daily_news",
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
            logger.warning(
                "publish_failed | target_key=%s | error=%s",
                target_key, result.error_message,
            )

    logger.info(
        "daily_news_pipeline_complete | topic=%r | social_posts_published=%d"
        " | bundles=%d | images=%d | wp_media_failures=%d"
        " | wordpress_posts_created=%d | wordpress_posts_published=%d",
        topic, summary.social_posts_published,
        summary.bundles_created, summary.images_generated,
        summary.wordpress_media_failures,
        summary.wordpress_posts_created, summary.wordpress_posts_published,
    )

    return summary


if __name__ == "__main__":
    main()
