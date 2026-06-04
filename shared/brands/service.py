# shared/brands/service.py
"""
Brand service — the only place BrandContext objects are constructed.

Priority for every field:
    1. Database (brand_credentials / brand_profiles)
    2. Environment variables (brand_id=1 fallback only)

RULE: No module may construct BrandContext directly.
      Always call get_brand_context(brand_id) or get_brand_context_by_slug(slug).
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from .models import BrandContext
from .repository import (
    get_brand_by_id,
    get_brand_by_slug,
    get_credentials,
    get_profile,
)

logger = logging.getLogger(__name__)

# Credential type constants
CRED_FACEBOOK    = "facebook"
CRED_INSTAGRAM   = "instagram"
CRED_WORDPRESS   = "wordpress"
CRED_AI_OVERRIDE = "ai_override"
CRED_SOCIAL_TARGETS = "social_targets"


def get_brand_context(brand_id: int) -> BrandContext:
    """
    Build a BrandContext for brand_id.

    For brand_id=1: missing DB values fall back to environment variables.
    For brand_id>1: all values must come from DB.

    Raises ValueError if brand not found or disabled.
    """
    brand = get_brand_by_id(brand_id)
    if not brand:
        raise ValueError(f"Brand not found: id={brand_id}")
    if not brand.enabled:
        raise ValueError(f"Brand is disabled: id={brand_id} slug={brand.slug}")

    return _build_context(brand)


def get_brand_context_by_slug(slug: str) -> BrandContext:
    """Build a BrandContext for a brand slug."""
    brand = get_brand_by_slug(slug)
    if not brand:
        raise ValueError(f"Brand not found: slug={slug!r}")
    if not brand.enabled:
        raise ValueError(f"Brand is disabled: slug={slug!r}")

    return _build_context(brand)


def get_default_brand_context() -> BrandContext:
    """Return BrandContext for brand_id=1 (always GermanySupport)."""
    return get_brand_context(1)


def _build_context(brand) -> BrandContext:
    """Internal: resolve all fields with DB→env fallback for brand_id=1."""
    is_default = brand.id == 1
    profile = get_profile(brand.id)

    # --- Profile fields ---
    website_url     = _resolve(profile.website_url if profile else None,
                               "DEFAULT_BRAND_WEBSITE" if is_default else None)
    brand_name      = _resolve(profile.brand_name if profile else None,
                               "DEFAULT_BRAND_NAME" if is_default else None,
                               default=brand.name)
    logo_path       = _resolve(profile.logo_path if profile else None,
                               "BRAND_LOGO_PATH" if is_default else None)
    brand_cta       = _resolve(profile.brand_cta if profile else None,
                               "BRAND_CTA" if is_default else None)
    branding_layout = _resolve(profile.branding_layout if profile else None,
                               "BRAND_BRANDING_LAYOUT" if is_default else None)

    # --- Social targets ---
    social_targets = _resolve_social_targets(brand.id, is_default)

    # --- WordPress credentials ---
    wp_url, wp_user, wp_password, wp_status = _resolve_wordpress(brand.id, is_default)

    # --- AI overrides ---
    ai_provider, ai_model = _resolve_ai(brand.id, is_default)

    # --- Publish mode ---
    publish_mode = _resolve(None, "PUBLISH_MODE" if is_default else None, default="disabled")

    ctx = BrandContext(
        brand_id        = brand.id,
        brand_slug      = brand.slug,
        brand_name      = brand_name,
        website_url     = website_url,
        logo_path       = logo_path,
        brand_cta       = brand_cta,
        branding_layout = branding_layout,
        social_targets  = social_targets,
        wp_url          = wp_url,
        wp_user         = wp_user,
        wp_password     = wp_password,
        wp_default_status = wp_status,
        ai_provider     = ai_provider,
        ai_model        = ai_model,
        publish_mode    = publish_mode,
    )

    logger.debug(
        "brand_context_built | brand_id=%d | brand_slug=%s | targets=%s | wp=%s",
        brand.id, brand.slug, social_targets, bool(wp_url),
    )
    return ctx


def _resolve(
    db_value: Optional[str],
    env_key: Optional[str],
    default: str = "",
) -> str:
    """Return first non-empty value from: db_value → env → default."""
    if db_value:
        return db_value.strip()
    if env_key:
        env_val = os.getenv(env_key, "").strip()
        if env_val:
            return env_val
    return default


def _resolve_social_targets(brand_id: int, is_default: bool) -> list[str]:
    """
    Resolve social publishing targets.

    DB: brand_credentials row of type 'social_targets'
        credential_json: {"targets": ["gs_facebook_main", "gs_instagram_main"]}

    Fallback (brand_id=1 only): DAILY_NEWS_TARGETS env var.
    """
    cred = get_credentials(brand_id, CRED_SOCIAL_TARGETS)
    if cred:
        data = cred.as_dict()
        targets = data.get("targets", [])
        if targets:
            return [t.strip() for t in targets if t.strip()]

    if is_default:
        raw = os.getenv("DAILY_NEWS_TARGETS", "").strip()
        if raw:
            return [t.strip() for t in raw.split(",") if t.strip()]

    return []


def _resolve_wordpress(
    brand_id: int, is_default: bool
) -> tuple[Optional[str], Optional[str], Optional[str], str]:
    """
    Returns (wp_url, wp_user, wp_password, wp_default_status).

    DB: brand_credentials of type 'wordpress'
        {"url": "...", "user": "...", "password": "...", "default_status": "draft"}

    Fallback (brand_id=1): WP_URL, WP_USER, WP_APP_PASSWORD env vars.
    """
    cred = get_credentials(brand_id, CRED_WORDPRESS)
    if cred:
        data = cred.as_dict()
        return (
            data.get("url"),
            data.get("user"),
            data.get("password"),
            data.get("default_status", "draft"),
        )

    if is_default:
        return (
            os.getenv("WP_URL") or os.getenv("WORDPRESS_URL"),
            os.getenv("WP_USER") or os.getenv("WORDPRESS_USER"),
            os.getenv("WP_APP_PASSWORD") or os.getenv("WORDPRESS_PASSWORD"),
            os.getenv("DAILY_NEWS_WORDPRESS_STATUS", "draft"),
        )

    return None, None, None, "draft"


def _resolve_ai(
    brand_id: int, is_default: bool
) -> tuple[Optional[str], Optional[str]]:
    """
    Returns (ai_provider, ai_model) overrides, or (None, None) to use defaults.

    DB: brand_credentials of type 'ai_override'
        {"provider": "anthropic", "model": "claude-haiku-4-5"}
    """
    cred = get_credentials(brand_id, CRED_AI_OVERRIDE)
    if cred:
        data = cred.as_dict()
        return data.get("provider"), data.get("model")

    # For brand_id=1, existing AI_DEFAULT_PROVIDER / DAILY_NEWS_AI_PROVIDER env
    # vars are already handled by shared.ai.config — no need to re-resolve here.
    return None, None
