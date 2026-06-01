# 📄 ContentPilot Project State

## Current Status

### Current Maturity

Production-capable publishing platform with media generation layer.

The platform has successfully transitioned from a proof-of-concept automation system into a stable, observable, containerized content automation platform with both social publishing and WordPress publishing infrastructure.

Core runtime, ingestion, AI generation, deduplication, social publishing, WordPress publishing, monitoring, operational safety, and media asset generation layers are now in place.

The project is currently entering its first controlled multi-channel publishing pilot stage with full media generation capabilities.

---

## System Capabilities

### Infrastructure

* Docker-first architecture
* Containerized module execution
* Docker Compose orchestration
* Environment-driven configuration
* GitHub Actions CI validation

### AI Layer

* Provider abstraction architecture
* Anthropic integration
* DeepSeek integration
* Automatic provider fallback support
* Shared AI routing layer

### Content Processing

* RSS / Atom ingestion
* Feed normalization
* Article fingerprinting
* Deduplication before AI processing
* AI summarization pipeline
* Static topic generation fallback

### Media & Asset Generation

* Provider-agnostic image generation (mock / OpenAI DALL-E 3 / Stability AI / Ideogram / Flux)
* Stock image sourcing (mock / Pexels / Unsplash / Pixabay)
* Deterministic image processing utilities (resize, crop, compress, convert, thumbnail)
* Social media image formatting (Facebook, Instagram, Stories — all 5 formats)
* Composition pipeline engine (branding overlay + ad strip — both optional)
* Featured image pipeline (stock → fallback AI → compose → result)
* Bytes-in / bytes-out architecture throughout
* Full attribution metadata tracking
* Mock providers require zero API keys

### Publishing

#### Social Publishing

* Facebook publishing
* Instagram publishing framework
* Named social target routing
* Publisher-level duplicate protection
* Safe mode / live mode publishing controls
* Per-target enable/disable controls
* Publish audit logging
* Execution publish limits

#### WordPress Publishing

* WordPress REST API integration
* Draft publishing
* Live publishing
* Categories support
* Tags support
* Featured image support
* Structured publish result tracking
* Reusable publishing interface
* Retry-aware publishing client

### Reliability

* SQLite persistence
* WAL-enabled storage
* Runtime locking
* Duplicate detection
* Structured logging
* Health checks
* Database backups
* Telegram notifications
* Email notifications

---

## Current Repository Status

* Branch: `main`
* State: Stable
* Current Milestone: Phase 10 Complete
* Ready For: Phase 11 (Multi-Module Expansion)

---

## CI/CD Status

### GitHub Actions

Status: 🟢 Green

Validated:

* Runtime locking tests ✅
* Metadata storage tests ✅
* Publishing pipeline tests ✅
* Duplicate detection tests ✅
* RSS ingestion tests ✅
* Notification tests ✅
* WordPress publishing tests ✅
* Media foundation tests ✅
* Media composition tests ✅

All known automated validation pipelines are currently passing.

---

## Development Environment

* Host: Ubuntu VPS (1blu Dedicated Server)
* Client: VS Code Remote SSH
* Runtime: Docker Engine + Docker Compose V2
* Repository Path:

```text
/home/deployer/repos/contentpilot
```

* Primary Branch: `main`

---

## Architecture Overview

```text
contentpilot/
├── modules/
│   └── daily_news/
│
├── shared/
│   ├── ai/
│   ├── social/
│   ├── wordpress/
│   ├── ingestion/
│   ├── media/                    ← NEW (Phase 10)
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── image_generation.py
│   │   ├── image_sourcing.py
│   │   ├── image_processing.py
│   │   ├── image_composition.py
│   │   ├── featured_image.py
│   │   └── social_formatter.py
│   ├── runtime.py
│   ├── store.py
│   ├── notify.py
│   ├── logging.py
│   ├── models.py
│   └── config.py
│
├── infra/
│   ├── docker/
│   ├── compose/
│   └── cron/
│
├── scripts/
│
└── data/
    ├── db/
    ├── logs/
    ├── cache/
    ├── media/
    └── exports/
```

---

## Core Structural Principles

### Module Isolation

* One module = one deployable unit
* No cross-module dependencies
* Business logic belongs in modules

### Shared Platform Layer

* Generic reusable functionality only
* No module-specific assumptions
* Stable interfaces

### Configuration

* Environment-driven only
* No hardcoded credentials
* No embedded secrets

### Reliability

* Idempotent execution
* Retry-safe processing
* Observability first
* Docker-first development

---

## Implemented Phases

| Phase     | Name                                         | Status      |
| --------- | -------------------------------------------- | ----------- |
| Phase 1   | Docker Foundation & Skeleton Setup           | ✅ Complete  |
| Phase 2   | Daily News Core Module                       | ✅ Complete  |
| Phase 3   | Social Publishing Layer                      | ✅ Complete  |
| Phase 4   | Persistence & Deduplication Foundation       | ✅ Complete  |
| Phase 5   | Named Social Target Routing                  | ✅ Complete  |
| Phase 6   | Runtime, Scheduler & Alerts                  | ✅ Complete  |
| Phase 6.5 | Observability & Operational Stabilization    | ✅ Complete  |
| Phase 7   | RSS Ingestion Pipeline                       | ✅ Complete  |
| Phase 8   | Live Pilot Hardening & Credential Activation | ✅ Complete  |
| Phase 9   | WordPress Publishing Layer                   | ✅ Complete  |
| Phase 10  | Media & Asset Generation Layer               | ✅ Complete  |

---

# Project Timeline

## 2026-06-01 Phase 11A — Content Asset Bundle Storage (COMPLETE)
Completed: 2026-06-01 

### Goal
Transform media engine outputs into reusable content asset packages
stored on disk, ready for Phase 11B WordPress integration.

### What was implemented
- Added `shared/content/` package with four modules:
  - `models.py` — AssetFile, AssetBundle, AssetStorageResult dataclasses
  - `storage.py` — date-partitioned storage under data/media/YYYY/MM/DD/slug/
  - `asset_builder.py` — orchestrates media engine + storage into one call
  - `README.md` — architecture, storage layout, Phase 11B integration notes
- AssetBundle is the handoff artifact Phase 11B will consume
- AssetBuilder wired to real media engine:
  - get_featured_image() for featured image
  - format_for_social() for Facebook/Instagram/Story variants
- Injectable image_generator parameter for offline testing
- ENABLE_MEDIA_ASSETS flag gates entire pipeline

### Storage layout
data/media/YYYY/MM/DD/article-slug/
  featured.jpg, facebook_landscape.jpg, facebook_square.jpg,
  instagram_square.jpg, instagram_portrait.jpg, story.jpg,
  metadata.json, article.md

### Testing
- 11/11 tests passing, fully offline, all mocked
- Agent review completed — one bug found and fixed
  (_generate_real_images() had wrong function names and signatures)

### New environment variables
- ENABLE_MEDIA_ASSETS (default: true)
- MEDIA_STORAGE_DIR (default: /app/data/media)

### What is NOT included (Phase 11B)
- WordPress media upload
- Featured image attachment to posts
- daily_news pipeline integration
- Runtime metrics for media operations

## 2026-06-01 — Phase 10 / Media & Asset Generation Layer

### Completed

* Introduced reusable media generation layer for all modules.
* Added provider-agnostic image generation with retry and permanent-error fast-path.
* Added stock image sourcing with attribution metadata.
* Added deterministic image processing utilities.
* Added social media image formatter (5 platform formats).
* Added composition pipeline engine with optional branding and ad overlays.
* Added featured image pipeline (stock → AI fallback → compose).
* All image data travels as bytes — no file I/O in core pipeline.
* 112 tests passing (50 foundation + 62 composition). Zero network calls required.

### Technical Changes

Created:

```text
shared/media/
├── __init__.py
├── models.py
├── image_generation.py
├── image_sourcing.py
├── image_processing.py
├── image_composition.py
├── featured_image.py
└── social_formatter.py
```

Added tests:

```text
scripts/test_media_foundation.py    ← 50 tests
scripts/test_media_composition.py   ← 62 tests
```

Updated:

```text
infra/docker/base.Dockerfile        ← added Pillow>=10.0.0
requirements/base.txt               ← added Pillow>=10.0.0
```

#### Models

| Type | Frozen | Purpose |
|---|---|---|
| `ImageRequest` | No | Input for AI generation |
| `StockImageRequest` | No | Input for stock image search |
| `ImageMetadata` | Yes | Attribution + provenance |
| `ImageProviderResponse` | Yes | Raw provider output |
| `ImageResult` | Yes | Final processed image |
| `SocialImageResult` | Yes | Per-format social output |
| `BrandingConfig` | No | Composition branding config |
| `AdConfig` | No | Composition ad strip config |
| `ImageCompositionConfig` | No | Full composition config |
| `ComposedImageResult` | Yes | Composition pipeline output |
| `FeaturedImageResult` | No | Full pipeline result |

#### Image Generation Providers

| Provider | Status | Env Var |
|---|---|---|
| `mock` | ✅ Ready | None required |
| `openai` | ✅ Ready | `OPENAI_API_KEY` |
| `stability` | 🔧 Stub | `STABILITY_API_KEY` |
| `ideogram` | 🔧 Stub | `IDEOGRAM_API_KEY` |
| `flux` | 🔧 Stub | — |

#### Stock Image Providers

| Provider | Status | Env Var |
|---|---|---|
| `mock` | ✅ Ready | None required |
| `pexels` | ✅ Ready | `PEXELS_API_KEY` |
| `unsplash` | ✅ Ready | `UNSPLASH_ACCESS_KEY` |
| `pixabay` | ✅ Ready | `PIXABAY_API_KEY` |

#### Social Formats

| Format | Dimensions |
|---|---|
| `FACEBOOK_LANDSCAPE` | 1200 × 630 |
| `FACEBOOK_SQUARE` | 1080 × 1080 |
| `INSTAGRAM_SQUARE` | 1080 × 1080 |
| `INSTAGRAM_PORTRAIT` | 1080 × 1350 |
| `STORY` | 1080 × 1920 |

#### Configuration

New optional env vars:

```text
IMAGE_GENERATION_PROVIDER=mock       # mock | openai | stability | ideogram | flux
IMAGE_STOCK_PROVIDER=mock            # mock | pexels | unsplash | pixabay
OPENAI_API_KEY=                      # for DALL-E 3 generation
PEXELS_API_KEY=                      # for Pexels stock sourcing
UNSPLASH_ACCESS_KEY=                 # for Unsplash stock sourcing
PIXABAY_API_KEY=                     # for Pixabay stock sourcing
MEDIA_OUTPUT_DIR=/app/data/media     # where composed files are saved
```

### Validation

Verified:

* Mock image generation (deterministic, no API key)
* Mock stock sourcing (deterministic, no API key)
* Image processing (resize, crop, compress, convert, thumbnail)
* Social formatting (all 5 platform formats, correct dimensions)
* Branding overlay (brand name, CTA box, logo top-left/bottom-right)
* Ad strip (text and image types, height ratio bounds)
* Combined composition (branding + ads, strict layer order)
* Featured image pipeline end-to-end
* save_to_disk behaviour
* Frozen result types enforced
* All 112 tests pass in Docker with zero network calls

### Notes

* No database schema changes required
* No module architecture changes required
* No existing shared/ layers modified
* Media layer is fully reusable by all future modules
* Composition pipeline is deterministic — same config always produces identical output

---

## 2026-05-31 — Phase 9 / WordPress Publishing Layer

### Completed

* Introduced reusable WordPress publishing framework.
* Added WordPress REST API integration.
* Added draft publishing support.
* Added live publishing support.
* Added categories and tags support.
* Added featured image support.
* Added structured publish result tracking.
* Added retry-aware publishing client.
* Added WordPress-specific validation and logging.

### Technical Changes

Created:

```text
shared/wordpress/
├── __init__.py
├── client.py
└── models.py
```

Added:

* WordPress client abstraction
* WordPress REST API integration
* Publish request models
* Publish response models
* Draft publishing workflow
* Live publishing workflow
* Retry handling
* Structured publish results

#### Configuration

Updated:

```text
.env.example
```

Added:

```text
WORDPRESS_BASE_URL=
WORDPRESS_USERNAME=
WORDPRESS_APP_PASSWORD=
WORDPRESS_DEFAULT_STATUS=draft
WORDPRESS_TIMEOUT_SECONDS=30
```

### Validation

Verified:

* WordPress authentication
* Draft creation
* Published post creation
* Response parsing
* Retry handling
* Failure handling
* Structured logging

### Notes

* No database schema changes required
* No ingestion architecture changes required
* No module architecture changes required
* WordPress layer remains fully reusable and module-agnostic

---

## 2026-05-31 — Phase 8 / Live Pilot Hardening & Credential Activation

### Completed

* Introduced publishing safety controls for production deployment.
* Added Safe Mode / Live Mode enforcement.
* Added target-level publishing controls.
* Added publisher-level duplicate protection verification.
* Added execution-level publish rate limiting.
* Improved publishing audit logging.

### Technical Changes

#### Publishing Safety

Updated:

```text
shared/social/publisher.py
```

Added:

* `PUBLISH_MODE=safe|live`
* per-target enable checks
* publisher-level duplicate protection
* publish decision audit logs
* execution publish limit enforcement

#### Configuration

Updated:

```text
.env.example
```

Added:

* `MAX_POSTS_PER_RUN`
* publish mode documentation

### Validation

Verified:

* Safe mode blocks all real publishing
* Live mode enables publishing
* Duplicate content blocked before adapter execution
* Disabled targets skipped correctly
* Publish limit enforced

### Notes

* No database schema changes required
* No runtime architecture changes required
* No ingestion changes required

---

## 2026-05-30 — Phase 7 / RSS News Ingestion Pipeline

### Completed

* Transformed daily_news from static topic generation into a real-news processing pipeline.
* Implemented reusable RSS/Atom ingestion framework.
* Added article fingerprinting and deduplication.
* Added AI summarization of RSS content.
* Added draft-mode processing safety.

### Technical Changes

Created:

```text
shared/ingestion/
├── models.py
├── rss.py
├── normalizer.py
└── sources.py
```

Added:

* RSS article fingerprinting
* Feed normalization
* Feed merging
* Cross-feed deduplication
* Newest-first sorting
* Environment-driven feed configuration

Database:

* Added `rss_articles` table

Runner:

* RSS ingestion became primary execution path
* Static topic fallback preserved

Testing:

* Added 8 ingestion validation tests

### Validation

Verified:

* Live feed retrieval
* Deduplication
* Draft mode execution
* Network failure handling
* Feed limits
* Configuration loading

### Stabilization Fixes

Resolved:

* SQLite `target_key` migration issue
* publish_history compatibility issue
* RSS deduplication edge cases
* Topic-level duplicate publishing logic

---

## Active Modules

### modules/daily_news

Status: Production-capable

Capabilities:

* RSS ingestion
* Topic fallback generation
* AI summarization
* Facebook publishing
* WordPress publishing
* Deduplication
* Safe mode publishing
* Live mode publishing
* Runtime metrics tracking

---

## Shared Platform Components

### shared/ai

Provides:

* Provider abstraction
* Anthropic integration
* DeepSeek integration
* Fallback execution

### shared/social

Provides:

* Multi-target publishing
* Facebook adapter
* Instagram adapter
* Publish safety controls
* Duplicate protection

### shared/wordpress

Provides:

* WordPress REST API integration
* Draft publishing
* Live publishing
* Categories and tags support
* Featured image support
* Publish result tracking
* Retry-aware publishing

### shared/ingestion

Provides:

* RSS parsing
* Feed normalization
* Feed configuration
* Article fingerprinting

### shared/media

Provides:

* Provider-agnostic image generation
* Stock image sourcing with attribution
* Deterministic image processing (resize, crop, compress, convert)
* Social media format resizing (5 platform formats)
* Composition pipeline (branding + ad overlays)
* Featured image pipeline (stock → AI fallback → compose)
* Bytes-in / bytes-out architecture

### shared/runtime

Provides:

* Execution lifecycle management
* File locking
* Runtime metrics

### shared/store

Provides:

* SQLite persistence
* Publish history
* RSS article tracking
* Duplicate detection

### shared/notify

Provides:

* Telegram notifications
* Email notifications

---

## Deduplication Model

The platform currently contains two intentionally separate deduplication systems.

### RSS Article Deduplication

Purpose:

Prevent reprocessing identical feed articles.

Fingerprint:

```text
sha256(title + link)
```

Storage:

```text
rss_articles
```

Scope:

```text
ingestion layer
```

---

### Topic-Level Deduplication

Purpose:

Prevent repeated publishing of identical user topics.

Fingerprint:

```text
hash(normalized topic)
```

Storage:

```text
publish_history
```

Scope:

```text
publishing layer
```

---

## Architecture Decisions

### Docker Compose Before Kubernetes

Chosen to keep deployment simple and maintainable on a single VPS.

### SQLite Before PostgreSQL

Chosen to minimize operational complexity while maintaining persistence.

### Reliability Before Features

Operational safety and observability are prioritized before introducing new business functionality.

### Shared Services Remain Lightweight

Avoid heavy framework dependencies.

### WordPress As Output Adapter

WordPress remains a publishing destination only.

AI generation and publishing remain intentionally decoupled.

This allows future modules to reuse the same WordPress layer without modification.

### Media Layer As Pure Bytes Pipeline

All image data travels as raw bytes through the pipeline.
File I/O only happens at the explicit call site via `save_to_disk=True`.
This keeps the core pipeline testable without any filesystem dependency.

---

## Known Limitations

### Social Publishing

* Instagram live production publishing not fully validated

### Media

* No video generation pipeline
* Stability AI, Ideogram, Flux providers are stubs (not yet activated)

### Multi-Module Expansion

Only `daily_news` is currently production-ready.

### User-Driven Content Creation

* Article request workflow not yet implemented
* Article generation dashboard not yet implemented
* Multi-user content management not yet implemented

---

## Next Major Milestone

# Phase 11 — Multi-Module Expansion

### Goal

Expand the platform beyond `daily_news` into additional publishing modules
that consume the shared media, WordPress, and social layers.

### Planned Modules

```text
modules/
├── article_publisher/   ← Long-form article generation + WordPress publish
├── deals_engine/        ← Affiliate deals automation
├── social_tips/         ← Tips image + social publish pipeline
└── social_video/        ← Short-form video generation + publish
```

### Objectives

* Reuse shared/media for featured image generation in article_publisher
* Reuse shared/wordpress for structured publishing
* Reuse shared/social for multi-platform distribution
* Maintain strict module isolation

---

## Long-Term Roadmap

### Phase 11

Multi-Module Expansion

* article_publisher
* deals_engine
* social_tips
* social_video

### Phase 12

Multi-Tenant SaaS Readiness

---

## AI Agent Operating Rules

Before making changes:

1. Read project state fully.
2. Respect phase boundaries.
3. Avoid unnecessary abstractions.
4. Maintain module isolation.
5. Test inside Docker.
6. Update timeline before commit.

---

## Preferred Execution Loop

```text
Understand
→ Analyze
→ Implement Minimal Change
→ Test in Docker
→ Validate
→ Update Documentation
→ Commit
```