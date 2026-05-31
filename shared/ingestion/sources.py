# shared/ingestion/sources.py
"""
Feed source configuration reader.

Reads feed URLs and ingestion parameters from environment variables.
Keeps env parsing out of module code.
"""

import os


def get_feed_urls(env_var: str = "DAILY_NEWS_RSS_FEEDS") -> list[str]:
    """
    Parse a comma-separated list of RSS feed URLs from an env var.
    Returns empty list if the var is not set.
    """
    raw = os.getenv(env_var, "").strip()
    if not raw:
        return []
    return [url.strip() for url in raw.split(",") if url.strip()]


def get_max_articles(env_var: str = "DAILY_NEWS_MAX_ARTICLES", default: int = 10) -> int:
    try:
        return int(os.getenv(env_var, str(default)))
    except ValueError:
        return default


def get_feed_timeout(env_var: str = "DAILY_NEWS_FEED_TIMEOUT", default: int = 10) -> int:
    try:
        return int(os.getenv(env_var, str(default)))
    except ValueError:
        return default