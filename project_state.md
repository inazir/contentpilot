```markdown
# PROJECT_STATE.md

# ContentPilot — Current Project State

Last Updated: 2026-05-27 07:55 UTC

---

# 1. Project Goal

ContentPilot is a new Docker-first rewrite/re-architecture of the legacy Autoblogger system.

The legacy system remains operational and production-active during migration.

The new architecture focuses on:

- modular containerized services
- clean separation of concerns
- reusable shared libraries
- isolated Docker containers per module
- VPS-native deployment
- easier scaling and maintenance
- long-term SaaS/productization readiness

This is NOT a quick migration project.

The goal is:
- learn Docker/containerization properly
- build stable architecture incrementally
- migrate modules one-by-one safely
- avoid big-bang rewrites

---

# 2. Development Environment

## Main Development Workflow

Development happens directly on VPS using:

- VS Code Remote SSH
- Docker Engine
- Docker Compose V2
- Git + GitHub

Repository path:

```text
/home/deployer/repos/contentpilot

```

Primary branch:

```text
main

```

----------

# 3. Current Architecture Philosophy

Current strategy:

-   one module = one container
    
-   shared reusable code inside `shared/`
    
-   infrastructure isolated inside `infra/`
    
-   persistent runtime data inside `data/`
    
-   modules executed as one-shot containers
    
-   cron scheduling will happen later
    
-   no Kubernetes planned
    
-   Docker Compose is the orchestration layer
    

Important:

The project intentionally progresses slowly.

We prioritize:

1.  understanding architecture
    
2.  validating Docker concepts
    
3.  incremental milestones
    

before migrating real business logic.

----------

# 4. Current Repository Structure

```text
contentpilot/
│
├── modules/
│   └── daily_news/
│       ├── Dockerfile
│       └── main.py
│
├── shared/
│   ├── __init__.py
│   └── config.py
│
├── infra/
│   ├── docker/
│   │   ├── base.Dockerfile
│   │   └── .dockerignore
│   │
│   └── compose/
│       └── docker-compose.yml
│
├── data/
│
├── docs/
│
├── requirements/
│
├── scripts/
│
└── README.md

```

----------

# 5. Completed Milestones

## Phase 1 — Docker Foundation

Completed successfully.
### Latest Completed Work
#### 2026-05-26 (17:00)
### Phase 4 Completed — Production Reliability Layer

Implemented the first production-grade reliability layer for the social publishing pipeline.

Added:
- Structured logging system (`shared/logging.py`)
- SQLite-backed publish history store (`shared/store.py`)
- WAL mode database support for safer concurrent access
- Publish result models and failure handling
- Duplicate content detection using content hashing
- Retry-safe publish orchestration
- Mock vs real publish mode separation
- Persistent publish tracking in `/data/db/contentpilot.db`

Updated:
- `daily_news` runner now initializes DB, uses structured logs, and records publish results
- Facebook and Instagram adapters updated to Phase 4 interface
- Publisher now supports safe retries and duplicate prevention

Validation completed:
- Dry-run flow works
- Mock publishing works
- Docker execution works
- SQLite persistence verified
- Duplicate detection verified
- AI fallback logic still operational after refactor

Current architecture status:
- Shared AI layer operational
- First containerized module operational
- Production reliability layer operational
- System now supports persistent state tracking across container runs

## Phase 5 — Named Social Targets (COMPLETED): 27.05.2026 07:00

### Goal
Enable per-page/account publishing by using named social targets instead
of a single global page/account setting per platform.

### What was implemented
- Added `SocialTarget` model and `load_social_targets()` in `shared/config.py`
- Reworked `shared/social/publisher.py` to publish by target key instead of platform name
- Updated Facebook and Instagram adapters to accept a `SocialTarget` object
- Changed `shared/store.py` to deduplicate by `target_key` instead of `platform`
- Updated `modules/daily_news/runner.py` to use `DAILY_NEWS_TARGETS` from env
- Updated environment docs and `.env.example` for per-target configuration

### Testing results
- Mock publish flow validated with named targets
- Duplicate prevention works per target
- Invalid/unknown target handling is safe and does not crash the runner

## Phase 6 — Scheduler + Automation Runtime Layer

### Goal
Add a reusable runtime execution layer with locking, metadata tracking, notification support, and cron-friendly execution so modules can be scheduled safely from cron or manual execution.

### What was implemented
- Added `shared/runtime.py` with managed run lifecycle, file locking, stale-lock cleanup, and runtime metadata persistence.
- Added `shared/notify.py` for email and Telegram failure notifications.
- Added `scripts/run_job.sh` as a reusable launcher for cron or manual execution.
- Added `modules/daily_news/main.py` as a standardized module entrypoint using `managed_run()`.
- Added cron example files under `infra/cron/crontabs/`.
- Added `data/locks/` and `data/runtime/` directories for runtime state.
- Added CI-friendly non-real runtime test scripts in `scripts/`.

### Testing and validation
- Runtime lock, metadata, and failure behavior were validated with isolated test scripts.
- Publish pipeline, duplicate detection, and mock publish tests were updated to be environment-independent.
- A GitHub Actions workflow now runs the core non-real test scripts automatically on push/PR.

### What was implemented
- Added `shared/runtime.py` for file-based locking and runtime metadata tracking
- Added `shared/notify.py` for email and Telegram failure notification support
- Added standardized module entrypoint `modules/daily_news/main.py`
- Added `scripts/run_job.sh` as the universal job launcher for cron and manual runs
- Added `infra/cron/crontabs/contentpilot` as the master cron schedule
- Added runtime test coverage for lock behavior, metadata tracking, and failure handling
- Added `data/locks/` and `data/runtime/` as bind-mounted runtime directories

### Testing results
- Runtime lock acquisition and stale lock cleanup validated
- Runtime metadata persisted correctly for success and failure cases
- Failure handling releases locks and records failed run state

#### 2026-05-26 (15:00)
## Phase 3 — Social Publishing Layer (COMPLETED - Core Wiring)

### Goal
Enable publishing pipeline from `daily_news` module to social platforms (Facebook + Instagram), with safe mock-first execution controlled via environment variables.

---

### What was implemented

- Introduced `shared/social/` publishing layer
  - `facebook.py` → Facebook publishing client (mock + real-ready structure)
  - `instagram.py` → Instagram publishing client (mock + real-ready structure)
  - `publisher.py` → unified orchestration layer for multi-platform publishing

- Extended `runner.py` in `modules/daily_news/`
  - Generates content (Phase 2)
  - Optionally triggers publishing based on `PUBLISH_ENABLED`

- Environment-driven publishing control:
  - `PUBLISH_ENABLED=false` → generation only (safe mode)
  - `PUBLISH_ENABLED=true` → publishing pipeline executes

- Docker integration updated:
  - `PUBLISH_ENABLED` passed into containers via `.env`
  - Publishing behavior controlled at runtime (no code changes required)

---

### Testing results

- Dry-run mode confirmed working:
  - Post generation successful
  - Publishing skipped as expected

- Enabled publishing mode confirmed working:
  - Facebook mock publish executed
  - Instagram mock publish executed
  - Graceful handling of missing image URLs for Instagram
  - No runtime crashes

---

### Key design decisions

- Social platforms are abstracted behind `shared/social/`
- No real API credentials required yet (mock-first design)
- Instagram and Facebook treated as independent adapters
- Publishing remains optional and controlled entirely via environment variables

---

### Current limitation (intentional)

- No real Facebook Page ID integration yet
- No real Instagram Graph API token setup yet
- Image generation pipeline not enforced for Instagram posts yet

These will be added in a later phase after stabilizing content pipeline.

---

### Status

Phase 3 core infrastructure: COMPLETED
Ready for production-grade integration in next phase.
#### 2026-05-26 (14:00)
## Phase 2 — First Production Module (daily_news) ✅ COMPLETED

### Status
The first end-to-end module (`daily_news`) has been successfully implemented and validated inside Docker on VPS.

### Implemented Components
- `modules/daily_news/runner.py` (execution entrypoint)
- `modules/daily_news/generator.py` (AI-driven content generation)
- Dockerized execution via `infra/compose/docker-compose.yml`
- Isolated container execution using `contentpilot-base` image
- Full integration with shared AI layer (`shared/ai`)
- Env-driven AI configuration (provider, model, fallback, temperature, max_tokens)

### Verified Capabilities
- Docker build pipeline works correctly
- Container execution works via Docker Compose
- AI layer works inside container (Anthropic + DeepSeek verified)
- Router system correctly selects default provider from `.env`
- Fallback provider execution works correctly
- Dry-run mode successfully generates content without publishing

### Key Output
- Daily news content generation pipeline is functional end-to-end
- Example topic generation confirmed inside container runtime
- Stable reproducible execution via `docker compose run`

### Current Limitation (Intentional)
- Publishing layer is NOT implemented yet
- Output is currently only printed / dry-run logged

### Architectural Note
The runner includes a dedicated hook:

```python
# Publishing not yet implemented

#### 2026-05-25
- Implemented shared/ai reusable provider layer
- Added:
  - anthropic_client.py
  - deepseek_client.py
  - exceptions.py
  - __init__.py
- Added retry/backoff handling
- Added normalized AIClientError abstraction
- Verified shared.ai import path with direct script execution
- Discovered and fixed missing Docker base dependency for requests
- Verified Docker `--env-file .env` injection and Anthropic request execution^
- validated both Anthropic and DeepSeek providers
- verified provider interchangeability
- confirmed Docker env propagation for multiple providers

## Architecture Decisions

- AI provider logic belongs in shared/ai
- Business logic stays inside modules/
- shared layer must remain small and reusable
- No LangChain/framework abstractions
- Docker-first development workflow
- Module-by-module migration only

### Completed Tasks

-   repository skeleton created
    
-   Docker installed and working
    
-   Docker Compose V2 verified
    
-   base Docker image created
    
-   first compose setup created
    
-   first module container created
    
-   shared package imports validated
    
-   environment variable injection validated
    

----------

# 6. Existing Working Docker Setup

## Base Image

File:

```text
infra/docker/base.Dockerfile

```

Current contents:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

```

Current image name:

```text
contentpilot-base:latest

```

Successfully builds.

----------

# 7. Current Shared Package

## shared/config.py

Current responsibility:

-   read ENVIRONMENT variable
    
-   provide centralized configuration entry point
    

Current implementation:

```python
import os

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

```

----------

# 8. Current Module

## Module: daily_news

Purpose currently:

-   architecture validation only
    
-   NOT real business logic yet
    

Current file:

```text
modules/daily_news/main.py

```

Current behavior:

```python
from shared.config import ENVIRONMENT

print("Daily News Module Started")
print(f"Environment: {ENVIRONMENT}")

```

----------

# 9. Current Compose Setup

Compose file:

```text
infra/compose/docker-compose.yml

```

Current service:

```yaml
services:
  daily_news:
    build:
      context: ../..
      dockerfile: modules/daily_news/Dockerfile
    image: contentpilot-daily-news:latest
    environment:
      ENVIRONMENT: development

```

----------

# 10. Verified Working Commands

Build:

```bash
docker compose -f infra/compose/docker-compose.yml build

```

Run:

```bash
docker compose -f infra/compose/docker-compose.yml run --rm daily_news

```

Expected output:

```text
Daily News Module Started
Environment: development

```

This currently works successfully.

----------

# 11. Current Learning Focus

The current phase is:

```text
FOUNDATION + ARCHITECTURE LEARNING

```

NOT:

```text
FULL MODULE MIGRATION

```

Current learning topics:

-   Docker fundamentals
    
-   images vs containers
    
-   Docker Compose
    
-   build context
    
-   Python package structure
    
-   containerized imports
    
-   module boundaries
    
-   Docker layering basics
    

----------

# 12. Things NOT Added Yet (Intentional)

The following are intentionally postponed:

-   real legacy module migration
    
-   AI providers
    
-   Anthropic/OpenAI integrations
    
-   FFmpeg workflows
    
-   social posting
    
-   cron scheduler
    
-   persistent volumes
    
-   SQLite databases
    
-   bind mounts
    
-   logging system
    
-   health checks
    
-   deployment automation
    
-   Portainer
    
-   production optimization
    
-   environment files
    
-   CI/CD
    
-   watchtower
    
-   nginx/reverse proxy
    

Reason:

Avoid mixing:

-   architecture debugging
    
-   Docker debugging
    
-   business logic debugging
    

too early.

----------

# 13. Immediate Next Planned Step

Next planned learning milestone:

```text
Live development workflow with bind mounts

```

Topics to learn next:

-   bind mounts
    
-   live code editing without rebuild
    
-   dev vs production compose
    
-   rebuild vs restart
    
-   container development workflow
    

After that:

-   migrate first REAL legacy module logic slowly
    

----------

# 14. Important Architectural Rules

## Rule 1

Do NOT migrate multiple modules simultaneously.

Only one module at a time.

----------

## Rule 2

Every stable milestone should be:

-   tested
    
-   committed
    
-   pushed
    

before continuing.

----------

## Rule 3

Prefer understanding over speed.

This project is intentionally educational + production-oriented.

----------

## Rule 4

Keep containers simple initially.

Avoid premature optimization.

----------

## Rule 5

Shared logic belongs in `shared/`.

Business-specific logic belongs in `modules/`.

----------

# 15. Current Status Summary

Current status:

```text
Docker foundation established successfully.
First modular container architecture validated.
Ready for live-development workflow learning phase.

```
# 16. AI Agent Operating Instructions

This file is the single source of truth for the project state.

Any AI agent working on this repository must:

1. Read this file BEFORE making changes
2. Understand the current project phase
3. Respect the incremental learning-first workflow
4. Avoid introducing unplanned complexity
5. Update this file after every meaningful milestone

---

## Required Update Rules

After each completed milestone, the AI agent should update:

- completed tasks
- current architecture
- current active module(s)
- current compose setup
- current Docker setup
- current learning phase
- next planned step
- known issues/blockers
- important decisions made

---

## Important Constraints

AI agents must NOT:

- skip architectural phases
- migrate multiple modules simultaneously
- introduce Kubernetes
- add production optimizations prematurely
- add hidden magic abstractions
- restructure the repository aggressively
- overwrite existing working architecture without reason

---

## Preferred Workflow

The project follows this workflow:

Research
→ Explain
→ Implement minimally
→ Test
→ Verify understanding
→ Update PROJECT_STATE.md
→ Commit
→ Continue

---

## Documentation Discipline

Every stable checkpoint should result in:

1. verified working state
2. PROJECT_STATE.md update
3. git commit

before moving forward.

---

## Philosophy

This project prioritizes:

- clarity
- maintainability
- learning
- modularity
- operational simplicity
- incremental progress

over rapid feature migration.