# shared/content/asset_builder.py
"""
Asset Builder — generates complete content asset bundles.

Input:  title, summary, article body, keywords
Output: AssetBundle (with all images generated and stored on disk)

Uses existing shared/media services. Does NOT publish.
Does NOT modify WordPress. Does NOT touch daily_news pipeline.

Phase 11B will call build() to obtain an AssetBundle, then upload
assets to WordPress media library and attach the featured image.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import AssetBundle, AssetFile, AssetStorageResult
from .storage import AssetStorage

logger = logging.getLogger(__name__)


def _media_enabled() -> bool:
    return os.getenv("ENABLE_MEDIA_ASSETS", "true").strip().lower() in {"1", "true", "yes"}


class AssetBuilder:
    """
    Orchestrates media generation and storage for a content article.

    Decoupled from any publisher. Call build() to get a ready AssetBundle.

    Usage:
        builder = AssetBuilder()
        result = builder.build(
            title="Opening a bank account in Germany",
            summary="A practical guide for expats...",
            article_body="## Introduction\\n...",
            keywords=["Germany", "banking", "expat"],
        )
        if result.success:
            bundle = result.bundle
    """

    def __init__(
        self,
        storage: AssetStorage | None = None,
        image_generator=None,   # injectable for testing
    ) -> None:
        self._storage = storage or AssetStorage()
        self._image_generator = image_generator  # None = use real media engine

    def build(
        self,
        title: str,
        summary: str,
        article_body: str = "",
        keywords: list[str] | None = None,
        branding_enabled: bool = True,
        ads_enabled: bool = False,
        extra_metadata: dict[str, Any] | None = None,
    ) -> AssetStorageResult:
        """
        Generate and store a complete asset bundle for the given article.

        Returns AssetStorageResult — never raises.
        """
        keywords = keywords or []
        extra_metadata = extra_metadata or {}

        if not _media_enabled():
            logger.info("asset_builder_skip | reason=ENABLE_MEDIA_ASSETS=false")
            slug = self._storage.generate_slug(title)
            storage_dir = self._storage.build_storage_dir(slug)
            bundle = AssetBundle(
                article_slug=slug,
                title=title,
                summary=summary,
                keywords=keywords,
                storage_dir=storage_dir,
                branding_enabled=branding_enabled,
                ads_enabled=ads_enabled,
                metadata=extra_metadata,
            )
            return AssetStorageResult(
                success=True,
                bundle=bundle,
                assets_written=0,
                storage_dir=storage_dir,
            )

        slug = self._storage.generate_slug(title)
        storage_dir = self._storage.build_storage_dir(slug)

        bundle = AssetBundle(
            article_slug=slug,
            title=title,
            summary=summary,
            keywords=keywords,
            storage_dir=storage_dir,
            branding_enabled=branding_enabled,
            ads_enabled=ads_enabled,
            metadata=extra_metadata,
        )

        logger.info(
            "asset_builder_start | slug=%s | keywords=%s | branding=%s",
            slug, keywords, branding_enabled,
        )

        image_data = self._generate_images(title, summary, keywords, branding_enabled=branding_enabled,
    ads_enabled=ads_enabled)

        result = self._storage.save(
            bundle=bundle,
            image_data=image_data,
            article_markdown=self._format_article_markdown(title, summary, article_body, keywords),
        )

        if result.success:
            logger.info(
                "asset_builder_complete | slug=%s | assets=%d",
                slug, result.assets_written,
            )
        else:
            logger.error(
                "asset_builder_failed | slug=%s | error=%s",
                slug, result.error_message,
            )

        return result

    def _generate_images(
        self,
        title: str,
        summary: str,
        keywords: list[str],
        branding_enabled: bool = False,
        ads_enabled: bool = False,
    ) -> dict[str, bytes]:
        """
        Generate all image variants. Returns {key: jpeg_bytes}.
        Falls back gracefully — missing images are skipped, not fatal.
        """
        if self._image_generator is not None:
            # Injected generator (used in tests)
            return self._image_generator(title, summary, keywords)

        return self._generate_real_images(
            title,
            summary,
            keywords,
            branding_enabled=branding_enabled,
            ads_enabled=ads_enabled,
        )

    def _generate_real_images(
        self,
        title: str,
        summary: str,
        keywords: list[str],
        branding_enabled: bool = False,
        ads_enabled: bool = False,
    ) -> dict[str, bytes]:
        """Generate images using the real media engine."""
        results: dict[str, bytes] = {}

        try:
            from shared.media.featured_image import get_featured_image
            from shared.media.social_formatter import format_for_social
            from shared.media.models import (
                SocialFormat,
                ImageCompositionConfig,
                BrandingConfig,
                AdConfig,
            )
        except ImportError as exc:
            logger.warning(
                "asset_builder_media_import_failed | error=%s | skipping_images", exc
            )
            return results
        
        config = ImageCompositionConfig(
            branding=BrandingConfig(
                enable=branding_enabled
            ),
            ads=AdConfig(
                enable=ads_enabled
            ),
        )
        # Featured image
        try:
            featured_result = get_featured_image(
                title=title,
                summary=summary,
                keywords=keywords,
                config=config, 
                save_to_disk=False,
            )
            if featured_result.success and featured_result.composed:
                results["featured"] = featured_result.composed.image_bytes
                logger.debug("asset_builder_image_ok | key=featured")
            else:
                logger.warning(
                    "asset_builder_image_failed | key=featured | error=%s",
                    featured_result.error,
                )
        except Exception as exc:
            logger.warning("asset_builder_image_failed | key=featured | error=%s", exc)

        # Social variants (only if we have a featured image to resize)
        source_bytes = results.get("featured")
        if source_bytes:
            try:
                all_formats = [
                    SocialFormat.FACEBOOK_LANDSCAPE,
                    SocialFormat.FACEBOOK_SQUARE,
                    SocialFormat.INSTAGRAM_SQUARE,
                    SocialFormat.INSTAGRAM_PORTRAIT,
                    SocialFormat.STORY,
                ]
                social_results = format_for_social(
                    image_bytes=source_bytes,
                    formats=all_formats,
                )
                for r in social_results:
                    if r.success and r.image_bytes:
                        results[r.format.value.lower()] = r.image_bytes
                        logger.debug("asset_builder_image_ok | key=%s", r.format.value)
                    else:
                        logger.warning(
                            "asset_builder_image_failed | key=%s | error=%s",
                            r.format.value, r.error,
                        )
            except Exception as exc:
                logger.warning(
                    "asset_builder_social_variants_failed | error=%s", exc
                )

        return results

    @staticmethod
    def _format_article_markdown(
        title: str,
        summary: str,
        body: str,
        keywords: list[str],
    ) -> str:
        """Format article content as Markdown for storage."""
        parts = [f"# {title}", "", f"_{summary}_", ""]
        if keywords:
            parts.append(f"**Keywords:** {', '.join(keywords)}")
            parts.append("")
        if body:
            parts.append(body)
        return "\n".join(parts)
