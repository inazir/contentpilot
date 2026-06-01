# shared/content — Content Asset System

## Overview

The `shared/content` package provides a reusable content asset packaging system for ContentPilot.

It transforms article content and generated media into structured **AssetBundles** stored on disk, ready for publishing or distribution.

---

## Architecture

```
Article (title, summary, body, keywords)
        ↓
  AssetBuilder
        ↓
  Media Engine (shared/media)
        ↓
  AssetBundle (in memory)
        ↓
  AssetStorage (to disk)
        ↓
  data/media/YYYY/MM/DD/article-slug/
        ├── featured.jpg
        ├── facebook_landscape.jpg
        ├── facebook_square.jpg
        ├── instagram_square.jpg
        ├── instagram_portrait.jpg
        ├── story.jpg
        ├── metadata.json
        └── article.md
```

---

## Asset Lifecycle

1. **Build** — `AssetBuilder.build()` generates all images and formats article content
2. **Store** — `AssetStorage.save()` persists assets to a date-partitioned directory
3. **Return** — `AssetStorageResult` contains the completed `AssetBundle` with all paths
4. **Consume** — Phase 11B picks up the bundle to upload assets to WordPress

---

## Storage Layout

```
data/media/
└── 2026/
    └── 06/
        └── 01/
            └── opening-a-bank-account-in-germany/
                ├── featured.jpg           ← WordPress featured image candidate
                ├── facebook_landscape.jpg ← 1200×628
                ├── facebook_square.jpg    ← 1080×1080
                ├── instagram_square.jpg   ← 1080×1080
                ├── instagram_portrait.jpg ← 1080×1350
                ├── story.jpg              ← 1080×1920
                ├── metadata.json          ← machine-readable bundle metadata
                └── article.md             ← article content export
```

---

## Bundle Structure

`AssetBundle` is the central handoff artifact:

```python
bundle.article_slug       # URL-safe slug
bundle.title              # original article title
bundle.summary            # article summary
bundle.keywords           # list of keywords
bundle.storage_dir        # absolute Path to directory
bundle.assets             # dict[str, AssetFile]
bundle.generated_at       # ISO 8601 UTC timestamp
bundle.branding_enabled   # whether branding was applied
bundle.ads_enabled        # whether ads were enabled
bundle.metadata           # extensible dict for future fields

# Convenience properties
bundle.featured_image     # AssetFile or None
bundle.facebook_landscape
bundle.facebook_square
bundle.instagram_square
bundle.instagram_portrait
bundle.story
bundle.metadata_file
bundle.article_file
```

---

## Configuration

```env
# Root directory for media asset storage
MEDIA_STORAGE_DIR=/app/data/media

# Toggle the entire media asset pipeline
ENABLE_MEDIA_ASSETS=true
```

---

## Phase 11B Integration

Phase 11B will extend this system to:

1. Call `AssetBuilder.build()` to obtain an `AssetBundle`
2. Upload `bundle.featured_image` to WordPress media library
3. Attach the media ID to the WordPress post as featured image
4. Integrate into `daily_news` runner pipeline

No changes to `shared/content` are required for Phase 11B integration. The `AssetBundle` model is designed as a stable handoff contract.

---

## Extension Guide

To add a new image variant:

1. Add generation logic in `asset_builder.py → _generate_real_images()`
2. Add the filename mapping in `storage.py → image_ext_map`
3. Add a convenience property to `AssetBundle` if needed
4. Add a test case in `scripts/test_content_assets.py`
