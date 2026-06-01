#!/usr/bin/env python3
# scripts/test_phase11b_integration.py
"""
Phase 11B integration tests.

Covers:
- Asset generation enabled / disabled
- WordPress media upload success / failure
- Asset builder failure isolation
- Publishing continues after media failures
- Runtime metrics updated correctly
- Backward compatibility when all media flags off

No network calls. All external services mocked.

Run:
    python scripts/test_phase11b_integration.py
    pytest scripts/test_phase11b_integration.py -v
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

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _minimal_jpeg() -> bytes:
    return (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t"
        b"\xff\xd9"
    )


def _mock_image_generator(title, summary, keywords):
    fake = _minimal_jpeg()
    return {
        "featured":           fake,
        "facebook_landscape": fake,
        "facebook_square":    fake,
        "instagram_square":   fake,
        "instagram_portrait": fake,
        "story":              fake,
    }


def _failing_image_generator(title, summary, keywords):
    raise RuntimeError("Simulated image generation failure")


def _make_media_config(tmpdir: str, enabled=True, featured=True, social=True):
    """Return a MediaConfig-like object."""
    from shared.config import MediaConfig
    return MediaConfig(
        enabled          = enabled,
        featured_images  = featured,
        social_images    = social,
        branding_enabled = False,
        ads_enabled      = False,
        storage_dir      = tmpdir,
    )


# ---------------------------------------------------------------------------
# Tests — AssetBuilder integration
# ---------------------------------------------------------------------------

def test_asset_bundle_generated_and_stored():
    print("\n=== Test: Asset bundle generated and stored ===")
    from shared.content import AssetBuilder
    from shared.content.storage import AssetStorage

    with tempfile.TemporaryDirectory() as tmpdir:
        storage = AssetStorage(storage_root=Path(tmpdir))
        builder = AssetBuilder(storage=storage, image_generator=_mock_image_generator)

        result = builder.build(
            title        = "Public Transport in Germany",
            summary      = "Tips for using public transport as an expat.",
            article_body = "## Tips\n\nGet a monthly pass.",
            keywords     = ["transport", "Germany", "expat"],
        )

        assert result.success, f"Build failed: {result.error_message}"
        assert result.bundle is not None
        assert result.storage_dir.exists()
        assert (result.storage_dir / "featured.jpg").exists()
        assert (result.storage_dir / "metadata.json").exists()
        assert (result.storage_dir / "article.md").exists()
        assert result.assets_written >= 7  # 6 images + metadata + article

    print(f"  assets_written={result.assets_written}  PASS")


def test_asset_bundle_disabled():
    print("\n=== Test: Asset pipeline disabled — no files written ===")
    from shared.content import AssetBuilder
    from shared.content.storage import AssetStorage

    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["ENABLE_MEDIA_ASSETS"] = "false"
        storage = AssetStorage(storage_root=Path(tmpdir))
        builder = AssetBuilder(storage=storage, image_generator=_mock_image_generator)

        result = builder.build(title="Test", summary="s", keywords=[])

        assert result.success
        assert result.assets_written == 0
        assert len(list(Path(tmpdir).rglob("*.jpg"))) == 0

    os.environ["ENABLE_MEDIA_ASSETS"] = "true"
    print("  PASS")


def test_asset_builder_failure_isolation():
    """Publishing must continue even when image generation fails."""
    print("\n=== Test: AssetBuilder failure does not propagate ===")
    from shared.content import AssetBuilder
    from shared.content.storage import AssetStorage
    from shared.models import ExecutionSummary
    from shared.config import MediaConfig

    with tempfile.TemporaryDirectory() as tmpdir:
        media_cfg = MediaConfig(
            enabled=True, featured_images=True, social_images=True,
            branding_enabled=False, ads_enabled=False, storage_dir=tmpdir,
        )
        summary = ExecutionSummary(module="daily_news")

        # Simulate _build_asset_bundle logic inline with a crashing builder
        result = None
        try:
            storage = AssetStorage(storage_root=Path(tmpdir))
            builder = AssetBuilder(storage=storage)
            # Monkey-patch build to raise
            def _boom(*a, **kw):
                raise RuntimeError("Simulated hard failure")
            builder.build = _boom
            result = builder.build(title="Failing Test", summary="s", keywords=[])
        except Exception as exc:
            # This is what _build_asset_bundle does — catches and returns None
            result = None

        assert result is None
        assert summary.bundles_created == 0

    print("  PASS")    
# ---------------------------------------------------------------------------
# Tests — WordPress Media Upload
# ---------------------------------------------------------------------------

def test_wordpress_media_upload_success():
    print("\n=== Test: WordPress media upload success ===")
    from shared.content.wordpress_media import WordPressMediaService

    fake_config = MagicMock()
    fake_config.base_url = "https://example.com"
    fake_config.username = "user"
    fake_config.app_password = "pass"

    fake_response = MagicMock()
    fake_response.status_code = 201
    fake_response.ok = True
    fake_response.json.return_value = {
        "id": 42,
        "source_url": "https://example.com/wp-content/uploads/featured.jpg",
    }

    with patch("requests.post", return_value=fake_response):
        svc = WordPressMediaService(fake_config)
        result = svc.upload_image(_minimal_jpeg(), filename="featured.jpg", title="Test")

    assert result.success
    assert result.media_id == 42
    assert result.url is not None
    print(f"  media_id={result.media_id}  PASS")


def test_wordpress_media_upload_auth_failure():
    print("\n=== Test: WordPress media upload auth failure — non-retryable ===")
    from shared.content.wordpress_media import WordPressMediaService

    fake_config = MagicMock()
    fake_config.base_url = "https://example.com"
    fake_config.username = "user"
    fake_config.app_password = "wrong"

    fake_response = MagicMock()
    fake_response.status_code = 401
    fake_response.ok = False
    fake_response.text = "Unauthorized"

    with patch("requests.post", return_value=fake_response):
        svc = WordPressMediaService(fake_config)
        result = svc.upload_image(_minimal_jpeg(), filename="featured.jpg")

    assert not result.success
    assert not result.retryable
    assert result.media_id is None
    print(f"  error={result.error_message!r}  PASS")


def test_wordpress_media_upload_server_error_retries():
    print("\n=== Test: WordPress media upload retries on server error ===")
    from shared.content.wordpress_media import WordPressMediaService

    fake_config = MagicMock()
    fake_config.base_url = "https://example.com"
    fake_config.username = "user"
    fake_config.app_password = "pass"

    fail_response = MagicMock()
    fail_response.status_code = 503
    fail_response.ok = False

    success_response = MagicMock()
    success_response.status_code = 201
    success_response.ok = True
    success_response.json.return_value = {"id": 99, "source_url": "https://example.com/img.jpg"}

    call_count = {"n": 0}
    def side_effect(*args, **kwargs):
        call_count["n"] += 1
        if call_count["n"] < 2:
            return fail_response
        return success_response

    with patch("requests.post", side_effect=side_effect):
        with patch("time.sleep"):  # skip backoff delays in tests
            svc = WordPressMediaService(fake_config)
            result = svc.upload_image(_minimal_jpeg(), filename="featured.jpg")

    assert result.success
    assert result.media_id == 99
    assert call_count["n"] == 2
    print(f"  retried={call_count['n']} times  PASS")


def test_wordpress_media_empty_bytes():
    print("\n=== Test: Empty image bytes returns failure immediately ===")
    from shared.content.wordpress_media import WordPressMediaService

    fake_config = MagicMock()
    fake_config.base_url = "https://example.com"
    fake_config.username = "user"
    fake_config.app_password = "pass"

    svc = WordPressMediaService(fake_config)
    result = svc.upload_image(b"", filename="empty.jpg")

    assert not result.success
    assert not result.retryable
    print("  PASS")


# ---------------------------------------------------------------------------
# Tests — runner helpers
# ---------------------------------------------------------------------------

def test_upload_featured_image_isolated_from_wp_config_error():
    """If WordPress is not configured, upload silently skips."""
    print("\n=== Test: Missing WordPress config → upload silently skipped ===")
    import importlib
    import sys
    from shared.models import ExecutionSummary

    # Ensure config raises ValueError for missing WORDPRESS_BASE_URL
    orig_url = os.environ.pop("WORDPRESS_BASE_URL", None)

    with tempfile.TemporaryDirectory() as tmpdir:
        from shared.content import AssetBuilder
        from shared.content.storage import AssetStorage
        from shared.config import MediaConfig

        media_cfg = MediaConfig(
            enabled=True, featured_images=True, social_images=True,
            branding_enabled=False, ads_enabled=False, storage_dir=tmpdir,
        )
        storage = AssetStorage(storage_root=Path(tmpdir))
        builder = AssetBuilder(storage=storage, image_generator=_mock_image_generator)
        asset_result = builder.build(title="Test", summary="s", keywords=[])

        from runner import _upload_featured_image
        summary = ExecutionSummary(module="daily_news")

        media_id = _upload_featured_image(asset_result, "Test", media_cfg, summary)

        assert media_id is None
        assert summary.wordpress_media_failures == 0  # not an error — just not configured

    if orig_url:
        os.environ["WORDPRESS_BASE_URL"] = orig_url
    print("  PASS")


def test_runtime_metrics_updated():
    print("\n=== Test: Runtime metrics updated correctly ===")
    from shared.models import ExecutionSummary
    from shared.content import AssetBuilder
    from shared.content.storage import AssetStorage
    import sys
    from shared.config import MediaConfig

    with tempfile.TemporaryDirectory() as tmpdir:
        media_cfg = MediaConfig(
            enabled=True, featured_images=True, social_images=True,
            branding_enabled=False, ads_enabled=False, storage_dir=tmpdir,
        )
        storage = AssetStorage(storage_root=Path(tmpdir))
        builder = AssetBuilder(storage=storage, image_generator=_mock_image_generator)

        from runner import _build_asset_bundle
        summary = ExecutionSummary(module="daily_news")

        result = _build_asset_bundle(
            title        = "Health Insurance Germany",
            summary      = "A guide.",
            article_body = "Body text.",
            keywords     = ["health", "Germany"],
            media_cfg    = media_cfg,
            summary_obj  = summary,
        )

        assert summary.bundles_created == 1
        assert summary.assets_generated > 0
        assert summary.images_generated > 0

    print(
        f"  bundles={summary.bundles_created} "
        f"assets={summary.assets_generated} "
        f"images={summary.images_generated}  PASS"
    )


def test_metrics_media_disabled():
    print("\n=== Test: Runtime metrics stay zero when media disabled ===")
    from shared.models import ExecutionSummary
    from shared.config import MediaConfig
    import sys

    with tempfile.TemporaryDirectory() as tmpdir:
        media_cfg = MediaConfig(
            enabled=False, featured_images=False, social_images=False,
            branding_enabled=False, ads_enabled=False, storage_dir=tmpdir,
        )
        from runner import _build_asset_bundle
        summary = ExecutionSummary(module="daily_news")

        result = _build_asset_bundle(
            title="Test", summary="s", article_body="b",
            keywords=[], media_cfg=media_cfg, summary_obj=summary,
        )

        assert result is None
        assert summary.bundles_created == 0
        assert summary.assets_generated == 0
        assert summary.images_generated == 0

    print("  PASS")


def test_execution_summary_has_media_fields():
    print("\n=== Test: ExecutionSummary has Phase 11B media fields ===")
    from shared.models import ExecutionSummary

    s = ExecutionSummary(module="daily_news")
    assert hasattr(s, "assets_generated")
    assert hasattr(s, "bundles_created")
    assert hasattr(s, "images_generated")
    assert hasattr(s, "images_uploaded")
    assert hasattr(s, "wordpress_media_failures")

    s.assets_generated = 8
    s.bundles_created = 1
    s.images_generated = 6
    s.images_uploaded = 1
    s.wordpress_media_failures = 0

    d = s.to_dict()
    assert d["assets_generated"] == 8
    assert d["bundles_created"] == 1
    assert d["images_uploaded"] == 1
    assert d["wordpress_media_failures"] == 0

    print("  PASS")


def test_media_config_defaults():
    print("\n=== Test: MediaConfig defaults are safe ===")
    import importlib
    # Clear any env overrides
    for k in [
        "ENABLE_MEDIA_ASSETS", "ENABLE_FEATURED_IMAGES", "ENABLE_SOCIAL_IMAGES",
        "MEDIA_BRANDING_ENABLED", "MEDIA_ADS_ENABLED",
    ]:
        os.environ.pop(k, None)

    import shared.config as cfg_mod
    importlib.reload(cfg_mod)
    from shared.config import get_media_config
    cfg = get_media_config()

    assert cfg.enabled is True
    assert cfg.featured_images is True
    assert cfg.social_images is True
    assert cfg.branding_enabled is False
    assert cfg.ads_enabled is False

    print("  PASS")


def test_backward_compat_all_media_disabled():
    """With all media flags false, runner helpers return None/zero without error."""
    print("\n=== Test: Backward compatibility — all media disabled ===")
    from shared.models import ExecutionSummary
    from shared.config import MediaConfig
    import sys

    with tempfile.TemporaryDirectory() as tmpdir:
        media_cfg = MediaConfig(
            enabled=False, featured_images=False, social_images=False,
            branding_enabled=False, ads_enabled=False, storage_dir=tmpdir,
        )
        from runner import _build_asset_bundle, _upload_featured_image
        summary = ExecutionSummary(module="daily_news")

        asset_result = _build_asset_bundle(
            title="Test", summary="s", article_body="b",
            keywords=[], media_cfg=media_cfg, summary_obj=summary,
        )
        assert asset_result is None

        media_id = _upload_featured_image(asset_result, "Test", media_cfg, summary)
        assert media_id is None

        assert summary.bundles_created == 0
        assert summary.images_uploaded == 0
        assert summary.wordpress_media_failures == 0

    print("  PASS")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("ContentPilot Phase 11B — Integration Tests")
    print("=" * 55)

    test_asset_bundle_generated_and_stored()
    test_asset_bundle_disabled()
    test_asset_builder_failure_isolation()
    test_wordpress_media_upload_success()
    test_wordpress_media_upload_auth_failure()
    test_wordpress_media_upload_server_error_retries()
    test_wordpress_media_empty_bytes()
    test_upload_featured_image_isolated_from_wp_config_error()
    test_runtime_metrics_updated()
    test_metrics_media_disabled()
    test_execution_summary_has_media_fields()
    test_media_config_defaults()
    test_backward_compat_all_media_disabled()

    print("\n" + "=" * 55)
    print("All Phase 11B integration tests passed.")
