# shared/ingestion/models.py
"""
Core data models for the ingestion layer.

Article is the normalized unit of work produced by any feed source
and consumed by any module. It carries no platform-specific logic.
"""

from dataclasses import dataclass


@dataclass
class Article:
    source:       str           # feed URL or feed title
    title:        str
    link:         str
    published_at: str           # ISO 8601 UTC string, e.g. "2026-05-27T08:00:00Z"
    summary:      str           # RSS-provided summary, may be empty string

    def fingerprint(self) -> str:
        """
        Stable identity hash for deduplication.
        Based on title + link so the same article from two feeds
        is still treated as one item.
        """
        import hashlib
        return hashlib.sha256(
            f"{self.title.strip().lower()}|{self.link.strip().lower()}".encode()
        ).hexdigest()