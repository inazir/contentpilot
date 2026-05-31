# shared/ingestion/normalizer.py
"""
Cleans raw feed data into consistent Article objects.

Handles: whitespace, missing fields, timestamp formats, HTML fragments
in RSS summaries (some feeds put <p> tags in their summary field).
"""

import html
import re
from datetime import datetime, timezone

import feedparser


def _clean_text(value: str | None) -> str:
    """Strip HTML tags, decode HTML entities, normalize whitespace."""
    if not value:
        return ""
    # Remove HTML tags
    value = re.sub(r"<[^>]+>", " ", value)
    # Decode HTML entities (& < etc.)
    value = html.unescape(value)
    # Normalize whitespace
    return " ".join(value.split()).strip()


def _parse_timestamp(entry) -> str:
    """
    Convert feedparser's parsed time struct to ISO 8601 UTC string.
    Falls back to current UTC time if the feed doesn't provide a date.
    """
    time_struct = (
        getattr(entry, "published_parsed", None)
        or getattr(entry, "updated_parsed", None)
    )

    if time_struct:
        try:
            dt = datetime(*time_struct[:6], tzinfo=timezone.utc)
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            pass

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_entry(entry, source: str) -> "Article | None":
    """
    Convert a feedparser entry dict into a clean Article.
    Returns None if the entry lacks a title or link (unusable).
    """
    from shared.ingestion.models import Article

    title = _clean_text(getattr(entry, "title", None))
    link  = (getattr(entry, "link", "") or "").strip()

    if not title or not link:
        return None

    # Summary: prefer summary over description, some feeds use different keys
    raw_summary = (
        getattr(entry, "summary", None)
        or getattr(entry, "description", None)
        or ""
    )
    summary = _clean_text(raw_summary)

    return Article(
        source       = source,
        title        = title,
        link         = link,
        published_at = _parse_timestamp(entry),
        summary      = summary,
    )