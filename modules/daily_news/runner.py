# modules/daily_news/runner.py
import argparse
import os
import sys

# Allow running as: python -m modules.daily_news.runner
sys.path.insert(0, "/app")

from shared.logging import configure_logging, get_logger
from shared.models import ExecutionSummary
from shared.store import init_db
from shared.config import get_publish_mode
from shared.social import publish_post
from generator import generate_news_post

configure_logging(module_name="daily_news")
logger = get_logger("daily_news")

DEFAULT_TOPICS = [
    "registering your address in Germany (Anmeldung) and why it matters",
    "opening a bank account in Germany as a foreigner",
    "health insurance options in Germany for expats",
    "public transport tips for newcomers in Germany",
    "filing taxes in Germany for the first time",
]

# Read publishing targets from env, comma-separated
# Example: DAILY_NEWS_TARGETS=gs_facebook_main,gs_instagram_main
_TARGETS = [t.strip() for t in os.getenv("DAILY_NEWS_TARGETS", "").split(",") if t.strip()]


def main() -> ExecutionSummary:
    parser = argparse.ArgumentParser(description="Daily News Post Generator")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate only and skip publishing",
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Custom topic override",
    )
    args = parser.parse_args()

    import random
    topic = args.topic or random.choice(DEFAULT_TOPICS)

    summary = ExecutionSummary(module="daily_news", dry_run=args.dry_run)

    init_db()
    logger.info(
        "Starting daily_news run",
        extra={
            "topic": topic,
            "dry_run": args.dry_run,
            "publish_mode": get_publish_mode(),
        },
    )

    try:
        post_text = generate_news_post(topic)
        summary.posts_generated = 1
    except Exception as exc:
        logger.error("Content generation failed", extra={"error": str(exc)})
        summary.failures = 1
        return summary

    print("\n" + "=" * 60)
    print("GENERATED POST:")
    print("=" * 60)
    print(post_text)
    print("=" * 60 + "\n")

    if args.dry_run:
        logger.info("Dry-run enabled — skipping publishing")
        return summary

    publish_summary = publish_post(
        content={
            "title": topic,
            "text": post_text,
            "image_url": None,
        },
        targets=_TARGETS,
        module_name="daily_news",
    )

    logger.info(str(publish_summary))
    for result in publish_summary.results:
        logger.info(str(result))
        if result.success:
            if result.metadata.get("duplicate"):
                summary.duplicates_skipped += 1
            else:
                summary.published += 1
        else:
            summary.failures += 1

    if publish_summary.failed:
        logger.warning(
            "%d target(s) failed",
            len(publish_summary.failed),
            extra={"failed_targets": [r.platform for r in publish_summary.failed]},
        )

    return summary


if __name__ == "__main__":
    main()
