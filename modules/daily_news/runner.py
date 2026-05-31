# modules/daily_news/runner.py
import argparse
import logging
import os
import sys

sys.path.insert(0, "/app")

from shared.logging import configure_logging, get_logger
from shared.store import init_db, is_article_processed, mark_article_processed, compute_content_hash, already_published, record_publish
from shared.config import get_publish_mode
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


def main() -> ExecutionSummary:
    parser = argparse.ArgumentParser(description="Daily News Post Generator")
    parser.add_argument("--dry-run", action="store_true",
                        help="Skip AI generation and publishing entirely")
    parser.add_argument("--topic", type=str, default=None,
                        help="Force a specific topic (bypasses RSS)")
    args = parser.parse_args()

    mode     = _get_mode()
    summary  = ExecutionSummary(module="daily_news", dry_run=args.dry_run)

    init_db()

    logger.info(
        "daily_news start | mode=%s | dry_run=%s | publish_mode=%s",
        mode, args.dry_run, get_publish_mode(),
    )

    # ------------------------------------------------------------------
    # FORCED TOPIC (bypasses RSS, used for testing)
    # ------------------------------------------------------------------
    if args.topic:
        return _run_single_topic(args.topic, summary, args.dry_run, mode)

    # ------------------------------------------------------------------
    # RSS PIPELINE
    # ------------------------------------------------------------------
    feed_urls = get_feed_urls("DAILY_NEWS_RSS_FEEDS")

    if not feed_urls:
        logger.warning(
            "DAILY_NEWS_RSS_FEEDS not set — falling back to static topic"
        )
        import random
        return _run_single_topic(
            random.choice(_FALLBACK_TOPICS), summary, args.dry_run, mode
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

        # Deduplicate BEFORE AI call — protect token budget
        if is_article_processed(article.fingerprint()):
            logger.info(
                "Article already processed | title=%r | fingerprint=%s",
                article.title, article.fingerprint()[:12],
            )
            summary.duplicates_skipped += 1
            continue

        # Summarize
        try:
            post_text = summarize_article(article)
            summary.posts_generated += 1
        except Exception as exc:
            logger.error(
                "Summarization failed | title=%r | error=%s",
                article.title, exc,
            )
            summary.failures += 1
            continue

        logger.info(
            "Generated post | title=%r\n%s",
            article.title, post_text,
        )

        # Mark processed immediately after successful summarization
        # so even draft-mode runs don't re-process on next run
        mark_article_processed(article)

        # Publish only in publish mode
        if mode == "publish":
            pub_summary = publish_post(
                content={
                    "title":     article.title,
                    "text":      post_text,
                    "image_url": None,
                },
                targets=_get_publish_platforms(),
                module_name="daily_news",
            )

            for result in pub_summary.results:
                logger.info(str(result))
                if result.success and not result.metadata.get("duplicate"):
                    summary.published += 1
                elif not result.success:
                    summary.failures += 1
        else:
            logger.info(
                "draft mode: publish skipped | title=%r",
                article.title,
            )

    return summary

def _run_single_topic(
    topic: str,
    summary: ExecutionSummary,
    dry_run: bool,
    mode: str,
) -> ExecutionSummary:
    logger.info("Single topic path | topic=%r", topic)

    if dry_run:
        logger.info("dry_run: would generate for topic=%r", topic)
        summary.posts_generated = 1
        return summary

    topic_hash = compute_content_hash(topic.strip().lower())
    platforms  = _get_publish_platforms()

    # Dedup check before AI call — uses target keys, same as record_publish below
    if platforms and all(already_published(topic_hash, t) for t in platforms):
        logger.info(
            "Topic already published — skipping | topic=%r | hash=%s",
            topic, topic_hash[:12],
        )
        summary.duplicates_skipped = 1
        return summary

    try:
        post_text = generate_news_post(topic)
        summary.posts_generated = 1
    except Exception as exc:
        logger.error("Generation failed | error=%s", exc)
        summary.failures = 1
        return summary

    print("\n" + "=" * 60)
    print("GENERATED POST:")
    print("=" * 60)
    print(post_text)
    print("=" * 60 + "\n")

    if mode != "publish":
        return summary

    pub_summary = publish_post(
        content={"title": topic, "text": post_text, "image_url": None},
        targets=platforms,
        module_name="daily_news",
    )

    # publisher.py returns results in the same order as targets.
    # Zip them so we always record the topic hash under the correct
    # target key — never under result.platform which is the platform
    # name ('facebook') not the target key ('gs_facebook_main').
    # zip() is safe here: publisher.py returns results in the same order
    # as the targets list (synchronous loop, no reordering).
    for target_key, result in zip(platforms, pub_summary.results):
        logger.info(str(result))
        if result.success and not result.metadata.get("duplicate"):
            summary.published += 1
            record_publish(
                content_hash     = topic_hash,
                target_key       = target_key,        # ← gs_facebook_main
                platform         = result.platform,   # ← facebook
                module_name      = "daily_news",
                status           = "success",
                external_post_id = result.external_post_id,
            )
            logger.info(
                "Recorded topic_hash | hash=%s | target_key=%s",
                topic_hash[:12], target_key,
            )
        elif not result.success:
            summary.failures += 1
            logger.warning(
                "Publish failed | target_key=%s | error=%s",
                target_key, result.error_message,
            )

    return summary

def _get_publish_platforms() -> list[str]:
    raw = os.getenv("DAILY_NEWS_TARGETS", "").strip()
    if raw:
        return [t.strip() for t in raw.split(",") if t.strip()]
    return []


if __name__ == "__main__":
    main()