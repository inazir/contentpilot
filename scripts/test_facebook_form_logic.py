#!/usr/bin/env python3
"""
Tests modules/dashboard/facebook_form.py — pure logic, no FastAPI needed.
This is the highest-risk logic in Step 5: getting the "blank token
means keep existing" behavior wrong would mean a brand's working
Facebook connection silently breaks the next time someone saves the
content-strategy form without touching the token field.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "modules", "dashboard"))

from facebook_form import (
    parse_list_field,
    list_field_to_text,
    build_content_config,
    merge_credential_update,
    validate_content_config,
)


def test_parse_list_field_basic():
    print("=== Test: parse_list_field splits and trims ===")
    assert parse_list_field("#a, #b ,#c") == ["#a", "#b", "#c"]
    assert parse_list_field("") == []
    assert parse_list_field("   ") == []
    assert parse_list_field("single") == ["single"]
    print("  PASS")


def test_list_field_roundtrip():
    print("=== Test: list_field_to_text is the inverse ===")
    items = ["#a", "#b", "#c"]
    text = list_field_to_text(items)
    assert parse_list_field(text) == items
    assert list_field_to_text([]) == ""
    assert list_field_to_text(None) == ""
    print("  PASS")


def test_build_content_config_full():
    print("=== Test: build_content_config maps all fields ===")
    form = {
        "caption_topics": "Anmeldung, taxes",
        "hashtags": "#expat,#germany",
        "excluded_keywords": "politics",
        "location_text": "Stuttgart",
        "cta_text": "DM us",
        "image_source": "pexels",
        "image_title_template": "{topic}",
        "image_subtitle_template": "sub",
        "first_comment_template": "comment here",
        "tone": "friendly",
    }
    result = build_content_config(form)
    assert result["caption_topics"] == ["Anmeldung", "taxes"]
    assert result["hashtags"] == ["#expat", "#germany"]
    assert result["cta_text"] == "DM us"
    print(f"  {result}  PASS")


def test_build_content_config_missing_fields_defaults_safely():
    print("=== Test: missing form fields don't crash, default sensibly ===")
    result = build_content_config({})
    assert result["caption_topics"] == []
    assert result["image_source"] == "pexels"
    assert result["cta_text"] == ""
    print("  PASS")


def test_merge_credential_blank_token_keeps_existing():
    print("=== Test: CRITICAL — blank token in form preserves existing token ===")
    existing = {"page_id": "111", "access_token": "REAL_LIVE_TOKEN_DO_NOT_LOSE"}
    merged = merge_credential_update(existing, page_id="111", access_token="")
    assert merged["access_token"] == "REAL_LIVE_TOKEN_DO_NOT_LOSE", (
        "Blank token submission must NOT erase the existing token!"
    )
    print(f"  token preserved: {merged['access_token']}  PASS")


def test_merge_credential_nonblank_token_overwrites():
    print("=== Test: non-blank token in form overwrites existing ===")
    existing = {"page_id": "111", "access_token": "OLD_TOKEN"}
    merged = merge_credential_update(existing, page_id="111", access_token="NEW_TOKEN")
    assert merged["access_token"] == "NEW_TOKEN"
    print("  PASS")


def test_merge_credential_first_time_no_existing():
    print("=== Test: first-time save with no existing credential ===")
    merged = merge_credential_update({}, page_id="999", access_token="FIRST_TOKEN")
    assert merged["page_id"] == "999"
    assert merged["access_token"] == "FIRST_TOKEN"
    print("  PASS")


def test_merge_credential_first_time_blank_token_has_no_token_key():
    print("=== Test: first-time save with blank token leaves no token set ===")
    merged = merge_credential_update({}, page_id="999", access_token="")
    assert merged.get("page_id") == "999"
    assert "access_token" not in merged, (
        "First save with blank token should not invent a token key"
    )
    print("  PASS")


def test_merge_credential_blank_page_id_keeps_existing():
    print("=== Test: blank page_id in form preserves existing page_id ===")
    existing = {"page_id": "EXISTING_PAGE", "access_token": "tok"}
    merged = merge_credential_update(existing, page_id="", access_token="tok")
    assert merged["page_id"] == "EXISTING_PAGE"
    print("  PASS")


def test_validate_rejects_oversized_cta():
    print("=== Test: validation rejects CTA text over 200 chars ===")
    config = {"cta_text": "x" * 201}
    errors = validate_content_config(config)
    assert any("200 characters" in e for e in errors)
    print(f"  {errors}  PASS")


def test_validate_rejects_unknown_image_source():
    print("=== Test: validation rejects unsupported image source ===")
    config = {"image_source": "midjourney"}
    errors = validate_content_config(config)
    assert any("not supported" in e for e in errors)
    print(f"  {errors}  PASS")


def test_validate_accepts_clean_config():
    print("=== Test: validation passes a clean config with no errors ===")
    config = build_content_config({
        "cta_text": "Message us",
        "image_source": "pexels",
        "hashtags": "#a,#b",
    })
    errors = validate_content_config(config)
    assert errors == [], f"Expected no errors, got {errors}"
    print("  PASS")


def test_validate_rejects_too_many_hashtags():
    print("=== Test: validation rejects more than 30 hashtags ===")
    config = {"hashtags": [f"#tag{i}" for i in range(31)]}
    errors = validate_content_config(config)
    assert any("Too many hashtags" in e for e in errors)
    print(f"  {errors}  PASS")


if __name__ == "__main__":
    test_parse_list_field_basic()
    test_list_field_roundtrip()
    test_build_content_config_full()
    test_build_content_config_missing_fields_defaults_safely()
    test_merge_credential_blank_token_keeps_existing()
    test_merge_credential_nonblank_token_overwrites()
    test_merge_credential_first_time_no_existing()
    test_merge_credential_first_time_blank_token_has_no_token_key()
    test_merge_credential_blank_page_id_keeps_existing()
    test_validate_rejects_oversized_cta()
    test_validate_rejects_unknown_image_source()
    test_validate_accepts_clean_config()
    test_validate_rejects_too_many_hashtags()
    print("\nAll facebook form logic tests passed.")
