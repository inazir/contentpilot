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
        platforms=["facebook", "instagram"],
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

    summary = publish_post(
        content=content,
        platforms=["facebook", "unknown_platform"],
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
        platforms=["facebook"],
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
