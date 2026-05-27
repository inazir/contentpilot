#!/usr/bin/env python3
# scripts/test_duplicate_detection.py
"""
Lightweight duplicate detection tests for ContentPilot.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

os.environ.setdefault("PUBLISH_MODE", "mock")
os.environ.setdefault("STORE_DB_PATH", os.path.join(ROOT, "data", "db", "contentpilot_test.db"))
os.environ.setdefault("SOCIAL_TARGETS", "test_facebook_main")
os.environ.setdefault("SOCIAL__TEST_FACEBOOK_MAIN__PLATFORM", "facebook")
os.environ.setdefault("SOCIAL__TEST_FACEBOOK_MAIN__ENABLED", "true")
os.environ.setdefault("SOCIAL__TEST_FACEBOOK_MAIN__PAGE_ID", "mock_page_123")
os.environ.setdefault("SOCIAL__TEST_FACEBOOK_MAIN__ACCESS_TOKEN", "mock_token_xyz")

_store_db_path = os.environ["STORE_DB_PATH"]
if os.path.exists(_store_db_path):
    os.remove(_store_db_path)

from shared.logging import configure_logging, get_logger
from shared.store import (
    init_db,
    compute_content_hash,
    already_published,
    record_publish,
)
from shared.social import publish_post

configure_logging()
logger = get_logger("test_duplicates")


def test_hash_consistency() -> None:
    print("=== Test: Hash Consistency ===")
    text = "Hello from ContentPilot"
    h1 = compute_content_hash(text)
    h2 = compute_content_hash(text)
    assert h1 == h2, "Same text must produce same hash"
    assert len(h1) == 64, "SHA-256 should be 64 hex chars"
    print(f"Hash: {h1[:16]}... PASS\n")


def test_duplicate_prevention() -> None:
    print("=== Test: Duplicate Prevention ===")
    init_db()

    content = "Duplicate test post content"
    content_hash = compute_content_hash(content)

    assert not already_published(content_hash, "test_facebook_main")

    record_publish(
        content_hash=content_hash,
        target_key="test_facebook_main",
        platform="facebook",
        module_name="test",
        status="success",
        external_post_id="fb_test_001",
    )

    assert already_published(content_hash, "test_facebook_main")
    assert not already_published(content_hash, "test_instagram_main")
    print("PASS\n")


def test_full_pipeline_dedup() -> None:
    print("=== Test: Full Pipeline Duplicate Skip ===")
    init_db()

    content = {
        "title": "Dedup test",
        "text": "This specific text was already published.",
        "image_url": None,
    }

    s1 = publish_post(content=content, targets=["test_facebook_main"], module_name="test")
    assert s1.results[0].success

    s2 = publish_post(content=content, targets=["test_facebook_main"], module_name="test")
    assert s2.results[0].success
    assert s2.results[0].metadata.get("duplicate") is True
    print("PASS\n")


if __name__ == "__main__":
    test_hash_consistency()
    test_duplicate_prevention()
    test_full_pipeline_dedup()
    print("All duplicate detection tests passed.")
