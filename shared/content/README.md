# shared/content — Content Asset System

## Overview

The `shared/content` package provides a reusable content asset packaging system for ContentPilot.

It transforms article content and generated media into structured **AssetBundles** stored on disk, and (Phase 11B) uploads featured images to WordPress.

---

## Production Workflow (Phase 11B)

```
RSS Article
    ↓
AI Summarization
    ↓
AssetBuilder.build()          ← shared/content/asset_builder.py
    ↓
Media Engine                  ← shared/media/
    - featured.jpg
    - facebook_landscape.jpg
    - facebook_square.jpg
    - instagram_square.jpg
    - instagram_portrait.jpg
    - story.jpg
    ↓
AssetStorage.save()           ← shared/content/storage.py
    ↓
data/media/YYYY/MM/DD/slug/
    ↓
WordPressMediaService.upload_image()   ← shared/content/wordpress_media.py
    ↓
WordPress media_id
    ↓
PostRequest(featured_media=media_id)
    ↓
WordPressClient.create_post()          ← shared/wordpress/client.py
    ↓
Facebook / Instagram publish           ← shared/social/
```

Each stage is **failure-isolated**. A failure in asset generation or media upload
logs a warning and continues — publishing always proceeds if possible.

---

## Feature Flags

All flags default to safe values. No `.env` changes are required for the pre-Phase-11 workflow to continue working.

```env
# Master toggle for the asset pipeline
ENABLE_MEDIA_ASSETS=true          # default: true

# Upload featured image to WordPress
ENABLE_FEATURED_IMAGES=true       # default: true

# Generate social image variants (facebook, instagram, story)
ENABLE_SOCIAL_IMAGES=true         # default: true

# Apply branding overlay to images
MEDIA_BRANDING_ENABLED=false      # default: false

# Apply ads overlay to images
MEDIA_ADS_ENABLED=false           # default: false

# Root directory for asset storage
MEDIA_STORAGE_DIR=/app/data/media # default: /app/data/media
```

To run in pre-Phase-11 mode (zero media pipeline):

```env
ENABLE_MEDIA_ASSETS=false
ENABLE_FEATURED_IMAGES=false
ENABLE_SOCIAL_IMAGES=false
```

---

## daily_news Integration

The `modules/daily_news/runner.py` integrates the asset pipeline via three isolated helpers:

```python
# 1. Build and store asset bundle
asset_result = _build_asset_bundle(title, summary, article_body, keywords, media_cfg, summary)

# 2. Upload featured image to WordPress (returns media_id or None)
featured_media_id = _upload_featured_image(asset_result, title, media_cfg, summary)

# 3. Publish WordPress post with featured image attached
_publish_to_wordpress(title, post_text, featured_media_id, summary)
```

Each helper catches all exceptions internally and logs warnings. The publish pipeline
(social targets) always runs regardless of what happened in the media steps.

---

## Storage Layout

```
data/media/
└── 2026/
    └── 06/
        └── 01/
            └── opening-a-bank-account-in-germany/
                ├── featured.jpg           ← WordPress featured image
                ├── facebook_landscape.jpg ← 1200×628
                ├── facebook_square.jpg    ← 1080×1080
                ├── instagram_square.jpg   ← 1080×1080
                ├── instagram_portrait.jpg ← 1080×1350
                ├── story.jpg              ← 1080×1920
                ├── metadata.json          ← machine-readable bundle
                └── article.md             ← article content export
```

Storage is date-partitioned and deterministic: same slug + same date = same path.

---

## Bundle Structure

`AssetBundle` is the central handoff artifact between the media pipeline and WordPress:

```python
bundle.article_slug          # URL-safe slug
bundle.title                 # article title
bundle.summary               # article summary
bundle.keywords              # keyword list
bundle.storage_dir           # absolute Path to directory
bundle.assets                # dict[str, AssetFile]
bundle.generated_at          # ISO 8601 UTC timestamp
bundle.branding_enabled
bundle.ads_enabled

# Convenience properties
bundle.featured_image        # AssetFile or None
bundle.facebook_landscape
bundle.facebook_square
bundle.instagram_square
bundle.instagram_portrait
bundle.story
bundle.metadata_file
bundle.article_file
```

---

## Runtime Metrics

`ExecutionSummary` tracks these Phase 11B fields:

| Field | Description |
|---|---|
| `assets_generated` | Total asset files written |
| `bundles_created` | AssetBundles successfully stored |
| `images_generated` | Image files generated |
| `images_uploaded` | Images successfully uploaded to WordPress |
| `wordpress_media_failures` | Upload failures (warning only, not fatal) |

---

## Troubleshooting

**Assets not being generated**
- Check `ENABLE_MEDIA_ASSETS=true` in `.env`
- Check that `shared/media` is installed and importable in the container
- Check `data/media/` is writable (bind-mounted from host)

**Featured image not appearing on WordPress posts**
- Check `ENABLE_FEATURED_IMAGES=true`
- Check `WORDPRESS_BASE_URL`, `WORDPRESS_USERNAME`, `WORDPRESS_APP_PASSWORD`
- Check that the WordPress user has `upload_files` capability
- Check logs for `wp_media_upload_failed`

**Publishing continues but media fields are zero**
- All media flags may be `false` — check `.env`
- The media engine (`shared/media`) may have failed to import — check for import errors in logs

**Container can't write to data/media/**
- Ensure `data/media` exists on the host and is mounted:
  ```yaml
  volumes:
    - ../../data:/app/data
  ```

---

## Deployment Notes

1. Create `data/media/` on the host before first run:
   ```bash
   mkdir -p /home/deployer/repos/contentpilot/data/media
   ```
2. The `data/` directory is already bind-mounted in `docker-compose.yml` — no changes needed.
3. Add Phase 11B env vars to `.env` (all have safe defaults, so adding them is optional).

---

## Extension Guide

**Add a new image variant:**
1. Add generation in `asset_builder.py → _generate_real_images()`
2. Add filename mapping in `storage.py → image_ext_map`
3. Add convenience property to `AssetBundle` in `models.py`
4. Add test case in `scripts/test_content_assets.py`

**Add a new upload target (e.g., Cloudinary):**
1. Create `shared/content/cloudinary_media.py` following `wordpress_media.py` pattern
2. Return a result dataclass with `success`, `url`, `media_id`
3. Call from a new helper in `runner.py` (keep it isolated)
