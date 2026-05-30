# ContentPilot Project State

## Current Status

### Current Maturity

Production-capable foundation completed. The platform has successfully transitioned from a single-container proof of concept to a stable, observable, autonomous multi-target execution runtime layer.

### System Capabilities

* **Docker-First Architecture:** Complete encapsulation of workloads with independent runtime base boundaries.
* **AI Abstraction Layer:** Decoupled multi-provider execution supporting Anthropic + DeepSeek failover routines.
* **Social Publishing Layer:** Dynamic routing engine enabling multi-page distribution tracking.
* **Runtime Automation:** Process shielding featuring file-based locking maps and automated alarm distributions.
* **Observability Layer:** Uniform metrics tracking, structured rotation log files, and data snapshotting routines.
* **CI Pipeline Validation:** Active GitHub Actions automated engine testing repository safety on updates.

### Next Major Milestone

* **Phase 7 — RSS News Ingestion Pipeline**

---

## Current Repository Status

* **Branch:** `main`
* **State:** Stable
* **Last Major Completed Phase:** Phase 6.5 (Operational Stabilization Layer)
* **Ready For:** Phase 7 (RSS Ingestion Pipeline Implementation)

---

## CI/CD Status

* **Current State:** GitHub Actions CI active on push and pull requests
* **Automated Test Execution:** Enabled (Isolated environment-independent validation scripts)
* **Runtime Locking Tests:** ✅ Passing
* **Runtime Metadata Storage Tests:** ✅ Passing
* **Publish Pipeline & Social Targets Tests:** ✅ Passing
* **Duplicate Content Detection Tests:** ✅ Passing
* **Notification Layer Alerts Tests:** ✅ Passing
* **Status:** 🟢 Green

---

## Development Environment

* **Platform Host:** Ubuntu VPS (1blu Dedicated Setup)
* **Local Client Access:** VS Code Remote SSH via Windows Workstation Terminal
* **Engine Layer:** Docker Engine + Docker Compose V2
* **Automation Verification:** GitHub Actions CI Configuration Engine
* **Secured Configurations:** Managed locally using `.env` injection filters matched with explicit `.clineignore` rulesets to safeguard tokens.
* **Project Root Path:** `/home/deployer/repos/contentpilot`
* **Primary Operational Branch:** `main`

---

## Current Architecture Overview

The system follows a module-first, decoupled, container-native architecture orchestrated by Docker Compose:

```text
contentpilot/
├── modules/
│   └── daily_news/            # Fully operational business automation container
├── shared/
│   ├── ai/                    # Abstracted generation clients (Anthropic/DeepSeek)
│   ├── social/                # Multi-target social adapters (Facebook/Instagram)
│   ├── logging.py             # Structured log configuration and file rotation
│   ├── models.py              # Central data schemas and execution summaries
│   ├── notify.py              # Alarm pipelines (Telegram bot and system mail)
│   ├── runtime.py             # Lifecycle wrapper and atomic system file locking
│   └── store.py               # Local persistence and content duplicate processing
├── infra/
│   ├── docker/                # Platform base images and build definitions
│   ├── compose/               # Orchestration topologies and volume mounts
│   └── cron/                  # System automation schedules and tasks
├── scripts/                   # System validation tools and database backups
└── data/                      # Host persistent volume mounts (git-ignored)

```

### Core Structural Principles

* **One Module = One Deployable Unit:** Every workflow is isolated to its respective container space.
* **Shared Platform Logic belongs in `shared/`:** Common SDK tasks (AI, notifications, database utilities) are centralized and reusable.
* **Business Logic belongs in `modules/`:** Process-specific parameters are strictly containerized.
* **Docker-First Development Workflow:** Development environments match VPS runtime conditions precisely using volume-bound filesystems.

---

## Implemented Phases

| Phase | Name | Status |
| --- | --- | --- |
| **Phase 1** | Docker Foundation & Skeleton Setup | ✅ Complete |
| **Phase 2** | First Module (`daily_news` Generation Core) | ✅ Complete |
| **Phase 3** | Social Publishing Layer (Facebook & Instagram Abstracted Adapters) | ✅ Complete |
| **Phase 4** | Production Reliability Layer (SQLite Storage + Deduplication) | ✅ Complete |
| **Phase 5** | Named Social Targets Mapping (Multi-Account Routing Engine) | ✅ Complete |
| **Phase 6** | Automation Runtime & Scheduler Layer (Locks + Telegram Alarms) | ✅ Complete |
| **Phase 6.5** | Operational Stabilization Layer (Observability + Backups) | ✅ Complete |
| **CI** | GitHub Actions Workflow | ✅ Complete |
| **Phase 7** | External Data Ingestion Layer (RSS & Parsers) | 📋 Planned |

---

## Project Timeline

### 2026-05-27 — Phase 6.5 / Operational Stabilization Layer

#### Completed

* Implemented automated preflight system diagnostic scanning and database snapshotting routines.
* Standardized uniform execution reporting metrics across active module routines.

#### Technical Changes

* Updated `shared/logging.py` to write to a rotating file logger tracking 5 rolled backups at 5MB limits inside `data/logs/<module>.log`.
* Created `shared/models.py` exporting the `ExecutionSummary` data schema to track container loop metadata (durations, generation counts, published volumes, duplicates skipped, and errors).
* Built `scripts/healthcheck.py` to audit disk constraints, write permissions, key environment variables, and AI platform availability.
* Designed `scripts/backup_db.sh` to trigger timestamped, gzipped database backups retaining snapshots based on `BACKUP_KEEP_DAYS`.

#### Validation

* Verified structural logging file rotation behavior under high load limit simulations.
* Executed healthcheck script to validate local preflight diagnostics.
* Tested database backup snapshot compilation and verified retention cleanup constraints.

#### Notes

* Operational hygiene must precede external API ingestion patterns. Ensuring that background container operations are observable prevents invisible processing drops.

### 2026-05-27 — Phase 6 / Runtime & Scheduler Layer

#### Completed

* Engineered an automated execution runtime layer providing process protection and automated system alert delivery.
* Established crontab automation blueprints for background service initialization.

#### Technical Changes

* Programmed `shared/runtime.py` implementing file-based atomic process locking (`data/locks/`) along with stale lock cleanup logic.
* Implemented `shared/notify.py` integrating explicit Telegram Bot API push alert notifications and backup email hooks for processing faults.
* Created `scripts/run_job.sh` acting as the main infrastructure launcher to wrap container processes cleanly.
* Added cron config maps inside `infra/cron/crontabs/contentpilot`.

#### Validation

* Simulated process collisions; stale lock eviction routines cleanly freed paths without execution stalls.
* Triggered synthetic workflow failures and verified successful execution metadata tracking and immediate Telegram notification delivery.

#### Notes

* Decoupling the orchestration loop from the container runtime allows standard cron managers to handle process initialization without maintaining heavy long-running cron daemons inside application boundaries.

### 2026-05-27 — Phase 5 / Named Social Targets Mapping

#### Completed

* Upgraded the system from global account configurations to explicit per-page/per-account multi-target distribution routing.

#### Technical Changes

* Added the `SocialTarget` data map and built out the initialization workflow `load_social_targets()` inside `shared/config.py`.
* Refactored `shared/social/publisher.py` to decouple tracking keys from technology platform definitions.
* Patched database store layers inside `shared/store.py` to index asset fingerprint deduplication maps by explicit `target_key`.

#### Validation

* Validated target parsing using multi-account configurations.
* Verified that asset deduplication blocks content on a target-by-target level, allowing identical items to post to separate destination targets securely.

### 2026-05-26 — Phase 4 / Production Reliability Layer

#### Completed

* Introduced local transactional persistence and content hashing structures to guarantee reliable execution states across processing attempts.

#### Technical Changes

* Provisioned a persistent SQLite storage layer (`shared/store.py`) backed by Write-Ahead Logging (WAL) configuration flags.
* Configured real-time content hashing fingerprints to enforce strict duplicate publishing prevention.
* Added structured log context management layers to track retry operations across individual container lifetimes.

#### Validation

* Verified data persistence across sequential run instances within `/data/db/contentpilot.db`.
* Tested the deduplication behavior; matching content hashes correctly blocked duplicate target publishing.

### 2026-05-26 — Phase 3 / Social Publishing Layer

#### Completed

* Engineered unified publishing abstractions mapping to multiple target social platforms, supporting an environment-switched testing architecture.

#### Technical Changes

* Built out `shared/social/facebook.py` and `shared/social/instagram.py` platform interfaces.
* Written unified routing clients in `shared/social/publisher.py` utilizing the target-based mapping pipeline and environment run flags.

#### Validation

* Confirmed that with target testing configurations active, processing blocks safely halt before execution or route to clean execution mocks.
* Verified mock execution routines handle structural payloads without processing faults.

### 2026-05-26 — Phase 2 / First Production Module (`daily_news`)

#### Completed

* Built and isolated the initial production processing pipeline loop within active container boundaries.

#### Technical Changes

* Created `modules/daily_news/runner.py` and `modules/daily_news/generator.py`.
* Wired system contexts into `shared/ai` to implement multi-provider fallbacks (Anthropic and DeepSeek).

#### Validation

* Verified environment injection setups across independent AI service backends.
* Confirmed automatic client recovery paths handle missing client parameters cleanly.

### 2026-05-25 — Phase 1 / Docker Foundation & Skeleton Setup

#### Completed

* Established the base infrastructure footprint and package layout for development.

#### Technical Changes

* Configured `infra/docker/base.Dockerfile` hosting a slim Linux distribution layout.
* Designed core path controls within `infra/compose/docker-compose.yml`.

#### Validation

* Verified module build loops and checked package cross-import paths between `shared/` context targets and independent application modules.

---

## Active Modules Status

* **`modules/daily_news`**: Fully operational containerized module. Generates structured informational summaries using the decoupled AI client packages, logs to dynamic runtime directories, and validates post routing configuration against named social database stores. Content pipeline is generated via targeted test data inputs pending final Phase 7 parsing configurations.

---

## Shared Platform Components

* **`shared/ai`**: Abstraction provider layer offering standardized text formatting across distinct external generation services, paired with dynamic retry loops and seamless fallback client matching.
* **`shared/social`**: Architecture routing matrix directing generated payloads into discrete target distribution networks.
* **`shared/runtime`**: Host-level orchestration wrapper managing atomic processing locks, clearing stagnant workspace executions, and tracking container process limits.
* **`shared/notify`**: Critical alert dispatcher transmitting unexpected container processing terminations directly to designated Telegram communication channels.

---

## Architecture Decisions

* **Docker Compose over Kubernetes:** Enforces absolute operational simplicity, keeping processing footprints minimal on a single managed VPS host.
* **SQLite before PostgreSQL:** Employs disk-efficient local single-file transactional containers using WAL mode, avoiding infrastructure overhead until scalability demands cross-host cluster routing.
* **Module-by-Module Migration:** Guarantees structural platform integrity; migrations progress incrementally, ensuring complete test coverage before new code patterns are merged.
* **Reliability before Feature Growth:** Observability layers, diagnostic scripts, validation controls, and process isolation protocols must always be finalized before expanding input logic.
* **Shared Services remain Framework-Light:** Avoids heavy dependencies or wrapper engines (e.g., LangChain); uses simple, native Python configurations to stay fast and future-proof.
* **Environment-Driven Configuration:** Swaps testing execution maps dynamically using standard container environment matrices, keeping absolute code parity across dev paths and real-world deployment states.

---

## Explicit Non-Goals

To prevent unnecessary architecture complication and premature optimization, **do not introduce** any of the following components or frameworks into this codebase unless an explicit architecture review milestone specifically mandates them:

* Kubernetes (K8s) or advanced multi-node container orchestration layers
* Redis, RabbitMQ, or standalone memory cache layers
* Celery or complex external task distribution worker queues
* Microservice decomposition (Keep services module-focused inside this mono-repo)
* PostgreSQL or external enterprise database server migrations
* LangChain, LlamaIndex, or heavy multi-layered AI wrapper frameworks
* Long-running background daemon architectures (Leverage host-level `run_job.sh` cron triggers instead)

---

## Known Limitations

* **Facebook Production Publishing:** Verified and fully operational for at least one live target production page.
* **Instagram Production Credentials:** Direct publishing calls navigate via the simulated target architecture; live production Graph API tokens remain unlinked.
* **External Data Sourcing:** Content construction relies entirely on defined data variables; active web scrapers and external feed parsers are not yet live.
* **WordPress Publishing Integration:** Core abstract targets and ingestion storage pipelines have not yet been wired for content publishing to external content management systems.
* **Asset Generation Engine:** Visual generation templates, media compression pipelines, and video rendering utilities are completely omitted.

---

## Next Recommended Phase: Phase 7 — External Data Ingestion Layer

* **Goal:** Introduce real-world external input feeds to drive the automated generation tools.
* **Target Pipeline Topology:**
`RSS Feed Input` ➔ `Parse Core` ➔ `Normalize Model` ➔ `Deduplicate (DB Hash)` ➔ `AI Summarize` ➔ `Multi-Target Publish`
* **Implementation Strategy:** Build out a robust, network-fault-tolerant RSS parsing and HTML content normalization engine inside a clean subpackage `shared/ingestion/`. Enforce careful exception wrappers to ensure malformed target pages or network connection drops are cleanly reported using the `ExecutionSummary` schema.

---

## Long-Term Roadmap

* **Phase 8:** Real-World Credential Activation & Live Channel Pilot Program.
* **Phase 9:** Asset Creation Frameworks (Automated image composition and media transformations).
* **Phase 10:** Multi-Module Scale Expansion & Multi-Tenant SaaS Interface readiness.

---

## AI Agent Operating Instructions

This file represents the absolute Single Source of Truth (SSOT) regarding architecture states and current build constraints. Any autonomous coding agent initializing a terminal or chat frame within this repository must rigorously adhere to the following sequence:

1. **Read this file entirely** before writing any code or modifying infrastructure trees.
2. **Respect the current phase boundaries.** Never write advanced ingestion patterns or integrate live API assets if the timeline notes specify that structural foundation checks are the current focus.
3. **Avoid adding unmapped complexity.** Do not introduce extra databases, background daemons, or heavy dependencies unless explicitly authorized.
4. **Maintain chronological integrity.** Every stable deployment step, validation check, or architecture revision must update the `Project Timeline` section (most recent entries first) before code commits are created.

### Preferred Automation Loop

```text
Research Context ➔ Explain Strategy ➔ Implement Minimally ➔ Test Runtime ➔ Update Document ➔ Commit Repo

```