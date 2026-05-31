````markdown
# ContentPilot

ContentPilot is a modular, Docker-first AI automation platform for content generation, content ingestion, and multi-channel publishing.

The platform is designed around isolated business modules, reusable shared services, and lightweight infrastructure suitable for VPS deployment and long-term scaling.

Current focus areas:

* AI-powered content generation
* RSS/Atom news ingestion
* Facebook publishing automation
* Instagram publishing pipeline (mock/live-ready architecture)
* Runtime reliability and scheduling
* Duplicate-safe publishing
* Publishing safety controls
* Dockerized execution
* Modular automation workflows

---

# Project Goals

ContentPilot is being built as a long-term automation platform rather than a collection of scripts.

Core principles:

* Docker-first runtime
* Module isolation
* Shared reusable services
* Provider-agnostic AI layer
* Reliability before feature expansion
* Infrastructure simplicity
* Gradual migration toward production-grade architecture

The platform currently prioritizes:

1. Operational stability
2. Publishing reliability
3. Clear architecture boundaries
4. Observability
5. Future extensibility

---

# Current Features

## AI Layer

Implemented:

* Anthropic integration
* DeepSeek integration
* AI provider fallback
* Configurable provider/model selection via `.env`
* Shared retry/error handling
* Shared AI abstraction layer

Example:

```env
AI_DEFAULT_PROVIDER=deepseek
AI_DEFAULT_MODEL=deepseek-chat
AI_DEFAULT_FALLBACK_PROVIDER=anthropic
AI_DEFAULT_FALLBACK_MODEL=claude-haiku-4-5
````

---

## Social Publishing

Implemented:

* Facebook real publishing
* Instagram publishing architecture
* Structured publish results
* Multi-target routing
* Publisher-level duplicate protection
* Per-target enable/disable controls
* Publish audit logging
* Publish rate limiting
* Live pilot safety controls

Supported modes:

```env
PUBLISH_MODE=safe
PUBLISH_MODE=live
```

Additional safety controls:

* Disabled targets are skipped automatically
* Publisher-level deduplication prevents accidental reposts
* Publish rate limiting protects against bursts
* Full audit logging of publish decisions

---

## Runtime Reliability

Implemented:

* File locking
* Stale lock detection
* Runtime metadata persistence
* Structured logging
* Retry-safe execution
* SQLite WAL mode
* Notification hooks

---

## Daily News Module

Current capabilities:

* RSS/Atom feed ingestion
* RSS article deduplication
* AI summarization
* AI-generated topic content
* Dockerized execution
* Real Facebook publishing
* Topic-level deduplication
* Publisher-level deduplication
* Runtime-safe execution
* Draft/safe execution mode

The module supports two content paths:

### RSS Pipeline

```text
RSS Feed
→ Normalize
→ Deduplicate
→ AI Summarize
→ Publish
```

### Fallback Topic Pipeline

```text
Topic
→ AI Generate
→ Publish
```

---

# Architecture Overview

The platform follows a modular architecture:

```text
modules/     → business workflows
shared/      → reusable platform services
infra/       → Docker, compose, cron
scripts/     → operational/testing utilities
data/        → persistent runtime state
```

The architecture intentionally separates responsibilities:

| Layer    | Responsibility             |
| -------- | -------------------------- |
| modules/ | business logic             |
| shared/  | reusable platform services |
| infra/   | deployment/runtime         |
| data/    | persistence                |
| scripts/ | operational tooling        |

---

# Repository Structure

```text
contentpilot/
├── modules/
├── shared/
├── infra/
├── scripts/
├── data/
├── requirements/
├── docs/
├── project_state.md
└── README.md
```

---

# Modules

Each module is designed to become independently deployable.

Current modules:

| Module            | Purpose                     |
| ----------------- | --------------------------- |
| daily_news        | AI-generated daily content  |
| social_tips       | Social content automation   |
| deals_engine      | Deals/affiliate workflows   |
| article_publisher | Long-form publishing        |
| social_video      | Short-form video automation |

Recommended module structure:

```text
module/
├── Dockerfile
├── main.py
├── runner.py
├── services/
├── prompts/
├── models/
└── tests/
```

---

# Shared Layer

The `shared/` directory acts as the internal platform SDK.

Current shared domains:

```text
shared/
├── ai/
├── social/
├── ingestion/
├── logging.py
├── runtime.py
├── store.py
├── notify.py
└── config.py
```

Rules:

* Shared code must remain reusable
* Shared code must not depend on modules
* Platform-specific logic stays isolated
* Environment loading is centralized
* Runtime contracts are standardized

---

# CI and Testing

GitHub Actions CI is configured and active.

Current automated coverage includes:

* Runtime lock tests
* Metadata persistence tests
* Publish pipeline tests
* Duplicate detection tests
* Notification tests
* RSS ingestion tests

CI-safe runs execute with:

```env
PUBLISH_MODE=safe
```

No external publishing occurs during CI execution.

---

# AI Architecture

The AI layer is provider-agnostic.

Modules do not directly call providers.

Instead:

```python
from shared.ai import ai_complete
```

Current providers:

* Anthropic
* DeepSeek

Features:

* Fallback chains
* Retry handling
* Centralized configuration
* Typed exceptions
* Docker-safe execution

Future plans:

* Cost tracking
* Async pipelines
* Provider routing
* Queue-based execution

---

# Social Publishing Architecture

Publishing flows through:

```text
module
  ↓
shared.social.publisher
  ↓
platform adapter
  ↓
external API
```

Platform adapters remain isolated:

```text
shared/social/
├── facebook.py
├── instagram.py
├── publisher.py
└── models.py
```

Design goals:

* Platform-agnostic orchestration
* Typed publish results
* Duplicate-safe publishing
* Auditable decisions
* Future extensibility

Planned future platforms:

* LinkedIn
* X
* TikTok
* YouTube Shorts
* WordPress

---

# Runtime Architecture

Current execution model:

```text
cron/systemd
  ↓
scripts/run_job.sh
  ↓
docker compose run
  ↓
module execution
```

Features:

* File locking
* Stale lock detection
* Runtime metadata
* Retry-safe execution
* Structured logs
* Failure notifications

---

# Docker Philosophy

Everything runs containerized.

Current infrastructure:

```text
infra/
├── docker/
├── compose/
└── cron/
```

Design principles:

* Isolated module containers
* Shared base image
* Bind-mounted persistence
* Minimal VPS dependencies
* Compose over Kubernetes

The platform intentionally avoids unnecessary orchestration complexity.

---

# Persistence Layer

Current database:

* SQLite (WAL mode enabled)

Current usage:

* RSS article deduplication
* Topic-level deduplication
* Publish history
* Runtime metadata

Storage structure:

```text
data/
├── db/
├── cache/
└── logs/
```

Future PostgreSQL migration remains possible.

---

# Configuration Philosophy

Configuration is environment-driven.

Sources:

* `.env`
* `shared/config.py`

Rules:

* No hardcoded secrets
* No hardcoded credentials
* No environment-specific code
* Configuration centralized

---

# Development Workflow

Current workflow:

```text
Local Windows PC
    ↓
VS Code Remote SSH
    ↓
Ubuntu VPS
    ↓
Docker Compose execution
```

Recommended cycle:

```text
edit
→ test
→ test in Docker
→ commit
→ push
```

---

# Testing Philosophy

Tests currently live under:

```text
scripts/
```

Examples:

```text
scripts/test_ai.py
scripts/test_publish_pipeline.py
scripts/test_runtime_lock.py
scripts/test_rss_ingestion.py
```

Tests should:

* Run locally
* Run inside Docker
* Avoid external dependencies
* Remain environment-independent

Future migration to pytest remains possible.

---

# Current Implemented Phases

| Phase                                                  | Status     |
| ------------------------------------------------------ | ---------- |
| Phase 1 — Docker Foundation                            | ✅ Complete |
| Phase 2 — Daily News Core Module                       | ✅ Complete |
| Phase 3 — Social Publishing Layer                      | ✅ Complete |
| Phase 4 — Persistence & Deduplication Foundation       | ✅ Complete |
| Phase 5 — Named Social Targets Routing                 | ✅ Complete |
| Phase 6 — Runtime, Scheduler & Alerts                  | ✅ Complete |
| Phase 6.5 — Observability & Stability Layer            | ✅ Complete |
| Phase 7 — RSS Ingestion Pipeline                       | ✅ Complete |
| Phase 8 — Live Pilot Hardening & Credential Activation | ✅ Complete |

---

# Planned Future Phases

## Phase 9 — Media & Asset Generation Layer

Planned:

* AI image generation
* Social media visual assets
* Instagram-ready image workflows
* Media hosting
* Automated asset enrichment

---

## Phase 10 — Multi-Module Scale Expansion

Planned:

* Additional production modules
* Multi-brand publishing
* Multi-tenant readiness
* Distribution scaling

---

# Operational Philosophy

The platform intentionally prioritizes:

* Reliability
* Maintainability
* Observability
* Deterministic execution
* Infrastructure simplicity

The system evolves incrementally through small, validated improvements rather than large-scale rewrites.

---

# Current Status

ContentPilot has evolved from:

```text
AI publishing infrastructure
```

into:

```text
Production-ready AI content ingestion and publishing platform
```

and is progressing toward:

```text
Multi-module AI content automation platform
```

while maintaining a Docker-first, reliability-focused architecture.

```
```
