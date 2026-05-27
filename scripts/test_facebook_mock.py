#!/usr/bin/env python3
# scripts/test_facebook_mock.py
import sys
sys.path.insert(0, "/app")

import os

# Setup mock targets
os.environ["PUBLISH_MODE"]       = "mock"
os.environ["STORE_DB_PATH"]      = "/tmp/test_cp_mock.db"

# Remove stale test database before startup
_store_db_path = os.environ["STORE_DB_PATH"]
if os.path.exists(_store_db_path):
    os.remove(_store_db_path)

# Define mock targets
os.environ["SOCIAL_TARGETS"] = "test_facebook_main"
os.environ["SOCIAL__TEST_FACEBOOK_MAIN__PLATFORM"] = "facebook"
os.environ["SOCIAL__TEST_FACEBOOK_MAIN__ENABLED"] = "true"
os.environ["SOCIAL__TEST_FACEBOOK_MAIN__PAGE_ID"] = "mock_page_123"
os.environ["SOCIAL__TEST_FACEBOOK_MAIN__ACCESS_TOKEN"] = "mock_token_xyz"

from shared.logging import configure_logging, get_logger
from shared.store import init_db
from shared.social import publish_post

configure_logging()
logger = get_logger("test_facebook_mock")


def test_mock_publishes():
    print("\n=== Test: Facebook mock publishes ===")
    init_db()
    summary = publish_post(
        content={"title": "Test", "text": "Mock test post.", "image_url": None},
        targets=["test_facebook_main"],
        module_name="test",
    )
    assert summary.any_succeeded, "Expected mock success"
    result = summary.results[0]
    assert result.external_post_id.startswith("fb_mock_"), \
        f"Expected mock ID, got: {result.external_post_id}"
    print(f"  post_id={result.external_post_id}  PASS")


def test_duplicate_skipped():
    print("\n=== Test: Duplicate detection in mock mode ===")
    init_db()
    content = {"title": "T", "text": "Unique mock text for dedup test.", "image_url": None}

    s1 = publish_post(content=content, targets=["test_facebook_main"], module_name="test")
    assert s1.results[0].success

    s2 = publish_post(content=content, targets=["test_facebook_main"], module_name="test")
    assert s2.results[0].metadata.get("duplicate") is True, \
        "Second run should be flagged as duplicate"
    print("  Duplicate correctly skipped  PASS")


def test_disabled_mode():
    print("\n=== Test: Disabled mode produces no results ===")
    os.environ["PUBLISH_MODE"] = "disabled"
    summary = publish_post(
        content={"title": "x", "text": "y", "image_url": None},
        targets=["test_facebook_main"],
        module_name="test",
    )
    assert len(summary.results) == 0
    print("  No results in disabled mode  PASS")
    os.environ["PUBLISH_MODE"] = "mock"


def test_multi_target():
    print("\n=== Test: Publish to multiple targets ===")
    os.environ["SOCIAL_TARGETS"] = "test_facebook_main,test_facebook_brand2"
    os.environ["SOCIAL__TEST_FACEBOOK_BRAND2__PLATFORM"] = "facebook"
    os.environ["SOCIAL__TEST_FACEBOOK_BRAND2__ENABLED"] = "true"
    os.environ["SOCIAL__TEST_FACEBOOK_BRAND2__PAGE_ID"] = "mock_page_456"
    os.environ["SOCIAL__TEST_FACEBOOK_BRAND2__ACCESS_TOKEN"] = "mock_token_abc"

    init_db()
    summary = publish_post(
        content={"title": "T", "text": "Multi-target test.", "image_url": None},
        targets=["test_facebook_main", "test_facebook_brand2"],
        module_name="test",
    )
    assert len(summary.results) == 2, f"Expected 2 results, got {len(summary.results)}"
    assert all(r.success for r in summary.results), "All targets should succeed"
    print(f"  Successfully published to {len(summary.results)} targets  PASS")


if __name__ == "__main__":
    test_mock_publishes()
    test_duplicate_skipped()
    test_disabled_mode()
    test_multi_target()
    print("\nAll mock tests passed.")
