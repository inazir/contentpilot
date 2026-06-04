# Phase 13B — Multi-Brand SaaS Foundation

## Overview

Phase 13B introduces a multi-brand execution model to ContentPilot. Every execution path — scheduling, AI generation, WordPress publishing, social publishing, and asset storage — is now brand-aware via a `BrandContext` object.

The architecture is backward-compatible: **GermanySupport (brand_id=1) continues working with zero configuration changes** using existing environment variables as fallback.

---

## Database Schema

### New tables

#### `brands`
One row per brand.

```sql
CREATE TABLE brands (
    id         INTEGER PRIMARY KEY,
    name       TEXT    NOT NULL,
    slug       TEXT    UNIQUE NOT NULL,
    enabled    INTEGER NOT NULL DEFAULT 1,
    created_at TEXT    NOT NULL,
    updated_at TEXT    NOT NULL
);
```

#### `brand_profiles`
Display and branding configuration per brand.

```sql
CREATE TABLE brand_profiles (
    id               INTEGER PRIMARY KEY,
    brand_id         INTEGER NOT NULL,
    website_url      TEXT,
    logo_path        TEXT,
    brand_name       TEXT,
    brand_cta        TEXT,
    branding_layout  TEXT,
    FOREIGN KEY(brand_id) REFERENCES brands(id)
);
```

#### `brand_credentials`
Per-brand service credentials stored as JSON blobs.

```sql
CREATE TABLE brand_credentials (
    id               INTEGER PRIMARY KEY,
    brand_id         INTEGER NOT NULL,
    credential_type  TEXT    NOT NULL,
    credential_json  TEXT    NOT NULL,
    created_at       TEXT    NOT NULL,
    FOREIGN KEY(brand_id) REFERENCES brands(id)
);
```

### Modified tables (migrations, backward-compatible)

#### `schedules` — added `brand_id INTEGER NOT NULL DEFAULT 1`
All existing schedules default to GermanySupport.

#### `job_runs` — added `brand_id INTEGER` (nullable)
Existing historical rows remain valid with NULL brand_id.

---

## BrandContext

`BrandContext` is the primary execution context for all brand-aware operations.

```python
from shared.brands import get_brand_context, get_brand_context_by_slug

# By ID
ctx = get_brand_context(1)

# By slug
ctx = get_brand_context_by_slug("technewshub")

# Default (brand_id=1 / GermanySupport)
ctx = get_default_brand_context()
```

### Fields

| Field | Source | Fallback (brand_id=1 only) |
|---|---|---|
| `brand_id` | brands table | — |
| `brand_slug` | brands table | — |
| `brand_name` | brand_profiles | `DEFAULT_BRAND_NAME` env |
| `website_url` | brand_profiles | `DEFAULT_BRAND_WEBSITE` env |
| `social_targets` | brand_credentials (social_targets) | `DAILY_NEWS_TARGETS` env |
| `wp_url` | brand_credentials (wordpress) | `WP_URL` env |
| `wp_user` | brand_credentials (wordpress) | `WP_USER` env |
| `wp_password` | brand_credentials (wordpress) | `WP_APP_PASSWORD` env |
| `publish_mode` | — | `PUBLISH_MODE` env |
| `media_storage_root` | computed from slug | `MEDIA_STORAGE_DIR` env + slug |

---

## Configuration Resolution Strategy

```
BrandContext fields  (highest priority)
       ↓
Database (brand_credentials / brand_profiles)
       ↓
Environment Variables  (fallback — brand_id=1 only)
```

Brands 2+ must have all credentials stored in the database. No new environment variables are needed for additional brands.

---

## Credential Types

Stored in `brand_credentials.credential_type`:

| Type | JSON structure |
|---|---|
| `social_targets` | `{"targets": ["slug1", "slug2"]}` |
| `wordpress` | `{"url": "...", "user": "...", "password": "...", "default_status": "draft"}` |
| `ai_override` | `{"provider": "anthropic", "model": "claude-haiku-4-5"}` |

Phase 13B stores plaintext JSON. Future phases may add encryption.

---

## Scheduler Integration

### Flow

```
Scheduler boots
  → init_brand_db() (runs migrations)
  → seed_default_brand() (ensures brand_id=1 exists)
  → load_enabled_schedules() (each schedule carries brand_id)
  → APScheduler registers jobs
  → On trigger: execute_with_retry(schedule, retry_manager)
    → execute_job(schedule)
      → _resolve_brand_context(schedule.brand_id)
      → BrandContext built
      → main(brand_context=ctx) called
```

### Brand-per-schedule

Each schedule row has a `brand_id`. To run a module for multiple brands, create multiple schedule rows:

```sql
-- GermanySupport runs every hour
INSERT INTO schedules (module_name, enabled, interval_hours, brand_id, ...)
VALUES ('daily_news', 1, 1, 1, ...);

-- TechNewsHub runs every 2 hours  
INSERT INTO schedules (module_name, enabled, interval_hours, brand_id, ...)
VALUES ('daily_news', 1, 2, 2, ...);
```

---

## Asset Storage

Brand-isolated paths:

```
data/media/germanysupport/2026/06/01/article-slug/
data/media/technewshub/2026/06/01/article-slug/
```

Existing assets from before Phase 13B are **not moved**. New executions write to the brand-isolated path.

The storage root is exposed via `BrandContext.media_storage_root` and injected into the media pipeline automatically.

---

## Adding a New Brand

### Method 1: CLI (recommended)

```bash
python scripts/create_brand.py \
    --name "TechNewsHub" \
    --slug "technewshub" \
    --website "https://technewshub.com" \
    --schedule-hours 2

# Then run with credentials prompt:
python scripts/create_brand.py --name "TechNewsHub" --add-credentials
```

### Method 2: Direct DB

```python
from shared.brands import (
    init_brand_db, create_brand, upsert_profile, upsert_credential,
    CRED_SOCIAL_TARGETS, CRED_WORDPRESS
)

init_brand_db()
brand_id = create_brand(name="TechNewsHub", slug="technewshub")

upsert_profile(brand_id, website_url="https://technewshub.com", brand_name="TechNewsHub")

upsert_credential(brand_id, CRED_SOCIAL_TARGETS, {
    "targets": ["tn_facebook_main"]
})

upsert_credential(brand_id, CRED_WORDPRESS, {
    "url":            "https://technewshub.com",
    "user":           "admin",
    "password":       "your-app-password",
    "default_status": "draft",
})
```

---

## Running a Module for a Specific Brand

```bash
# Default (brand_id=1, GermanySupport)
python modules/daily_news/main.py

# Named brand by slug
python modules/daily_news/main.py --brand-slug technewshub

# Named brand by ID
python modules/daily_news/main.py --brand-id 2

# Dry run for a brand
python modules/daily_news/main.py --brand-slug technewshub --dry-run
```

---

## Architecture Rules

1. **No module may query brand tables directly.** Modules receive `BrandContext` and use its fields.
2. Only `shared/brands/service.py` and `shared/brands/repository.py` access brand persistence.
3. BrandContext is always constructed by `shared.brands.service` — never instantiated directly in modules.
4. All publishing functions accept `brand_context=None` — legacy callers are unaffected.

---

## Backward Compatibility

GermanySupport (brand_id=1) continues working without any configuration changes:

- `SOCIAL_TARGETS`, `DAILY_NEWS_TARGETS` env vars still used as fallback
- `WP_URL`, `WP_USER`, `WP_APP_PASSWORD` env vars still used as fallback
- `PUBLISH_MODE` env var still controls publish behavior
- All Phase 12 publishing paths remain functional

The only behavioral change: log lines now include `brand_id=1 | brand_slug=germanysupport`.

---

## Migration Strategy

`init_brand_db()` runs automatically on:
- Scheduler startup
- Module startup (via `main.py`)

It applies all migrations idempotently:
- Creates brand tables if missing
- Adds `brand_id` to `schedules` (DEFAULT 1) if missing
- Adds `brand_id` to `job_runs` (nullable) if missing
- Seeds brand_id=1 if brands table is empty

**No manual migration steps required.**

---

## Future SaaS Roadmap

Phase 13B establishes the data model for a future SaaS product:

| Phase | Addition |
|---|---|
| 13C | Brand-scoped RSS feed configuration |
| 14 | REST API for brand management |
| 15 | Next.js dashboard (brand CRUD, schedule management) |
| 16 | User authentication + RBAC |
| 17 | Billing / subscription tiers |
| 18 | Credential encryption at rest |

The `brand_credentials` JSON blob design intentionally keeps the credential schema flexible — new credential types can be added without schema changes.
