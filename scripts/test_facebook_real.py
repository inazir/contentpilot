#!/usr/bin/env python3
# scripts/test_facebook_real.py
"""
Publishes a real test post to your Facebook Page using a named target.
Requires FACEBOOK_PAGE_ID and FACEBOOK_PAGE_ACCESS_TOKEN to be set in .env.

Run only when you want to verify real API connectivity.
"""
import sys
sys.path.insert(0, "/app")

import os
os.environ["PUBLISH_MODE"]     = "real"
os.environ["STORE_DB_PATH"]    = "/tmp/test_cp_real.db"

from shared.logging import configure_logging, get_logger
from shared.store import init_db
from shared.social import publish_post

configure_logging()
logger = get_logger("test_facebook_real")


def test_real_publish():
    print("\n=== Test: Real Facebook publish ===")

    page_id = os.getenv("FACEBOOK_PAGE_ID", "").strip()
    token   = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "").strip()

    if not page_id or not token:
        print("SKIP: FACEBOOK_PAGE_ID or FACEBOOK_PAGE_ACCESS_TOKEN not set in .env")
        return

    # Setup target from env credentials
    os.environ["SOCIAL_TARGETS"] = "gs_facebook_real_test"
    os.environ["SOCIAL__GS_FACEBOOK_REAL_TEST__PLATFORM"] = "facebook"
    os.environ["SOCIAL__GS_FACEBOOK_REAL_TEST__ENABLED"] = "true"
    os.environ["SOCIAL__GS_FACEBOOK_REAL_TEST__PAGE_ID"] = page_id
    os.environ["SOCIAL__GS_FACEBOOK_REAL_TEST__ACCESS_TOKEN"] = token

    init_db()
    summary = publish_post(
        content={
            "title": "ContentPilot test",
            "text":  "✅ ContentPilot Phase 6 multi-target real publishing test. "
                     "This post was published automatically.",
            "image_url": None,
        },
        targets=["gs_facebook_real_test"],
        module_name="test_real",
    )

    result = summary.results[0]
    print(f"  success={result.success}")
    print(f"  post_id={result.external_post_id}")
    print(f"  error={result.error_message}")

    assert result.success, f"Real publish failed: {result.error_message}"
    assert result.external_post_id, "Expected a real post ID"
    print("  PASS")


if __name__ == "__main__":
    test_real_publish()
