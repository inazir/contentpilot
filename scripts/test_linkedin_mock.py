#!/usr/bin/env python3
# scripts/test_linkedin_mock.py
"""
Validates LinkedIn mock publishing and WordPress mock publishing.
No credentials required — runs entirely in mock mode.
"""
import sys
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ["PUBLISH_MODE"] = "mock"
os.environ["WP_POST_STATUS"] = "draft"

tmpdir = tempfile.mkdtemp(prefix="cp_linkedin_test_")
os.environ["STORE_DB_PATH"] = str(Path(tmpdir) / "contentpilot_test.db")

os.environ["SOCIAL_TARGETS"] = "test_linkedin_main,test_xing_main"
os.environ["SOCIAL__TEST_LINKEDIN_MAIN__PLATFORM"] = "linkedin"
os.environ["SOCIAL__TEST_LINKEDIN_MAIN__ENABLED"] = "true"
os.environ["SOCIAL__TEST_LINKEDIN_MAIN__PAGE_ID"] = "12345678"
os.environ["SOCIAL__TEST_LINKEDIN_MAIN__ACCESS_TOKEN"] = "mock_li_token"
os.environ["SOCIAL__TEST_LINKEDIN_MAIN__NAME"] = "Test LinkedIn Page"

os.environ["SOCIAL__TEST_XING_MAIN__PLATFORM"] = "xing"
os.environ["SOCIAL__TEST_XING_MAIN__ENABLED"] = "true"
os.environ["SOCIAL__TEST_XING_MAIN__PAGE_ID"] = "placeholder"
os.environ["SOCIAL__TEST_XING_MAIN__ACCESS_TOKEN"] = "placeholder"

from shared.logging import configure_logging, get_logger
from shared.store import init_db
from shared.social import publish_post

configure_logging()
logger = get_logger("test_linkedin_mock")


def test_linkedin_mock_publish() -> None:
    print("\n=== Test: LinkedIn mock publish ===")
    init_db()

    summary = publish_post(
        content={
            "title": "ContentPilot LinkedIn Test",
            "text": "Testing LinkedIn mock publishing via ContentPilot automation platform.",
            "image_url": None,
        },
        targets=["test_linkedin_main"],
        module_name="test",
    )

    assert summary.any_succeeded, "Expected LinkedIn mock success"
    result = summary.results[0]
    assert result.platform == "linkedin"
    assert result.external_post_id.startswith("urn:li:share:li_mock_"), \
        f"Expected LinkedIn URN format, got: {result.external_post_id}"
    print(f"  post_urn={result.external_post_id}  PASS")


def test_xing_mock_publish() -> None:
    print("\n=== Test: Xing mock publish (mock-only platform) ===")
    init_db()

    summary = publish_post(
        content={
            "title": "ContentPilot Xing Test",
            "text": "Testing Xing mock publishing.",
            "image_url": None,
        },
        targets=["test_xing_main"],
        module_name="test",
    )

    assert summary.any_succeeded, "Expected Xing mock success"
    result = summary.results[0]
    assert result.platform == "xing"
    assert result.external_post_id.startswith("xing_mock_"), \
        f"Expected xing mock ID, got: {result.external_post_id}"
    assert result.metadata.get("note"), "Expected deprecation note in metadata"
    print(f"  post_id={result.external_post_id}  PASS")


def test_xing_real_raises_not_implemented() -> None:
    print("\n=== Test: Xing real mode raises NotImplementedError ===")

    from shared.social.xing import publish_post as xing_publish
    from shared.config import SocialTarget

    target = SocialTarget(
        key="test_xing",
        platform="xing",
        enabled=True,
        page_id="placeholder",
        access_token="placeholder",
    )

    try:
        xing_publish(content="test", target=target, mode="real")
        assert False, "Should have raised NotImplementedError"
    except NotImplementedError as exc:
        print(f"  Correctly raised NotImplementedError: {str(exc)[:80]}...  PASS")


def test_multi_platform_publish() -> None:
    print("\n=== Test: Multi-platform publish (Facebook + LinkedIn) ===")

    os.environ["SOCIAL_TARGETS"] = "test_linkedin_main,test_facebook_main"
    os.environ["SOCIAL__TEST_FACEBOOK_MAIN__PLATFORM"] = "facebook"
    os.environ["SOCIAL__TEST_FACEBOOK_MAIN__ENABLED"] = "true"
    os.environ["SOCIAL__TEST_FACEBOOK_MAIN__PAGE_ID"] = "mock_page_123"
    os.environ["SOCIAL__TEST_FACEBOOK_MAIN__ACCESS_TOKEN"] = "mock_fb_token"

    init_db()
    summary = publish_post(
        content={
            "title": "Multi-platform test",
            "text": "ContentPilot publishing to LinkedIn and Facebook simultaneously.",
            "image_url": None,
        },
        targets=["test_linkedin_main", "test_facebook_main"],
        module_name="test",
    )

    assert len(summary.results) == 2, f"Expected 2 results, got {len(summary.results)}"
    assert all(r.success for r in summary.results), \
        f"All targets should succeed: {[str(r) for r in summary.results]}"

    platforms = {r.platform for r in summary.results}
    assert "linkedin" in platforms
    assert "facebook" in platforms
    print(f"  Published to: {platforms}  PASS")


def test_wordpress_mock() -> None:
    print("\n=== Test: WordPress mock publish (draft mode) ===")

    os.environ["WP_URL"] = "https://example.com"
    os.environ["WP_USERNAME"] = "mock_user"
    os.environ["WP_APP_PASSWORD"] = "mock_password"
    os.environ["WP_POST_STATUS"] = "draft"

    from shared.wordpress import publish_post as wp_publish

    result = wp_publish(
        title="ContentPilot Test Post",
        content="<p>This is a test post from ContentPilot.</p>",
        excerpt="A test excerpt.",
        module_name="test",
        target_key="wordpress_main",
        mode="mock",
    )

    assert result.success, f"Expected WP mock success, got: {result.error_message}"
    assert result.wordpress_post_id is not None
    assert result.status == "draft", f"Expected draft status, got: {result.status}"
    assert result.url is not None
    print(f"  post_id={result.wordpress_post_id} status={result.status} url={result.url}  PASS")


if __name__ == "__main__":
    test_linkedin_mock_publish()
    test_xing_mock_publish()
    test_xing_real_raises_not_implemented()
    test_multi_platform_publish()
    test_wordpress_mock()
    print("\nAll LinkedIn/Xing/WordPress mock tests passed.")
