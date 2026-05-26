# modules/daily_news/runner.py
import argparse
import logging
import os
import sys

# Allow running as: python -m modules.daily_news.runner
sys.path.insert(0, "/app")

from generator import generate_news_post

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("daily_news")

DEFAULT_TOPICS = [
    "registering your address in Germany (Anmeldung) and why it matters",
    "opening a bank account in Germany as a foreigner",
    "health insurance options in Germany for expats",
    "public transport tips for newcomers in Germany",
    "filing taxes in Germany for the first time",
]

# Platforms to publish to when PUBLISH_ENABLED=true
# Override per-module via env if needed later
_PUBLISH_PLATFORMS = ["facebook", "instagram"]


def _publishing_enabled() -> bool:
    return os.getenv("PUBLISH_ENABLED", "false").strip().lower() in {"1", "true", "yes"}


def _publish(topic: str, post_text: str) -> None:
    """Publishing hook — only called when PUBLISH_ENABLED=true."""
    from shared.social import publish_post, PublishError

    content = {
        "title": topic,
        "text": post_text,
        "image_url": None,   # Phase 4 will add image generation here
    }

    for platform in _PUBLISH_PLATFORMS:
        try:
            publish_post(platform, content)
        except PublishError as exc:
            logger.error("Publish failed for %s: %s", platform, exc)
        except ValueError as exc:
            logger.error("Invalid platform config: %s", exc)


def main():
    parser = argparse.ArgumentParser(description="Daily News Post Generator")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate and print post without publishing",
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

    logger.info("Selected topic: %s", topic)
    logger.info("Generating post...")

    try:
        post = generate_news_post(topic)
    except Exception as exc:
        logger.error("Failed to generate post: %s", exc)
        sys.exit(1)

    print("\n" + "=" * 60)
    print("GENERATED POST:")
    print("=" * 60)
    print(post)
    print("=" * 60 + "\n")

    if args.dry_run:
        logger.info("Dry-run mode: publishing skipped.")
        return

    if not _publishing_enabled():
        logger.info("PUBLISH_ENABLED=false: publishing skipped.")
        return

    logger.info("Publishing to social platforms...")
    _publish(topic, post)


if __name__ == "__main__":
    main()