# shared/brands — Multi-Brand Package

## Purpose

`shared/brands` is the brand management layer for ContentPilot.

It owns:
- Brand database tables and migrations
- `BrandContext` — the execution context passed through all pipelines
- Service layer for resolving brand configuration (DB → env fallback)
- Repository layer for all brand data access

## Rules

- **No module may import from `repository.py` directly.** Use `service.py`.
- **`BrandContext` is never constructed in modules.** Call `get_brand_context()` or `get_default_brand_context()`.
- Modules receive `BrandContext` and use its fields. They do not query brands tables.

## Quick Start

```python
from shared.brands import (
    init_brand_db,
    seed_default_brand,
    get_brand_context,
    get_default_brand_context,
    get_brand_context_by_slug,
)

# On startup
init_brand_db()       # creates tables + migrations (idempotent)
seed_default_brand()  # ensures brand_id=1 exists

# In scheduler / module
ctx = get_default_brand_context()      # brand_id=1
ctx = get_brand_context(2)             # by ID
ctx = get_brand_context_by_slug("tn")  # by slug

# Use context
print(ctx.brand_slug)
print(ctx.social_targets)
print(ctx.media_storage_root)
```

## Credential Types

| `credential_type` | JSON keys |
|---|---|
| `social_targets` | `targets: list[str]` |
| `wordpress` | `url, user, password, default_status` |
| `ai_override` | `provider, model` |

## Files

| File | Responsibility |
|---|---|
| `models.py` | Dataclasses, DB schema, migrations |
| `repository.py` | Raw DB access (brands, profiles, credentials) |
| `service.py` | BrandContext construction with fallback logic |
| `validation.py` | Input validation for slugs, names, URLs |
| `__init__.py` | Public API |
