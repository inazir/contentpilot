# ContentPilot Project State

## Current Status

### Current Maturity

Production-ready multi-brand AI content automation platform with:

* Multi-brand execution support
* Brand-aware scheduling
* Brand-aware publishing
* AI content generation
* WordPress publishing
* Social media publishing
* Media asset generation
* Visual branding system
* Stateful background scheduling
* Structured logging and observability

ContentPilot has successfully evolved from a single-brand automation platform into a multi-brand SaaS-ready architecture capable of serving multiple brands from a single deployment while maintaining backward compatibility.

---

# Current Project Status

| Property             | Value                       |
| -------------------- | --------------------------- |
| Branch               | `main`                      |
| State                | Stable                      |
| Current Milestone    | Phase 13B Extended Complete |
| Next Milestone       | Phase 14A                   |
| Production Readiness | Multi-brand pilot capable   |
| Architecture Stage   | SaaS Foundation Established |

---

# Completed Phases

| Phase | Name                                            | Status |
| ----- | ----------------------------------------------- | ------ |
| 1     | Docker Foundation & Skeleton Setup              | ✅      |
| 2     | Daily News Core Module                          | ✅      |
| 3     | Social Publishing Layer                         | ✅      |
| 4     | Persistence & Deduplication Foundation          | ✅      |
| 5     | Named Social Target Routing                     | ✅      |
| 6     | Runtime, Scheduler & Alerts                     | ✅      |
| 6.5   | Observability & Operational Stabilization       | ✅      |
| 7     | RSS Ingestion Pipeline                          | ✅      |
| 8     | Live Pilot Hardening & Credential Activation    | ✅      |
| 9     | WordPress Publishing Layer                      | ✅      |
| 10    | Media & Asset Generation Layer                  | ✅      |
| 11    | Content Asset Pipeline                          | ✅      |
| 12A   | Social Media Image Publishing                   | ✅      |
| 12B   | Visual Branding & Template System               | ✅      |
| 13A   | Scheduler Service Core Integration              | ✅      |
| 13B   | Multi-Brand SaaS Foundation                     | ✅      |
| 13B-E | Multi-Brand Validation & Routing Test Hardening | ✅      |

---

# Platform Overview

ContentPilot is a Docker-first AI automation platform focused on:

* AI content generation
* WordPress publishing
* Social media automation
* Multi-brand content distribution
* Automated media generation
* Scheduled publishing workflows
* Future SaaS expansion

Primary technology stack:

* Python 3.12+
* Docker & Docker Compose
* SQLite
* APScheduler
* Anthropic
* DeepSeek

---

# System Capabilities

## Infrastructure

* Docker-first architecture
* Containerized execution
* Docker Compose orchestration
* Environment-driven configuration
* GitHub Actions CI validation
* Stateful scheduler daemon
* Multi-brand execution model

## AI Layer

Provider abstraction architecture:

* Anthropic
* DeepSeek

Features:

* Shared AI routing layer
* Provider abstraction
* Retry-aware execution
* Future provider expansion ready

Modules never communicate directly with AI providers.

Access pattern:

```text
Module
    ↓
shared.ai.router
    ↓
Provider
```

---

# Content Processing

Capabilities:

* RSS ingestion
* Atom feed ingestion
* Feed normalization
* Article fingerprinting
* Duplicate detection
* AI rewriting
* AI summarization
* Static fallback generation

Workflow:

```text
RSS Feed
    ↓
Normalize
    ↓
Deduplicate
    ↓
AI Processing
    ↓
Media Generation
    ↓
Publishing
```

---

# Multi-Brand SaaS Foundation (Phase 13B)

## Overview

Phase 13B introduced a complete multi-brand execution architecture.

Every execution path is now brand-aware:

* Scheduling
* AI generation
* WordPress publishing
* Social publishing
* Media generation
* Asset storage

This is achieved through the BrandContext system.

---

## BrandContext

BrandContext is now the primary execution object throughout the platform.

Example:

```python
ctx = get_brand_context(brand_id)

main(brand_context=ctx)
```

BrandContext provides:

* brand_id
* brand_slug
* brand_name
* website_url
* social_targets
* WordPress credentials
* publish mode
* media storage root

Modules no longer need to access brand configuration directly.

---

## Configuration Resolution

Priority order:

```text
BrandContext
    ↓
Database
    ↓
Environment Variables
```

Environment variable fallback exists only for the default brand.

---

## Database Schema

### brands

Stores brand definitions.

### brand_profiles

Stores:

* website_url
* logo_path
* brand_name
* brand_cta
* branding_layout

### brand_credentials

Stores:

* WordPress credentials
* Social credentials
* AI overrides

---

## Brand-Aware Scheduling

Every schedule now belongs to a specific brand.

Example:

```text
GermanySupport
    ↓
Daily News
    ↓
Every Hour

TechNewsHub
    ↓
Daily News
    ↓
Every Two Hours
```

Multiple brands can independently run the same module.

---

## Brand-Aware Storage

Media assets are now isolated per brand:

```text
data/media/germanysupport/
data/media/technewshub/
data/media/client-x/
```

This prevents cross-brand asset contamination.

---

# Phase 13B Extended — Multi-Brand Validation & Routing Test Hardening

## Status

✅ COMPLETE

### Goal

Validate the newly introduced multi-brand architecture and routing behavior inside the actual Docker Compose orchestration environment.

The objective was to ensure that routing logic, client enable/disable handling, and scheduler execution paths behave identically in production containers as they do during local development.

---

## Implemented

### Docker-Orchestrated Test Execution

Verified routing and distribution logic through container-native execution:

```bash
docker compose exec scheduler \
python -m unittest modules.daily_news.tests.test_routing
```

This validates the routing subsystem using the same runtime environment used in production.

---

### Routing Validation

Confirmed correct behavior for:

* Enabled client routing
* Disabled client exclusion
* Missing client handling
* Empty routing targets
* Safe fallback paths
* Distribution boundary conditions

Example validated behavior:

```text
routing_no_clients | article=art_006 | reason=no_enabled_clients
```

ensuring articles are safely skipped when no eligible distribution target exists.

---

### Import Resolution Hardening

Improved test execution reliability by standardizing Python module invocation through dotted module notation.

This removes path-resolution inconsistencies between local execution and Docker-based execution environments.

---

### Test Coverage

Validated:

* 19 routing tests
* Multi-brand distribution logic
* Scheduler container execution paths
* Client enable/disable state handling
* Routing edge cases
* Distribution safety boundaries

All tests passing.

---

## Outcome

### Isolated Testing Alignment

Routing behavior verified inside the actual scheduler container environment rather than only through local execution.

### Robust Edge-Case Coverage

Distribution logic safely handles missing, disabled, and unavailable clients.

### Reproducible CI/CD Foundation

Container-native test execution now provides a standardized validation command suitable for:

* CI pipelines
* GitHub Actions
* Pre-deployment validation
* Future pre-commit automation

The routing subsystem is now validated against the same execution environment used in production deployments.

---

# Media & Asset Generation

## Image Generation

Provider-agnostic architecture:

* Mock
* OpenAI DALL-E 3
* Stability AI
* Ideogram
* Flux

---

## Stock Image Sourcing

Supported providers:

* Mock
* Pexels
* Unsplash
* Pixabay

---

## Image Processing

Features:

* Resize
* Crop
* Compress
* Format conversion
* Thumbnail generation

---

## Social Media Formatting

| Format             | Resolution  |
| ------------------ | ----------- |
| Facebook Landscape | 1200 × 630  |
| Facebook Square    | 1080 × 1080 |
| Instagram Square   | 1080 × 1080 |
| Instagram Portrait | 1080 × 1350 |
| Story              | 1080 × 1920 |

---

## Branding System (Phase 12B)

Supported layouts:

### Layout A — Editorial Bands

* Header band
* Footer band
* News-style presentation

### Layout B — Modern Overlay

* Floating content card
* Corner logo
* Social-first design

### Layout C — Minimalist Typography

* Gradient overlays
* Large typography
* CTA focused

---

## Rendering Engine Features

* Responsive scaling
* Dynamic text sizing
* Automatic wrapping
* Relative positioning
* Docker-safe font loading
* PIL fallback chain

---

# Publishing

## WordPress

Features:

* WordPress REST API
* Draft publishing
* Live publishing
* Categories
* Tags
* Featured images
* Publish result tracking
* Retry-aware publishing

---

## Facebook

Features:

* Direct image uploads
* Graph API integration
* Text fallback support
* Duplicate protection
* Publish logging

---

## Instagram

Features:

* Publishing framework
* Shared publishing integration
* Image routing compatibility

---

## Publishing Controls

* Named social target routing
* Duplicate protection
* Safe Mode
* Live Mode
* Per-target enable/disable
* Publish limits
* Audit logging

---

# Scheduler Service (Phase 13A)

## Status

Complete and operational.

Built on APScheduler.

Responsibilities:

* Schedule management
* Retry management
* Execution tracking
* Health monitoring
* Heartbeat telemetry

---

## Core Components

```text
shared/scheduler/
├── models.py
├── retry_manager.py
├── job_executor.py
├── heartbeat.py
└── scheduler_service.py
```

---

## Scheduler Flow

```text
Scheduler Startup
    ↓
Load Schedules
    ↓
Resolve BrandContext
    ↓
Execute Module
    ↓
Track Job Run
    ↓
Retry If Needed
```

---

# Reliability & Operations

## Persistence

Databases:

```text
data/db/contentpilot.db
data/db/scheduler.db
```

Features:

* SQLite persistence
* WAL mode
* Migration support
* Brand-aware scheduling

---

## Runtime Safety

Features:

* Thread-safe execution
* Runtime locking
* Duplicate detection
* Retry-safe processing
* Structured logging
* Health checks

---

## Notifications

Supported:

* Telegram
* Email

---

# CI/CD Status

## GitHub Actions

Status: Green

Validated areas:

* Runtime locking
* Metadata storage
* Publishing pipelines
* Duplicate detection
* RSS ingestion
* Notifications
* WordPress publishing
* Media generation
* Image publishing
* Branding layouts
* Scheduler service
* Retry handling
* Heartbeat monitoring
* Multi-brand routing tests
* Client distribution edge-case handling
* Scheduler container routing validation

All known automated validation pipelines are passing.

---

# Architecture Overview

```text
contentpilot/
├── modules/
│   ├── daily_news/
│   ├── article_publisher/
│   ├── deals_engine/
│   ├── social_tips/
│   └── social_video/
│
├── shared/
│   ├── ai/
│   ├── brands/
│   ├── social/
│   ├── wordpress/
│   ├── media/
│   ├── content/
│   ├── scheduler/
│   ├── logging/
│   ├── storage/
│   └── config/
│
├── infra/
├── scripts/
└── data/
```

---

# Core Architectural Principles

## Module Isolation

* One module = one deployable unit
* No cross-module dependencies
* Business logic remains inside modules

## Shared Platform Layer

* Generic reusable functionality only
* No module-specific assumptions
* Stable interfaces

## Multi-Brand Execution

* BrandContext is the source of truth
* No module may access brand persistence directly
* Shared brand services manage all brand resolution

## Configuration

* Environment driven
* Database backed
* No hardcoded credentials
* Backward compatible fallbacks

## Reliability

* Idempotent execution
* Retry-safe processing
* Observability-first design

## Runtime Philosophy

* Docker-first
* Migration-friendly architecture
* Incremental evolution
* Production readiness before complexity

---

# Current Limitations

## Social Publishing

* Instagram production validation remains limited

## Media

Not yet activated:

* Stability AI
* Ideogram
* Flux

Not yet implemented:

* Video generation pipeline

## SaaS Features

Not yet implemented:

* Dashboard
* REST API
* Authentication
* Billing
* Credential encryption

---

# Next Major Milestone

# Phase 14A — Shared Routing Framework

## Goal

Introduce intelligent content routing capabilities.

Current workflow:

```text
RSS
    ↓
Rewrite
    ↓
Publish
```

Future workflow:

```text
RSS
    ↓
Rewrite
    ↓
Classify
    ↓
Route
    ↓
Publish
```

---

## Planned Architecture

```text
shared/routing/
├── router.py
├── classifiers/
├── repositories/
├── models/
└── exceptions/
```

---

## Objectives

### Routing

* Client-aware routing
* Business-category matching
* Dynamic destination selection

### Classification

Initial:

* KeywordClassifier

Future:

* EmbeddingClassifier
* LLMClassifier

### Persistence

Initial:

* JSON configuration

Future:

* SQLite
* PostgreSQL

### Publishing

Maintain compatibility with existing:

* WordPress publishers
* Facebook publishers
* Instagram publishers

---

# Long-Term Roadmap

## Phase 13C

Brand-scoped RSS feed configuration.

## Phase 14

Routing framework and Auto-Publisher foundation.

## Phase 15

REST API and management dashboard.

## Phase 16

Authentication and RBAC.

## Phase 17

Billing and subscriptions.

## Phase 18

Credential encryption.

---

# Long-Term Vision

```text
ContentPilot
    ↓
Multi-Brand Platform
    ↓
Multi-Client Platform
    ↓
Self-Service SaaS
    ↓
Subscription Business
```

---

# AI Agent Operating Rules

Before making changes:

1. Read project state completely.
2. Respect phase boundaries.
3. Maintain module isolation.
4. Avoid unnecessary abstractions.
5. Test inside Docker.
6. Update documentation before commit.
7. Preserve backward compatibility.
8. Follow BrandContext architecture.

---

# Preferred Development Workflow

```text
Understand
    ↓
Analyze
    ↓
Implement Minimal Change
    ↓
Test In Docker
    ↓
Validate
    ↓
Update Documentation
    ↓
Commit
```

---

# Current Direction

ContentPilot is now a production-ready, multi-brand AI publishing platform with a SaaS-ready foundation.

The scheduler, publishing stack, media system, AI layer, brand architecture, and multi-brand routing validation suite are operational and stable.

The next evolution is the introduction of a shared routing framework that will transform ContentPilot from a multi-brand publishing system into a dynamic multi-client content distribution platform.
