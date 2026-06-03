# shared/media/branding.py
"""
Brand Profile — loads brand identity from environment variables.

All fields have sensible defaults so the system works out-of-the-box
with zero configuration. Set MEDIA_BRANDING_ENABLED=true and the
MEDIA_BRAND_* env vars to activate real branding.

Environment variables:
    MEDIA_BRANDING_ENABLED      master toggle (default: false)
    MEDIA_BRAND_NAME            brand display name
    MEDIA_BRAND_TAGLINE         short tagline shown in header/footer bands
    MEDIA_BRAND_CTA             call-to-action text (e.g. "Read more at...")
    MEDIA_BRAND_WEBSITE         website URL shown in overlay
    MEDIA_BRAND_PRIMARY_COLOR   hex colour for bands/bars (default: #0F172A)
    MEDIA_BRAND_ACCENT_COLOR    hex colour for CTA elements (default: #38BDF8)
    MEDIA_BRAND_LOGO_PATH       absolute path to PNG logo file (optional)
    MEDIA_BRAND_LAYOUT          layout template: A | B | C (default: B)

Usage:
    from shared.media.branding import load_brand_profile
    profile = load_brand_profile()
    if profile.enabled:
        image = apply_branding(image_bytes, profile)
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class BrandProfile:
    """
    Complete brand identity configuration for visual overlay generation.

    All fields are optional — the system degrades gracefully when fields
    are missing (e.g. no logo → draws brand name as text instead).
    """
    enabled: bool = False

    name: str = ""
    tagline: str = ""
    primary_cta: str = ""
    website: str = ""

    # Hex colour strings — validated and converted to RGBA at render time
    primary_color: str = "#0F172A"   # dark navy — works on most images
    accent_color: str = "#38BDF8"    # sky blue

    logo_path: Optional[str] = None

    # Which layout template to use: "A" | "B" | "C"
    layout: str = "B"

    def has_logo(self) -> bool:
        return bool(self.logo_path and os.path.isfile(self.logo_path))

    def display_name(self) -> str:
        """Safe display name — falls back to website domain if name not set."""
        if self.name:
            return self.name
        if self.website:
            return self.website.replace("https://", "").replace("http://", "").rstrip("/")
        return "ContentPilot"

    def __str__(self) -> str:
        return (
            f"BrandProfile(enabled={self.enabled}, name={self.name!r}, "
            f"layout={self.layout}, logo={self.has_logo()})"
        )


def _env_bool(key: str, default: bool = False) -> bool:
    raw = os.getenv(key, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes"}


def _env_str(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


def load_brand_profile() -> BrandProfile:
    """
    Build a BrandProfile from environment variables.

    Always returns a valid BrandProfile — never raises.
    When MEDIA_BRANDING_ENABLED is false (default), profile.enabled=False
    and callers should skip branding entirely.
    """
    enabled = _env_bool("MEDIA_BRANDING_ENABLED", False)

    profile = BrandProfile(
        enabled=enabled,
        name=_env_str("MEDIA_BRAND_NAME"),
        tagline=_env_str("MEDIA_BRAND_TAGLINE"),
        primary_cta=_env_str("MEDIA_BRAND_CTA"),
        website=_env_str("MEDIA_BRAND_WEBSITE"),
        primary_color=_env_str("MEDIA_BRAND_PRIMARY_COLOR", "#0F172A"),
        accent_color=_env_str("MEDIA_BRAND_ACCENT_COLOR", "#38BDF8"),
        logo_path=_env_str("MEDIA_BRAND_LOGO_PATH") or None,
        layout=_env_str("MEDIA_BRAND_LAYOUT", "B").upper(),
    )

    if profile.layout not in {"A", "B", "C"}:
        logger.warning(
            "branding_invalid_layout | layout=%r | falling_back_to_B", profile.layout
        )
        profile.layout = "B"

    logger.debug(
        "branding_profile_loaded | enabled=%s | name=%r | layout=%s | logo=%s",
        profile.enabled, profile.name, profile.layout, profile.has_logo(),
    )

    return profile


def apply_branding(image_bytes: bytes, profile: BrandProfile) -> bytes:
    """
    Apply brand overlay to image bytes using the configured layout template.

    This is the main entry point called by the media pipeline.

    Args:
        image_bytes: Raw JPEG/PNG bytes of the source image.
        profile:     BrandProfile loaded via load_brand_profile().

    Returns:
        JPEG bytes of the branded image.
        On any failure returns the ORIGINAL image_bytes unchanged — never raises.
    """
    if not profile.enabled:
        return image_bytes

    if not image_bytes:
        logger.warning("apply_branding | skipped | reason=empty_image_bytes")
        return image_bytes

    import time
    t_start = time.monotonic()

    try:
        from PIL import Image
        import io

        img = Image.open(io.BytesIO(image_bytes))
        W, H = img.size

        logger.info(
            "branding_pipeline_started | enabled=True | image_size=(%d, %d) | layout=%s",
            W, H, profile.layout,
        )

        from shared.media.layouts import apply_layout_a, apply_layout_b, apply_layout_c

        layout_fn = {
            "A": apply_layout_a,
            "B": apply_layout_b,
            "C": apply_layout_c,
        }.get(profile.layout, apply_layout_b)

        logger.info("branding_template_selected | template_id=Layout_%s", profile.layout)

        result_img = layout_fn(img, profile)

        # Encode back to JPEG
        buf = io.BytesIO()
        if result_img.mode != "RGB":
            result_img = result_img.convert("RGB")
        result_img.save(buf, format="JPEG", quality=88, optimize=True)
        result_bytes = buf.getvalue()

        duration = time.monotonic() - t_start
        logger.info(
            "branding_pipeline_completed | duration=%.3fs | status=success"
            " | original_bytes=%d | branded_bytes=%d",
            duration, len(image_bytes), len(result_bytes),
        )

        return result_bytes

    except Exception as exc:
        duration = time.monotonic() - t_start
        logger.error(
            "branding_pipeline_failed | duration=%.3fs | error=%s | returning_original",
            duration, exc,
        )
        return image_bytes
