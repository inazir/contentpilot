#!/usr/bin/env python3
# scripts/test_phase12a_social_images.py
"""
Phase 12A — Social image publishing tests.

Covers:
- Image selection from asset bundle
- Facebook image publish path
- Facebook fallback to text on image failure
- Text-only path when no image available
- Mock mode with image

No network calls. All mocked.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_module_path = ROOT / "module"
if not _module_path.exists():
    _module_path = ROOT / "modules" / "daily_news"
sys.path.insert(0, str(_module_path))


def _minimal_jpeg() -> bytes:
    return (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t"
        b"\xff\xd9"
    )


# ---------------------------------------------------------------------------
# Test: image selection
# ---------------------------------------------------------------------------

def test_select_social_image_prefers_landscape():
    print("\n=== Test: Image selection prefers facebook_landscape ===")
    from runner import _select_social_image
    from shared.content.models import AssetBundle, AssetFile, AssetStorageResult

    with tempfile.TemporaryDirectory() as tmpdir:
        storage_dir = Path(tmpdir)
        bundle = AssetBundle(
            article_slug="test", title="T", summary="S",
            keywords=[], storage_dir=storage_dir,
        )

        for key, filename in [
            ("featured",           "featured.jpg"),
            ("facebook_landscape", "facebook_landscape.jpg"),
            ("facebook_square",    "facebook_square.jpg"),
        ]:
            p = storage_dir / filename
            p.write_bytes(_minimal_jpeg())
            bundle.assets[key] = AssetFile(
                key=key, path=p, mime_type="image/jpeg", size_bytes=len(_minimal_jpeg())
            )

        result = MagicMock()
        result.success = True
        result.bundle = bundle

        image_bytes, filename = _select_social_image(result)

        assert image_bytes is not None
        assert filename == "facebook_landscape.jpg"

    print(f"  selected={filename}  PASS")


def test_select_social_image_fallback_to_featured():
    print("\n=== Test: Image selection falls back to featured ===")
    from runner import _select_social_image
    from shared.content.models import AssetBundle, AssetFile, AssetStorageResult

    with tempfile.TemporaryDirectory() as tmpdir:
        storage_dir = Path(tmpdir)
        bundle = AssetBundle(
            article_slug="test", title="T", summary="S",
            keywords=[], storage_dir=storage_dir,
        )
        p = storage_dir / "featured.jpg"
        p.write_bytes(_minimal_jpeg())
        bundle.assets["featured"] = AssetFile(
            key="featured", path=p, mime_type="image/jpeg", size_bytes=len(_minimal_jpeg())
        )

        result = MagicMock()
        result.success = True
        result.bundle = bundle

        image_bytes, filename = _select_social_image(result)

        assert image_bytes is not None
        assert filename == "featured.jpg"

    print(f"  selected={filename}  PASS")


def test_select_social_image_no_bundle():
    print("\n=== Test: Image selection returns None when no bundle ===")
    from runner import _select_social_image

    image_bytes, filename = _select_social_image(None)
    assert image_bytes is None
    assert filename == ""
    print("  PASS")


# ---------------------------------------------------------------------------
# Test: Facebook adapter
# ---------------------------------------------------------------------------

def test_facebook_mock_with_image():
    print("\n=== Test: Facebook mock publish includes image flag ===")
    from shared.social.facebook import publish_post
    from shared.config import SocialTarget

    target = SocialTarget(
        key="test_fb", platform="facebook", enabled=True,
        page_id="123", access_token="tok", name="Test",
    )

    result = publish_post(
        content="Test post with image",
        target=target,
        mode="mock",
        image_bytes=_minimal_jpeg(),
    )

    assert result.success
    assert result.metadata.get("has_image") is True
    print(f"  has_image={result.metadata['has_image']}  PASS")


def test_facebook_mock_without_image():
    print("\n=== Test: Facebook mock publish text-only ===")
    from shared.social.facebook import publish_post
    from shared.config import SocialTarget

    target = SocialTarget(
        key="test_fb", platform="facebook", enabled=True,
        page_id="123", access_token="tok", name="Test",
    )

    result = publish_post(
        content="Text only post",
        target=target,
        mode="mock",
        image_bytes=None,
    )

    assert result.success
    assert result.metadata.get("has_image") is False
    print("  PASS")


def test_facebook_real_image_publish_success():
    print("\n=== Test: Facebook real image publish via /photos ===")
    from shared.social.facebook import publish_post
    from shared.config import SocialTarget

    target = SocialTarget(
        key="test_fb", platform="facebook", enabled=True,
        page_id="123", access_token="real_token", name="Test",
    )

    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.ok = True
    fake_response.json.return_value = {"post_id": "123_456", "id": "789"}

    with patch("requests.post", return_value=fake_response):
        result = publish_post(
            content="Caption here",
            target=target,
            mode="real",
            image_bytes=_minimal_jpeg(),
        )

    assert result.success
    assert result.metadata.get("has_image") is True
    print(f"  post_id={result.external_post_id}  PASS")


def test_facebook_real_image_fallback_to_text_on_server_error():
    print("\n=== Test: Facebook image publish falls back to text on 500 ===")
    from shared.social.facebook import publish_post
    from shared.config import SocialTarget

    target = SocialTarget(
        key="test_fb", platform="facebook", enabled=True,
        page_id="123", access_token="real_token", name="Test",
    )

    fail_response = MagicMock()
    fail_response.status_code = 500
    fail_response.ok = False

    text_response = MagicMock()
    text_response.status_code = 200
    text_response.ok = True
    text_response.json.return_value = {"id": "text_post_id"}

    call_count = {"n": 0}
    def side_effect(*args, **kwargs):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return fail_response
        return text_response

    with patch("requests.post", side_effect=side_effect):
        result = publish_post(
            content="Caption",
            target=target,
            mode="real",
            image_bytes=_minimal_jpeg(),
        )

    assert result.success
    assert result.metadata.get("has_image") is False  # fell back to text
    print(f"  fell_back_to_text=True | post_id={result.external_post_id}  PASS")


def test_publisher_passes_image_bytes():
    print("\n=== Test: publisher.publish_post passes image_bytes to adapter ===")
    import os
    os.environ["PUBLISH_MODE"] = "mock"
    os.environ["SOCIAL_TARGETS"] = "test_fb_img"
    os.environ["SOCIAL__TEST_FB_IMG__PLATFORM"] = "facebook"
    os.environ["SOCIAL__TEST_FB_IMG__ENABLED"] = "true"
    os.environ["SOCIAL__TEST_FB_IMG__PAGE_ID"] = "mock_page"
    os.environ["SOCIAL__TEST_FB_IMG__ACCESS_TOKEN"] = "mock_token"

    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["STORE_DB_PATH"] = str(Path(tmpdir) / "test.db")
        from shared.store import init_db
        from shared.social import publish_post
        init_db()

        summary = publish_post(
            content={
                "title":       "Test",
                "text":        "Test post with image bytes",
                "image_url":   None,
                "image_bytes": _minimal_jpeg(),
                "image_name":  "facebook_landscape.jpg",
            },
            targets=["test_fb_img"],
            module_name="test",
        )

    assert summary.any_succeeded
    result = summary.results[0]
    assert result.metadata.get("has_image") is True
    print(f"  has_image={result.metadata['has_image']}  PASS")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("ContentPilot Phase 12A — Social Image Publishing Tests")
    print("=" * 55)

    test_select_social_image_prefers_landscape()
    test_select_social_image_fallback_to_featured()
    test_select_social_image_no_bundle()
    test_facebook_mock_with_image()
    test_facebook_mock_without_image()
    test_facebook_real_image_publish_success()
    test_facebook_real_image_fallback_to_text_on_server_error()
    test_publisher_passes_image_bytes()

    print("\n" + "=" * 55)
    print("All Phase 12A tests passed.")
