# shared/content/storage.py
"""
Asset Storage Layer.

Persists generated content assets to:
    data/media/YYYY/MM/DD/article_slug/

Layout:
    featured.jpg
    facebook_landscape.jpg
    facebook_square.jpg
    instagram_square.jpg
    instagram_portrait.jpg
    story.jpg
    metadata.json
    article.md

Deterministic behavior: same slug + date = same directory.
Safe to call multiple times (idempotent directory creation).
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import AssetBundle, AssetFile, AssetStorageResult

logger = logging.getLogger(__name__)

_DEFAULT_STORAGE_DIR = "/app/data/media"


def _get_storage_root() -> Path:
    return Path(os.getenv("MEDIA_STORAGE_DIR", _DEFAULT_STORAGE_DIR))


def _slugify(text: str) -> str:
    """Convert title to URL-safe slug."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text[:80] or "article"


def _storage_path(slug: str, dt: datetime | None = None) -> Path:
    """Build deterministic storage path for a given slug and date."""
    dt = dt or datetime.now(timezone.utc)
    return _get_storage_root() / dt.strftime("%Y") / dt.strftime("%m") / dt.strftime("%d") / slug


class AssetStorage:
    """
    Persists content asset bundles to the local filesystem.

    Usage:
        storage = AssetStorage()
        result = storage.save(bundle, image_bytes_by_key, article_markdown)
    """

    def __init__(self, storage_root: Path | None = None) -> None:
        self._root = storage_root or _get_storage_root()

    def generate_slug(self, title: str) -> str:
        return _slugify(title)

    def build_storage_dir(self, slug: str, dt: datetime | None = None) -> Path:
        dt = dt or datetime.now(timezone.utc)
        return self._root / dt.strftime("%Y") / dt.strftime("%m") / dt.strftime("%d") / slug

    def save(
        self,
        bundle: AssetBundle,
        image_data: dict[str, bytes],
        article_markdown: str = "",
    ) -> AssetStorageResult:
        """
        Persist all assets for a bundle to disk.

        Args:
            bundle:           AssetBundle with metadata populated.
            image_data:       {key: jpeg_bytes} for each image asset.
            article_markdown: Optional article body to save as article.md.

        Returns:
            AssetStorageResult — never raises.
        """
        storage_dir = bundle.storage_dir
        try:
            storage_dir.mkdir(parents=True, exist_ok=True)
            logger.info(
                "asset_storage_start | slug=%s | dir=%s | images=%d",
                bundle.article_slug, storage_dir, len(image_data),
            )
        except Exception as exc:
            return AssetStorageResult(
                success=False,
                error_message=f"Could not create storage directory: {exc}",
            )

        assets_written = 0

        # Write image assets
        image_ext_map = {
            "featured":           "featured.jpg",
            "facebook_landscape": "facebook_landscape.jpg",
            "facebook_square":    "facebook_square.jpg",
            "instagram_square":   "instagram_square.jpg",
            "instagram_portrait": "instagram_portrait.jpg",
            "story":              "story.jpg",
        }

        for key, filename in image_ext_map.items():
            data = image_data.get(key)
            if data is None:
                logger.debug("asset_storage_skip | key=%s | reason=no_data", key)
                continue

            file_path = storage_dir / filename
            try:
                file_path.write_bytes(data)
                asset = AssetFile(
                    key=key,
                    path=file_path,
                    mime_type="image/jpeg",
                    size_bytes=len(data),
                )
                bundle.assets[key] = asset
                assets_written += 1
                logger.debug(
                    "asset_storage_write | key=%s | size=%d | path=%s",
                    key, len(data), file_path,
                )
            except Exception as exc:
                logger.error(
                    "asset_storage_write_failed | key=%s | error=%s", key, exc
                )

        # Write article markdown
        if article_markdown:
            md_path = storage_dir / "article.md"
            try:
                md_path.write_text(article_markdown, encoding="utf-8")
                bundle.assets["article"] = AssetFile(
                    key="article",
                    path=md_path,
                    mime_type="text/markdown",
                    size_bytes=len(article_markdown.encode("utf-8")),
                )
                assets_written += 1
            except Exception as exc:
                logger.error("asset_storage_write_failed | key=article | error=%s", exc)

        # Write metadata.json
        metadata_path = storage_dir / "metadata.json"
        try:
            meta = bundle.to_metadata_dict()
            metadata_path.write_text(
                json.dumps(meta, indent=2, default=str),
                encoding="utf-8",
            )
            bundle.assets["metadata"] = AssetFile(
                key="metadata",
                path=metadata_path,
                mime_type="application/json",
                size_bytes=metadata_path.stat().st_size,
            )
            assets_written += 1
        except Exception as exc:
            logger.error("asset_storage_write_failed | key=metadata | error=%s", exc)

        logger.info(
            "asset_storage_complete | slug=%s | assets_written=%d",
            bundle.article_slug, assets_written,
        )

        return AssetStorageResult(
            success=True,
            bundle=bundle,
            assets_written=assets_written,
            storage_dir=storage_dir,
        )

    def load_metadata(self, storage_dir: Path) -> dict | None:
        """Load metadata.json from a storage directory. Returns None if missing."""
        meta_path = storage_dir / "metadata.json"
        if not meta_path.exists():
            return None
        try:
            return json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.error("asset_storage_load_metadata_failed | error=%s", exc)
            return None
