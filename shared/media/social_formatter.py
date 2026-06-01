# shared/media/social_formatter.py
"""
Social Media Image Formatter — Phase 10A (resize only).

Transforms a source image into one or more platform-specific pixel
dimensions using center-fill cropping.

Phase 10A scope — this module ONLY handles dimension transformation.
It does NOT apply text, branding, logos, ads, or overlays of any kind.
Those capabilities are introduced in Phase 10B via image_composition.py.

Supported formats
-----------------
  FACEBOOK_LANDSCAPE  1200 × 630   Recommended for link posts & ads
  FACEBOOK_SQUARE     1080 × 1080  Boosted posts, carousel
  INSTAGRAM_SQUARE    1080 × 1080  Standard feed post
  INSTAGRAM_PORTRAIT  1080 × 1350  Vertical feed (max crop ratio)
  STORY               1080 × 1920  Instagram / Facebook Stories

Usage
-----
    from shared.media.social_formatter import format_for_social
    from shared.media.models import SocialFormat

    results = format_for_social(
        image_bytes=raw_bytes,
        formats=[SocialFormat.FACEBOOK_LANDSCAPE, SocialFormat.INSTAGRAM_SQUARE],
    )
    for r in results:
        if r.success:
            Path(f"{r.format.value}.jpg").write_bytes(r.image_bytes)
"""

from __future__ import annotations

import logging
import time

from .image_processing import resize_fill
from .models import SocialFormat, SocialImageResult

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Format registry  (width, height) in pixels
# ---------------------------------------------------------------------------


_DIMENSIONS: dict[SocialFormat, tuple[int, int]] = {
    SocialFormat.FACEBOOK_LANDSCAPE:  (1200, 630),
    SocialFormat.FACEBOOK_SQUARE:     (1080, 1080),
    SocialFormat.INSTAGRAM_SQUARE:    (1080, 1080),
    SocialFormat.INSTAGRAM_PORTRAIT:  (1080, 1350),
    SocialFormat.STORY:               (1080, 1920),
}

_DEFAULT_FORMAT  = "JPEG"
_DEFAULT_QUALITY = 90


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def format_for_social(
    image_bytes: bytes,
    formats: list[SocialFormat],
    output_format: str = _DEFAULT_FORMAT,
    quality: int = _DEFAULT_QUALITY,
) -> list[SocialImageResult]:
    """
    Transform a source image into one or more social media sizes.

    Each format is processed independently — a failure in one format does
    not prevent the others from completing.

    Args:
        image_bytes:   Source image as raw bytes (any Pillow-readable format).
        formats:       Which SocialFormat values to produce.
        output_format: Output encoding — "JPEG", "PNG", or "WEBP".
        quality:       Compression quality (1–95 for JPEG / WEBP).

    Returns:
        List[SocialImageResult] in the same order as `formats`.
        Never raises.
    """
    if not image_bytes:
        logger.warning("format_for_social | empty image_bytes received")
        return [
            SocialImageResult(format=fmt, success=False, error="image_bytes is empty")
            for fmt in formats
        ]

    if not formats:
        logger.warning("format_for_social | empty formats list")
        return []

    logger.info(
        "social_formatter_start | formats=%s | output_format=%s | quality=%d",
        [f.value for f in formats], output_format, quality,
    )

    results: list[SocialImageResult] = [
        _format_one(image_bytes, fmt, output_format, quality)
        for fmt in formats
    ]

    ok    = sum(1 for r in results if r.success)
    fail  = len(results) - ok
    logger.info(
        "social_formatter_done | total=%d | ok=%d | failed=%d",
        len(results), ok, fail,
    )
    return results


def get_dimensions(fmt: SocialFormat) -> tuple[int, int]:
    """Return the registered (width, height) for a SocialFormat."""
    return _DIMENSIONS[fmt]


def all_formats() -> list[SocialFormat]:
    """Return every registered SocialFormat."""
    return list(_DIMENSIONS)


# ---------------------------------------------------------------------------
# Internal
# ---------------------------------------------------------------------------


def _format_one(
    image_bytes: bytes,
    fmt: SocialFormat,
    output_format: str,
    quality: int,
) -> SocialImageResult:
    """Process one format. Returns SocialImageResult — never raises."""
    dims = _DIMENSIONS.get(fmt)
    if dims is None:
        return SocialImageResult(
            format=fmt, success=False,
            error=f"No dimensions registered for format '{fmt}'",
        )

    width, height = dims
    t = time.monotonic()

    try:
        out_bytes = resize_fill(
            image_bytes,
            width=width,
            height=height,
            output_format=output_format,
            quality=quality,
        )
        logger.debug(
            "social_format_ok | fmt=%s | %dx%d | %d bytes | %.3fs",
            fmt.value, width, height, len(out_bytes), time.monotonic() - t,
        )
        return SocialImageResult(
            format=fmt,
            success=True,
            image_bytes=out_bytes,
            width=width,
            height=height,
        )

    except Exception as exc:
        logger.error(
            "social_format_error | fmt=%s | error=%s | %.3fs",
            fmt.value, exc, time.monotonic() - t,
        )
        return SocialImageResult(format=fmt, success=False, error=str(exc))
