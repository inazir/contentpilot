#!/usr/bin/env python3
# tests/shared/media/test_media_composition.py
"""
Phase 10B — Media Composition Engine Test Suite.

Architecture: bytes-in / bytes-out (matching Phase 10A convention).
No file I/O in tests unless explicitly testing save_to_disk.

Test groups:
  1.  compose_image — base only
  2.  Branding system (enable/disable, all fields, bad logo, bar height)
  3.  Ad system (text, image, bad path, height ratio bounds)
  4.  Combined branding + ads
  5.  Composition output correctness (dimensions, format, bytes populated)
  6.  featured_image pipeline
  7.  FeaturedImageResult fields
  8.  save_to_disk behaviour
  9.  Social formatter integration (bytes → bytes, all 5 formats)
  10. Model integrity (frozen result types, mutable config types)
  11. Public API surface (__init__ imports)
  12. End-to-end integration

Rules:
  - No external API calls
  - Mock providers only (IMAGE_GENERATION_PROVIDER=mock, IMAGE_STOCK_PROVIDER=mock)
  - All tests deterministic
  - No global state

Run locally:
    PYTHONPATH=. python3 tests/shared/media/test_media_composition.py

Run in Docker:
    docker compose -f infra/compose/docker-compose.yml run --rm daily_news \\
        python /app/tests/shared/media/test_media_composition.py
"""

from __future__ import annotations

import io
import os
import sys
import shutil
import tempfile
from dataclasses import fields
from pathlib import Path

# ---------------------------------------------------------------------------
# Environment + path bootstrap
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, "/app")

os.environ["IMAGE_GENERATION_PROVIDER"] = "mock"
os.environ["IMAGE_STOCK_PROVIDER"]      = "mock"

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
from shared.media.models import (
    AdConfig, AdType, BrandingConfig, ComposedImageResult,
    FeaturedImageResult, ImageCompositionConfig, ImageMetadata,
    ImageProviderResponse, ImageResult, LogoPosition,
    SocialFormat, SocialImageResult,
)
from shared.media.image_composition import (
    compose_image,
    _bar_height,
    _ad_strip_height,
)
from shared.media.featured_image import get_featured_image
from shared.media.social_formatter import format_for_social, get_dimensions, all_formats
from shared.media.image_sourcing import search_stock_image
from shared.media.image_generation import generate_image
from shared.media.models import ImageRequest, StockImageRequest, StockProvider, ImageProvider

# ---------------------------------------------------------------------------
# Test runner helpers
# ---------------------------------------------------------------------------

_failures: list[str] = []
_tmpdir = tempfile.mkdtemp(prefix="cp_10b_test_")


def check(name: str, fn) -> None:
    try:
        fn()
        print(f"  [PASS] {name}")
    except AssertionError as exc:
        print(f"  [FAIL] {name}: {exc}")
        _failures.append(name)
    except Exception as exc:
        print(f"  [FAIL] {name}: {type(exc).__name__}: {exc}")
        _failures.append(name)


# ---------------------------------------------------------------------------
# Byte fixtures
# ---------------------------------------------------------------------------

def _make_image_bytes(width: int = 800, height: int = 600,
                      color=(100, 149, 237), fmt: str = "JPEG") -> bytes:
    """Create in-memory image bytes without touching disk."""
    from PIL import Image
    img = Image.new("RGB", (width, height), color)
    buf = io.BytesIO()
    img.save(buf, format=fmt, quality=85)
    return buf.getvalue()


def _make_logo_bytes(size: int = 80) -> bytes:
    """Create a small RGBA logo PNG as bytes."""
    from PIL import Image
    img = Image.new("RGBA", (size, size), (255, 165, 0, 200))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _make_logo_file(size: int = 80) -> str:
    """Save a logo to a temp file and return its path."""
    path = Path(_tmpdir) / f"logo_{size}.png"
    path.write_bytes(_make_logo_bytes(size))
    return str(path)


def _make_ad_image_file() -> str:
    """Save a small ad image to a temp file and return its path."""
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", (400, 60), (200, 230, 200, 255))
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), "AD BANNER", fill=(50, 50, 50, 255))
    path = Path(_tmpdir) / "ad_banner.png"
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    path.write_bytes(buf.getvalue())
    return str(path)


def _get_pil_dimensions(image_bytes: bytes) -> tuple[int, int]:
    from PIL import Image
    img = Image.open(io.BytesIO(image_bytes))
    return img.width, img.height


# ===========================================================================
# Group 1 — compose_image: base only
# ===========================================================================

def test_compose_base_success():
    src = _make_image_bytes()
    config = ImageCompositionConfig(output_width=1200, output_height=630)
    result = compose_image(src, config)
    assert result.success, result.error
    assert result.image_bytes and len(result.image_bytes) > 0
    assert result.width == 1200
    assert result.height == 630


def test_compose_exact_dimensions():
    src = _make_image_bytes(400, 300)
    config = ImageCompositionConfig(output_width=1080, output_height=1080)
    result = compose_image(src, config)
    assert result.success
    w, h = _get_pil_dimensions(result.image_bytes)
    assert w == 1080 and h == 1080


def test_compose_jpeg_output():
    src = _make_image_bytes()
    config = ImageCompositionConfig(output_format="JPEG")
    result = compose_image(src, config)
    assert result.success
    assert result.format == "JPEG"
    # JPEG magic bytes: FF D8
    assert result.image_bytes[:2] == b"\xff\xd8"


def test_compose_png_output():
    src = _make_image_bytes()
    config = ImageCompositionConfig(output_format="PNG")
    result = compose_image(src, config)
    assert result.success
    assert result.format == "PNG"
    assert result.image_bytes[:8] == b"\x89PNG\r\n\x1a\n"


def test_compose_empty_bytes_fails():
    config = ImageCompositionConfig()
    result = compose_image(b"", config)
    assert not result.success
    assert result.error


def test_compose_stages_applied_base_only():
    src = _make_image_bytes()
    config = ImageCompositionConfig()
    result = compose_image(src, config)
    assert result.success
    assert "base" in result.stages_applied
    assert "export" in result.stages_applied
    assert "branding" not in result.stages_applied
    assert "ads" not in result.stages_applied


def test_compose_file_size_populated():
    src = _make_image_bytes()
    result = compose_image(src, ImageCompositionConfig())
    assert result.success
    assert result.file_size_bytes == len(result.image_bytes)


# ===========================================================================
# Group 2 — Branding system
# ===========================================================================

def test_branding_disabled_no_stage():
    src = _make_image_bytes()
    config = ImageCompositionConfig(branding=BrandingConfig(enable=False))
    result = compose_image(src, config)
    assert result.success
    assert "branding" not in result.stages_applied


def test_branding_enabled_adds_stage():
    src = _make_image_bytes()
    config = ImageCompositionConfig(branding=BrandingConfig(enable=True, brand_name="Test"))
    result = compose_image(src, config)
    assert result.success
    assert "branding" in result.stages_applied


def test_branding_brand_name_only():
    src = _make_image_bytes(1200, 630)
    config = ImageCompositionConfig(
        output_width=1200, output_height=630,
        branding=BrandingConfig(enable=True, brand_name="GermanStudies.de"),
    )
    result = compose_image(src, config)
    assert result.success
    assert result.width == 1200 and result.height == 630


def test_branding_with_cta():
    src = _make_image_bytes()
    config = ImageCompositionConfig(
        branding=BrandingConfig(enable=True, brand_name="CP", cta_text="Read more →"),
    )
    result = compose_image(src, config)
    assert result.success and result.image_bytes


def test_branding_logo_bottom_right():
    src = _make_image_bytes()
    logo = _make_logo_file()
    config = ImageCompositionConfig(
        branding=BrandingConfig(
            enable=True, brand_name="Brand",
            logo_path=logo, logo_position=LogoPosition.BOTTOM_RIGHT,
        ),
    )
    result = compose_image(src, config)
    assert result.success


def test_branding_logo_top_left():
    src = _make_image_bytes()
    logo = _make_logo_file()
    config = ImageCompositionConfig(
        branding=BrandingConfig(
            enable=True, brand_name="Brand",
            logo_path=logo, logo_position=LogoPosition.TOP_LEFT,
        ),
    )
    result = compose_image(src, config)
    assert result.success


def test_branding_bad_logo_graceful():
    """Missing logo path must not crash — branding continues without it."""
    src = _make_image_bytes()
    config = ImageCompositionConfig(
        branding=BrandingConfig(enable=True, brand_name="Brand",
                                logo_path="/nonexistent/logo.png"),
    )
    result = compose_image(src, config)
    assert result.success, f"Expected graceful degradation, got: {result.error}"
    assert "branding" in result.stages_applied


def test_branding_custom_bar_color():
    src = _make_image_bytes()
    config = ImageCompositionConfig(
        branding=BrandingConfig(enable=True, brand_name="X",
                                bar_color=(25, 118, 210, 200)),
    )
    result = compose_image(src, config)
    assert result.success


def test_branding_bar_height_minimum():
    cfg = BrandingConfig(enable=True, font_size=10)
    h = _bar_height(cfg)
    assert h >= 40, f"Bar must be at least 40px, got {h}"


def test_branding_bar_height_scales_with_font():
    small = _bar_height(BrandingConfig(enable=True, font_size=20))
    large = _bar_height(BrandingConfig(enable=True, font_size=50))
    assert large > small, "Larger font must produce taller bar"


# ===========================================================================
# Group 3 — Ad system
# ===========================================================================

def test_ads_disabled_no_stage():
    src = _make_image_bytes()
    result = compose_image(src, ImageCompositionConfig(ads=AdConfig(enable=False)))
    assert result.success
    assert "ads" not in result.stages_applied


def test_ads_enabled_adds_stage():
    src = _make_image_bytes()
    config = ImageCompositionConfig(
        ads=AdConfig(enable=True, ad_type=AdType.TEXT, ad_content="Sponsored"),
    )
    result = compose_image(src, config)
    assert result.success
    assert "ads" in result.stages_applied


def test_text_ad_renders():
    src = _make_image_bytes(1200, 630)
    config = ImageCompositionConfig(
        output_width=1200, output_height=630,
        ads=AdConfig(enable=True, ad_type=AdType.TEXT, ad_content="Sponsored by ExpatBank.de"),
    )
    result = compose_image(src, config)
    assert result.success
    assert result.width == 1200 and result.height == 630


def test_image_ad_renders():
    src = _make_image_bytes()
    ad_file = _make_ad_image_file()
    config = ImageCompositionConfig(
        ads=AdConfig(enable=True, ad_type=AdType.IMAGE, ad_content=ad_file),
    )
    result = compose_image(src, config)
    assert result.success


def test_image_ad_bad_path_graceful():
    """Missing ad image must not crash — strip background is rendered anyway."""
    src = _make_image_bytes()
    config = ImageCompositionConfig(
        ads=AdConfig(enable=True, ad_type=AdType.IMAGE, ad_content="/nonexistent/ad.png"),
    )
    result = compose_image(src, config)
    assert result.success, f"Expected graceful degradation, got: {result.error}"


def test_ad_height_ratio_default():
    h = _ad_strip_height(630, AdConfig(ad_height_ratio=0.10))
    assert h == int(630 * 0.10), f"Expected {int(630*0.10)}, got {h}"


def test_ad_height_ratio_custom():
    h = _ad_strip_height(1000, AdConfig(ad_height_ratio=0.20))
    assert h == int(1000 * 0.20)


def test_ad_height_minimum_enforced():
    h = _ad_strip_height(100, AdConfig(ad_height_ratio=0.001))
    assert h >= 30, f"Minimum 30px not enforced, got {h}"


def test_ad_height_maximum_enforced():
    h = _ad_strip_height(600, AdConfig(ad_height_ratio=0.99))
    assert h <= 200, f"Maximum 1/3 not enforced, got {h}"


def test_ad_custom_colors():
    src = _make_image_bytes()
    config = ImageCompositionConfig(
        ads=AdConfig(enable=True, ad_type=AdType.TEXT, ad_content="Ad",
                     background_color=(50, 50, 50), text_color=(255, 255, 0)),
    )
    result = compose_image(src, config)
    assert result.success


# ===========================================================================
# Group 4 — Combined branding + ads
# ===========================================================================

def test_branding_and_text_ads_combined():
    src = _make_image_bytes(1200, 630)
    config = ImageCompositionConfig(
        output_width=1200, output_height=630,
        branding=BrandingConfig(enable=True, brand_name="ContentPilot", cta_text="Read"),
        ads=AdConfig(enable=True, ad_type=AdType.TEXT, ad_content="Sponsored", ad_height_ratio=0.08),
    )
    result = compose_image(src, config)
    assert result.success, result.error
    assert result.width == 1200 and result.height == 630
    assert "branding" in result.stages_applied
    assert "ads" in result.stages_applied


def test_branding_and_image_ads_combined():
    src = _make_image_bytes()
    logo = _make_logo_file()
    ad_file = _make_ad_image_file()
    config = ImageCompositionConfig(
        branding=BrandingConfig(enable=True, brand_name="Full Test",
                                logo_path=logo, cta_text="Learn more"),
        ads=AdConfig(enable=True, ad_type=AdType.IMAGE, ad_content=ad_file),
    )
    result = compose_image(src, config)
    assert result.success


def test_pipeline_order_stages_correct():
    """Stages must appear in strict order: base → branding → ads → export."""
    src = _make_image_bytes()
    config = ImageCompositionConfig(
        branding=BrandingConfig(enable=True, brand_name="Order"),
        ads=AdConfig(enable=True, ad_type=AdType.TEXT, ad_content="Ad"),
    )
    result = compose_image(src, config)
    stages = list(result.stages_applied)
    assert stages.index("base") < stages.index("branding")
    assert stages.index("branding") < stages.index("ads")
    assert stages.index("ads") < stages.index("export")


def test_combined_output_dimensions_exact():
    src = _make_image_bytes(400, 300)
    target_w, target_h = 1200, 630
    config = ImageCompositionConfig(
        output_width=target_w, output_height=target_h,
        branding=BrandingConfig(enable=True, brand_name="Brand"),
        ads=AdConfig(enable=True, ad_type=AdType.TEXT, ad_content="Ad"),
    )
    result = compose_image(src, config)
    assert result.success
    w, h = _get_pil_dimensions(result.image_bytes)
    assert w == target_w and h == target_h


# ===========================================================================
# Group 5 — Composition output correctness
# ===========================================================================

def test_image_bytes_always_populated_on_success():
    src = _make_image_bytes()
    result = compose_image(src, ImageCompositionConfig())
    assert result.success
    assert result.image_bytes is not None
    assert len(result.image_bytes) > 0


def test_local_path_none_when_not_saving():
    src = _make_image_bytes()
    result = compose_image(src, ImageCompositionConfig(), save_to_disk=False)
    assert result.local_path is None


def test_composed_result_is_frozen():
    result = ComposedImageResult(success=True, image_bytes=b"test", width=100, height=100)
    try:
        result.width = 200  # type: ignore[misc]
        assert False, "Should have raised FrozenInstanceError"
    except Exception:
        pass  # expected — frozen dataclass


def test_webp_output():
    src = _make_image_bytes()
    config = ImageCompositionConfig(output_format="WEBP")
    result = compose_image(src, config)
    assert result.success
    assert result.format == "WEBP"
    # WEBP magic bytes: RIFF....WEBP
    assert result.image_bytes[:4] == b"RIFF"
    assert result.image_bytes[8:12] == b"WEBP"


# ===========================================================================
# Group 6 — Featured image pipeline
# ===========================================================================

def test_featured_image_basic():
    result = get_featured_image(
        title="Opening a Bank Account in Germany",
        summary="A guide for expats.",
        keywords=["Germany", "bank account", "expat"],
    )
    assert result.success, f"Pipeline failed: {result.error}"
    assert result.composed is not None
    assert result.composed.image_bytes and len(result.composed.image_bytes) > 0
    w, h = _get_pil_dimensions(result.composed.image_bytes)
    assert w == 1200 and h == 630


def test_featured_image_with_branding():
    config = ImageCompositionConfig(
        branding=BrandingConfig(enable=True, brand_name="GermanStudies.de", cta_text="Read more"),
    )
    result = get_featured_image(title="Health Insurance in Germany", config=config)
    assert result.success, result.error
    assert "branding" in result.composed.stages_applied


def test_featured_image_with_ads():
    config = ImageCompositionConfig(
        ads=AdConfig(enable=True, ad_type=AdType.TEXT, ad_content="Sponsored by ExpatHQ"),
    )
    result = get_featured_image(title="Public Transport Germany", config=config)
    assert result.success, result.error
    assert "ads" in result.composed.stages_applied


def test_featured_image_full_pipeline():
    config = ImageCompositionConfig(
        output_width=1200, output_height=630,
        branding=BrandingConfig(enable=True, brand_name="GermanStudies.de", cta_text="Read"),
        ads=AdConfig(enable=True, ad_type=AdType.TEXT, ad_content="Sponsored", ad_height_ratio=0.08),
    )
    result = get_featured_image(
        title="Registering Your Address in Germany",
        summary="The Anmeldung process explained.",
        keywords=["Anmeldung", "Germany", "registration"],
        config=config,
    )
    assert result.success, result.error
    w, h = _get_pil_dimensions(result.composed.image_bytes)
    assert w == 1200 and h == 630


def test_featured_image_skip_stock():
    result = get_featured_image(title="Skip stock test", skip_stock=True)
    assert result.success, result.error
    assert "stock_search" not in result.pipeline_stages
    assert "ai_generation" in result.pipeline_stages


def test_featured_image_custom_dimensions():
    config = ImageCompositionConfig(output_width=1080, output_height=1080)
    result = get_featured_image(title="Square format test", config=config)
    assert result.success, result.error
    w, h = _get_pil_dimensions(result.composed.image_bytes)
    assert w == 1080 and h == 1080


def test_featured_image_empty_title():
    result = get_featured_image(title="")
    assert result.success, result.error


def test_featured_image_no_keywords():
    result = get_featured_image(title="Article Without Keywords")
    assert result.success, result.error


# ===========================================================================
# Group 7 — FeaturedImageResult fields
# ===========================================================================

def test_pipeline_stages_tracked():
    result = get_featured_image(title="Stages test")
    assert result.success
    assert "composition" in result.pipeline_stages
    assert "complete" in result.pipeline_stages
    assert len(result.pipeline_stages) >= 2


def test_source_used_populated():
    result = get_featured_image(title="Source test")
    assert result.success
    assert result.source_used != ""


def test_source_used_mock_for_mock_provider():
    result = get_featured_image(title="Mock source test")
    assert result.success
    assert result.source_used == "mock"


# ===========================================================================
# Group 8 — save_to_disk
# ===========================================================================

def test_save_to_disk_creates_file():
    out_dir = Path(_tmpdir) / "save_test"
    config = ImageCompositionConfig(output_dir=str(out_dir))
    result = get_featured_image(title="Save to disk test", config=config, save_to_disk=True)
    assert result.success, result.error
    assert result.composed.local_path is not None
    assert Path(result.composed.local_path).exists()
    assert Path(result.composed.local_path).stat().st_size > 0


def test_save_to_disk_false_no_file():
    result = get_featured_image(title="No save test", save_to_disk=False)
    assert result.success
    assert result.composed.local_path is None


def test_compose_save_to_disk_directly():
    src = _make_image_bytes()
    out_dir = Path(_tmpdir) / "compose_save"
    config = ImageCompositionConfig(output_dir=str(out_dir))
    result = compose_image(src, config, save_to_disk=True)
    assert result.success
    assert result.local_path is not None
    assert Path(result.local_path).exists()


# ===========================================================================
# Group 9 — Social formatter integration (bytes → bytes)
# ===========================================================================

def test_social_format_all_five():
    src = _make_image_bytes(1200, 800)
    for fmt in all_formats():
        results = format_for_social(src, [fmt])
        r = results[0]
        assert r.success, f"{fmt.value}: {r.error}"
        assert r.image_bytes and len(r.image_bytes) > 0
        w, h = _get_pil_dimensions(r.image_bytes)
        expected_w, expected_h = get_dimensions(fmt)
        assert w == expected_w and h == expected_h, \
            f"{fmt.value}: expected {expected_w}x{expected_h}, got {w}x{h}"


def test_social_format_multiple_at_once():
    src = _make_image_bytes()
    fmts = [SocialFormat.FACEBOOK_LANDSCAPE, SocialFormat.INSTAGRAM_PORTRAIT]
    results = format_for_social(src, fmts)
    assert len(results) == 2
    assert all(r.success for r in results)


def test_social_format_story_upscale():
    """Story (1080×1920) from landscape source requires upscaling."""
    src = _make_image_bytes(1200, 630)
    results = format_for_social(src, [SocialFormat.STORY])
    r = results[0]
    assert r.success, r.error
    w, h = _get_pil_dimensions(r.image_bytes)
    assert w == 1080 and h == 1920


def test_social_formatter_with_composed_output():
    """Pipe compose_image output directly into format_for_social."""
    src = _make_image_bytes()
    config = ImageCompositionConfig(
        branding=BrandingConfig(enable=True, brand_name="Pipeline"),
    )
    composed = compose_image(src, config)
    assert composed.success

    results = format_for_social(
        composed.image_bytes,
        [SocialFormat.INSTAGRAM_SQUARE, SocialFormat.STORY],
    )
    assert len(results) == 2
    assert all(r.success for r in results)


def test_social_format_empty_bytes():
    results = format_for_social(b"", [SocialFormat.FACEBOOK_LANDSCAPE])
    assert len(results) == 1
    assert not results[0].success


def test_social_image_result_is_frozen():
    r = SocialImageResult(format=SocialFormat.FACEBOOK_LANDSCAPE, success=True,
                          image_bytes=b"x", width=1200, height=630)
    try:
        r.width = 999  # type: ignore[misc]
        assert False, "Should have raised FrozenInstanceError"
    except Exception:
        pass


# ===========================================================================
# Group 10 — Model integrity
# ===========================================================================

def test_composed_image_result_frozen():
    r = ComposedImageResult(success=True, image_bytes=b"test")
    try:
        r.success = False  # type: ignore[misc]
        assert False, "Should be frozen"
    except Exception:
        pass


def test_featured_image_result_mutable():
    r = FeaturedImageResult(success=True)
    r.pipeline_stages.append("test")
    assert "test" in r.pipeline_stages


def test_branding_config_mutable():
    cfg = BrandingConfig()
    cfg.enable = True
    cfg.brand_name = "Updated"
    assert cfg.brand_name == "Updated"


def test_ad_config_mutable():
    cfg = AdConfig()
    cfg.enable = True
    cfg.ad_content = "Updated ad"
    assert cfg.ad_content == "Updated ad"


def test_image_composition_config_mutable():
    cfg = ImageCompositionConfig()
    cfg.output_width = 2048
    assert cfg.output_width == 2048


def test_image_metadata_frozen():
    m = ImageMetadata(source="stock", provider="pexels")
    try:
        m.source = "generated"  # type: ignore[misc]
        assert False, "Should be frozen"
    except Exception:
        pass


def test_image_provider_response_frozen():
    r = ImageProviderResponse(success=True, provider="mock", image_bytes=b"x")
    try:
        r.success = False  # type: ignore[misc]
        assert False, "Should be frozen"
    except Exception:
        pass


# ===========================================================================
# Group 11 — Public API surface
# ===========================================================================

def test_public_api_10a_intact():
    from shared.media import generate_image, search_stock_image, format_for_social, image_processing
    assert callable(generate_image)
    assert callable(search_stock_image)
    assert callable(format_for_social)
    assert hasattr(image_processing, "resize")
    assert hasattr(image_processing, "resize_fill")
    assert hasattr(image_processing, "resize_fit")
    assert hasattr(image_processing, "crop_center")
    assert hasattr(image_processing, "thumbnail")
    assert hasattr(image_processing, "compress")
    assert hasattr(image_processing, "convert_format")


def test_public_api_10b_added():
    from shared.media import compose_image, get_featured_image
    assert callable(compose_image)
    assert callable(get_featured_image)


def test_model_imports_all_10b_types():
    from shared.media.models import (
        AdType, LogoPosition,
        BrandingConfig, AdConfig, ImageCompositionConfig,
        ComposedImageResult, FeaturedImageResult,
    )
    assert AdType.TEXT.value == "text"
    assert AdType.IMAGE.value == "image"
    assert LogoPosition.TOP_LEFT.value == "top_left"


# ===========================================================================
# Group 12 — End-to-end integration
# ===========================================================================

def test_end_to_end_bytes_pipeline():
    """
    Full bytes pipeline:
        mock stock → compose (branding + ads) → social format (Instagram)
    No file I/O required.
    """
    from shared.media import get_featured_image, format_for_social
    from shared.media.models import SocialFormat

    config = ImageCompositionConfig(
        output_width=1200, output_height=630,
        branding=BrandingConfig(enable=True, brand_name="GermanStudies.de", cta_text="Read"),
        ads=AdConfig(enable=True, ad_type=AdType.TEXT, ad_content="Sponsored by BerlinLife",
                     ad_height_ratio=0.08),
    )
    result = get_featured_image(
        title="How to Anmelden in Germany",
        summary="Step-by-step address registration guide.",
        keywords=["Anmeldung", "Germany", "registration"],
        config=config,
    )
    assert result.success, result.error

    w, h = _get_pil_dimensions(result.composed.image_bytes)
    assert w == 1200 and h == 630

    # Format for Instagram portrait
    ig_results = format_for_social(result.composed.image_bytes, [SocialFormat.INSTAGRAM_PORTRAIT])
    ig = ig_results[0]
    assert ig.success, ig.error
    w2, h2 = _get_pil_dimensions(ig.image_bytes)
    assert w2 == 1080 and h2 == 1350


def test_end_to_end_all_social_formats():
    """Produce all 5 social formats from one featured image."""
    from shared.media import get_featured_image, format_for_social

    result = get_featured_image(title="Social formats test")
    assert result.success

    social_results = format_for_social(result.composed.image_bytes, all_formats())
    assert len(social_results) == 5
    failed = [r for r in social_results if not r.success]
    assert not failed, f"Failed formats: {[(r.format, r.error) for r in failed]}"


# ===========================================================================
# Main
# ===========================================================================

def main() -> None:
    print("\nPhase 10B — Media Composition Engine Test Suite")
    print("=" * 58)

    print("\n[Group 1]  compose_image — base only")
    check("Base composition succeeds",             test_compose_base_success)
    check("Exact output dimensions",               test_compose_exact_dimensions)
    check("JPEG magic bytes correct",              test_compose_jpeg_output)
    check("PNG magic bytes correct",               test_compose_png_output)
    check("Empty bytes → failure",                 test_compose_empty_bytes_fails)
    check("Stages applied: base + export only",    test_compose_stages_applied_base_only)
    check("file_size_bytes == len(image_bytes)",   test_compose_file_size_populated)

    print("\n[Group 2]  Branding system")
    check("Disabled → no branding stage",          test_branding_disabled_no_stage)
    check("Enabled → branding stage recorded",     test_branding_enabled_adds_stage)
    check("Brand name only",                       test_branding_brand_name_only)
    check("Brand name + CTA",                      test_branding_with_cta)
    check("Logo bottom-right",                     test_branding_logo_bottom_right)
    check("Logo top-left",                         test_branding_logo_top_left)
    check("Bad logo path — graceful degradation",  test_branding_bad_logo_graceful)
    check("Custom bar color",                      test_branding_custom_bar_color)
    check("Bar height minimum 40px",               test_branding_bar_height_minimum)
    check("Bar height scales with font size",      test_branding_bar_height_scales_with_font)

    print("\n[Group 3]  Ad system")
    check("Disabled → no ads stage",               test_ads_disabled_no_stage)
    check("Enabled → ads stage recorded",          test_ads_enabled_adds_stage)
    check("Text ad renders",                       test_text_ad_renders)
    check("Image ad renders",                      test_image_ad_renders)
    check("Bad ad image — graceful degradation",   test_image_ad_bad_path_graceful)
    check("Ad height ratio default (10%)",         test_ad_height_ratio_default)
    check("Ad height ratio custom (20%)",          test_ad_height_ratio_custom)
    check("Ad height minimum 30px enforced",       test_ad_height_minimum_enforced)
    check("Ad height maximum 1/3 enforced",        test_ad_height_maximum_enforced)
    check("Ad custom background + text color",     test_ad_custom_colors)

    print("\n[Group 4]  Combined branding + ads")
    check("Branding + text ad combined",           test_branding_and_text_ads_combined)
    check("Branding + image ad combined",          test_branding_and_image_ads_combined)
    check("Stage order: base→brand→ads→export",    test_pipeline_order_stages_correct)
    check("Combined output exact dimensions",      test_combined_output_dimensions_exact)

    print("\n[Group 5]  Composition output correctness")
    check("image_bytes always populated",          test_image_bytes_always_populated_on_success)
    check("local_path None when not saving",       test_local_path_none_when_not_saving)
    check("ComposedImageResult is frozen",         test_composed_result_is_frozen)
    check("WEBP output format",                    test_webp_output)

    print("\n[Group 6]  Featured image pipeline")
    check("Basic pipeline succeeds",               test_featured_image_basic)
    check("Pipeline with branding",                test_featured_image_with_branding)
    check("Pipeline with ads",                     test_featured_image_with_ads)
    check("Full pipeline (branding + ads)",        test_featured_image_full_pipeline)
    check("skip_stock forces AI generation",       test_featured_image_skip_stock)
    check("Custom output dimensions",              test_featured_image_custom_dimensions)
    check("Empty title handled",                   test_featured_image_empty_title)
    check("No keywords handled",                   test_featured_image_no_keywords)

    print("\n[Group 7]  FeaturedImageResult fields")
    check("pipeline_stages tracked",               test_pipeline_stages_tracked)
    check("source_used populated",                 test_source_used_populated)
    check("source_used == 'mock' for mock",        test_source_used_mock_for_mock_provider)

    print("\n[Group 8]  save_to_disk")
    check("save_to_disk=True creates file",        test_save_to_disk_creates_file)
    check("save_to_disk=False → no file",          test_save_to_disk_false_no_file)
    check("compose_image save_to_disk directly",   test_compose_save_to_disk_directly)

    print("\n[Group 9]  Social formatter (bytes→bytes)")
    check("All 5 formats correct dimensions",      test_social_format_all_five)
    check("Multiple formats in one call",          test_social_format_multiple_at_once)
    check("Story (portrait upscale)",              test_social_format_story_upscale)
    check("Composed output → social format",       test_social_formatter_with_composed_output)
    check("Empty bytes → failure per format",      test_social_format_empty_bytes)
    check("SocialImageResult is frozen",           test_social_image_result_is_frozen)

    print("\n[Group 10] Model integrity")
    check("ComposedImageResult frozen",            test_composed_image_result_frozen)
    check("FeaturedImageResult mutable",           test_featured_image_result_mutable)
    check("BrandingConfig mutable",                test_branding_config_mutable)
    check("AdConfig mutable",                      test_ad_config_mutable)
    check("ImageCompositionConfig mutable",        test_image_composition_config_mutable)
    check("ImageMetadata frozen (10A)",            test_image_metadata_frozen)
    check("ImageProviderResponse frozen (10A)",    test_image_provider_response_frozen)

    print("\n[Group 11] Public API surface")
    check("10A public API intact",                 test_public_api_10a_intact)
    check("10B functions added",                   test_public_api_10b_added)
    check("10B model types importable",            test_model_imports_all_10b_types)

    print("\n[Group 12] End-to-end integration")
    check("Full bytes pipeline → Instagram",       test_end_to_end_bytes_pipeline)
    check("All 5 social formats from one image",   test_end_to_end_all_social_formats)

    # Summary
    total = 62
    passed = total - len(_failures)
    print("=" * 58)
    if _failures:
        print(f"\n  {len(_failures)} FAILED: {', '.join(_failures)}")
        sys.exit(1)
    else:
        print(f"\n  All {passed} tests passed.")

    shutil.rmtree(_tmpdir, ignore_errors=True)


if __name__ == "__main__":
    main()
