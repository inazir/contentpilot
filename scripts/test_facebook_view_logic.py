#!/usr/bin/env python3
"""
Tests the data-merging and token-masking logic behind GET /brands/{slug}/facebook.

NOTE: app.py imports fastapi, which isn't installable in this sandbox
(no network access). So _mask_token is reproduced here verbatim — byte
for byte identical to app.py's version — rather than imported, so this
test proves the LOGIC is correct, not that app.py itself runs under
FastAPI. The deploy/test instructions below cover that final gap via
real curl calls against the running container.
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

_TMPDIR = tempfile.TemporaryDirectory(prefix="cp_fb_view_")
os.environ["STORE_DB_PATH"] = os.path.join(_TMPDIR.name, "contentpilot.db")

from shared.brands import (
    init_brand_db,
    seed_default_brand,
    get_brand_by_slug,
    upsert_credential,
    upsert_content_config,
    get_credentials,
    get_content_config,
    CRED_FACEBOOK,
)


def _mask_token(token):
    """Verbatim copy of app.py's _mask_token — kept identical on purpose."""
    if not token:
        return "(not set)"
    if len(token) <= 8:
        return "****"
    return f"{token[:4]}...{token[-4:]}"


init_brand_db()
seed_default_brand()


def test_mask_token_short():
    print("=== Test: short/empty tokens masked safely ===")
    assert _mask_token(None) == "(not set)"
    assert _mask_token("") == "(not set)"
    assert _mask_token("short") == "****"
    print("  PASS")


def test_mask_token_real_length():
    print("=== Test: realistic token shows only prefix/suffix ===")
    fake_token = "EAABwzLixnjYBO1234567890abcdefghijklmnopXYZ"
    masked = _mask_token(fake_token)
    assert masked.startswith("EAAB")
    assert masked.endswith("XYZ")
    assert fake_token not in masked, "Full token must never appear in masked output"
    assert "..." in masked
    print(f"  {masked}  PASS")


def test_merge_credentials_and_content():
    print("=== Test: facebook view merges credential + content config ===")
    brand = get_brand_by_slug("germanysupport")

    upsert_credential(brand.id, CRED_FACEBOOK, {
        "page_id": "1234567890",
        "access_token": "EAABsecrettoken1234567890",
    })
    upsert_content_config(brand.id, "facebook", {
        "cta_text": "Message us",
        "hashtags": ["#expat", "#germany"],
    })

    cred = get_credentials(brand.id, CRED_FACEBOOK)
    content = get_content_config(brand.id, "facebook")

    cred_data = cred.as_dict()
    content_data = content.as_dict()

    assert cred_data["page_id"] == "1234567890"
    assert content_data["cta_text"] == "Message us"

    masked = _mask_token(cred_data["access_token"])
    assert "secrettoken" not in masked
    print(f"  page_id={cred_data['page_id']} cta={content_data['cta_text']} token={masked}  PASS")


def test_missing_credential_handled_gracefully():
    print("=== Test: brand with no facebook credential yet doesn't crash ===")
    cred = get_credentials(brand_id=999, credential_type=CRED_FACEBOOK)
    assert cred is None
    cred_data = cred.as_dict() if cred else {}
    assert cred_data == {}
    assert _mask_token(cred_data.get("access_token")) == "(not set)"
    print("  PASS")


if __name__ == "__main__":
    test_mask_token_short()
    test_mask_token_real_length()
    test_merge_credentials_and_content()
    test_missing_credential_handled_gracefully()
    print("\nAll facebook view logic tests passed.")
