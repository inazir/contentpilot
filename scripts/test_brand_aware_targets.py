#!/usr/bin/env python3
"""
Integration tests for load_social_targets_for_brand() — Step 7a.

This is the highest-stakes test in Phase 13C so far: a bug here means
the publish pipeline could send a real post to the WRONG Facebook page,
or fail to pick up a token rotated through the dashboard. Tests both
the happy path and every fallback branch explicitly.
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

_TMPDIR = tempfile.TemporaryDirectory(prefix="cp_brand_targets_")
os.environ["STORE_DB_PATH"] = os.path.join(_TMPDIR.name, "contentpilot.db")

from shared.brands import init_brand_db, seed_default_brand, upsert_credential, CRED_FACEBOOK
from shared.config import load_social_targets, load_social_targets_for_brand, SocialTarget

init_brand_db()
seed_default_brand()


def _set_env_target(key: str, platform: str, page_id: str, token: str, enabled: str = "true"):
    env_key = key.upper()
    os.environ["SOCIAL_TARGETS"] = key
    os.environ[f"SOCIAL__{env_key}__PLATFORM"] = platform
    os.environ[f"SOCIAL__{env_key}__ENABLED"] = enabled
    os.environ[f"SOCIAL__{env_key}__PAGE_ID"] = page_id
    os.environ[f"SOCIAL__{env_key}__ACCESS_TOKEN"] = token


def test_no_db_credential_falls_back_to_env_exactly():
    print("=== Test: no DB credential -> falls back to env, identical to load_social_targets() ===")
    _set_env_target("gs_facebook_main", "facebook", "ENV_PAGE_111", "ENV_TOKEN_111")

    env_result = load_social_targets()
    brand_result = load_social_targets_for_brand(brand_id=1)

    assert brand_result["gs_facebook_main"].page_id == "ENV_PAGE_111"
    assert brand_result["gs_facebook_main"].access_token == "ENV_TOKEN_111"
    assert brand_result["gs_facebook_main"] == env_result["gs_facebook_main"], (
        "With no DB credential, brand-aware result must exactly match env-only result"
    )
    print("  PASS")


def test_db_credential_overrides_env():
    print("=== Test: CRITICAL — DB credential takes priority over env ===")
    upsert_credential(1, CRED_FACEBOOK, {
        "page_id": "DB_PAGE_999",
        "access_token": "DB_TOKEN_999",
    })

    result = load_social_targets_for_brand(brand_id=1)
    target = result["gs_facebook_main"]

    assert target.page_id == "DB_PAGE_999", f"Expected DB page_id, got {target.page_id}"
    assert target.access_token == "DB_TOKEN_999", f"Expected DB token, got {target.access_token}"
    print(f"  page_id={target.page_id} token={target.access_token}  PASS")


def test_partial_db_credential_falls_back_per_field():
    print("=== Test: DB credential with only page_id set falls back to env for token ===")
    upsert_credential(1, CRED_FACEBOOK, {"page_id": "DB_PAGE_ONLY"})

    result = load_social_targets_for_brand(brand_id=1)
    target = result["gs_facebook_main"]

    assert target.page_id == "DB_PAGE_ONLY"
    assert target.access_token == "ENV_TOKEN_111", (
        f"Expected fallback to env token, got {target.access_token}"
    )
    print(f"  page_id={target.page_id} (db) token={target.access_token} (env fallback)  PASS")


def test_empty_db_credential_falls_back_entirely():
    print("=== Test: DB credential row exists but both fields empty -> full env fallback ===")
    upsert_credential(1, CRED_FACEBOOK, {})

    result = load_social_targets_for_brand(brand_id=1)
    target = result["gs_facebook_main"]

    assert target.page_id == "ENV_PAGE_111"
    assert target.access_token == "ENV_TOKEN_111"
    print("  PASS")


def test_unrelated_brand_id_does_not_leak_credentials():
    print("=== Test: brand_id isolation — brand 2's resolution doesn't see brand 1's DB credential ===")
    upsert_credential(1, CRED_FACEBOOK, {"page_id": "BRAND1_PAGE", "access_token": "BRAND1_TOKEN"})

    # brand_id=2 has no row in brand_credentials at all
    result = load_social_targets_for_brand(brand_id=2)
    target = result["gs_facebook_main"]

    assert target.page_id != "BRAND1_PAGE", "Brand 2 must not see brand 1's DB credential!"
    assert target.page_id == "ENV_PAGE_111", "Brand 2 with no DB row should fall back to env"
    print(f"  brand 2 correctly isolated, got env fallback: {target.page_id}  PASS")


def test_unsupported_platform_passes_through_unchanged():
    print("=== Test: platform with no brand_credentials support (e.g. future platform) passes through ===")
    _set_env_target("gs_tiktok_main", "tiktok", "TT_PAGE", "TT_TOKEN")
    # SOCIAL_TARGETS env var only holds one key at a time in this test
    # helper, so re-set it to include tiktok for this specific check
    os.environ["SOCIAL_TARGETS"] = "gs_tiktok_main"

    result = load_social_targets_for_brand(brand_id=1, target_keys=["gs_tiktok_main"])
    target = result["gs_tiktok_main"]

    assert target.page_id == "TT_PAGE"
    assert target.platform == "tiktok"
    print("  PASS")


def test_missing_env_key_skipped_safely():
    print("=== Test: a target_key with no env definition at all is skipped, not crashed ===")
    os.environ["SOCIAL_TARGETS"] = "gs_facebook_main"
    result = load_social_targets_for_brand(brand_id=1, target_keys=["gs_facebook_main", "does_not_exist_anywhere"])
    assert "does_not_exist_anywhere" not in result
    assert "gs_facebook_main" in result
    print("  PASS")


if __name__ == "__main__":
    test_no_db_credential_falls_back_to_env_exactly()
    test_db_credential_overrides_env()
    test_partial_db_credential_falls_back_per_field()
    test_empty_db_credential_falls_back_entirely()
    test_unrelated_brand_id_does_not_leak_credentials()
    test_unsupported_platform_passes_through_unchanged()
    test_missing_env_key_skipped_safely()
    print("\nAll brand-aware target resolution tests passed.")
