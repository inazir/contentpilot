# modules/daily_news/runner.py
import argparse
import sys

# Allow running as: python -m modules.daily_news.runner
sys.path.insert(0, "/app")

from shared.logging import configure_logging, get_logger
from shared.store import init_db
from shared.social import publish_post, get_publish_mode
from generator import generate_news_post

configure_logging()
logger = get_logger("daily_news")

DEFAULT_TOPICS = [
    "registering your address in Germany (Anmeldung) and why it matters",
    "opening a bank account in Germany as a foreigner",
    "health insurance options in Germany for expats",
    "public transport tips for newcomers in Germany",
    "filing taxes in Germany for the first time",
]

_PLATFORMS = ["facebook", "instagram"]


def main() -> None:
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
    except Exception as exc:
        logger.error("Content generation failed", extra={"error": str(exc)})
        sys.exit(1)

    print("\n" + "=" * 60)
    print("GENERATED POST:")
    print("=" * 60)
    print(post_text)
    print("=" * 60 + "\n")

    if args.dry_run:
        logger.info("Dry-run enabled — skipping publishing")
        return

    summary = publish_post(
        content={
            "title": topic,
            "text": post_text,
            "image_url": None,
        },
        platforms=_PLATFORMS,
        module_name="daily_news",
    )

    logger.info(str(summary))
    for result in summary.results:
        logger.info(str(result))

    if summary.failed:
        logger.warning(
            "%d platform(s) failed",
            len(summary.failed),
            extra={"failed_platforms": [r.platform for r in summary.failed]},
        )


if __name__ == "__main__":
    main()
