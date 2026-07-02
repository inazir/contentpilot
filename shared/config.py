"""
Central runtime configuration for ContentPilot.

All environment variable reads go through here.
Nothing else should call os.getenv() for platform/publish config.

AI-specific config still lives in shared/ai/config.py (backward compat).
That file will eventually merge here.
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

    SOCIAL_TARGETS format: "gs_facebook_main,gs_facebook_brand2,gs_instagram_main"

    Each target must have these env vars:
    - SOCIAL__{TARGET_KEY}__PLATFORM
    - SOCIAL__{TARGET_KEY}__ENABLED
    - SOCIAL__{TARGET_KEY}__PAGE_ID
    - SOCIAL__{TARGET_KEY}__ACCESS_TOKEN
    - SOCIAL__{TARGET_KEY}__NAME (optional)

    Example:
        SOCIAL_TARGETS=gs_facebook_main,gs_facebook_brand2
        SOCIAL__GS_FACEBOOK_MAIN__PLATFORM=facebook
        SOCIAL__GS_FACEBOOK_MAIN__ENABLED=true
        SOCIAL__GS_FACEBOOK_MAIN__PAGE_ID=111111111
        SOCIAL__GS_FACEBOOK_MAIN__ACCESS_TOKEN=EAAxxxxx
        SOCIAL__GS_FACEBOOK_BRAND2__PLATFORM=facebook
        SOCIAL__GS_FACEBOOK_BRAND2__ENABLED=true
        SOCIAL__GS_FACEBOOK_BRAND2__PAGE_ID=222222222
        SOCIAL__GS_FACEBOOK_BRAND2__ACCESS_TOKEN=EAAyyyyy

    Returns:
        dict[str, SocialTarget]: Empty dict if SOCIAL_TARGETS is not set.
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
            continue   # skip incomplete target definitions

        targets[normalized_key] = SocialTarget(
            key=key,
            platform=platform,
            enabled=os.getenv(f"{prefix}__ENABLED", "false").strip().lower() in {"1", "true", "yes"},
            page_id=os.getenv(f"{prefix}__PAGE_ID", "").strip(),
            access_token=os.getenv(f"{prefix}__ACCESS_TOKEN", "").strip(),
            name=os.getenv(f"{prefix}__NAME", key).strip(),
        )

    return targets


def load_social_targets_for_brand(
    brand_id: int, target_keys: list[str] | None = None
) -> dict[str, SocialTarget]:
    """
    Brand-aware variant of load_social_targets(). Phase 13C Step 7a.

    Resolution priority per target_key:
        1. brand_credentials row (credential_type='facebook' or 'instagram')
           for this brand_id, IF it contains page_id/access_token
        2. Fall back to load_social_targets()'s env-based resolution for
           that same key (so existing env-configured brands/keys keep
           working with zero changes — this function is purely additive)

    Args:
        brand_id:    The brand whose credentials to check first.
        target_keys: Which target keys to resolve. If None, uses every
                      key that load_social_targets() would find from env
                      (SOCIAL_TARGETS) — preserves current behavior when
                      no dashboard-configured credential exists yet.

    Returns:
        dict[str, SocialTarget] — same shape as load_social_targets().

    Note: this function intentionally does NOT replace load_social_targets().
    Both exist side by side. Callers (e.g. runner.py) opt into brand-aware
    resolution explicitly by calling this function with a brand_id.
    """
    # Lazy import: shared.brands depends on shared.config indirectly via
    # the same data dir conventions, and importing at module level here
    # would risk a circular import if shared.brands ever imports from
    # shared.config in the future. Importing inside the function avoids
    # that risk entirely.
    from shared.brands import get_credentials, CRED_FACEBOOK, CRED_INSTAGRAM

    env_targets = load_social_targets()

    if target_keys is None:
        target_keys = list(env_targets.keys())

    # Map platform name -> which credential_type constant to check.
    # Only facebook and instagram have brand_credentials support today;
    # anything else falls straight through to the env-based result.
    _CRED_TYPE_BY_PLATFORM = {
        "facebook": CRED_FACEBOOK,
        "instagram": CRED_INSTAGRAM,
    }

    resolved: dict[str, SocialTarget] = {}

    for key in target_keys:
        normalized_key = key.strip().lower()
        env_target = env_targets.get(normalized_key)

        if env_target is None:
            # No env definition for this key at all — nothing to merge
            # with, and we don't know its platform. Skip it; this
            # mirrors load_social_targets()'s existing behavior of
            # silently skipping incomplete target definitions.
            continue

        cred_type = _CRED_TYPE_BY_PLATFORM.get(env_target.platform)
        if cred_type is None:
            # Unsupported platform for brand_credentials lookup (e.g.
            # future platforms not yet added to brand_credentials) —
            # use the env-resolved target as-is.
            resolved[normalized_key] = env_target
            continue

        cred = get_credentials(brand_id, cred_type)
        if cred is None:
            # No dashboard-saved credential yet for this brand+platform —
            # fall back to whatever load_social_targets() already found.
            resolved[normalized_key] = env_target
            continue

        cred_data = cred.as_dict()
        db_page_id = cred_data.get("page_id", "").strip()
        db_access_token = cred_data.get("access_token", "").strip()

        if not db_page_id and not db_access_token:
            # Credential row exists but is empty (e.g. only one field
            # was ever saved) — fall back to env rather than building
            # a SocialTarget with missing required fields.
            resolved[normalized_key] = env_target
            continue

        # Build a SocialTarget using DB values where present, env
        # values as fallback for any individual field left unset in
        # the DB credential.
        resolved[normalized_key] = SocialTarget(
            key=env_target.key,
            platform=env_target.platform,
            enabled=env_target.enabled,  # enabled flag stays env-controlled for now
            page_id=db_page_id or env_target.page_id,
            access_token=db_access_token or env_target.access_token,
            name=env_target.name,
        )

    return resolved


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
