# shared/routing/models/publishing.py
"""
Data models for the multi-client publishing layer.

PublishTarget  — a resolved destination (platform + credentials ready to use)
PublishRequest — everything the publisher needs to send one piece of content
PublishOutcome — result of one platform publish attempt
PublishSummary — aggregated result across all platforms for one article
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class PublishFormat(str, Enum):
    TEXT_LINK  = "text_link"
    IMAGE_POST = "image_post"
    REEL       = "reel"


class PublishPlatform(str, Enum):
    WORDPRESS = "wordpress"
    FACEBOOK  = "facebook"


@dataclass(frozen=True)
class PublishTarget:
    """
    A fully resolved publish destination.

    Credentials are resolved values (strings), not env var names.
    This object is ephemeral — never persisted, never logged in full.
    """
    client_id: str
    platform: PublishPlatform
    format: PublishFormat
    # Resolved credentials (platform-specific)
    credentials: dict[str, str] = field(default_factory=dict)
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class PublishRequest:
    """
    Everything needed to publish one piece of content to one client.

    article_id:   Unique identifier for deduplication / logging.
    title:        Article or post title.
    body:         Full text content (HTML-safe for WordPress).
    summary:      Short excerpt / social caption.
    url:          Source URL (used in text_link posts).
    image_url:    Optional image for image_post / reel cover.
    video_url:    Optional video URL for reels.
    tags:         AI-generated tags for classification and WP tagging.
    """
    article_id: str
    title: str
    body: str
    summary: str
    url: str = ""
    image_url: str | None = None
    video_url: str | None = None
    tags: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class PublishOutcome:
    """Result of one publish attempt to one platform."""
    client_id: str
    platform: PublishPlatform
    format: PublishFormat
    success: bool
    external_id: str | None = None       # WP post ID, FB post ID, etc.
    url: str | None = None
    error_message: str | None = None
    retryable: bool = False
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        status = "OK" if self.success else "FAILED"
        return (
            f"[{self.client_id}:{self.platform.value}:{self.format.value}] "
            f"{status} id={self.external_id} err={self.error_message}"
        )


@dataclass
class PublishSummary:
    """Aggregated result of routing + publishing for one article."""
    article_id: str
    client_id: str | None
    routing_score: float
    outcomes: list[PublishOutcome] = field(default_factory=list)
    routed: bool = False

    @property
    def succeeded(self) -> list[PublishOutcome]:
        return [o for o in self.outcomes if o.success]

    @property
    def failed(self) -> list[PublishOutcome]:
        return [o for o in self.outcomes if not o.success]

    @property
    def all_succeeded(self) -> bool:
        return bool(self.outcomes) and all(o.success for o in self.outcomes)

    def __str__(self) -> str:
        ok = len(self.succeeded)
        total = len(self.outcomes)
        return (
            f"PublishSummary(article={self.article_id!r}, client={self.client_id!r}, "
            f"score={self.routing_score:.3f}, {ok}/{total} succeeded)"
        )
