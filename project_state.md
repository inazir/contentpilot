```markdown
# PROJECT_STATE.md

# ContentPilot — Current Project State

Last Updated: 2026-05-25

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

#### 2026-05-25
- Implemented shared/ai reusable provider layer
- Added:
  - anthropic_client.py
  - deepseek_client.py
  - exceptions.py
  - __init__.py
- Added retry/backoff handling
- Added normalized AIClientError abstraction
- Verified imports and Docker compatibility

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