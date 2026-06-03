# ContentPilot Project State

## Current Status

### Current Maturity

Production-capable publishing platform with an automated media generation and visual branding layer.

The platform has successfully transitioned from a proof-of-concept automation system into a stable, observable, containerized content automation platform with:

* Multi-channel social publishing
* WordPress integration
* Robust image rendering template engines
* Direct image upload pipelines
* Responsive branding systems

Core runtime, ingestion, AI generation, deduplication, social publishing, WordPress publishing, media asset generation, and highly responsive branding overlay configurations are fully operational.

The project is entering **Phase 13 (Scheduler Service / APScheduler Integration)** with complete multi-ratio visual branding capabilities verified.

---

# System Capabilities

## Infrastructure

* Docker-first architecture
* Containerized module execution
* Docker Compose orchestration
* Environment-driven configuration
* GitHub Actions CI validation

## AI Layer

* Provider abstraction architecture
* Anthropic integration
* DeepSeek integration
* Automatic provider fallback support
* Shared AI routing layer

## Content Processing

* RSS / Atom ingestion
* Feed normalization
* Article fingerprinting
* Deduplication before AI processing
* AI summarization pipeline
* Static topic generation fallback

---

# Media & Asset Generation

## Image Generation

Provider-agnostic image generation:

* Mock
* OpenAI DALL-E 3
* Stability AI
* Ideogram
* Flux

## Stock Image Sourcing

* Mock
* Pexels
* Unsplash
* Pixabay

## Image Processing

* Resize
* Crop
* Compress
* Convert
* Thumbnail generation

## Social Media Formatting

Supported formats:

| Format             | Resolution  |
| ------------------ | ----------- |
| Facebook Landscape | 1200 × 630  |
| Facebook Square    | 1080 × 1080 |
| Instagram Square   | 1080 × 1080 |
| Instagram Portrait | 1080 × 1350 |
| Story              | 1080 × 1920 |

## Composition Pipeline

Supports:

* Branding overlays (optional)
* Advertisement overlays (optional)

## Featured Image Pipeline

Workflow:

```text
Stock Image
→ AI Fallback
→ Composition
→ Final Asset
```

---

## Responsive Visual Branding System (Phase 12B)

### Layout A — Editorial Bands

Features:

* Structured top header band
* Structured bottom footer band
* Contrast-aware typography
* Editorial/news style presentation

### Layout B — Modern Overlay

Features:

* Floating semi-transparent content card
* Corner logo positioning
* Adaptive internal spacing
* Social-first appearance

### Layout C — Minimalist Typography

Features:

* Soft vertical gradient mask
* Large typography overlays
* High readability CTA presentation

### Rendering Engine Features

* Aspect-ratio-independent scaling
* Relative percentage positioning
* Dynamic text sizing
* Automatic line wrapping
* Dynamic width calculations
* Responsive logo placement

### Typography System

Bundled fonts:

```text
Inter-Regular.ttf
Inter-SemiBold.ttf
Inter-Bold.ttf
```

### Reliability Features

* Native TrueType font bundling
* Docker-safe font loading
* PIL fallback chain
* Non-crashing rendering guarantees

---

## Architecture Characteristics

* Bytes-in / bytes-out architecture
* Full attribution metadata tracking
* Mock providers require zero API keys
* Deterministic rendering behavior

---

# Publishing

## Social Publishing

### Facebook

Implemented:

* Direct high-resolution image uploads
* Graph API `/photos` integration
* Automatic text-only fallback
* Publish logging
* Duplicate protection

### Instagram

Implemented:

* Publishing framework
* Image-bytes routing compatibility
* Shared publishing integration

### Publishing Controls

* Named social target routing
* Publisher-level duplicate protection
* Safe Mode / Live Mode controls
* Per-target enable/disable controls
* Publish audit logging
* Execution publish limits

---

## WordPress Publishing

Features:

* WordPress REST API integration
* Draft publishing
* Live publishing
* Categories support
* Tags support
* Featured image support
* Structured publish result tracking
* Retry-aware publishing client
* Reusable publishing interface

---

# Reliability

## Persistence

* SQLite persistence
* WAL-enabled database

## Runtime Safety

* Runtime locking
* Duplicate detection
* Structured logging
* Health checks
* Database backups

## Notifications

* Telegram notifications
* Email notifications

---

# Current Repository Status

| Property             | Value                       |
| -------------------- | --------------------------- |
| Branch               | `main`                      |
| State                | Stable                      |
| Current Milestone    | Phase 12B Complete          |
| Next Milestone       | Phase 13                    |
| Production Readiness | Multi-channel pilot capable |

---

# CI/CD Status

## GitHub Actions

Status: 🟢 Green

### Validated Test Suites

* Runtime locking tests ✅
* Metadata storage tests ✅
* Publishing pipeline tests ✅
* Duplicate detection tests ✅
* RSS ingestion tests ✅
* Notification tests ✅
* WordPress publishing tests ✅
* Media foundation tests ✅
* Media composition tests ✅
* Social image publishing tests (Phase 12A) ✅
* Visual branding layout tests (Phase 12B) ✅

All known automated validation pipelines are currently passing.

---

# Development Environment

| Item            | Value                               |
| --------------- | ----------------------------------- |
| Host            | Ubuntu VPS (1blu Dedicated Server)  |
| Client          | VS Code Remote SSH                  |
| Runtime         | Docker Engine + Docker Compose V2   |
| Repository Path | `/home/deployer/repos/contentpilot` |
| Primary Branch  | `main`                              |

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
│   │   ├── facebook.py
│   │   └── instagram.py
│   │
│   ├── wordpress/
│   ├── ingestion/
│   ├── content/
│   │   ├── storage.py
│   │   ├── asset_builder.py
│   │   └── wordpress_media.py
│   │
│   ├── media/
│   │   ├── image_generation.py
│   │   ├── image_sourcing.py
│   │   ├── image_processing.py
│   │   ├── image_composition.py
│   │   ├── featured_image.py
│   │   ├── social_formatter.py
│   │   ├── branding.py
│   │   ├── layouts.py
│   │   ├── utils.py
│   │   └── assets/fonts/
│   │
│   ├── runtime.py
│   ├── store.py
│   ├── notify.py
│   ├── logging.py
│   ├── models.py
│   └── config.py
│
├── infra/
├── scripts/
└── data/
```

---

# Core Structural Principles

## Module Isolation

* One module = one deployable unit
* No cross-module dependencies
* Business logic remains inside modules

## Shared Platform Layer

* Generic reusable functionality only
* No module-specific assumptions
* Stable interfaces

## Configuration

* Environment-driven only
* No hardcoded credentials
* No embedded secrets

## Reliability

* Idempotent execution
* Retry-safe processing
* Observability-first design

## Runtime Philosophy

* Docker-first development

---

# Implemented Phases

| Phase | Name                                         | Status |
| ----- | -------------------------------------------- | ------ |
| 1     | Docker Foundation & Skeleton Setup           | ✅      |
| 2     | Daily News Core Module                       | ✅      |
| 3     | Social Publishing Layer                      | ✅      |
| 4     | Persistence & Deduplication Foundation       | ✅      |
| 5     | Named Social Target Routing                  | ✅      |
| 6     | Runtime, Scheduler & Alerts                  | ✅      |
| 6.5   | Observability & Operational Stabilization    | ✅      |
| 7     | RSS Ingestion Pipeline                       | ✅      |
| 8     | Live Pilot Hardening & Credential Activation | ✅      |
| 9     | WordPress Publishing Layer                   | ✅      |
| 10    | Media & Asset Generation Layer               | ✅      |
| 11    | Content Asset Pipeline                       | ✅      |
| 12A   | Social Media Image Publishing                | ✅      |
| 12B   | Visual Branding & Template System            | ✅      |

---

# Phase 12B — Visual Branding & Template System

## Status

✅ COMPLETE

**Completed:** 2026-06-03

### Goal

Implement a responsive, template-driven visual branding and CTA overlay layer supporting:

* Auto-wrapping
* Dynamic layouts
* Bundled local assets
* Docker-safe rendering
* Multi-ratio compatibility

### Implemented

#### shared/media/utils.py

* Relative coordinate calculations
* Relative sizing calculations
* Dynamic typography sizing
* Auto-wrap algorithms
* Font fallback helpers

#### shared/media/branding.py

* BrandProfile dataclass
* CTA configuration support
* Color configuration support
* Website configuration support
* Logo configuration support
* Fail-safe apply_branding() wrapper

#### shared/media/layouts.py

Layout A:

* Header/footer bands

Layout B:

* Floating content card
* Corner logo

Layout C:

* Gradient overlay
* Minimalist typography

#### Embedded Assets

```text
shared/media/assets/fonts/

Inter-Regular.ttf
Inter-SemiBold.ttf
Inter-Bold.ttf
```

#### Asset Pipeline Integration

```text
shared/content/asset_builder.py
```

Branding insertion point:

```text
MEDIA_BRANDING_ENABLED=true
```

#### Test Coverage

```text
scripts/test_phase12b_branding.py
```

Coverage:

* 25 rendering tests
* Multiple aspect ratios
* Missing logos
* Font fallbacks
* Layout selection validation
* Rendering safety checks

---

# Environment Variables

## Media Pipeline

| Variable               | Default         |
| ---------------------- | --------------- |
| ENABLE_MEDIA_ASSETS    | true            |
| ENABLE_FEATURED_IMAGES | true            |
| ENABLE_SOCIAL_IMAGES   | true            |
| MEDIA_BRANDING_ENABLED | false           |
| MEDIA_ADS_ENABLED      | false           |
| MEDIA_STORAGE_DIR      | /app/data/media |

## Branding System

| Variable                  | Default |
| ------------------------- | ------- |
| MEDIA_BRAND_NAME          | ""      |
| MEDIA_BRAND_TAGLINE       | ""      |
| MEDIA_BRAND_CTA           | ""      |
| MEDIA_BRAND_WEBSITE       | ""      |
| MEDIA_BRAND_LAYOUT        | B       |
| MEDIA_BRAND_PRIMARY_COLOR | #0F172A |
| MEDIA_BRAND_ACCENT_COLOR  | #38BDF8 |
| MEDIA_BRAND_LOGO_PATH     | null    |

---

# Known Limitations

## Social Publishing

* Instagram production validation still limited

## Media

* No video generation pipeline
* Stability AI provider not activated
* Ideogram provider not activated
* Flux provider not activated

## Platform Expansion

Currently production-ready:

```text
daily_news
```

Future modules:

* article_publisher
* deals_engine
* social_tips
* social_video

---

# Next Major Milestone

# Phase 13 — Scheduler Service & Execution Queues

## Goal

Transition ContentPilot away from system-level cron execution toward an integrated scheduling architecture based on APScheduler and future queue-worker orchestration.

## Objectives

### Scheduling

* Database-driven schedules
* Dynamic job registration
* Environment-controlled timing

### Queue Layer

* Persistent task queues
* Worker isolation
* Failure-safe execution

### Reliability

* Automatic retries
* Backoff support
* Execution tracing
* Metrics collection

### Observability

* Centralized scheduler monitoring
* Execution history tracking
* Health monitoring integration

### Architecture Requirements

* Maintain module isolation
* Preserve Docker-first runtime
* APScheduler-first implementation
* Future Celery/Redis migration path

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

# Preferred Development Workflow

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

# Current Direction

ContentPilot is now a production-capable AI publishing platform with:

* RSS ingestion
* AI content generation
* WordPress publishing
* Social publishing
* Media generation
* Responsive branding
* Automated asset packaging

The next architectural evolution focuses on centralized scheduling, execution orchestration, queue management, and operational scalability while preserving simplicity and maintainability.
