# ContentPilot Project State

## Current Status

**Current Maturity:** Production-ready multi-brand AI content automation platform with:

- Multi-brand execution support
- Brand-aware scheduling
- Brand-aware publishing
- AI content generation
- WordPress publishing
- Social media publishing
- Media asset generation
- Visual branding system
- Stateful background scheduling
- Structured logging and observability

ContentPilot has successfully evolved from a single-brand automation platform into a multi-brand SaaS-ready architecture capable of serving multiple brands from a single deployment while maintaining backward compatibility.

---

## Current Project Status

| Property | Value |
|---|---|
| Branch | main |
| State | Stable |
| Current Milestone | Phase 15 Complete |
| Next Milestone | Phase 14B-Ext (Routing Dashboard UI) |
| Production Readiness | Multi-brand pilot capable |
| Architecture Stage | SaaS Foundation Established |

---

## Completed Phases

| Phase | Name | Status |
|---|---|---|
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
| 13B | Multi-Brand SaaS Foundation | ✅ |
| 13B-E | Multi-Brand Validation & Routing Test Hardening | ✅ |
| 13C | Brand Dashboard Foundation | ✅ |
| 13D | Dashboard Enhancements | ✅ |
| 13D-Ext | Scheduler Wiring | ✅ |
| 14A | Admin Panel | ✅ |
| 14B | Shared Routing Framework | ✅ |
| 15  | Client Login & Multi-User Auth | ✅ |

---

## Platform Overview

ContentPilot is a Docker-first AI automation platform focused on:

- AI content generation
- WordPress publishing
- Social media automation
- Multi-brand content distribution
- Automated media generation
- Scheduled publishing workflows
- Future SaaS expansion

**Primary technology stack:** Python 3.12+, Docker & Docker Compose, SQLite, APScheduler, Anthropic, DeepSeek

---

## System Capabilities

### Infrastructure

- Docker-first architecture
- Containerized execution
- Docker Compose orchestration
- Environment-driven configuration
- GitHub Actions CI validation
- Stateful scheduler daemon
- Multi-brand execution model

### AI Layer

Provider abstraction architecture: Anthropic, DeepSeek

Features:
- Shared AI routing layer
- Provider abstraction
- Retry-aware execution
- Future provider expansion ready

> Modules never communicate directly with AI providers.

Access pattern:
```
Module
  ↓
shared.ai.router
  ↓
Provider
```

### Content Processing

Capabilities:
- RSS ingestion
- Atom feed ingestion
- Feed normalization
- Article fingerprinting
- Duplicate detection
- AI rewriting
- AI summarization
- Static fallback generation

Workflow:
```
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
## Recent Milestones & Updates

### June 2026 — LinkedIn Live Publishing Integration
- **Status:** Fully Functional & Verified (`REAL` mode active).
- **Infrastructure Shift:** Successfully migrated from the deprecated `/v2/ugcPosts` nested schema architecture to the modern, flat LinkedIn REST API (`/rest/posts`) using explicit versioned headers (`LinkedIn-Version: 202603` and `X-Restli-Protocol-Version: 2.0.0`).
- **Authorization & Scopes:** - Provisioned a dedicated business application (`ID: 256380148`) with Development Tier access to the **Community Management API**.
  - Isolated and locked down the required corporate publishing permission scope: `w_organization_social`.
- **Core Pipeline Implementation:**
  - Implemented robust corporate URN resolution (`_build_author_urn`) inside `shared/social/linkedin.py` to seamlessly parse raw numerical page IDs into validated `urn:li:organization:<id>` elements.
  - Resolved structural `422 (Invalid Urn Format)` and `400 (Organization permissions)` validation blockers.
- **Verification & Testing:**
  - Created automated live verification script (`scripts/test_linkedin_real.py`).
  - Successfully ran integration suite tests confirming zero regressions across the multi-tenant routing core (`test_publish_pipeline.py`) and the WordPress subsystem (`test_wordpress.py`).

## Phase: Mietvertrag Generator v2.0 Refactor

**Status:** Complete
**Date:** June 2026

### Summary

Full architecture refactor of the Mietvertrag Generator (`frontend/mietvertrag/`). The existing 659-line single-file monolith was replaced with a 63-file schema-driven, wizard-based application.

### Architecture

- **Config layer:** `src/config/siteConfig.js` — all URLs/branding from `VITE_` env vars with fallbacks
- **Schema system:** 8 schemas (`src/schemas/`) define visible sections, required fields, default rules, clauses, and available document types per contract category
- **State management:** `useContract` hook owns all form state; `useDraft` + `storageService` handle localStorage persistence
- **Services:** `contractGenerator.js` produces structured document models; `pdfGenerator.js` renders them to PDF via jsPDF
- **UI:** 11 wizard steps, shared component library (11 common components), global CSS design system with dark mode

### Contract Types Supported (14)

WG möbliert/unmöbliert, Wohnung möbliert/unmöbliert, Haus, Garage, Stellplatz, Kellerraum, Lagerraum, Büro, Gewerberaum, Zwischenmiete, Untervermietung, Studentenwohnheim

### Documents Generated (up to 8 per contract type)

Mietvertrag, Übergabeprotokoll, Schlüsselprotokoll, Inventarliste, Hausordnung, Wohnungsgeberbestätigung, Kündigungsformular, Mietbescheinigung

### New Dependency

`jspdf ^2.5.1`

### Environment Variables Added

`VITE_CONTENTPILOT_URL`, `VITE_CONTENTPILOT_NAME`, `VITE_PRODUCT_NAME`, `VITE_PRODUCT_DOMAIN`, `VITE_IMPRESSUM_URL`, `VITE_DATENSCHUTZ_URL`, `VITE_AGB_URL`, `VITE_CONTACT_URL`, `VITE_SUPPORT_EMAIL`

### Key Decisions

- No English language support (contracts are German legal documents)
- No client-side router added (wizard uses step state, not URL routes)
- jsPDF chosen over html2canvas for PDF (no DOM dependency, smaller bundle, precise layout control)
- `schema.visibleSections` array drives which wizard steps appear, making new contract types addable with a single schema file

---

## Multi-Brand SaaS Foundation (Phase 13B)

### Overview

Phase 13B introduced a complete multi-brand execution architecture. Every execution path is now brand-aware: scheduling, AI generation, WordPress publishing, social publishing, media generation, and asset storage. This is achieved through the BrandContext system.

### BrandContext

BrandContext is now the primary execution object throughout the platform.

```python
ctx = get_brand_context(brand_id)
main(brand_context=ctx)
```

BrandContext provides: `brand_id`, `brand_slug`, `brand_name`, `website_url`, `social_targets`, WordPress credentials, publish mode, media storage root.

Modules no longer need to access brand configuration directly.

### Configuration Resolution

Priority order:
```
BrandContext
  ↓
Database
  ↓
Environment Variables
```

Environment variable fallback exists only for the default brand.

### Database Schema

| Table | Stores |
|---|---|
| `brands` | Brand definitions |
| `brand_profiles` | `website_url`, `logo_path`, `brand_name`, `brand_cta`, `branding_layout` |
| `brand_credentials` | WordPress credentials, social credentials, AI overrides |

### Brand-Aware Scheduling

Every schedule now belongs to a specific brand:

```
GermanySupport → Daily News → Every Hour
TechNewsHub    → Daily News → Every Two Hours
```

Multiple brands can independently run the same module.

### Brand-Aware Storage

Media assets are isolated per brand:

```
data/media/germanysupport/
data/media/technewshub/
data/media/client-x/
```

This prevents cross-brand asset contamination.

---

## Phase 13B Extended — Multi-Brand Validation & Routing Test Hardening

**Status:** ✅ COMPLETE

### Goal

Validate the newly introduced multi-brand architecture and routing behavior inside the actual Docker Compose orchestration environment. The objective was to ensure that routing logic, client enable/disable handling, and scheduler execution paths behave identically in production containers as they do during local development.

### Implemented

**Docker-Orchestrated Test Execution**

```bash
docker compose exec scheduler \
python -m unittest modules.daily_news.tests.test_routing
```

**Routing Validation** — Confirmed correct behavior for:
- Enabled client routing
- Disabled client exclusion
- Missing client handling
- Empty routing targets
- Safe fallback paths
- Distribution boundary conditions

Example validated behavior:
```
routing_no_clients | article=art_006 | reason=no_enabled_clients
```

**Import Resolution Hardening** — Standardized Python module invocation through dotted module notation, removing path-resolution inconsistencies between local and Docker-based execution.

### Test Coverage

- 19 routing tests
- Multi-brand distribution logic
- Scheduler container execution paths
- Client enable/disable state handling
- Routing edge cases
- Distribution safety boundaries

All tests passing.

### Outcome

- **Isolated Testing Alignment:** Routing behavior verified inside the actual scheduler container environment.
- **Robust Edge-Case Coverage:** Distribution logic safely handles missing, disabled, and unavailable clients.
- **Reproducible CI/CD Foundation:** Container-native test execution provides a standardized validation command suitable for CI pipelines, GitHub Actions, pre-deployment validation, and future pre-commit automation.

---

## Media & Asset Generation

### Image Generation

Provider-agnostic architecture: Mock, OpenAI DALL-E 3, Stability AI, Ideogram, Flux

### Stock Image Sourcing

Supported providers: Mock, Pexels, Unsplash, Pixabay

### Image Processing

Features: Resize, Crop, Compress, Format conversion, Thumbnail generation

### Social Media Formatting

| Format | Resolution |
|---|---|
| Facebook Landscape | 1200 × 630 |
| Facebook Square | 1080 × 1080 |
| Instagram Square | 1080 × 1080 |
| Instagram Portrait | 1080 × 1350 |
| Story | 1080 × 1920 |

### Branding System (Phase 12B)

**Layout A — Editorial Bands:** Header band, footer band, news-style presentation

**Layout B — Modern Overlay:** Floating content card, corner logo, social-first design

**Layout C — Minimalist Typography:** Gradient overlays, large typography, CTA focused

**Rendering Engine Features:** Responsive scaling, dynamic text sizing, automatic wrapping, relative positioning, Docker-safe font loading, PIL fallback chain

---

## Publishing

### WordPress

Features: WordPress REST API, draft publishing, live publishing, categories, tags, featured images, publish result tracking, retry-aware publishing

### Facebook

Features: Direct image uploads, Graph API integration, text fallback support, duplicate protection, publish logging

### Instagram

Features: Publishing framework, shared publishing integration, image routing compatibility

### Publishing Controls

- Named social target routing
- Duplicate protection
- Safe Mode / Live Mode
- Per-target enable/disable
- Publish limits
- Audit logging

---

## Scheduler Service (Phase 13A)

**Status:** Complete and operational. Built on APScheduler.

**Responsibilities:** Schedule management, retry management, execution tracking, health monitoring, heartbeat telemetry

### Core Components

```
shared/scheduler/
├── models.py
├── retry_manager.py
├── job_executor.py
├── heartbeat.py
└── scheduler_service.py
```

### Scheduler Flow

```
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

## Reliability & Operations

### Persistence

```
data/db/contentpilot.db
data/db/scheduler.db
```

Features: SQLite persistence, WAL mode, migration support, brand-aware scheduling

### Runtime Safety

Features: Thread-safe execution, runtime locking, duplicate detection, retry-safe processing, structured logging, health checks

### Notifications

Supported: Telegram, Email

---

## CI/CD Status

**GitHub Actions:** 🟢 Green

Validated areas:
- Runtime locking
- Metadata storage
- Publishing pipelines
- Duplicate detection
- RSS ingestion
- Notifications
- WordPress publishing
- Media generation
- Image publishing
- Branding layouts
- Scheduler service
- Retry handling
- Heartbeat monitoring
- Multi-brand routing tests
- Client distribution edge-case handling
- Scheduler container routing validation

All known automated validation pipelines are passing.

---

## Architecture Overview

```
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
├── frontend/
│   ├── mietvertrag/
│   │   ├── src/
│   │   │   ├── config/
│   │   │   │   └── siteConfig.js
│   │   │   ├── schemas/
│   │   │   ├── components/
│   │   │   └── services/
│   │   └── package.json
│   └── wordpress/
│       └── wp-content/
│           └── themes/
│               └── mycontentpilot-theme/
│                   ├── front-page.php
│                   ├── page-preise.php
│                   ├── page-funktionen.php
│                   ├── page-kontakt.php
│                   ├── page-impressum.php
│                   ├── page-datenschutz.php
│                   ├── page-agb.php
│                   └── style.css
│
├── infra/
├── scripts/
└── data/
```

---

## Core Architectural Principles

### Module Isolation
- One module = one deployable unit
- No cross-module dependencies
- Business logic remains inside modules

### Shared Platform Layer
- Generic reusable functionality only
- No module-specific assumptions
- Stable interfaces

### Multi-Brand Execution
- BrandContext is the source of truth
- No module may access brand persistence directly
- Shared brand services manage all brand resolution

### Configuration
- Environment driven
- Database backed
- No hardcoded credentials
- Backward compatible fallbacks

### Reliability
- Idempotent execution
- Retry-safe processing
- Observability-first design

### Runtime Philosophy
- Docker-first
- Migration-friendly architecture
- Incremental evolution
- Production readiness before complexity

---

## Current Limitations

### Social Publishing
- Instagram production validation remains limited

### Media
Not yet activated: Stability AI, Ideogram, Flux
Not yet implemented: Video generation pipeline

### SaaS Features
Not yet implemented: REST API, Billing, Credential encryption, Instagram real publishing, per-brand routing dashboard UI
Dashboard + Admin Panel + Client Login: operational — brand dashboard at {slug}.mycontentpilot.de, admin panel at mycontentpilot.de/admin

---

## Phase History (Recent)

### Phase 13+ Frontend Edition — Monorepo + Git-Driven Deployment
**Date:** 09.06.2026 | **Status:** ✅ Complete

**What changed:**
- Merged `mycontentpilot-site` repo into `contentpilot` monorepo
- New layout: `backend/` (modules, shared), `frontend/` (wordpress, mietvertrag), `deploy/` (all ops)
- `deploy/sites.yml` is now the single file to edit when adding a new subdomain

**Deployment pipeline:**
```
GitHub webhook → VPS :9000 → deploy.sh → nginx-sync + docker compose up
```

- SSL auto-issued via `ssl-issue.sh` on first deploy of a new domain
- Systemd service `contentpilot-webhook` runs the listener (enabled, auto-restart)

**To add a new subdomain:**
1. Add entry to `deploy/sites.yml`
2. Add compose file to `deploy/compose/` if new service
3. `git push` — everything else is automatic

**Manual infrastructure (one-time, already done):**
- `contentpilot-webhook.service` installed and enabled on VPS
- Port 9000 opened in UFW
- GitHub webhook configured pointing to VPS :9000

---

### Phase 13+ Extended — Production Infrastructure, Email & Branding Alignment
**Date:** 15.06.2026 – 16.06.2026 | **Status:** ✅ Complete

**What changed:**
- **Host Network Optimization:** Configured the edge SSL reverse proxy container to `network_mode: host` inside `deploy/compose/docker-compose.yml`, successfully bypassing deep bridge network/firewall boundaries (iptables/ufw) that triggered 502 Bad Gateway drops.
- **Edge Architecture Upgrades:** Restructured the central Caddyfile to cleanly proxy local loops directly over the host network loopback space (`127.0.0.1:8080` for main WordPress site and `127.0.0.1:3010` for the mietvertrag contract automation service), completely normalizing multi-domain production routing.
- **Unified Brand Alignment:** Sanitized the entire custom theme codebase (`mycontentpilot-theme`) using precise terminal lookaheads, systematically swapping all disconnected frontend references from `ContentPilot` to the correct public-facing brand token: `MyContentPilot` across core templates (`front-page.php`, `page-preise.php`, `page-funktionen.php`, `page-agb.php`, `page-impressum.php`, `page-datenschutz.php`).
- **Production Transactional Mail Integration:** Successfully integrated WP Mail SMTP directly into the persistent WordPress stack. Authorized secure programmatic dispatch over Brevo's direct API tier, completed public domain registration for `mycontentpilot.de`, and deployed valid DKIM parameters inside Cloudflare DNS to guarantee absolute deliverability.
- **Git Housekeeping and Tracking Optimization:** Implemented a comprehensive repository `.gitignore` targeting automated container storage and default WordPress structural paths. Flushed index state caches (`git rm -r --cached .`), dropping tracked file bulk cleanly from 849 files back to exact code modifications.

---

### Phase 13C — Brand Dashboard Foundation
**Date:** June–July 2026 | **Status:** ✅ Complete

**What was built:**
- New module: modules/dashboard/ (FastAPI, uvicorn, port 8090)
- Session-based single-admin login (itsdangerous signed cookies,
  SHA-256 password hash stored in DASHBOARD_ADMIN_PASSWORD_HASH env var)
- Facebook config edit form: Page ID, access token (masked display,
  never pre-filled), caption topics, hashtags, excluded keywords,
  location, CTA text, image source, title/subtitle templates,
  first comment template, tone
- Secure token handling: blank token on save preserves existing token
- AI-powered dry-run preview: generates caption from saved config
  with zero side effects on publish_history (verified by row count)
- Hostname-based brand scoping: {slug}.mycontentpilot.de auto-resolves
  brand from Host header; / redirects to /brands/{slug}
- New DB table: brand_content_config (brand_id, platform, config_json,
  updated_at) — mirrors brand_credentials pattern
- Caddy + sites.yml updated for germanysupport.mycontentpilot.de

**Pipeline wiring (Steps 7a/7b/7c):**
- load_social_targets_for_brand(): DB credentials take priority over
  SOCIAL__ {KEY} __ env vars for page_id/access_token per brand
- generate_news_post() accepts optional content_config dict — uses
  configured tone/excluded_keywords/location when present, falls back
  to hardcoded defaults when not (byte-identical fallback verified)
- publisher.py routes brand_context through to brand-aware credential
  resolution; failure falls back to env silently (never crashes publish)

**Key decisions:**
- Shared container model retained (not per-brand containers)
- JSON blob per (brand_id, platform) for content config
- Credential secrets separated from content config by table
- Token masking on all HTML output

---

### Phase 13D — Dashboard Enhancements + Scheduler Wiring
**Date:** July 2026 | **Status:** ✅ Complete

**Step 1 — Scheduling UI (modules/dashboard/facebook_schedule.py):**
- parse_schedule_form, validate_schedule, schedule_to_display,
  merge_schedule_into_config — pure logic, 10 unit tests
- Schedule stored in brand_content_config under 'schedule' key:
  frequency (daily/twice_daily/weekly), times (HH:MM UTC),
  active_days (0=Mon…6=Sun), max_posts_per_day (1–10)
- Scheduling section added to Facebook edit form with full validation

**Step 2 — CSV topic upload (modules/dashboard/facebook_csv.py):**
- POST /brands/{slug}/facebook/upload-topics
- parse_csv_bytes, merge_topics, validate_topics_list — 8 unit tests
- UTF-8, auto-detects header row, merge or replace mode
- Max 100 topics / 300 chars each, deduplication

**Step 3 — Post history view:**
- GET /brands/{slug}/history — last 50 publish_history rows in a table

**Phase 13D-Ext — Scheduler Wiring (shared/scheduler/schedule_config.py):**
- schedule_config_to_cron_expressions(): dashboard config → APScheduler
  cron strings; 0=Mon mapping (not 0=Sun like Unix cron), verified
- Multiple posting times → multiple schedule rows (one per time)
- sync_schedule_to_db(): disables old rows (preserves job_runs FK
  history), inserts new rows; called on every Facebook settings save
- Schedule failure never blocks content config save (try/except)
- GET /brands/{slug}/facebook shows active cron expressions + status
- POST /brands/{slug}/facebook/schedule/pause disables without deleting
- 10 unit tests, all passing
- Verified end-to-end: save form → DB row confirmed → UI shows active
  → scheduler restart → schedule_registered log line confirmed
---

### Phase 14A — Admin Panel
**Date:** July 2026 | **Status:** ✅ Complete

**What was built:**
- New modules/dashboard/admin_auth.py: separate admin authentication
  using ADMIN_PANEL_PASSWORD_HASH env var and cp_admin_session cookie
  (distinct from brand cp_dashboard_session — isolation verified)
- New modules/dashboard/admin_views.py: pure rendering functions +
  form validation; 14 unit tests, all passing
- Admin routes at /admin/...:
    GET/POST /admin/login — admin-only login
    GET      /admin       — list all brands with enabled/disabled status
    GET/POST /admin/brands/new — create brand (writes brands +
                                 brand_profiles tables)
    GET      /admin/brands/{slug} — detail view with credentials + schedules
    POST     /admin/brands/{slug}/enable|disable — toggle brand status
- Brand creation page shows exact Caddyfile block and sites.yml entry
  to add (does not auto-edit Caddy — intentional safety choice)
- Security: brand session cookie cannot access admin panel (verified:
  302 to /admin/login when hitting /admin with only brand cookie)
- Verified: admin login, brand list, brand creation (DB confirmed),
  disable/enable toggle; test brand cleaned up post-verification
- Access: https://mycontentpilot.de/admin/login

---

### Phase 14B — Shared Routing Framework
**Date:** July 2026 | **Status:** ✅ Complete

**What was built:**
- New shared/routing/ package with three routing strategies:
  - manual: always routes — every article from brand's feeds
    goes to that brand (default, zero cost)
  - keyword: scores article title+summary against brand's
    caption_topics list; word-boundary aware; fractional scoring
  - ai: calls shared.ai to score relevance 0-100 per brand;
    falls back to keyword on AI failure; never crashes pipeline
- ArticleRouter: reads routing config from brand_content_config
  (platform='routing'), falls back to global env vars
- RoutingConfig per brand: strategy, threshold, rss_feeds, topics
- RouteDecision: route bool, score, strategy, reason — fully logged
- modules/daily_news/runner.py patched: ArticleRouter integrated,
  per-brand feed resolution with DAILY_NEWS_RSS_FEEDS env fallback,
  routing decision logged before article processing
- 14 unit tests, all passing
- Verified: routing_decision log lines confirmed in production
  (strategy=manual score=1.00 for all articles — correct default)
- Next: Phase 14B-Ext adds dashboard UI to configure per-brand
  RSS feeds and routing strategy

---

### Phase 15 — Client Login & Multi-User Auth
**Date:** July 2026 | **Status:** ✅ Complete

**What was built:**
- New modules/dashboard/user_auth.py:
  - users table: brand_id, email, password_hash, created_at,
    last_login; UNIQUE(brand_id, email) constraint
  - PBKDF2-HMAC-SHA256 password hashing with random salt
    (260k iterations) — proper hashing distinct from admin SHA-256
  - create_user, delete_user (brand_id scoped — cross-brand
    deletion impossible), get_users_for_brand, authenticate_user
  - cp_user_session cookie (24h) — third distinct cookie:
    cp_dashboard_session (legacy), cp_admin_session (admin),
    cp_user_session (client) — all verified distinct in tests
  - validate_new_user_form: email regex, min 8 chars, confirm match
  - init_user_db() called on dashboard startup — idempotent
  - 16 unit tests, all passing
- Updated app.py:
  - /login shows email+password form on brand subdomains,
    legacy single-password form on direct/admin access
  - _require_session accepts cp_user_session OR cp_dashboard_session
  - /logout clears both session cookies
  - Admin routes added:
      GET  /admin/brands/{slug}/users — list users + add form
      POST /admin/brands/{slug}/users/add — create client user
      POST /admin/brands/{slug}/users/{id}/delete — remove user
- Verified end-to-end:
  - Client email login issues cp_user_session (200 on brand view)
  - Wrong password: 303 to /login?error=Invalid+email+or+password
  - Legacy single-password: still issues cp_dashboard_session
  - users table schema confirmed in production DB



---

## Next Major Milestone

### Phase 14A — Shared Routing Framework

**Goal:** Introduce intelligent content routing capabilities.

Current workflow:
```
RSS → Rewrite → Publish
```

Future workflow:
```
RSS → Rewrite → Classify → Route → Publish
```

**Planned Architecture:**
```
shared/routing/
├── router.py
├── classifiers/
├── repositories/
├── models/
└── exceptions/
```

**Routing Objectives:**
- Client-aware routing
- Business-category matching
- Dynamic destination selection

**Classification:**
- Initial: `KeywordClassifier`
- Future: `EmbeddingClassifier`, `LLMClassifier`

**Persistence:**
- Initial: JSON configuration
- Future: SQLite, PostgreSQL

**Publishing:** Maintain compatibility with existing WordPress, Facebook, and Instagram publishers.

---

## Long-Term Roadmap

| Phase | Focus |
|---|---|
| 13C | Brand-scoped RSS feed configuration |
| 14 | Routing framework and Auto-Publisher foundation |
| 15 | REST API and management dashboard |
| 16 | Authentication and RBAC |
| 17 | Billing and subscriptions |
| 18 | Credential encryption |

**Long-Term Vision:**
```
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

## AI Agent Operating Rules

**Before making changes:**
1. Read project state completely
2. Respect phase boundaries
3. Maintain module isolation
4. Avoid unnecessary abstractions
5. Test inside Docker
6. Update documentation before commit
7. Preserve backward compatibility
8. Follow BrandContext architecture

**Preferred Development Workflow:**
```
Understand → Analyze → Implement Minimal Change → Test In Docker → Validate → Update Documentation → Commit
```

---

## Current Direction

ContentPilot is now a production-ready, multi-brand AI publishing platform with a SaaS-ready foundation.

The scheduler, publishing stack, media system, AI layer, brand architecture, and multi-brand routing validation suite are operational and stable.

The next evolution is the introduction of a shared routing framework that will transform ContentPilot from a multi-brand publishing system into a dynamic multi-client content distribution platform.