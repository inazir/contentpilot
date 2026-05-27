#!/usr/bin/env python3
# scripts/test_publish_pipeline.py
"""
Lightweight publish pipeline tests for ContentPilot.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

os.environ.setdefault("PUBLISH_MODE", "mock")
os.environ.setdefault("STORE_DB_PATH", os.path.join(ROOT, "data", "db", "contentpilot_test.db"))
os.environ.setdefault("SOCIAL_TARGETS", "test_facebook_main,test_instagram_main")
os.environ.setdefault("SOCIAL__TEST_FACEBOOK_MAIN__PLATFORM", "facebook")
os.environ.setdefault("SOCIAL__TEST_FACEBOOK_MAIN__ENABLED", "true")
os.environ.setdefault("SOCIAL__TEST_FACEBOOK_MAIN__PAGE_ID", "mock_page_123")
os.environ.setdefault("SOCIAL__TEST_FACEBOOK_MAIN__ACCESS_TOKEN", "mock_token_xyz")
os.environ.setdefault("SOCIAL__TEST_INSTAGRAM_MAIN__PLATFORM", "instagram")
os.environ.setdefault("SOCIAL__TEST_INSTAGRAM_MAIN__ENABLED", "true")
os.environ.setdefault("SOCIAL__TEST_INSTAGRAM_MAIN__PAGE_ID", "mock_ig_123")
os.environ.setdefault("SOCIAL__TEST_INSTAGRAM_MAIN__ACCESS_TOKEN", "mock_ig_token")

_store_db_path = os.environ["STORE_DB_PATH"]
if os.path.exists(_store_db_path):
    os.remove(_store_db_path)

from shared.logging import configure_logging, get_logger
from shared.store import init_db
from shared.social import publish_post

configure_logging()
logger = get_logger("test_publish_pipeline")


def test_mock_publish() -> None:
    print("=== Test: Mock Publish ===")
    init_db()

    content = {
        "title": "Test post",
        "text": "This is a test post from ContentPilot pipeline test.",
        "image_url": None,
    }

    summary = publish_post(
        content=content,
        targets=["test_facebook_main", "test_instagram_main"],
        module_name="test",
    )

    print(str(summary))
    for result in summary.results:
        print(" ", str(result))

    assert summary.any_succeeded, "Expected at least one success"
    print("PASS\n")


def test_partial_failure() -> None:
    print("=== Test: Partial Failure Handling ===")
    init_db()

    content = {
        "title": "Test",
        "text": "Testing partial failure handling.",
        "image_url": None,
    }

    os.environ["SOCIAL_TARGETS"] = "test_facebook_main,test_unknown_platform"
    os.environ["SOCIAL__TEST_UNKNOWN_PLATFORM__PLATFORM"] = "unknown_platform"
    os.environ["SOCIAL__TEST_UNKNOWN_PLATFORM__ENABLED"] = "true"
    os.environ["SOCIAL__TEST_UNKNOWN_PLATFORM__PAGE_ID"] = "bad_id"
    os.environ["SOCIAL__TEST_UNKNOWN_PLATFORM__ACCESS_TOKEN"] = "bad_token"

    summary = publish_post(
        content=content,
        targets=["test_facebook_main", "test_unknown_platform"],
        module_name="test",
    )

    print(str(summary))
    for result in summary.results:
        print(" ", str(result))

    fb_result = next(r for r in summary.results if r.platform == "facebook")
    assert fb_result.success, "Facebook should succeed"

    unknown_result = next(r for r in summary.results if r.platform == "unknown_platform")
    assert not unknown_result.success, "Unknown platform should fail"
    print("PASS\n")


def test_disabled_mode() -> None:
    print("=== Test: Disabled Mode ===")
    original_mode = os.environ.get("PUBLISH_MODE")
    os.environ["PUBLISH_MODE"] = "disabled"

    init_db()
    summary = publish_post(
        content={"title": "x", "text": "y", "image_url": None},
        targets=["test_facebook_main"],
        module_name="test",
    )

    assert len(summary.results) == 0, "Disabled mode should produce no results"
    print("PASS\n")

    if original_mode is not None:
        os.environ["PUBLISH_MODE"] = original_mode
    else:
        del os.environ["PUBLISH_MODE"]


if __name__ == "__main__":
    test_mock_publish()
    test_partial_failure()
    test_disabled_mode()
    print("All pipeline tests passed.")
