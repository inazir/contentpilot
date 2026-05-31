# 📄 ContentPilot Project State (Updated)

## Current Status

### Current Maturity

Production-capable foundation completed. The platform has successfully transitioned from a single-container proof of concept to a stable, observable, autonomous multi-target execution runtime layer.

The system is operational, but still in **active architectural stabilization phase (post-Phase 7 refinement)**.

---

## System Capabilities

* **Docker-First Architecture:** Fully containerized module execution with isolated runtime boundaries.
* **AI Abstraction Layer:** Provider-agnostic execution supporting Anthropic and DeepSeek with fallback routing.
* **Social Publishing Layer:** Multi-target routing with named social destination keys.
* **Runtime Automation Layer:** Process locking, lifecycle safety guards, and execution tracking.
* **Observability Layer:** Structured logs, execution summaries, and runtime diagnostics.
* **CI Pipeline Validation:** GitHub Actions-based automated testing for core workflows.
* **RSS News Ingestion Pipeline:** Full feed ingestion, normalization, and AI summarization system with deduplication.

---

## Next Major Milestone

### Phase 8 — Real-World Credential Activation & Live Channel Pilot Program

**Goal:** Activate production social media credentials and run controlled live publishing.

Pipeline Target:

```text
RSS Feed → Parse → Normalize → Deduplicate → AI Summarize → Multi-Target Publish
```

---

## Current Repository Status

* **Branch:** `main`
* **State:** Stable (post-Phase 7 stabilization)
* **Last Completed Phase:** Phase 7 (RSS Ingestion Pipeline + Dedup Stabilization)
* **Ready For:** Phase 8 (Live Credential Activation)

---

## CI/CD Status

* GitHub Actions CI: Active
* Automated test execution: Enabled
* Runtime locking tests: ✅ Passing
* Metadata storage tests: ✅ Passing
* Publish pipeline tests: ✅ Passing
* Duplicate detection tests: ✅ Passing *(after Phase 7 stabilization fixes)*
* Notification system tests: ✅ Passing
* Status: 🟢 Green

---

## Development Environment

* Platform Host: Ubuntu VPS (1blu Dedicated Setup)
* Client Access: VS Code Remote SSH
* Engine Layer: Docker + Docker Compose V2
* Runtime Model: Container-per-module execution
* Config System: Environment-driven `.env` injection

---

## Project Architecture Overview

```text
contentpilot/
├── modules/
│   └── daily_news/
├── shared/
│   ├── ai/
│   ├── social/
│   ├── ingestion/
│   ├── runtime.py
│   ├── store.py
│   ├── notify.py
│   ├── logging.py
│   └── models.py
├── infra/
│   ├── docker/
│   ├── compose/
│   └── cron/
├── scripts/
└── data/
```

---

## Core Structural Principles

* One module = one deployable unit
* Shared logic lives in `shared/`
* Business logic lives in `modules/`
* Docker is the execution baseline
* No hidden global dependencies
* Environment-driven configuration only

---

## Implemented Phases

| Phase     | Name                                         | Status     |
| --------- | -------------------------------------------- | ---------- |
| Phase 1   | Docker Foundation                            | ✅ Complete |
| Phase 2   | Daily News Core Module                       | ✅ Complete |
| Phase 3   | Social Publishing Layer                      | ✅ Complete |
| Phase 4   | Persistence + Dedup Foundation               | ✅ Complete |
| Phase 5   | Named Social Targets Routing                 | ✅ Complete |
| Phase 6   | Runtime + Scheduler + Alerts                 | ✅ Complete |
| Phase 6.5 | Observability + Stability Layer              | ✅ Complete |
| Phase 7   | RSS Ingestion Pipeline + Dedup Stabilization | ✅ Complete |

---

## Phase 7 Summary (Important)

### Achievements

* Built full RSS/Atom ingestion system
* Added article fingerprinting (`sha256(title + link)`)
* Implemented feed merging, normalization, and sorting
* Introduced `rss_articles` persistence table
* Integrated AI summarization pipeline
* Added safe draft mode (no publishing side effects)
* Built full test suite for ingestion pipeline

### Key Stabilization Fixes During Phase 7

* Fixed SQLite schema mismatch (`target_key`)
* Fixed publish_history compatibility issue
* Stabilized deduplication across publishing pipeline

---

## Active Modules Status

### `modules/daily_news`

Fully operational content automation module supporting:

* RSS-driven news ingestion
* Static topic fallback mode
* AI-based content generation
* Multi-target social publishing
* Deduplication before and after publishing

---

## Shared Platform Components

* `shared/ai`: Provider abstraction layer (Anthropic, DeepSeek)
* `shared/social`: Multi-target publishing system
* `shared/ingestion`: RSS ingestion framework (reusable across modules)
* `shared/runtime`: Execution lifecycle + locking system
* `shared/store`: SQLite persistence + deduplication logic
* `shared/notify`: Alerting system (Telegram/email)

---

## Architecture Decisions

* Docker Compose chosen over Kubernetes for simplicity and single-host control
* SQLite chosen before PostgreSQL for lightweight local persistence
* Modular monorepo structure enforced for long-term scalability
* No external queues or Redis to avoid premature complexity
* Environment-driven configuration ensures portability

---

## Deduplication Model (Critical Clarification)

The system currently uses **two independent deduplication systems**:

### 1. RSS Article Deduplication

* Purpose: Prevent reprocessing same RSS articles
* Key: `sha256(title + link)`
* Storage: `rss_articles` table
* Scope: ingestion layer only

---

### 2. Topic-Level Deduplication (daily_news module)

* Purpose: Prevent repeated publishing of identical topics
* Key: `hash(normalized topic string)`
* Storage: `publish_history` table
* Scope: publishing layer only

---

### Important Note

These systems are **intentionally separate** and not yet unified into a global deduplication framework.

This separation ensures:

* ingestion stability
* publishing flexibility
* module independence

---

## Known Limitations

* Instagram production publishing not fully wired with live credentials
* WordPress publishing not yet implemented
* No centralized deduplication abstraction layer (intentional for now)
* No media generation pipeline yet (images/video not implemented)

---

## Phase 8 — Next Direction

### Real-World Credential Activation

Focus areas:

* Activate production social media credentials
* Run controlled live publishing tests
* Add monitoring for real audience interactions
* Validate cross-platform publishing stability

---

## Long-Term Roadmap

* Phase 8: Live Credential Activation
* Phase 9: Media + Asset Generation Layer
* Phase 10: Multi-module scaling + SaaS readiness

---

## AI Agent Operating Rules

* Read full context before modifying code
* Maintain module isolation
* Avoid premature abstraction
* Prefer minimal, reversible changes
* Ensure every change is testable in Docker

---

## Preferred Execution Loop

```text
Understand → Analyze → Implement Minimal Fix → Test in Docker → Validate → Commit
```