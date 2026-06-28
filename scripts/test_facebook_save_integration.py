#!/usr/bin/env python3
"""
Integration test: simulates exactly what POST /brands/{slug}/facebook/edit
does internally — calling the real shared.brands repository functions —
without going through FastAPI (unavailable in this sandbox). Proves the
full save path is correct against a real (temp, isolated) SQLite DB.
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "modules", "dashboard"))

_TMPDIR = tempfile.TemporaryDirectory(prefix="cp_fb_save_")
os.environ["STORE_DB_PATH"] = os.path.join(_TMPDIR.name, "contentpilot.db")

from shared.brands import (
    init_brand_db,
    seed_default_brand,
    get_brand_by_slug,
    get_credentials,
    get_content_config,
    upsert_credential,
    upsert_content_config,
    CRED_FACEBOOK,
)
from facebook_form import build_content_config, merge_credential_update, validate_content_config

init_brand_db()
seed_default_brand()


def simulate_save(slug: str, form: dict) -> tuple[bool, list[str]]:
    """Mirrors facebook_edit_submit()'s logic exactly."""
    brand = get_brand_by_slug(slug)
    assert brand is not None

    new_content_config = build_content_config(form)
    errors = validate_content_config(new_content_config)
    if errors:
        return False, errors

    existing_cred = get_credentials(brand.id, CRED_FACEBOOK)
    existing_cred_data = existing_cred.as_dict() if existing_cred else {}
    merged_cred = merge_credential_update(
        existing_cred_data, form.get("page_id", ""), form.get("access_token", "")
    )

    upsert_credential(brand.id, CRED_FACEBOOK, merged_cred)
    upsert_content_config(brand.id, "facebook", new_content_config)
    return True, []


def test_first_save_creates_everything():
    print("=== Test: first save creates credential + content config from scratch ===")
    ok, errors = simulate_save("germanysupport", {
        "page_id": "111222333",
        "access_token": "FIRST_REAL_TOKEN",
        "cta_text": "Message us",
        "hashtags": "#expat,#germany",
    })
    assert ok, f"Expected success, got errors: {errors}"

    brand = get_brand_by_slug("germanysupport")
    cred = get_credentials(brand.id, CRED_FACEBOOK)
    content = get_content_config(brand.id, "facebook")

    assert cred.as_dict()["page_id"] == "111222333"
    assert cred.as_dict()["access_token"] == "FIRST_REAL_TOKEN"
    assert content.as_dict()["cta_text"] == "Message us"
    print("  PASS")


def test_second_save_with_blank_token_preserves_it():
    print("=== Test: CRITICAL — editing content only, leaving token blank, doesn't lose it ===")
    # User comes back later, only wants to change the CTA text.
    # They leave the access_token field blank (as the UI instructs).
    ok, errors = simulate_save("germanysupport", {
        "page_id": "111222333",
        "access_token": "",  # blank — should NOT erase FIRST_REAL_TOKEN
        "cta_text": "New CTA text",
        "hashtags": "#expat,#germany",
    })
    assert ok, f"Expected success, got errors: {errors}"

    brand = get_brand_by_slug("germanysupport")
    cred = get_credentials(brand.id, CRED_FACEBOOK)
    content = get_content_config(brand.id, "facebook")

    assert cred.as_dict()["access_token"] == "FIRST_REAL_TOKEN", (
        "Token was lost on a content-only edit! This is the exact bug "
        "the merge logic exists to prevent."
    )
    assert cred.as_dict()["page_id"] == "111222333"
    assert content.as_dict()["cta_text"] == "New CTA text"
    print("  token still intact, CTA updated  PASS")


def test_invalid_submission_does_not_write_to_db():
    print("=== Test: validation failure means NO db write happens ===")
    brand = get_brand_by_slug("germanysupport")
    before_content = get_content_config(brand.id, "facebook").as_dict()

    ok, errors = simulate_save("germanysupport", {
        "page_id": "111222333",
        "access_token": "",
        "cta_text": "x" * 250,  # too long, should fail validation
    })
    assert not ok
    assert len(errors) > 0

    after_content = get_content_config(brand.id, "facebook").as_dict()
    assert after_content == before_content, (
        "DB was modified despite validation failure!"
    )
    print(f"  rejected cleanly, DB unchanged: {errors}  PASS")


def test_token_update_actually_overwrites_when_provided():
    print("=== Test: providing a new token does replace the old one ===")
    ok, errors = simulate_save("germanysupport", {
        "page_id": "111222333",
        "access_token": "ROTATED_TOKEN_456",
        "cta_text": "Still here",
    })
    assert ok, f"Expected success, got: {errors}"

    brand = get_brand_by_slug("germanysupport")
    cred = get_credentials(brand.id, CRED_FACEBOOK)
    assert cred.as_dict()["access_token"] == "ROTATED_TOKEN_456"
    print("  PASS")


if __name__ == "__main__":
    test_first_save_creates_everything()
    test_second_save_with_blank_token_preserves_it()
    test_invalid_submission_does_not_write_to_db()
    test_token_update_actually_overwrites_when_provided()
    print("\nAll facebook save integration tests passed.")
