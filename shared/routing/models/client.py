# shared/routing/models/client.py
"""
Client configuration data models.

These are the canonical data structures that flow through the routing and
publishing layers. They are fully decoupled from storage format — the
repository layer is responsible for hydrating these from JSON, SQLite, etc.

Design notes:
  - All credential values are read from environment variables at runtime,
    never embedded in the config object. The config stores the env var *name*
    (e.g. app_password_env = "FINANCE_A_WP_APP_PASSWORD"). Callers resolve
    these via os.getenv() when actually needed for an API call.
  - frozen=True on leaf configs enforces immutability after construction.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class WordPressClientConfig:
    """WordPress publishing credentials and defaults for one client."""
    base_url: str
    username: str
    app_password_env: str          # env var name containing the app password
    default_status: str = "draft"  # "draft" | "publish"
    default_categories: list[int] = field(default_factory=list)
    default_tags: list[int] = field(default_factory=list)
    timeout_seconds: int = 30

    def resolve_app_password(self) -> str:
        """
        Retrieve the app password from the environment at call time.
        Raises CredentialMissingError if the env var is not set.
        """
        from shared.routing.exceptions import CredentialMissingError
        value = os.getenv(self.app_password_env, "").strip()
        if not value:
            raise CredentialMissingError(
                f"WordPress app password not found in env var: {self.app_password_env}"
            )
        return value


@dataclass(frozen=True)
class FacebookClientConfig:
    """Facebook Page credentials for one client."""
    page_id_env: str          # env var name containing the Page ID
    access_token_env: str     # env var name containing the Page access token
    enabled: bool = True

    def resolve_page_id(self) -> str:
        from shared.routing.exceptions import CredentialMissingError
        value = os.getenv(self.page_id_env, "").strip()
        if not value:
            raise CredentialMissingError(
                f"Facebook Page ID not found in env var: {self.page_id_env}"
            )
        return value

    def resolve_access_token(self) -> str:
        from shared.routing.exceptions import CredentialMissingError
        value = os.getenv(self.access_token_env, "").strip()
        if not value:
            raise CredentialMissingError(
                f"Facebook access token not found in env var: {self.access_token_env}"
            )
        return value


@dataclass(frozen=True)
class ImagePostConfig:
    enabled: bool = False
    image_provider: str = "mock"   # "mock" | "openai" | "pexels" etc.


@dataclass(frozen=True)
class ReelConfig:
    enabled: bool = False
    video_url_env: str = ""        # env var name containing the video URL

    def resolve_video_url(self) -> str:
        from shared.routing.exceptions import CredentialMissingError
        if not self.video_url_env:
            raise CredentialMissingError("Reel video_url_env is not configured")
        value = os.getenv(self.video_url_env, "").strip()
        if not value:
            raise CredentialMissingError(
                f"Reel video URL not found in env var: {self.video_url_env}"
            )
        return value


@dataclass(frozen=True)
class PublishingPreferences:
    """
    Controls what formats and how often a client publishes.

    formats: ordered list of publish formats to attempt.
             Valid values: "text_link" | "image_post" | "reel"
    """
    formats: tuple[str, ...]
    image_post: ImagePostConfig = field(default_factory=ImagePostConfig)
    reel: ReelConfig = field(default_factory=ReelConfig)
    max_posts_per_day: int = 5


@dataclass
class ClientConfig:
    """
    Complete configuration for one publishing client.

    This is the primary entity in the routing system. Business type is
    metadata only — routing is always keyed on client_id.

    routing_keywords: list of keywords/phrases used to score article relevance.
    routing_priority: tiebreaker when multiple clients score equally (higher wins).
    """
    client_id: str
    client_name: str
    business_type: str
    enabled: bool
    routing_keywords: list[str]
    routing_priority: int
    wordpress: WordPressClientConfig
    facebook: FacebookClientConfig
    publishing_preferences: PublishingPreferences
    extra: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f"ClientConfig(id={self.client_id!r}, name={self.client_name!r}, "
            f"type={self.business_type!r}, enabled={self.enabled})"
        )
