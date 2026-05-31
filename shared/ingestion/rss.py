# shared/ingestion/rss.py
"""
RSS feed fetcher and parser.

Fetches one or more feeds, returns a flat list of normalized Articles
sorted newest-first, capped at max_articles.

Uses feedparser only. No HTTP scraping, no browser, no article body fetching.
"""

import logging
from datetime import datetime, timezone

import feedparser

from .models import Article
from .normalizer import normalize_entry

logger = logging.getLogger(__name__)


def fetch_feed(url: str, timeout: int = 10) -> list[Article]:
    """
    Fetch and parse a single RSS/Atom feed URL.

    Returns a list of Articles (may be empty on failure).
    Never raises — feed failures are logged and skipped.
    """
    logger.info("Fetching feed | url=%s", url)

    try:
        # feedparser does not expose a native timeout in its simple API,
        # but setting socket default timeout covers the underlying urllib call.
        import socket
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(timeout)

        try:
            parsed = feedparser.parse(url)
        finally:
            socket.setdefaulttimeout(old_timeout)

    except Exception as exc:
        logger.error("Feed fetch error | url=%s | error=%s", url, exc)
        return []

    if parsed.get("bozo") and not parsed.get("entries"):
        logger.warning(
            "Feed parse warning | url=%s | bozo_exception=%s",
            url, parsed.get("bozo_exception", "unknown"),
        )
        return []

    feed_title = parsed.feed.get("title", url)
    articles: list[Article] = []

    for entry in parsed.entries:
        article = normalize_entry(entry, source=feed_title)
        if article:
            articles.append(article)

    logger.info(
        "Feed fetched | url=%s | title=%r | articles=%d",
        url, feed_title, len(articles),
    )
    return articles


def fetch_feeds(
    feed_urls: list[str],
    max_articles: int = 10,
    timeout: int = 10,
) -> list[Article]:
    """
    Fetch multiple feeds, merge, deduplicate by fingerprint,
    sort newest-first, return up to max_articles.

    Args:
        feed_urls:    List of RSS/Atom URLs.
        max_articles: Maximum articles to return across all feeds.
        timeout:      Per-feed network timeout in seconds.

    Returns:
        List of Article objects, newest first, capped at max_articles.
    """
    all_articles: list[Article] = []
    seen_fingerprints: set[str] = set()

    for url in feed_urls:
        url = url.strip()
        if not url:
            continue

        articles = fetch_feed(url, timeout=timeout)

        for article in articles:
            fp = article.fingerprint()
            if fp not in seen_fingerprints:
                seen_fingerprints.add(fp)
                all_articles.append(article)

    # Sort newest first
    def _sort_key(a: Article) -> str:
        # ISO strings sort lexicographically correctly
        return a.published_at

    all_articles.sort(key=_sort_key, reverse=True)

    return all_articles[:max_articles]