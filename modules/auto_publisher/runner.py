# modules/auto_publisher/runner.py
"""
Auto Publisher — multi-client routing pipeline.

This module demonstrates the full end-to-end workflow:

    RSS Article
        ↓
    AI Summarization
        ↓
    AutoPublisherRouter  (score article against all clients)
        ↓
    RoutingDecision      (winning client + score)
        ↓
    MultiClientPublisher (WordPress + Facebook per client config)
        ↓
    PublishSummary       (structured results)

The module is deliberately thin: all routing and publishing logic lives in
shared/routing/. This file wires them together with logging and error handling.

Environment variables:
    CLIENTS_CONFIG_PATH   Path to clients_config.json (default: clients_config.json)
    PUBLISH_MODE          mock | real (default: mock)
    ROUTING_MIN_SCORE     Minimum routing score 0.0-1.0 (default: 0.05)
    AUTO_PUBLISHER_MODE   draft | publish (default: draft)
"""

from __future__ import annotations

import argparse
import logging
import os
import sys

sys.path.insert(0, "/app")

from shared.logging import configure_logging, get_logger
from shared.routing import (
    AutoPublisherRouter,
    MultiClientPublisher,
    JsonClientRepository,
    KeywordClassifier,
    NoClientMatchedError,
    PublishRequest,
)

configure_logging(module_name="auto_publisher")
logger = get_logger("auto_publisher")


def _get_mode() -> str:
    return os.getenv("AUTO_PUBLISHER_MODE", "draft").strip().lower()


def route_and_publish(
    article_id: str,
    title: str,
    body: str,
    summary: str,
    url: str = "",
    tags: list[str] | None = None,
    image_url: str | None = None,
) -> dict:
    """
    Full routing + publishing pipeline for one article.

    Returns a dict with routing and publish outcome details.
    Never raises — all failures are captured in the return value.
    """
    tags = tags or []
    mode = _get_mode()

    # 1. Build router and publisher (instantiated once per call in this
    #    simple runner; for high-volume use, instantiate once at startup)
    repository = JsonClientRepository()
    router = AutoPublisherRouter(
        repository=repository,
        classifier=KeywordClassifier(),
    )
    publisher = MultiClientPublisher()

    # 2. Route
    article_text = f"{title} {summary} {body[:500]}"
    logger.info(
        "auto_publisher_route | article=%s | title=%r | tags=%s",
        article_id, title, tags[:5],
    )

    decision = router.route(
        article_id=article_id,
        article_text=article_text,
        tags=tags,
        raise_on_no_match=False,
    )

    logger.info(
        "routing_decision | article=%s | routed=%s | client=%s | score=%.4f | reason=%r",
        article_id,
        decision.routed,
        decision.matched_client.client_id if decision.matched_client else "none",
        decision.score,
        decision.reason,
    )

    if not decision.routed or decision.matched_client is None:
        logger.warning(
            "auto_publisher_no_match | article=%s | reason=%r",
            article_id, decision.reason,
        )
        return {
            "article_id": article_id,
            "routed": False,
            "reason": decision.reason,
            "client_id": None,
            "score": decision.score,
            "published": False,
        }

    # 3. Publish (skip if draft mode)
    if mode != "publish":
        logger.info(
            "auto_publisher_draft_mode | article=%s | client=%s | would_publish_to=%s",
            article_id,
            decision.matched_client.client_id,
            list(decision.matched_client.publishing_preferences.formats),
        )
        return {
            "article_id": article_id,
            "routed": True,
            "client_id": decision.matched_client.client_id,
            "score": decision.score,
            "published": False,
            "reason": "draft mode — publishing skipped",
        }

    request = PublishRequest(
        article_id=article_id,
        title=title,
        body=body,
        summary=summary,
        url=url,
        image_url=image_url,
        tags=tags,
    )

    publish_summary = publisher.publish(request, decision.matched_client)
    publish_summary.routing_score = decision.score

    # 4. Log outcomes
    for outcome in publish_summary.outcomes:
        level = logging.INFO if outcome.success else logging.WARNING
        logger.log(level, "publish_outcome | %s", outcome)

    succeeded = len(publish_summary.succeeded)
    failed = len(publish_summary.failed)
    logger.info(
        "auto_publisher_complete | article=%s | client=%s | succeeded=%d | failed=%d",
        article_id, decision.matched_client.client_id, succeeded, failed,
    )

    return {
        "article_id": article_id,
        "routed": True,
        "client_id": decision.matched_client.client_id,
        "score": decision.score,
        "published": publish_summary.any_succeeded if hasattr(publish_summary, "any_succeeded") else succeeded > 0,
        "succeeded": succeeded,
        "failed": failed,
        "outcomes": [str(o) for o in publish_summary.outcomes],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Auto Publisher — multi-client routing pipeline")
    parser.add_argument("--article-id", default="test_001", help="Article identifier")
    parser.add_argument("--title", default="Federal Reserve Raises Interest Rates Again",
                        help="Article title")
    parser.add_argument("--summary", default="The Fed announced another rate hike this week.",
                        help="Article summary")
    parser.add_argument("--body", default="", help="Full article body")
    parser.add_argument("--url", default="https://example.com/article", help="Source URL")
    parser.add_argument("--tags", default="finance,Federal Reserve,interest rates",
                        help="Comma-separated tags")
    args = parser.parse_args()

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    result = route_and_publish(
        article_id=args.article_id,
        title=args.title,
        body=args.body or args.summary,
        summary=args.summary,
        url=args.url,
        tags=tags,
    )

    import json
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
