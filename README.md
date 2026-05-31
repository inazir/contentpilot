# ContentPilot

ContentPilot is a modular, Docker-first AI automation platform for content generation and social publishing.

The platform is designed around isolated business modules, reusable shared services, and lightweight infrastructure suitable for VPS deployment and long-term scaling.

Current focus areas:

* AI-powered content generation
* Facebook publishing automation
* Instagram publishing pipeline (mock mode currently)
* Runtime reliability and scheduling
* Duplicate-safe publishing
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
* Reliability before feature explosion
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
```

---

## Social Publishing

Implemented:

* Facebook real publishing
* Instagram mock publishing
* Structured publish results
* Duplicate-safe publishing
* Multi-target architecture foundations
* Mock vs real publish modes

Supported modes:

```env
PUBLISH_MODE=mock
PUBLISH_MODE=real
```

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

* AI-generated content
* Dockerized execution
* Real Facebook publishing
* Duplicate prevention
* Runtime-safe execution
* **RSS/Atom feed ingestion with deduplication and AI summarization**
* **Draft mode** — full pipeline without publishing (safe for testing)
* **Publish mode** — complete pipeline with social posting

The module now supports two content paths:
1. **RSS pipeline** — fetches real articles from configured RSS/Atom feeds, deduplicates, summarizes via AI, and publishes
2. **Fallback topic** — generates content from a static topic when no feeds are configured

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

The architecture intentionally separates:

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
├── image/
├── wordpress/
├── logging.py
├── store.py
└── config.py
```

Rules:

* Shared code must remain reusable
* Shared code must not depend on modules
* Platform-specific logic stays isolated
* Environment loading centralized
* Runtime contracts standardized

---

# CI and Testing

A GitHub Actions workflow is configured in `.github/workflows/ci.yml`.
It runs on `ubuntu-latest` and executes the main non-real test scripts under `PYTHONPATH=.`.

Current coverage includes:

* runtime lock and metadata tests
* mock publish tests
* duplicate detection tests
* failure simulation tests
* publish pipeline end-to-end tests

For CI-safe runs, the workflow uses `PUBLISH_MODE=mock` and disables external notifications.

---

# AI Architecture

The AI layer is provider-agnostic.

Modules do NOT directly call providers.

Instead:

```python
from shared.ai import ai_complete
```

Current providers:

* Anthropic
* DeepSeek

Features:

* fallback chains
* retry handling
* centralized config
* typed exceptions
* Docker-safe execution

Future plans:

* cost tracking
* async pipelines
* provider routing
* queue-based execution

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

Platform adapters are isolated:

```text
shared/social/
├── facebook.py
├── instagram.py
├── publisher.py
└── models.py
```

Design goals:

* platform-agnostic orchestration
* typed publish results
* isolated API communication
* future extensibility

Planned future platforms:

* TikTok
* YouTube Shorts
* LinkedIn
* Telegram
* WordPress

---

# Runtime Architecture

ContentPilot currently uses a lightweight scheduler model.

Execution flow:

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

* file locking
* stale lock detection
* runtime metadata
* retry-safe execution
* structured logs
* failure notifications

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

* isolated module containers
* shared base image
* bind-mounted persistence
* minimal VPS dependencies
* Compose over Kubernetes

The platform intentionally avoids unnecessary orchestration complexity at current scale.

---

# Persistence Layer

Current database:

* SQLite (WAL mode enabled)

Current usage:

* duplicate detection
* publish history
* runtime metadata

Storage structure:

```text
data/
├── db/
├── cache/
└── logs/
```

PostgreSQL migration remains possible later.

---

# Configuration Philosophy

Configuration is environment-driven.

No secrets should be hardcoded.

Configuration sources:

* `.env`
* `shared/config.py`

The platform intentionally centralizes configuration loading to avoid fragmented runtime behavior.

---

# Development Workflow

Current workflow:

```text
Local Windows PC
    ↓
VS Code Remote SSH
    ↓
VPS development
    ↓
Docker Compose execution
```

Recommended cycle:

```text
edit
→ test locally
→ test in Docker
→ commit
→ push
```

---

# Testing Philosophy

The project currently uses lightweight executable test scripts.

Tests live under:

```text
scripts/
```

Examples:

```text
scripts/test_ai.py
scripts/test_publish_pipeline.py
scripts/test_runtime_lock.py
```

Tests should:

* run locally
* run inside Docker
* avoid framework complexity
* remain environment-independent

Pytest and CI pipelines may be introduced later.

---

# Current Implemented Phases

| Phase                                   | Status   |
| --------------------------------------- | -------- |
| Phase 1 — Skeleton + Docker foundation  | Complete |
| Phase 2 — First module container        | Complete |
| Phase 3 — Shared publishing layer       | Complete |
| Phase 4 — Reliability + persistence     | Complete |
| Phase 5 — Real Facebook publishing      | Complete |
| Phase 6 — Runtime + scheduler hardening | Complete |
| Phase 7 — RSS News Ingestion Pipeline   | Complete |

---

# Planned Future Phases

## Phase 8 — Media Pipeline

Planned:

* AI image generation
* media hosting
* Instagram-ready assets
* ffmpeg workflows
* video automation

---

## Phase 9 — Multi-Target Distribution

Planned:

* multiple Facebook pages
* multi-brand publishing
* multilingual distribution
* advanced scheduling

---

# Operational Philosophy

The platform intentionally prioritizes:

* maintainability
* migration safety
* observability
* deterministic execution
* infrastructure simplicity

The system evolves incrementally instead of using large-scale rewrites.

---

# Important Design Decisions

## Why Docker First?

To guarantee:

* environment consistency
* deployment portability
* isolated execution
* migration flexibility

---

## Why Compose Instead of Kubernetes?

Current scale does not justify Kubernetes operational overhead.

Docker Compose provides:

* sufficient isolation
* portability
* operational simplicity

---

## Why Reliability Before Features?

Automation systems fail operationally before they fail functionally.

The platform therefore prioritized:

* locking
* persistence
* retries
* logging
* duplicate detection

before expanding feature scope.

---

# Current Status

ContentPilot is currently transitioning from:

```text
AI publishing infrastructure
```

toward:

```text
AI content ingestion + distribution platform
```

The architecture is intentionally designed to support future scaling without requiring major rewrites.
