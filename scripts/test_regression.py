#!/usr/bin/env python3
"""
Regression test — confirms Step 1 changes didn't break existing
brand_credentials / BrandContext behavior.
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

_TMPDIR = tempfile.TemporaryDirectory(prefix="cp_regress_")
os.environ["STORE_DB_PATH"] = os.path.join(_TMPDIR.name, "contentpilot.db")
os.environ["DAILY_NEWS_TARGETS"] = "gs_facebook_main"

from shared.brands import (
    init_brand_db,
    seed_default_brand,
    get_brand_context,
    get_default_brand_context,
    upsert_credential,
    get_credentials,
    CRED_FACEBOOK,
    CRED_SOCIAL_TARGETS,
)


def test_existing_credential_path_unchanged():
    print("\n=== Regression: brand_credentials still works ===")
    init_brand_db()
    seed_default_brand()

    upsert_credential(1, CRED_FACEBOOK, {"page_id": "123", "access_token": "tok"})
    cred = get_credentials(1, CRED_FACEBOOK)
    assert cred is not None
    assert cred.as_dict()["page_id"] == "123"
    print("  PASS")


def test_default_brand_context_still_builds():
    print("\n=== Regression: get_default_brand_context() still works ===")
    ctx = get_brand_context(1)
    assert ctx.brand_id == 1
    assert ctx.brand_slug == "germanysupport"
    # env fallback for brand_id=1 should still resolve social targets
    assert "gs_facebook_main" in ctx.social_targets
    print(f"  ctx={ctx!r} targets={ctx.social_targets}  PASS")


if __name__ == "__main__":
    test_existing_credential_path_unchanged()
    test_default_brand_context_still_builds()
    print("\nAll regression tests passed — existing behavior intact.")
