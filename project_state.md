```markdown
# ContentPilot Project State

## Current Status

### Current Maturity

Production-capable publishing platform with an automated media generation, visual branding layer, and a resilient, stateful task orchestration daemon.

The platform has successfully transitioned from a proof-of-concept automation system into a stable, observable, containerized content automation platform with:

* Multi-channel social publishing
* WordPress integration
* Robust image rendering template engines
* Direct image upload pipelines
* Responsive branding systems
* Stateful, thread-safe automated scheduling daemons

Core runtime, ingestion, AI generation, deduplication, social publishing, WordPress publishing, media asset generation, highly responsive branding overlay configurations, and background task orchestrators are fully operational.

The project has successfully completed **Phase 13A (Scheduler Service Core / APScheduler Integration)** and is entering **Phase 13B (Execution Queues & Workers)**.

---

# System Capabilities

## Infrastructure

* Docker-first architecture
* Containerized module execution
* Docker Compose orchestration
* Environment-driven configuration
* GitHub Actions CI validation
* Stateful background daemons with robust context-aware runtime boundaries

## AI Layer

* Provider abstraction architecture
* [cite_start]Anthropic integration [cite: 1]
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

# Reliability & Operations

## Persistence

* SQLite persistence (Multi-DB structure: core schema alongside the standalone `scheduler.db`)
* WAL-enabled database files

## Runtime Safety

* Runtime locking (Dual-layer: Thread-level module registry locks combined with `managed_run` filesystem locks)
* Duplicate detection
* Structured logging
* Health checks
* Host-level database backups (`scripts/backup_db.sh`) with intelligent context-aware container path normalization (`/app/*` -> `$REPO_ROOT/*`) and WAL-safe `sqlite3 .backup` routing with automatic `cp` fallbacks.

## Notifications

* Telegram notifications 


* Email notifications

---

# Current Repository Status

| Property | Value |
| --- | --- |
| Branch | `main` |
| State | Stable |
| Current Milestone | Phase 13A Complete |
| Next Milestone | Phase 13B |
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
* Stateful Scheduling, Retries & Heartbeat Engine Tests (Phase 13A — 27/27 Tests) ✅

All known automated validation pipelines are currently passing.

---

# Development Environment

| Item | Value |
| --- | --- |
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
│       ├── Dockerfile
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
│   │   └── utils.py
│   │
│   ├── scheduler/
│   │   ├── models.py
│   │   ├── retry_manager.py
│   │   ├── job_executor.py
│   │   ├── heartbeat.py
│   │   └── scheduler_service.py
│   │
│   ├── runtime.py
│   ├── store.py
│   ├── notify.py
│   ├── logging.py
│   ├── models.py
│   └── config.py
│
├── infra/
│   └── compose/
│       └── docker-compose.yml
├── requirements/
│   ├── base.txt
│   └── scheduler.txt
├── scripts/
│   └── backup_db.sh
└── data/
    └── db/
        ├── contentpilot.db
        └── scheduler.db

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
* Multi-context boundaries (Clear separation between Container Runtime paths and Host operational tooling script space)

---

# Implemented Phases

| Phase | Name | Status |
| --- | --- | --- |
| 1 | Docker Foundation & Skeleton Setup | ✅ |
| 2 | Daily News Core Module | ✅ |
| 3 | Social Publishing Layer | ✅ |
| 4 | Persistence & Deduplication Foundation | ✅ |
| 5 | Named Social Target Routing | ✅ |
| 6 | Runtime, Scheduler & Alerts | ✅ |
| 6.5 | Observability & Operational Stabilization | ✅ |
| 7 | RSS Ingestion Pipeline | ✅ |
| 8 | Live Pilot Hardening & Credential Activation | ✅ |
| 9 | WordPress Publishing Layer | ✅ |
| 10 | Media & Asset Generation Layer | ✅ |
| 11 | Content Asset Pipeline | ✅ |
| 12A | Social Media Image Publishing | ✅ |
| 12B | Visual Branding & Template System | ✅ |
| 13A | Scheduler Service Core Integration | ✅ |

---

# Phase 13A — Scheduler Service Core Integration

## Status

✅ COMPLETE

**Completed:** 2026-06-03

### Goal

Transition ContentPilot away from system-level host crons toward an integrated background daemon scheduling architecture backed by APScheduler, establishing full persistence layers and execution tracing.

### Implemented

#### shared/scheduler/models.py

* Dataclass definitions for state encapsulation: `Schedule` and `JobRun` matching active schema mappings.
* Database utility functions handling migrations, state reading, and insertion hooks: `init_scheduler_db()`, `load_enabled_schedules()`, `seed_default_schedule()`, `insert_job_run()`, and `update_job_run()`.

#### shared/scheduler/retry_manager.py

* Implemented the structural `RetryManager` handling deterministic exponential backoff delays.
* Configured boundaries: Retry 1 = 15m, Retry 2 = 1h, Retry 3 = 6h. Flagged execution loops as permanently exhausted on consecutive failures exceeding the threshold.

#### shared/scheduler/job_executor.py

* Designed thread-safe execution boundaries leveraging internal registry dictionaries (`_MODULE_REGISTRY`) and module-level thread locks (`_get_module_lock`).
* Dual-layer concurrency defense: Prevents multiple threads from running overlapping pipeline jobs simultaneously while working alongside container file-locks.

#### shared/scheduler/heartbeat.py

* Created the independent `HeartbeatService` tracking continuous execution performance.
* Emits regular telemetry payloads detailing scheduler engine uptime, status diagnostics, and processed total job counts without breaking runtime mocks during test coverage loops.

#### shared/scheduler/scheduler_service.py

* The primary persistent execution loop. Automatically initializes database connectivity, provisions default seed schedules, kicks off the `BackgroundScheduler` instance, and binds graceful signal catches for clean container teardowns.

#### Test Coverage

* Verified with a specialized local verification test matrix.
* **Test Metrics:** 27 assertions passed across the scheduler framework capturing thread safety boundaries, database state changes, backoff evaluations, and metrics tracking.

---

# Environment Variables

## Media Pipeline

| Variable | Default |
| --- | --- |
| ENABLE_MEDIA_ASSETS | true |
| ENABLE_FEATURED_IMAGES | true |
| ENABLE_SOCIAL_IMAGES | true |
| MEDIA_BRANDING_ENABLED | false |
| MEDIA_ADS_ENABLED | false |
| MEDIA_STORAGE_DIR | /app/data/media |

## Branding System

| Variable | Default |
| --- | --- |
| MEDIA_BRAND_NAME | "" |
| MEDIA_BRAND_TAGLINE | "" |
| MEDIA_BRAND_CTA | "" |
| MEDIA_BRAND_WEBSITE | "" |
| MEDIA_BRAND_LAYOUT | B |
| MEDIA_BRAND_PRIMARY_COLOR | #0F172A |
| MEDIA_BRAND_ACCENT_COLOR | #38BDF8 |
| MEDIA_BRAND_LOGO_PATH | null |

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

# Phase 13B — Execution Queues & Workers

## Goal

Extend the persistent scheduler service to delegate compute-heavy pipeline execution tasks to separated worker containers using background queuing architectures, protecting core engine memory loops during massive generation bursts.

## Objectives

### Queue Layer

* Migration pathway preparation for multi-container orchestration.
* Worker separation isolation protecting individual execution context environments.

### Reliability

* Metrics collecting structures reporting queue delays.
* Execution path tracing verifying transaction records cleanly down streaming tables.

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

ContentPilot is now a production-capable AI publishing platform with container-native scheduling. Background workloads are state-driven, resilient to runtime host-level path leakage, and ready for future modular worker horizontal scale-out.

```
***

This document now perfectly reflects your production environment! You are completely greenlit to commit everything.

```