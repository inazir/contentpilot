#!/usr/bin/env python3
# scripts/test_content_assets.py
"""
Phase 11A offline tests for the content asset system.

No external API calls. All image generation is mocked.
All storage uses isolated temp directories.

Run:
    python scripts/test_content_assets.py
    pytest scripts/test_content_assets.py -v
"""

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_image(size: int = 256) -> bytes:
    """Return minimal valid JPEG bytes for testing."""
    # Minimal 1x1 white JPEG
    return (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t"
        b"\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a"
        b"\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\x1eB"
        b"\xed\xa3\x93\xff\xd9"
    )


def _mock_image_generator(title: str, summary: str, keywords: list) -> dict:
    """Return fake image bytes for all variants."""
    fake = _make_mock_image()
    return {
        "featured":           fake,
        "facebook_landscape": fake,
        "facebook_square":    fake,
        "instagram_square":   fake,
        "instagram_portrait": fake,
        "story":              fake,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_slugify() -> None:
    print("\n=== Test: Slug generation ===")
    from shared.content.storage import _slugify

    assert _slugify("Opening a Bank Account in Germany") == "opening-a-bank-account-in-germany"
    assert _slugify("Anmeldung: Register Your Address!") == "anmeldung-register-your-address"
    assert _slugify("  spaces   ") == "spaces"
    assert _slugify("") == "article"
    assert len(_slugify("a" * 200)) <= 80
    print("  PASS")


def test_asset_bundle_model() -> None:
    print("\n=== Test: AssetBundle model ===")
    from shared.content.models import AssetBundle, AssetFile

    with tempfile.TemporaryDirectory() as tmpdir:
        storage_dir = Path(tmpdir)
        bundle = AssetBundle(
            article_slug="test-article",
            title="Test Article",
            summary="A test summary.",
            keywords=["Germany", "expat"],
            storage_dir=storage_dir,
        )

        assert bundle.featured_image is None
        assert bundle.facebook_landscape is None

        fake_path = storage_dir / "featured.jpg"
        fake_path.write_bytes(b"fake")
        asset = AssetFile(key="featured", path=fake_path, mime_type="image/jpeg", size_bytes=4)
        bundle.assets["featured"] = asset

        assert bundle.featured_image is not None
        assert bundle.featured_image.key == "featured"
        assert bundle.featured_image.exists()

        meta = bundle.to_metadata_dict()
        assert meta["title"] == "Test Article"
        assert "featured" in meta["assets"]
        assert meta["assets"]["featured"]["mime_type"] == "image/jpeg"

    print("  PASS")


def test_storage_path_deterministic() -> None:
    print("\n=== Test: Storage path is deterministic ===")
    from shared.content.storage import AssetStorage
    from datetime import datetime, timezone

    with tempfile.TemporaryDirectory() as tmpdir:
        storage = AssetStorage(storage_root=Path(tmpdir))
        dt = datetime(2026, 6, 1, tzinfo=timezone.utc)

        p1 = storage.build_storage_dir("test-slug", dt)
        p2 = storage.build_storage_dir("test-slug", dt)

        assert p1 == p2
        assert "2026" in str(p1)
        assert "06" in str(p1)
        assert "01" in str(p1)
        assert "test-slug" in str(p1)

    print("  PASS")


def test_storage_save_images() -> None:
    print("\n=== Test: AssetStorage saves image files ===")
    from shared.content.models import AssetBundle
    from shared.content.storage import AssetStorage

    with tempfile.TemporaryDirectory() as tmpdir:
        storage = AssetStorage(storage_root=Path(tmpdir))
        slug = "bank-account-germany"
        storage_dir = storage.build_storage_dir(slug)

        bundle = AssetBundle(
            article_slug=slug,
            title="Opening a Bank Account in Germany",
            summary="A practical guide.",
            keywords=["banking", "Germany"],
            storage_dir=storage_dir,
        )

        fake = _make_mock_image()
        image_data = {
            "featured":           fake,
            "facebook_landscape": fake,
            "facebook_square":    fake,
        }

        result = storage.save(bundle, image_data, article_markdown="# Test\n\nContent.")

        assert result.success, f"Storage failed: {result.error_message}"
        assert result.assets_written >= 4  # 3 images + metadata
        assert (storage_dir / "featured.jpg").exists()
        assert (storage_dir / "facebook_landscape.jpg").exists()
        assert (storage_dir / "facebook_square.jpg").exists()
        assert (storage_dir / "metadata.json").exists()
        assert (storage_dir / "article.md").exists()

    print(f"  assets_written={result.assets_written}  PASS")


def test_metadata_json_content() -> None:
    print("\n=== Test: metadata.json has correct content ===")
    from shared.content.models import AssetBundle
    from shared.content.storage import AssetStorage

    with tempfile.TemporaryDirectory() as tmpdir:
        storage = AssetStorage(storage_root=Path(tmpdir))
        slug = "metadata-test"
        storage_dir = storage.build_storage_dir(slug)

        bundle = AssetBundle(
            article_slug=slug,
            title="Metadata Test Article",
            summary="Testing metadata persistence.",
            keywords=["test", "metadata"],
            storage_dir=storage_dir,
            branding_enabled=True,
            ads_enabled=False,
            metadata={"custom_field": "hello"},
        )

        result = storage.save(bundle, {})
        assert result.success

        meta = json.loads((storage_dir / "metadata.json").read_text())
        assert meta["title"] == "Metadata Test Article"
        assert meta["keywords"] == ["test", "metadata"]
        assert meta["branding_enabled"] is True
        assert meta["ads_enabled"] is False
        assert meta["custom_field"] == "hello"
        assert "generated_at" in meta

    print("  PASS")


def test_load_metadata() -> None:
    print("\n=== Test: AssetStorage.load_metadata() ===")
    from shared.content.models import AssetBundle
    from shared.content.storage import AssetStorage

    with tempfile.TemporaryDirectory() as tmpdir:
        storage = AssetStorage(storage_root=Path(tmpdir))
        slug = "load-meta-test"
        storage_dir = storage.build_storage_dir(slug)

        bundle = AssetBundle(
            article_slug=slug,
            title="Load Meta Test",
            summary="Summary",
            keywords=[],
            storage_dir=storage_dir,
        )
        storage.save(bundle, {})

        loaded = storage.load_metadata(storage_dir)
        assert loaded is not None
        assert loaded["title"] == "Load Meta Test"

        missing = storage.load_metadata(Path(tmpdir) / "nonexistent")
        assert missing is None

    print("  PASS")


def test_article_markdown_export() -> None:
    print("\n=== Test: Article markdown export ===")
    from shared.content.models import AssetBundle
    from shared.content.storage import AssetStorage

    with tempfile.TemporaryDirectory() as tmpdir:
        storage = AssetStorage(storage_root=Path(tmpdir))
        slug = "markdown-test"
        storage_dir = storage.build_storage_dir(slug)

        bundle = AssetBundle(
            article_slug=slug,
            title="Markdown Export Test",
            summary="Summary here.",
            keywords=["test"],
            storage_dir=storage_dir,
        )

        result = storage.save(
            bundle, {},
            article_markdown="# Markdown Export Test\n\nSome content."
        )
        assert result.success

        md_content = (storage_dir / "article.md").read_text()
        assert "Markdown Export Test" in md_content

    print("  PASS")


def test_asset_builder_with_mock_images() -> None:
    print("\n=== Test: AssetBuilder with mock image generator ===")
    from shared.content.asset_builder import AssetBuilder
    from shared.content.storage import AssetStorage

    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["ENABLE_MEDIA_ASSETS"] = "true"
        storage = AssetStorage(storage_root=Path(tmpdir))
        builder = AssetBuilder(storage=storage, image_generator=_mock_image_generator)

        result = builder.build(
            title="Health Insurance in Germany for Expats",
            summary="Understanding your options as a foreign resident.",
            article_body="## Introduction\n\nHealth insurance is mandatory in Germany.",
            keywords=["health insurance", "Germany", "expat"],
        )

        assert result.success, f"Build failed: {result.error_message}"
        assert result.bundle is not None
        bundle = result.bundle

        assert bundle.article_slug == "health-insurance-in-germany-for-expats"
        assert "featured" in bundle.assets
        assert "facebook_landscape" in bundle.assets
        assert "instagram_square" in bundle.assets
        assert "article" in bundle.assets
        assert "metadata" in bundle.assets

        assert bundle.featured_image is not None
        assert bundle.featured_image.exists()
        assert result.storage_dir.exists()

    print(f"  slug={bundle.article_slug}")
    print(f"  assets={list(bundle.assets.keys())}")
    print(f"  dir={result.storage_dir}  PASS")


def test_asset_builder_media_disabled() -> None:
    print("\n=== Test: AssetBuilder skips generation when disabled ===")
    from shared.content.asset_builder import AssetBuilder
    from shared.content.storage import AssetStorage

    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["ENABLE_MEDIA_ASSETS"] = "false"
        storage = AssetStorage(storage_root=Path(tmpdir))
        builder = AssetBuilder(storage=storage, image_generator=_mock_image_generator)

        result = builder.build(
            title="Disabled Media Test",
            summary="No images should be generated.",
            keywords=[],
        )

        assert result.success
        assert result.assets_written == 0
        assert result.bundle is not None
        assert result.bundle.assets == {}

    os.environ["ENABLE_MEDIA_ASSETS"] = "true"
    print("  PASS")


def test_storage_handles_partial_images() -> None:
    print("\n=== Test: Storage handles partial image data gracefully ===")
    from shared.content.models import AssetBundle
    from shared.content.storage import AssetStorage

    with tempfile.TemporaryDirectory() as tmpdir:
        storage = AssetStorage(storage_root=Path(tmpdir))
        slug = "partial-test"
        storage_dir = storage.build_storage_dir(slug)

        bundle = AssetBundle(
            article_slug=slug,
            title="Partial Test",
            summary="Only some images provided.",
            keywords=[],
            storage_dir=storage_dir,
        )

        fake = _make_mock_image()
        # Only provide featured — others are absent
        result = storage.save(bundle, {"featured": fake})

        assert result.success
        assert (storage_dir / "featured.jpg").exists()
        assert not (storage_dir / "facebook_landscape.jpg").exists()

    print("  PASS")


def test_asset_file_model() -> None:
    print("\n=== Test: AssetFile model ===")
    from shared.content.models import AssetFile

    with tempfile.TemporaryDirectory() as tmpdir:
        p = Path(tmpdir) / "test.jpg"
        p.write_bytes(b"data")

        af = AssetFile(key="featured", path=p, mime_type="image/jpeg", size_bytes=4)
        assert af.exists()
        assert af.key == "featured"

        missing = AssetFile(key="x", path=Path(tmpdir) / "missing.jpg", mime_type="image/jpeg")
        assert not missing.exists()

    print("  PASS")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("ContentPilot Phase 11A — Content Asset Tests")
    print("=" * 50)

    test_slugify()
    test_asset_bundle_model()
    test_storage_path_deterministic()
    test_storage_save_images()
    test_metadata_json_content()
    test_load_metadata()
    test_article_markdown_export()
    test_asset_builder_with_mock_images()
    test_asset_builder_media_disabled()
    test_storage_handles_partial_images()
    test_asset_file_model()

    print("\n" + "=" * 50)
    print("All Phase 11A tests passed.")
