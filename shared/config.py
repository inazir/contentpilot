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
