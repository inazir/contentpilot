#!/usr/bin/env python3
# scripts/test_rss_ingestion.py
"""
Phase 7 RSS ingestion validation tests.

Tests run without real AI calls or publish calls.
Uses real RSS feeds where network is available,
falls back to a minimal mock feed for offline/CI use.

Run locally:
    PYTHONPATH=. python3 scripts/test_rss_ingestion.py

Run in Docker:
    docker compose -f infra/compose/docker-compose.yml run --rm daily_news \
        python /app/scripts/test_rss_ingestion.py
"""

import os
import sys
sys.path.insert(0, "/app")
sys.path.insert(0, ".")

os.environ["STORE_DB_PATH"]     = "/tmp/test_phase7.db"
os.environ["DAILY_NEWS_MODE"]   = "draft"
os.environ["PUBLISH_MODE"]      = "disabled"

from shared.logging import configure_logging, get_logger
from shared.store import init_db, is_article_processed, mark_article_processed
from shared.ingestion import fetch_feeds, get_feed_urls
from shared.ingestion.models import Article
from shared.ingestion.normalizer import _clean_text, normalize_entry
from shared.ingestion.rss import fetch_feed

configure_logging()
logger = get_logger("test_rss")

PASS = "PASS"
FAIL = "FAIL"
failures: list[str] = []


def check(name: str, fn) -> None:
    try:
        fn()
        print(f"  [{PASS}] {name}")
    except AssertionError as exc:
        print(f"  [{FAIL}] {name}: {exc}")
        failures.append(name)
    except Exception as exc:
        print(f"  [{FAIL}] {name}: {type(exc).__name__}: {exc}")
        failures.append(name)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_article_model():
    a = Article(
        source       = "Test Feed",
        title        = "German parliament passes new law",
        link         = "https://example.com/article-1",
        published_at = "2026-05-27T08:00:00Z",
        summary      = "A brief summary of the article.",
    )
    fp = a.fingerprint()
    assert len(fp) == 64,      "Fingerprint should be 64-char SHA-256 hex"
    assert isinstance(fp, str), "Fingerprint should be a string"

    # Same content = same fingerprint
    a2 = Article(
        source       = "Different Feed",
        title        = "German parliament passes new law",
        link         = "https://example.com/article-1",
        published_at = "2026-05-27T09:00:00Z",
        summary      = "Different summary",
    )
    assert a.fingerprint() == a2.fingerprint(), \
        "Same title+link should produce same fingerprint regardless of source"


def test_text_cleaning():
    assert _clean_text("<p>Hello & world</p>") == "Hello & world"
    assert _clean_text("  extra   spaces  ")       == "extra spaces"
    assert _clean_text(None)                        == ""
    assert _clean_text("")                          == ""
    assert _clean_text("<br/>Line<br/>break")       == "Line break"


def test_deduplication_in_store():
    import pathlib
    pathlib.Path(os.environ["STORE_DB_PATH"]).unlink(missing_ok=True)
    init_db()

    article = Article(
        source       = "Test",
        title        = "Dedup test article",
        link         = "https://example.com/dedup-test",
        published_at = "2026-05-27T08:00:00Z",
        summary      = "",
    )

    fp = article.fingerprint()
    assert not is_article_processed(fp), "Should not be processed yet"

    mark_article_processed(article)
    assert is_article_processed(fp),     "Should be processed after marking"

    # Second mark should be idempotent (INSERT OR IGNORE)
    mark_article_processed(article)
    assert is_article_processed(fp),     "Still processed after second mark"


def test_fetch_feeds_empty_list():
    articles = fetch_feeds(feed_urls=[], max_articles=10)
    assert articles == [], "Empty feed list should return empty list"


def test_fetch_feeds_invalid_url():
    # Should return empty, not raise
    articles = fetch_feed("https://this-url-does-not-exist-contentpilot.invalid/feed", timeout=3)
    assert isinstance(articles, list), "Should return a list even on failure"


def test_live_rss_feed():
    """
    Attempts to fetch a real RSS feed.
    Skipped gracefully if network is not available.
    """
    test_url = "https://feeds.bbci.co.uk/news/rss.xml"
    try:
        articles = fetch_feed(test_url, timeout=10)
    except Exception as exc:
        print(f"      (skipped — network not available: {exc})")
        return

    if not articles:
        print("      (skipped — feed returned no articles)")
        return

    assert len(articles) > 0
    a = articles[0]
    assert a.title,         "Article should have a title"
    assert a.link,          "Article should have a link"
    assert a.published_at,  "Article should have a published_at"
    assert a.source,        "Article should have a source"
    print(f"      Fetched {len(articles)} articles. First: {a.title[:60]!r}")


def test_max_articles_cap():
    """
    Build a synthetic feed with more than max_articles entries
    and verify the cap is respected.
    """
    from unittest.mock import patch, MagicMock
    import feedparser

    # Create 20 fake entries
    fake_entries = []
    for i in range(20):
        entry = MagicMock()
        entry.title = f"Article {i}"
        entry.link  = f"https://example.com/article-{i}"
        entry.summary = f"Summary {i}"
        entry.published_parsed = (2026, 5, 27, 8, i % 60, 0, 0, 0, 0)
        entry.updated_parsed   = None
        fake_entries.append(entry)

    mock_parsed = MagicMock()
    mock_parsed.entries = fake_entries
    mock_parsed.feed.get = MagicMock(return_value="Mock Feed")
    mock_parsed.get = MagicMock(return_value=False)

    with patch("shared.ingestion.rss.feedparser.parse", return_value=mock_parsed):
        articles = fetch_feeds(
            feed_urls    = ["https://fake-feed.example.com/rss"],
            max_articles = 5,
        )

    assert len(articles) == 5, f"Expected 5 articles, got {len(articles)}"


def test_get_feed_urls_from_env():
    from shared.ingestion.sources import get_feed_urls

    os.environ["TEST_FEED_URLS"] = "https://feed1.example.com, https://feed2.example.com,"
    urls = get_feed_urls("TEST_FEED_URLS")
    assert len(urls) == 2,                          "Should parse 2 URLs"
    assert urls[0] == "https://feed1.example.com",  "First URL should match"
    assert urls[1] == "https://feed2.example.com",  "Second URL should match"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("\nPhase 7 — RSS Ingestion Tests")
    print("=" * 45)

    check("Article model and fingerprint",       test_article_model)
    check("Text cleaning and normalization",     test_text_cleaning)
    check("Deduplication store (rss_articles)",  test_deduplication_in_store)
    check("Empty feed list returns empty",       test_fetch_feeds_empty_list)
    check("Invalid URL handled gracefully",      test_fetch_feeds_invalid_url)
    check("Live RSS feed fetch (BBC)",           test_live_rss_feed)
    check("max_articles cap enforced",           test_max_articles_cap)
    check("Feed URLs parsed from env var",       test_get_feed_urls_from_env)

    print("=" * 45)
    if failures:
        print(f"\n  {len(failures)} test(s) failed: {', '.join(failures)}")
        sys.exit(1)
    else:
        print("\n  All tests passed.")


if __name__ == "__main__":
    main()