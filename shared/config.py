"""
Central runtime configuration for ContentPilot.

All environment variable reads go through here.
Nothing else should call os.getenv() for platform/publish config.

AI-specific config still lives in shared/ai/config.py (backward compat).
"""

import os
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Publish
# ---------------------------------------------------------------------------

def get_publish_mode() -> str:
    """
    disabled → no publishing, generation only
    mock     → full pipeline, fake IDs, no real API calls
    real     → real API calls (platform must be enabled + configured)
    """
    return os.getenv("PUBLISH_MODE", "disabled").strip().lower()


# ---------------------------------------------------------------------------
# Social Targets (multi-page/account publishing)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SocialTarget:
    """
    Represents a specific social media account/page to publish to.

    Example target_key: "gs_facebook_main", "gs_facebook_brand2", "gs_instagram_main"
    """
    key:          str        # e.g. "gs_facebook_main"
    platform:     str        # "facebook" or "instagram"
    enabled:      bool
    page_id:      str        # Facebook Page ID or Instagram Account ID
    access_token: str
    name:         str = ""   # human-readable label for logs


def load_social_targets() -> dict[str, SocialTarget]:
    """
    Reads all targets from SOCIAL_TARGETS env var and builds
    a dict of {target_key: SocialTarget}.
    """
    raw = os.getenv("SOCIAL_TARGETS", "").strip()
    if not raw:
        return {}

    targets: dict[str, SocialTarget] = {}

    for key in [k.strip() for k in raw.split(",") if k.strip()]:
        normalized_key = key.lower()
        env_key = key.upper()
        prefix = f"SOCIAL__{env_key}"

        platform = os.getenv(f"{prefix}__PLATFORM", "").strip().lower()
        if not platform:
            continue

        targets[normalized_key] = SocialTarget(
            key=key,
            platform=platform,
            enabled=os.getenv(f"{prefix}__ENABLED", "false").strip().lower() in {"1", "true", "yes"},
            page_id=os.getenv(f"{prefix}__PAGE_ID", "").strip(),
            access_token=os.getenv(f"{prefix}__ACCESS_TOKEN", "").strip(),
            name=os.getenv(f"{prefix}__NAME", key).strip(),
        )

    return targets


# ---------------------------------------------------------------------------
# Store
# ---------------------------------------------------------------------------

def get_db_path() -> str:
    return os.getenv("STORE_DB_PATH", "/app/data/db/contentpilot.db").strip()


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def get_log_level() -> str:
    return os.getenv("LOG_LEVEL", "INFO").strip().upper()


# ---------------------------------------------------------------------------
# WordPress
# ---------------------------------------------------------------------------

def get_wordpress_config():
    """
    Build WordPressConfig from environment variables.
    Raises ValueError if required credentials are missing.
    """
    from shared.wordpress.models import WordPressConfig

    base_url     = os.getenv("WORDPRESS_BASE_URL", "").strip()
    username     = os.getenv("WORDPRESS_USERNAME", "").strip()
    app_password = os.getenv("WORDPRESS_APP_PASSWORD", "").strip()

    if not base_url:
        raise ValueError("WORDPRESS_BASE_URL is not set")
    if not username or not app_password:
        raise ValueError(
            "WORDPRESS_USERNAME and WORDPRESS_APP_PASSWORD must both be set"
        )

    return WordPressConfig(
        base_url        = base_url,
        username        = username,
        app_password    = app_password,
        default_status  = os.getenv("WORDPRESS_DEFAULT_STATUS", "draft").strip().lower(),
        timeout_seconds = int(os.getenv("WORDPRESS_TIMEOUT_SECONDS", "30")),
        max_retries     = int(os.getenv("WORDPRESS_MAX_RETRIES", "3")),
    )


# ---------------------------------------------------------------------------
# Media / Content Asset Feature Flags (Phase 11B)
# ---------------------------------------------------------------------------

def get_media_config() -> "MediaConfig":
    """Build MediaConfig from environment variables."""
    return MediaConfig(
        enabled           = _env_bool("ENABLE_MEDIA_ASSETS",    True),
        featured_images   = _env_bool("ENABLE_FEATURED_IMAGES", True),
        social_images     = _env_bool("ENABLE_SOCIAL_IMAGES",   True),
        branding_enabled  = _env_bool("MEDIA_BRANDING_ENABLED", False),
        ads_enabled       = _env_bool("MEDIA_ADS_ENABLED",      False),
        storage_dir       = os.getenv("MEDIA_STORAGE_DIR", "/app/data/media").strip(),
    )


@dataclass(frozen=True)
class MediaConfig:
    """
    Feature flags for the Phase 11 content asset pipeline.

    All flags default to safe values:
      - enabled=True   → asset generation active
      - featured_images=True → upload featured image to WordPress
      - social_images=True   → generate social variants
      - branding_enabled=False → no branding overlay by default
      - ads_enabled=False      → no ads by default
    """
    enabled:          bool
    featured_images:  bool
    social_images:    bool
    branding_enabled: bool
    ads_enabled:      bool
    storage_dir:      str


def _env_bool(key: str, default: bool) -> bool:
    raw = os.getenv(key, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes"}
