#!/usr/bin/env python3
"""
Tests the dashboard's DATA LOGIC (what app.py's route handlers compute),
independent of FastAPI/uvicorn, since those aren't installable in this
sandbox (no network access). This proves the brand_view() logic is
correct against the real shared.brands layer from Step 1.

This does NOT prove FastAPI routing/HTTP serialization works — that
needs to be confirmed once deployed (see deploy/test instructions).
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

_TMPDIR = tempfile.TemporaryDirectory(prefix="cp_dash_logic_")
os.environ["STORE_DB_PATH"] = os.path.join(_TMPDIR.name, "contentpilot.db")
os.environ["DEFAULT_BRAND_WEBSITE"] = "https://germanysupport.de"

from shared.brands import (
    init_brand_db,
    seed_default_brand,
    get_brand_context_by_slug,
    get_all_content_config,
    upsert_content_config,
)

init_brand_db()
seed_default_brand()
upsert_content_config(1, "facebook", {"cta_text": "DM us", "tone": "friendly"})


def render_brand_view_logic(slug: str) -> dict:
    """Mirrors exactly what app.py's brand_view() computes, sans HTML."""
    ctx = get_brand_context_by_slug(slug)
    configs = get_all_content_config(ctx.brand_id)
    return {
        "brand_name": ctx.brand_name,
        "slug": ctx.brand_slug,
        "website": ctx.website_url,
        "targets": ctx.social_targets,
        "publish_mode": ctx.publish_mode,
        "configs": {c.platform: c.as_dict() for c in configs},
    }


def test_known_brand():
    print("=== Test: known brand renders correct data ===")
    result = render_brand_view_logic("germanysupport")
    assert result["brand_name"] == "GermanySupport"
    assert result["website"] == "https://germanysupport.de"
    assert result["configs"]["facebook"]["cta_text"] == "DM us"
    print(f"  {result}  PASS")


def test_unknown_brand_raises():
    print("=== Test: unknown brand raises ValueError (→ 404 in app.py) ===")
    try:
        render_brand_view_logic("doesnotexist")
        assert False, "Expected ValueError"
    except ValueError as exc:
        print(f"  raised correctly: {exc}  PASS")


if __name__ == "__main__":
    test_known_brand()
    test_unknown_brand_raises()
    print("\nDashboard logic tests passed.")
