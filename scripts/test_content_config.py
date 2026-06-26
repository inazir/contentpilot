#!/usr/bin/env python3
"""
Standalone test for Phase 13C Step 1 — brand_content_config.

Uses an isolated temp SQLite DB so it never touches production data.
Run with: python3 test_content_config.py
"""
import os
import sys
import tempfile
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

_TMPDIR = tempfile.TemporaryDirectory(prefix="cp_content_config_")
os.environ["STORE_DB_PATH"] = os.path.join(_TMPDIR.name, "contentpilot.db")

from shared.brands import (
    init_brand_db,
    seed_default_brand,
    get_content_config,
    get_all_content_config,
    upsert_content_config,
)


def test_schema_creates_cleanly():
    print("\n=== Test: Schema creates cleanly ===")
    init_brand_db()
    init_brand_db()  # idempotent — call twice on purpose
    seed_default_brand()
    print("  init_brand_db() ran twice with no error  PASS")


def test_missing_config_returns_none():
    print("\n=== Test: Missing config returns None, not an exception ===")
    result = get_content_config(brand_id=1, platform="facebook")
    assert result is None, f"Expected None, got {result!r}"
    print("  PASS")


def test_upsert_then_read():
    print("\n=== Test: Upsert then read back ===")
    facebook_config = {
        "caption_topics": ["Anmeldung", "health insurance basics"],
        "hashtags": ["#expatgermany", "#germanysupport"],
        "excluded_keywords": ["politics"],
        "location_text": "Stuttgart, Germany",
        "cta_text": "DM us for help",
        "image_source": "pexels",
        "image_title_template": "{topic}",
        "image_subtitle_template": "What expats need to know",
        "first_comment_template": "Questions? Drop them below \U0001F447",
        "tone": "helpful, modern, trustworthy",
    }

    upsert_content_config(brand_id=1, platform="facebook", data=facebook_config)

    result = get_content_config(brand_id=1, platform="facebook")
    assert result is not None, "Expected a row after upsert"
    assert result.brand_id == 1
    assert result.platform == "facebook"

    round_tripped = result.as_dict()
    assert round_tripped == facebook_config, (
        f"Round-tripped data doesn't match.\nExpected: {facebook_config}\nGot: {round_tripped}"
    )
    print(f"  topics={round_tripped['caption_topics']}  PASS")


def test_upsert_overwrites_not_duplicates():
    print("\n=== Test: Second upsert overwrites, doesn't duplicate ===")
    upsert_content_config(brand_id=1, platform="facebook", data={"cta_text": "v1"})
    upsert_content_config(brand_id=1, platform="facebook", data={"cta_text": "v2"})

    all_rows = get_all_content_config(brand_id=1)
    facebook_rows = [c for c in all_rows if c.platform == "facebook"]
    assert len(facebook_rows) == 1, f"Expected exactly 1 facebook row, got {len(facebook_rows)}"
    assert facebook_rows[0].as_dict()["cta_text"] == "v2"
    print("  Only one row exists after two upserts, latest value wins  PASS")


def test_platforms_are_isolated_per_brand_and_type():
    print("\n=== Test: Different platforms for same brand don't collide ===")
    upsert_content_config(brand_id=1, platform="instagram", data={"cta_text": "ig version"})

    fb = get_content_config(brand_id=1, platform="facebook")
    ig = get_content_config(brand_id=1, platform="instagram")

    assert fb.as_dict()["cta_text"] == "v2"
    assert ig.as_dict()["cta_text"] == "ig version"

    all_configs = get_all_content_config(brand_id=1)
    platforms = sorted(c.platform for c in all_configs)
    assert platforms == ["facebook", "instagram"], f"Got {platforms}"
    print(f"  platforms={platforms}  PASS")


def test_unrelated_brand_unaffected():
    print("\n=== Test: brand_id isolation ===")
    # brand_id=2 doesn't exist as a real brand row, but content_config has no
    # FK enforcement issue here since we're only testing the config table's
    # own isolation logic, independent of the brands table.
    result = get_content_config(brand_id=2, platform="facebook")
    assert result is None, "brand_id=2 should have no config — isolation broken if not None"
    print("  PASS")


if __name__ == "__main__":
    test_schema_creates_cleanly()
    test_missing_config_returns_none()
    test_upsert_then_read()
    test_upsert_overwrites_not_duplicates()
    test_platforms_are_isolated_per_brand_and_type()
    test_unrelated_brand_unaffected()
    print("\nAll content_config tests passed.")
