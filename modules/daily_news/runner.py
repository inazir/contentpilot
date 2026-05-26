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
        logger.info("Dry-run mode: post not published.")
        return

    # Publishing hook — Phase 3 will wire this to social platforms
    logger.info("Publishing not yet implemented. Use --dry-run for now.")


if __name__ == "__main__":
    main()