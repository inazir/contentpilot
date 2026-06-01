# shared/media/featured_image.py
"""
Featured Image Service — Phase 10B.

Orchestrates the full pipeline from article metadata to a composed,
ready-to-publish image:

    1. Search stock image (StockImageRequest → search_stock_image)
    2. Fallback: AI generate  (ImageRequest → generate_image)
    3. Compose  (image_bytes → compose_image)
    4. [Optional] Save to disk
    5. Return FeaturedImageResult

Architecture contract (matching Phase 10A):
    - All image data travels as raw bytes until the optional final save.
    - No file I/O in generate_image() or search_stock_image() (10A convention).
    - File save happens here only, controlled by save_to_disk parameter.

Usage:
    from shared.media.featured_image import get_featured_image
    from shared.media.models import ImageCompositionConfig, BrandingConfig

    result = get_featured_image(
        title="Opening a Bank Account in Germany",
        summary="A guide for expats...",
        keywords=["Germany", "bank account", "expat"],
        config=ImageCompositionConfig(
            branding=BrandingConfig(enable=True, brand_name="GermanStudies.de"),
        ),
        save_to_disk=True,
    )
    if result.success:
        print(result.composed.local_path)   # written to disk
        print(result.composed.image_bytes)  # always available in memory
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

from .image_composition import compose_image
from .image_generation import generate_image
from .image_sourcing import search_stock_image
from .models import (
    FeaturedImageResult,
    ImageCompositionConfig,
    ImageProvider,
    ImageRequest,
    StockImageRequest,
    StockProvider,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Provider env-var helpers
# ---------------------------------------------------------------------------

def _get_generation_provider() -> ImageProvider:
    raw = os.getenv("IMAGE_GENERATION_PROVIDER", "mock").strip().lower()
    try:
        return ImageProvider(raw)
    except ValueError:
        logger.warning("Unknown IMAGE_GENERATION_PROVIDER=%r — falling back to mock", raw)
        return ImageProvider.MOCK


def _get_stock_provider() -> StockProvider:
    raw = os.getenv("IMAGE_STOCK_PROVIDER", "mock").strip().lower()
    try:
        return StockProvider(raw)
    except ValueError:
        logger.warning("Unknown IMAGE_STOCK_PROVIDER=%r — falling back to mock", raw)
        return StockProvider.MOCK


# ---------------------------------------------------------------------------
# Prompt / keyword helpers
# ---------------------------------------------------------------------------

def _build_generation_prompt(title: str, summary: str, keywords: list[str]) -> str:
    """Build a compact AI image-generation prompt from article metadata."""
    parts = [f"High-quality editorial photograph for article: {title}."]
    if keywords:
        parts.append(f"Theme: {', '.join(keywords[:6])}.")
    if summary:
        parts.append(f"Context: {summary[:120].rstrip()}.")
    parts.append("Professional, clean, suitable for news website. No text overlays.")
    return " ".join(parts)


def _extract_keywords(title: str, summary: str, provided: list[str]) -> list[str]:
    """Combine provided keywords with significant title words. Returns ≤6 terms."""
    combined = list(provided)
    stop = {"a", "an", "the", "in", "on", "at", "to", "for", "of", "and",
            "or", "is", "are", "was", "were", "be", "how", "why", "what"}
    for word in title.split():
        clean = word.strip(".,!?:;\"'").lower()
        if len(clean) > 3 and clean not in stop and clean not in [k.lower() for k in combined]:
            combined.append(word.strip(".,!?:;\"'"))
    return combined[:6]


# ---------------------------------------------------------------------------
# Pipeline acquisition stages
# ---------------------------------------------------------------------------

def _acquire_via_stock(
    keywords: list[str],
    config: ImageCompositionConfig,
) -> tuple[Optional[bytes], str]:
    """
    Try stock image sourcing.
    Returns (image_bytes, provider_name) or (None, "") on failure.
    """
    provider = _get_stock_provider()
    req = StockImageRequest(
        keywords=keywords,
        provider=provider,
        orientation="landscape",
        min_width=config.output_width,
        min_height=config.output_height,
    )
    response = search_stock_image(req)

    if response.success and response.image_bytes:
        logger.info("stock_acquire_ok | provider=%s | bytes=%d",
                    response.provider, len(response.image_bytes))
        return response.image_bytes, response.provider

    logger.warning("stock_acquire_failed | provider=%s | error=%s",
                   response.provider, response.error)
    return None, ""


def _acquire_via_generation(
    title: str,
    summary: str,
    keywords: list[str],
    config: ImageCompositionConfig,
) -> tuple[Optional[bytes], str]:
    """
    Fallback: AI-generate image from article context.
    Returns (image_bytes, provider_name) or (None, "") on failure.
    """
    provider = _get_generation_provider()
    req = ImageRequest(
        prompt=_build_generation_prompt(title, summary, keywords),
        width=config.output_width,
        height=config.output_height,
        provider=provider,
    )
    response = generate_image(req)

    if response.success and response.image_bytes:
        logger.info("generation_acquire_ok | provider=%s | bytes=%d",
                    response.provider, len(response.image_bytes))
        return response.image_bytes, response.provider

    logger.error("generation_acquire_failed | provider=%s | error=%s",
                 response.provider, response.error)
    return None, ""


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def get_featured_image(
    title: str,
    summary: str = "",
    keywords: Optional[list[str]] = None,
    config: Optional[ImageCompositionConfig] = None,
    save_to_disk: bool = False,
    skip_stock: bool = False,
) -> FeaturedImageResult:
    """
    Run the complete featured image pipeline for an article.

    Pipeline:
        1. StockImageRequest → search_stock_image       (unless skip_stock=True)
        2. ImageRequest      → generate_image           (fallback)
        3. image_bytes       → compose_image            (always)
        4. Optional disk save                           (if save_to_disk=True)

    Args:
        title:        Article title.
        summary:      Article summary/excerpt.
        keywords:     Search and prompt keywords.
        config:       ImageCompositionConfig (branding, ads, dimensions).
                      Defaults to 1200×630 JPEG, no branding, no ads.
        save_to_disk: Write output to disk. Path in result.composed.local_path.
        skip_stock:   Force AI generation, bypass stock search.

    Returns:
        FeaturedImageResult — never raises.
    """
    if config is None:
        config = ImageCompositionConfig()
    keywords = keywords or []

    pipeline_stages: list[str] = []
    raw_bytes: Optional[bytes] = None
    source_used = ""

    effective_kw = _extract_keywords(title, summary, keywords)

    logger.info(
        "featured_image_start | title=%.60r | keywords=%s | branding=%s | ads=%s",
        title, effective_kw, config.branding.enable, config.ads.enable,
    )

    # ---- Acquire ----
    if not skip_stock:
        pipeline_stages.append("stock_search")
        raw_bytes, source_used = _acquire_via_stock(effective_kw, config)

    if not raw_bytes:
        pipeline_stages.append("ai_generation")
        raw_bytes, source_used = _acquire_via_generation(
            title, summary, effective_kw, config
        )

    if not raw_bytes:
        msg = "All image acquisition methods failed (stock + generation)"
        logger.error("featured_image_failed | reason=%s | title=%.60r", msg, title)
        return FeaturedImageResult(
            success=False,
            pipeline_stages=pipeline_stages,
            error=msg,
        )

    # ---- Compose ----
    pipeline_stages.append("composition")
    composed = compose_image(raw_bytes, config, save_to_disk=save_to_disk)

    if not composed.success:
        return FeaturedImageResult(
            success=False,
            pipeline_stages=pipeline_stages,
            error=f"Composition failed: {composed.error}",
        )

    pipeline_stages.append("complete")

    logger.info(
        "featured_image_ok | stages=%s | source=%s | %dx%d | %d bytes",
        pipeline_stages, source_used,
        composed.width, composed.height, composed.file_size_bytes,
    )

    return FeaturedImageResult(
        success=True,
        composed=composed,
        source_used=source_used,
        pipeline_stages=pipeline_stages,
    )
