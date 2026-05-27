#!/usr/bin/env python3
# scripts/test_facebook_failure.py
"""
Simulates failure conditions without needing real credentials.
"""
import sys
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ["PUBLISH_MODE"] = "real"
os.environ["STORE_DB_PATH"] = str(ROOT / "data" / "db" / "contentpilot_fail_test.db")

# Setup targets with bad credentials
os.environ["SOCIAL_TARGETS"] = "test_facebook_bad"
os.environ["SOCIAL__TEST_FACEBOOK_BAD__PLATFORM"] = "facebook"
os.environ["SOCIAL__TEST_FACEBOOK_BAD__ENABLED"] = "true"
os.environ["SOCIAL__TEST_FACEBOOK_BAD__PAGE_ID"] = "000000000"
os.environ["SOCIAL__TEST_FACEBOOK_BAD__ACCESS_TOKEN"] = "bad_token_test"

from shared.logging import configure_logging, get_logger
from shared.store import init_db
from shared.social import publish_post

configure_logging()
logger = get_logger("test_facebook_failure")


def test_invalid_token_does_not_crash():
    print("\n=== Test: Invalid token — no crash, typed error ===")
    init_db()

    summary = publish_post(
        content={"title": "T", "text": "Failure test post.", "image_url": None},
        targets=["test_facebook_bad"],
        module_name="test_failure",
    )

    result = summary.results[0]
    assert not result.success, "Expected failure with bad credentials"
    assert result.error_message, "Expected an error message"
    assert not result.retryable, "Auth errors should not be retryable"
    print(f"  error_message={result.error_message!r}")
    print(f"  retryable={result.retryable}  PASS")


def test_runner_continues_after_target_failure():
    print("\n=== Test: Runner continues when one target fails ===")
    os.environ["PUBLISH_MODE"] = "mock"
    os.environ["SOCIAL_TARGETS"] = "test_facebook_bad,test_instagram_good"
    os.environ["SOCIAL__TEST_INSTAGRAM_GOOD__PLATFORM"] = "instagram"
    os.environ["SOCIAL__TEST_INSTAGRAM_GOOD__ENABLED"] = "true"
    os.environ["SOCIAL__TEST_INSTAGRAM_GOOD__PAGE_ID"] = "mock_ig_123"
    os.environ["SOCIAL__TEST_INSTAGRAM_GOOD__ACCESS_TOKEN"] = "mock_ig_token"

    init_db()
    summary = publish_post(
        content={"title": "T", "text": "Partial failure test.", "image_url": None},
        targets=["test_facebook_bad", "test_instagram_good"],
        module_name="test_failure",
    )

    print(f"  results={[str(r) for r in summary.results]}")
    ig_result = next((r for r in summary.results if r.platform == "instagram"), None)
    assert ig_result and ig_result.success, \
        "Instagram should succeed even if Facebook fails"
    print("  Instagram succeeded despite Facebook failure  PASS")


if __name__ == "__main__":
    test_invalid_token_does_not_crash()
    test_runner_continues_after_target_failure()
    print("\nAll failure tests passed.")
