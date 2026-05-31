# 📄 ContentPilot Project State

## Current Status

### Current Maturity

Production-capable foundation completed. The platform has successfully transitioned from a proof-of-concept automation system into a stable, observable, containerized content automation platform.

The core runtime, publishing, ingestion, deduplication, monitoring, and operational safety layers are now in place.

The project is currently entering its first controlled production pilot stage.

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

### Publishing

* Facebook publishing
* Named social target routing
* Publisher-level duplicate protection
* Safe mode / live mode publishing controls
* Per-target enable/disable controls
* Publish audit logging
* Execution publish limits

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
* Current Milestone: Phase 8 Complete
* Ready For: Phase 9 (WordPress Publishing Layer)

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
│   ├── ingestion/
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

| Phase     | Name                                         | Status     |
| --------- | -------------------------------------------- | ---------- |
| Phase 1   | Docker Foundation & Skeleton Setup           | ✅ Complete |
| Phase 2   | Daily News Core Module                       | ✅ Complete |
| Phase 3   | Social Publishing Layer                      | ✅ Complete |
| Phase 4   | Persistence & Deduplication Foundation       | ✅ Complete |
| Phase 5   | Named Social Target Routing                  | ✅ Complete |
| Phase 6   | Runtime, Scheduler & Alerts                  | ✅ Complete |
| Phase 6.5 | Observability & Operational Stabilization    | ✅ Complete |
| Phase 7   | RSS Ingestion Pipeline                       | ✅ Complete |
| Phase 8   | Live Pilot Hardening & Credential Activation | ✅ Complete |

---

# Project Timeline

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

### shared/ingestion

Provides:

* RSS parsing
* Feed normalization
* Feed configuration
* Article fingerprinting

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

---

## Known Limitations

### Social Publishing

* Instagram live production publishing not fully validated

### Content Destinations

* WordPress publishing not yet implemented

### Media

* No image generation pipeline
* No video generation pipeline

### Multi-Module Expansion

Only `daily_news` is currently production-ready.

---

## Next Major Milestone

# Phase 9 — WordPress Publishing Layer

### Goal

Introduce a reusable WordPress publishing framework that enables:

* daily_news publication to WordPress
* future article_publisher integration
* future affiliate/deals publishing

### Planned Components

```text
shared/wordpress/
├── __init__.py
├── client.py
└── models.py
```

### Objectives

* WordPress REST API integration
* Draft publishing
* Published article support
* Categories and tags
* Featured image support
* Structured result tracking
* Shared reusable interface

---

## Long-Term Roadmap

### Phase 9

WordPress Publishing Layer

### Phase 10

Media & Asset Generation Layer

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
