# ContentPilot Project State

## Current Status

### Current Maturity

Production-capable publishing platform with media generation layer.

The platform has successfully transitioned from a proof-of-concept automation system into a stable, observable, containerized content automation platform with both social publishing and WordPress publishing infrastructure.

Core runtime, ingestion, AI generation, deduplication, social publishing, WordPress publishing, monitoring, operational safety, and media asset generation layers are now in place.

The project is currently entering its first controlled multi-channel publishing pilot stage with full media generation capabilities.

---

# System Capabilities

## Infrastructure

- Docker-first architecture
- Containerized module execution
- Docker Compose orchestration
- Environment-driven configuration
- GitHub Actions CI validation

## AI Layer

- Provider abstraction architecture
- Anthropic integration
- DeepSeek integration
- Automatic provider fallback support
- Shared AI routing layer

## Content Processing

- RSS / Atom ingestion
- Feed normalization
- Article fingerprinting
- Deduplication before AI processing
- AI summarization pipeline
- Static topic generation fallback

## Media & Asset Generation

### Image Generation

Provider-agnostic image generation:

- Mock
- OpenAI DALL-E 3
- Stability AI
- Ideogram
- Flux

### Stock Image Sourcing

- Mock
- Pexels
- Unsplash
- Pixabay

### Image Processing

- Resize
- Crop
- Compress
- Convert
- Thumbnail generation

### Social Formatting

Supports:

- Facebook Landscape
- Facebook Square
- Instagram Square
- Instagram Portrait
- Story Format

### Composition Pipeline

Supports:

- Branding overlays (optional)
- Advertisement overlays (optional)

### Featured Image Pipeline

Workflow:

Stock Image
→ AI Fallback
→ Composition
→ Final Asset

### Architectural Characteristics

- Bytes-in / bytes-out architecture
- Full attribution metadata tracking
- Mock providers require zero API keys

---

## Publishing

### Social Publishing

#### Facebook

- Direct image uploading
- Automatic text fallback
- Duplicate protection
- Publish logging

#### Instagram

- Publishing framework implemented
- Image pipeline integrated

### Publishing Controls

- Named social target routing
- Publisher-level duplicate protection
- Safe Mode / Live Mode controls
- Per-target enable/disable controls
- Publish audit logging
- Execution publish limits

### WordPress Publishing

- WordPress REST API integration
- Draft publishing
- Live publishing
- Categories support
- Tags support
- Featured image support
- Structured publish result tracking
- Retry-aware publishing client
- Reusable publishing interface

---

## Reliability

### Storage

- SQLite persistence
- WAL-enabled database

### Operational Safety

- Runtime locking
- Duplicate detection
- Structured logging
- Health checks
- Database backups

### Notifications

- Telegram notifications
- Email notifications

---

# Current Repository Status

| Property | Value |
|-----------|---------|
| Branch | `main` |
| State | Stable |
| Current Milestone | Phase 12A Complete |
| Next Milestone | Phase 12B |

---

# CI/CD Status

## GitHub Actions

Status: 🟢 Green

### Validated Pipelines

- Runtime locking tests ✅
- Metadata storage tests ✅
- Publishing pipeline tests ✅
- Duplicate detection tests ✅
- RSS ingestion tests ✅
- Notification tests ✅
- WordPress publishing tests ✅
- Media foundation tests ✅
- Media composition tests ✅
- Social media image publishing tests (Phase 12A) ✅

All automated validation pipelines are currently passing.

---

# Development Environment

| Item | Value |
|--------|---------|
| Host | Ubuntu VPS (1blu Dedicated Server) |
| Client | VS Code Remote SSH |
| Runtime | Docker Engine + Docker Compose V2 |
| Repository Path | `/home/deployer/repos/contentpilot` |
| Primary Branch | `main` |

---

# Architecture Overview

```text
contentpilot/
├── modules/
│   └── daily_news/
│       ├── main.py
│       ├── runner.py
│       └── config.py
│
├── shared/
│   ├── ai/
│   ├── social/
│   │   ├── __init__.py
│   │   ├── exceptions.py
│   │   ├── models.py
│   │   ├── publisher.py
│   │   ├── facebook.py
│   │   └── instagram.py
│   │
│   ├── wordpress/
│   ├── ingestion/
│   │
│   ├── content/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── storage.py
│   │   ├── asset_builder.py
│   │   └── wordpress_media.py
│   │
│   ├── media/
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
│   ├── test_phase12a_social_images.py
│   ├── test_media_foundation.py
│   └── test_media_composition.py
│
└── data/
    ├── db/
    ├── logs/
    ├── cache/
    ├── media/
    └── exports/
```

---

# Core Structural Principles

## Module Isolation

- One module = one deployable unit
- No cross-module dependencies
- Business logic belongs inside modules

## Shared Platform Layer

- Generic reusable functionality only
- No module-specific assumptions
- Stable interfaces

## Configuration

- Environment-driven only
- No hardcoded credentials
- No embedded secrets

## Reliability

- Idempotent execution
- Retry-safe processing
- Observability-first architecture

## Runtime Philosophy

- Docker-first development

---

# Implemented Phases

| Phase | Name | Status |
|---------|---------|---------|
| Phase 1 | Docker Foundation & Skeleton Setup | ✅ Complete |
| Phase 2 | Daily News Core Module | ✅ Complete |
| Phase 3 | Social Publishing Layer | ✅ Complete |
| Phase 4 | Persistence & Deduplication Foundation | ✅ Complete |
| Phase 5 | Named Social Target Routing | ✅ Complete |
| Phase 6 | Runtime, Scheduler & Alerts | ✅ Complete |
| Phase 6.5 | Observability & Operational Stabilization | ✅ Complete |
| Phase 7 | RSS News Ingestion Pipeline | ✅ Complete |
| Phase 8 | Live Pilot Hardening & Credential Activation | ✅ Complete |
| Phase 9 | WordPress Publishing Layer | ✅ Complete |
| Phase 10 | Media & Asset Generation Layer | ✅ Complete |
| Phase 11 | Content Asset Pipeline | ✅ Complete |
| Phase 12A | Social Media Image Publishing | ✅ Complete |

---

# Phase 12 — Visual Branding & Production Reliability

## Status

🚧 IN PROGRESS

---

## Phase 12A — Social Media Image Publishing

### Status

✅ COMPLETE

**Completed:** 2026-06-03

### Goal

Integrate saved media asset bundles directly into the social publishing layer to enable high-resolution image publishing with fail-safe architecture.

### Implemented

#### Facebook `/photos` Support

File:

```text
shared/social/facebook.py
```

Features:

- Graph API `/photos` endpoint publishing
- 30-second timeout protection
- Network exception handling
- Automatic fallback to text-only publishing
- Pipeline-safe behavior

#### Publisher Layer Updates

File:

```text
shared/social/publisher.py
```

Features:

- Image byte routing
- Image name routing
- Unified content dictionary support

#### Instagram Compatibility Fix

File:

```text
shared/social/instagram.py
```

Added:

```python
image_bytes: bytes | None = None
```

Prevents runtime signature mismatches.

#### Social Image Selection

File:

```text
modules/daily_news/runner.py
```

Added deterministic image selection hierarchy:

```text
facebook_landscape
→ featured
→ facebook_square
```

Used for:

- Single-topic execution
- RSS execution

#### Test Suite

File:

```text
scripts/test_phase12a_social_images.py
```

Result:

- 8/8 tests passing
- Fully offline
- Docker validated

---

# Phase 11 — Content Asset Pipeline

## Status

✅ COMPLETE

Completed: 2026-06-01

## Goal

Build reusable content asset packaging and production integration workflow.

### Phase 11A — Asset Bundle Storage

Implemented:

```text
shared/content/
├── models.py
├── storage.py
├── asset_builder.py
└── README.md
```

Storage layout:

```text
data/media/YYYY/MM/DD/article-slug/

featured.jpg
facebook_landscape.jpg
facebook_square.jpg
instagram_square.jpg
instagram_portrait.jpg
story.jpg
metadata.json
article.md
```

Validation:

- 11/11 tests passing
- Fully offline
- Docker validated

---

### Phase 11B — Production Asset Integration

Implemented:

```text
shared/content/wordpress_media.py
```

Capabilities:

- WordPress media uploads
- Retry logic
- Exponential backoff
- Failure-safe result objects

Added configuration:

```python
MediaConfig
get_media_config()
get_wordpress_config()
```

Added execution metrics:

- assets_generated
- bundles_created
- images_generated
- images_uploaded
- wordpress_media_failures

Validation:

- 13/13 integration tests passing
- No regressions

---

# Phase 10 — Media & Asset Generation Layer

## Status

✅ COMPLETE

Completed: 2026-06-01

### Major Features

#### Media Layer

```text
shared/media/
├── image_generation.py
├── image_sourcing.py
├── image_processing.py
├── image_composition.py
├── featured_image.py
└── social_formatter.py
```

#### Supported Social Formats

| Format | Dimensions |
|----------|-------------|
| Facebook Landscape | 1200 × 630 |
| Facebook Square | 1080 × 1080 |
| Instagram Square | 1080 × 1080 |
| Instagram Portrait | 1080 × 1350 |
| Story | 1080 × 1920 |

#### Test Coverage

- Foundation tests: 50
- Composition tests: 62

Total:

- 112 tests passing

---

# Active Modules

## daily_news

Status: Production-capable

Capabilities:

- RSS ingestion
- Topic fallback generation
- AI summarization
- Facebook publishing
- WordPress publishing
- Media asset generation
- Social image publishing
- Deduplication
- Runtime metrics

---

# Deduplication Architecture

## RSS Article Deduplication

Purpose:

Prevent feed article reprocessing.

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

## Topic-Level Deduplication

Purpose:

Prevent duplicate publishing.

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

# Architecture Decisions

## Docker Compose Before Kubernetes

Chosen to maintain operational simplicity on a single VPS.

## SQLite Before PostgreSQL

Chosen to reduce infrastructure complexity while preserving persistence.

## Reliability Before Features

Operational safety and observability are prioritized ahead of feature expansion.

## Shared Services Stay Lightweight

Avoid unnecessary framework complexity.

## WordPress As Output Adapter

WordPress remains a publishing destination only.

Generation and publishing stay intentionally decoupled.

## Media Layer As Pure Bytes Pipeline

All images travel through the system as raw bytes.

File I/O only occurs at explicit storage boundaries.

Benefits:

- Fully testable
- Mock-friendly
- Filesystem-independent core logic

---

# Known Limitations

## Social Publishing

- Instagram live publishing not fully validated

## Media

- No video generation pipeline
- Stability AI provider stub
- Ideogram provider stub
- Flux provider stub

## Multi-Module Expansion

- Only `daily_news` is production-ready

## User-Facing Content Creation

Not yet implemented:

- Article request workflow
- Content dashboard
- Multi-user management

---

# Next Major Milestone

# Phase 12B — Visual Branding & CTA System

## Goal

Develop and integrate a responsive branding overlay layer supporting:

- Custom layouts
- Logos
- Typography
- Font management
- Brand colors
- CTA blocks
- Aspect-ratio-aware rendering

## Objectives

### Branding System

- Responsive relative positioning
- Social-format-safe rendering
- Layout presets

### Font Management

- Local open-source fonts
- Docker-safe deployment
- Non-root compatible volume handling

### Reliability

- Fully fail-safe composition
- Rendering failures never break publishing
- Graceful degradation paths

---

# AI Agent Operating Rules

Before making changes:

1. Read project state completely.
2. Respect phase boundaries.
3. Avoid unnecessary abstractions.
4. Maintain module isolation.
5. Test inside Docker.
6. Update timeline before commit.

---

# Preferred Development Loop

```text
Understand
→ Analyze
→ Implement Minimal Change
→ Test in Docker
→ Validate
→ Update Documentation
→ Commit
```

---

# Project Direction

ContentPilot is evolving toward a modular AI-powered content operations platform with:

- Automated news generation
- Multi-channel publishing
- Media generation
- Social automation
- WordPress automation
- Future video generation
- Future queue-based orchestration
- Future multi-module ecosystem

Current focus remains:

**Production reliability, branding integration, and controlled publishing pilots before major feature expansion.**