# shared/ingestion/__init__.py
from .models import Article
from .rss import fetch_feeds
from .sources import get_feed_urls, get_max_articles, get_feed_timeout

__all__ = [
    "Article",
    "fetch_feeds",
    "get_feed_urls",
    "get_max_articles",
    "get_feed_timeout",
]