# shared/wordpress/models.py
"""
Data models for WordPress publishing.

Dataclasses only — no logic, no imports from other shared modules.
Mirrors shared/social/models.py pattern.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class WordPressConfig:
    """
    Connection config for a single WordPress site.
    Built by shared/config.py — never constructed directly in modules.
    """
    base_url:        str
    username:        str
    app_password:    str
    default_status:  str = "draft"    # "draft" | "publish"
    timeout_seconds: int = 30
    max_retries:     int = 3


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

@dataclass
class PostRequest:
    """
    All fields needed to create or update a WordPress post.

    Only title and content are required.
    All other fields are optional and omitted from the API payload if None.
    """
    title:          str
    content:        str                      # HTML-safe content body
    status:         str = "draft"            # "draft" | "publish"
    excerpt:        str | None = None
    categories:     list[int] | None = None  # WordPress category IDs
    tags:           list[int] | None = None  # WordPress tag IDs
    featured_media: int | None = None        # WordPress media attachment ID
    slug:           str | None = None        # URL slug — auto-generated if None
    meta:           dict[str, Any] = field(default_factory=dict)

    def to_api_payload(self) -> dict:
        """
        Serialize to WordPress REST API payload.
        Omits None fields so WordPress uses its own defaults.
        """
        payload: dict[str, Any] = {
            "title":   self.title,
            "content": self.content,
            "status":  self.status,
        }
        if self.excerpt is not None:
            payload["excerpt"] = self.excerpt
        if self.categories is not None:
            payload["categories"] = self.categories
        if self.tags is not None:
            payload["tags"] = self.tags
        if self.featured_media is not None:
            payload["featured_media"] = self.featured_media
        if self.slug is not None:
            payload["slug"] = self.slug
        if self.meta:
            payload["meta"] = self.meta
        return payload


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

@dataclass
class PostResponse:
    """
    Structured result returned from every publish/update operation.
    Never raises — failures are represented as success=False.
    """
    success:           bool
    wordpress_post_id: int | None = None
    url:               str | None = None
    status:            str | None = None      # "draft", "publish", etc.
    timestamp:         str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    error_message:     str | None = None
    retryable:         bool = False
    metadata:          dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        if self.success:
            return (
                f"[wordpress] OK post_id={self.wordpress_post_id} "
                f"status={self.status} url={self.url}"
            )
        flag = "retryable" if self.retryable else "permanent"
        return f"[wordpress] FAILED ({flag}): {self.error_message}"
