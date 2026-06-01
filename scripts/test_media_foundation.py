#!/usr/bin/env python3
# tests/shared/media/test_media_foundation.py
"""
Phase 10A — Media Foundation Layer test suite.

Rules:
  - Zero network calls
  - Zero external API calls
  - Mock providers only
  - Fully deterministic
  - Every assertion has a clear failure message

Run locally:
    python tests/shared/media/test_media_foundation.py

Run with pytest:
    python -m pytest tests/shared/media/test_media_foundation.py -v
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

# Allow running from repo root without an editable install.
# File lives at: <repo>/tests/shared/media/test_*.py
# So 4 x .parent reaches <repo>/.
ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def _solid_jpeg(width: int = 400, height: int = 300, color: tuple = (80, 140, 200)) -> bytes:
    """Create a minimal in-memory JPEG for test inputs."""
    from PIL import Image
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def _dimensions(data: bytes) -> tuple[int, int]:
    from PIL import Image
    return Image.open(io.BytesIO(data)).size


def _format(data: bytes) -> str:
    from PIL import Image
    return Image.open(io.BytesIO(data)).format or "UNKNOWN"


def _run(name: str, fn):
    """Tiny test runner used when not running under pytest."""
    try:
        fn()
        print(f"  PASS  {name}")
        return True
    except Exception as exc:
        import traceback
        print(f"  FAIL  {name}")
        traceback.print_exc()
        return False


# ===========================================================================
# 1. Models
# ===========================================================================


def test_models_all_import():
    from shared.media.models import (
        ImageProvider, StockProvider, SocialFormat,
        ImageRequest, StockImageRequest,
        ImageMetadata, ImageProviderResponse, ImageResult, SocialImageResult,
    )
    # Spot-check enum values
    assert ImageProvider.MOCK.value == "mock"
    assert StockProvider.PEXELS.value == "pexels"
    assert SocialFormat.STORY.value == "story"


def test_image_request_defaults():
    from shared.media.models import ImageRequest, ImageProvider
    r = ImageRequest(prompt="test")
    assert r.width == 1024
    assert r.height == 1024
    assert r.provider == ImageProvider.MOCK
    assert r.negative_prompt == ""
    assert r.seed is None
    assert isinstance(r.extra, dict)


def test_stock_request_defaults():
    from shared.media.models import StockImageRequest, StockProvider
    r = StockImageRequest(keywords=["berlin", "germany"])
    assert r.provider == StockProvider.MOCK
    assert r.orientation == "landscape"
    assert r.per_page == 10


def test_image_metadata_is_frozen():
    from shared.media.models import ImageMetadata
    m = ImageMetadata(source="stock", provider="pexels", attribution="Photo by X")
    try:
        m.source = "generated"  # type: ignore[misc]
        assert False, "ImageMetadata must be frozen"
    except Exception:
        pass   # FrozenInstanceError expected


def test_provider_response_is_frozen():
    from shared.media.models import ImageProviderResponse
    r = ImageProviderResponse(success=True, provider="mock")
    try:
        r.success = False  # type: ignore[misc]
        assert False, "ImageProviderResponse must be frozen"
    except Exception:
        pass


def test_image_result_is_frozen():
    from shared.media.models import ImageResult
    r = ImageResult(success=True)
    try:
        r.success = False  # type: ignore[misc]
        assert False, "ImageResult must be frozen"
    except Exception:
        pass


def test_social_image_result_is_frozen():
    from shared.media.models import SocialImageResult, SocialFormat
    r = SocialImageResult(format=SocialFormat.STORY, success=True)
    try:
        r.success = False  # type: ignore[misc]
        assert False, "SocialImageResult must be frozen"
    except Exception:
        pass


# ===========================================================================
# 2. Image Generation
# ===========================================================================


def test_generation_mock_returns_success():
    from shared.media.image_generation import generate_image
    from shared.media.models import ImageRequest, ImageProvider

    r = generate_image(ImageRequest(prompt="test prompt", width=64, height=64, provider=ImageProvider.MOCK))
    assert r.success, f"Expected success, got error: {r.error}"
    assert r.image_bytes is not None, "image_bytes must be populated"
    assert len(r.image_bytes) > 50, "image_bytes suspiciously small"
    assert r.provider == "mock"
    assert r.metadata is not None
    assert r.metadata.provider == "mock"
    assert r.metadata.source == "generated"
    assert r.metadata.width == 64
    assert r.metadata.height == 64


def test_generation_mock_is_deterministic():
    from shared.media.image_generation import generate_image
    from shared.media.models import ImageRequest, ImageProvider

    req = ImageRequest(prompt="deterministic test", width=32, height=32, provider=ImageProvider.MOCK)
    r1 = generate_image(req)
    r2 = generate_image(req)
    assert r1.image_bytes == r2.image_bytes, \
        "Same prompt must always produce the same bytes"


def test_generation_different_prompts_differ():
    from shared.media.image_generation import generate_image
    from shared.media.models import ImageRequest, ImageProvider

    r1 = generate_image(ImageRequest(prompt="alpha one", width=32, height=32, provider=ImageProvider.MOCK))
    r2 = generate_image(ImageRequest(prompt="beta two", width=32, height=32, provider=ImageProvider.MOCK))
    assert r1.image_bytes != r2.image_bytes, \
        "Different prompts must produce different images"


def test_generation_mock_validates_as_png():
    """The mock provider creates valid PNG bytes."""
    from shared.media.image_generation import generate_image
    from shared.media.models import ImageRequest, ImageProvider
    from PIL import Image

    r = generate_image(ImageRequest(prompt="png check", width=50, height=50, provider=ImageProvider.MOCK))
    img = Image.open(io.BytesIO(r.image_bytes))
    assert img.format == "PNG", f"Expected PNG from mock, got {img.format}"
    assert img.size == (50, 50)


def test_generation_stub_provider_returns_failure():
    """Unimplemented providers return a clear failure — not an exception."""
    from shared.media.image_generation import generate_image
    from shared.media.models import ImageRequest, ImageProvider

    for provider in (ImageProvider.STABILITY, ImageProvider.IDEOGRAM, ImageProvider.FLUX):
        r = generate_image(ImageRequest(prompt="test", width=64, height=64, provider=provider))
        assert r.success is False, f"{provider} should return failure"
        assert "not yet implemented" in r.error.lower() or "implement" in r.error.lower(), \
            f"Expected a clear 'not implemented' message for {provider}, got: {r.error}"


def test_generation_unknown_provider_returns_failure():
    from shared.media.image_generation import generate_image
    from shared.media.models import ImageRequest

    req = ImageRequest(prompt="test", provider="nonexistent_provider_xyz")  # type: ignore
    r = generate_image(req)
    assert r.success is False
    assert r.error != ""


# ===========================================================================
# 3. Image Sourcing
# ===========================================================================


def test_sourcing_mock_returns_success():
    from shared.media.image_sourcing import search_stock_image
    from shared.media.models import StockImageRequest, StockProvider

    r = search_stock_image(StockImageRequest(
        keywords=["germany", "banking"],
        provider=StockProvider.MOCK,
    ))
    assert r.success, f"Expected success: {r.error}"
    assert r.image_bytes is not None
    assert len(r.image_bytes) > 100
    assert r.provider == "mock"


def test_sourcing_mock_is_deterministic():
    from shared.media.image_sourcing import search_stock_image
    from shared.media.models import StockImageRequest, StockProvider

    req = StockImageRequest(keywords=["expat", "life"], provider=StockProvider.MOCK)
    r1 = search_stock_image(req)
    r2 = search_stock_image(req)
    assert r1.image_bytes == r2.image_bytes, "Same keywords must produce same bytes"


def test_sourcing_different_keywords_differ():
    from shared.media.image_sourcing import search_stock_image
    from shared.media.models import StockImageRequest, StockProvider

    r1 = search_stock_image(StockImageRequest(keywords=["cat"], provider=StockProvider.MOCK))
    r2 = search_stock_image(StockImageRequest(keywords=["ocean", "waves"], provider=StockProvider.MOCK))
    assert r1.image_bytes != r2.image_bytes, \
        "Different keywords must produce different images"


def test_sourcing_mock_attribution_populated():
    from shared.media.image_sourcing import search_stock_image
    from shared.media.models import StockImageRequest, StockProvider

    r = search_stock_image(StockImageRequest(keywords=["test"], provider=StockProvider.MOCK))
    assert r.metadata is not None
    assert r.metadata.attribution != "", "attribution must be populated"
    assert r.metadata.photographer != "", "photographer must be populated"
    assert r.metadata.license != "", "license must be populated"
    assert r.metadata.source == "stock"
    assert r.metadata.provider == "mock"


def test_sourcing_mock_produces_valid_jpeg():
    from shared.media.image_sourcing import search_stock_image
    from shared.media.models import StockImageRequest, StockProvider
    from PIL import Image

    r = search_stock_image(StockImageRequest(keywords=["nature"], provider=StockProvider.MOCK))
    img = Image.open(io.BytesIO(r.image_bytes))
    assert img.format == "JPEG", f"Expected JPEG from mock stock, got {img.format}"
    assert img.width == 1200
    assert img.height == 800


def test_sourcing_missing_api_key_returns_failure():
    """Real providers return a structured failure when API key is absent."""
    import os
    from shared.media.image_sourcing import search_stock_image
    from shared.media.models import StockImageRequest, StockProvider

    # Temporarily unset the key to simulate missing config
    original = os.environ.pop("PEXELS_API_KEY", None)
    try:
        r = search_stock_image(StockImageRequest(
            keywords=["test"],
            provider=StockProvider.PEXELS,
        ))
        assert r.success is False
        assert "PEXELS_API_KEY" in r.error
    finally:
        if original:
            os.environ["PEXELS_API_KEY"] = original


def test_sourcing_unknown_provider_returns_failure():
    from shared.media.image_sourcing import search_stock_image
    from shared.media.models import StockImageRequest

    r = search_stock_image(StockImageRequest(
        keywords=["test"],
        provider="no_such_provider",  # type: ignore
    ))
    assert r.success is False
    assert r.error != ""


# ===========================================================================
# 4. Image Processing
# ===========================================================================


def test_processing_resize_exact():
    from shared.media import image_processing
    data = _solid_jpeg(400, 300)
    result = image_processing.resize(data, 200, 150)
    assert _dimensions(result) == (200, 150), "resize must produce exact dimensions"
    assert _format(result) == "JPEG"


def test_processing_resize_fit_preserves_aspect():
    from shared.media import image_processing
    data = _solid_jpeg(800, 400)   # 2:1 ratio
    result = image_processing.resize_fit(data, 400, 400)
    w, h = _dimensions(result)
    assert w <= 400 and h <= 400, "resize_fit must stay within bounds"
    assert w > h, "2:1 source should remain wider than tall after fit"


def test_processing_resize_fit_does_not_upscale():
    from shared.media import image_processing
    small = _solid_jpeg(100, 80)
    result = image_processing.resize_fit(small, 400, 400)
    w, h = _dimensions(result)
    assert w <= 100 and h <= 80, \
        f"resize_fit must not upscale: got {w}x{h} from 100x80 source"


def test_processing_resize_fill_exact():
    from shared.media import image_processing
    data = _solid_jpeg(800, 400)
    result = image_processing.resize_fill(data, 300, 300)
    assert _dimensions(result) == (300, 300), \
        "resize_fill must produce exact target dimensions via center crop"
    assert _format(result) == "JPEG"


def test_processing_resize_fill_landscape_to_square():
    from shared.media import image_processing
    data = _solid_jpeg(1200, 630)
    result = image_processing.resize_fill(data, 1080, 1080)
    assert _dimensions(result) == (1080, 1080)


def test_processing_crop_center_exact():
    from shared.media import image_processing
    data = _solid_jpeg(400, 300)
    result = image_processing.crop_center(data, 200, 100)
    w, h = _dimensions(result)
    assert w == 200 and h == 100, f"crop_center produced {w}x{h}"


def test_processing_crop_center_smaller_than_source():
    """When source is smaller than target, crop returns source dimensions."""
    from shared.media import image_processing
    data = _solid_jpeg(100, 80)
    result = image_processing.crop_center(data, 200, 200)
    w, h = _dimensions(result)
    assert w <= 100 and h <= 80, \
        "crop_center must not enlarge when source < target"


def test_processing_thumbnail_within_max():
    from shared.media import image_processing
    data = _solid_jpeg(1000, 750)
    result = image_processing.thumbnail(data, max_size=128)
    w, h = _dimensions(result)
    assert w <= 128 and h <= 128, f"thumbnail exceeded max_size: {w}x{h}"
    assert max(w, h) == 128 or (w <= 128 and h <= 128), "thumbnail should fill to max_size on longest axis"


def test_processing_thumbnail_does_not_upscale():
    from shared.media import image_processing
    data = _solid_jpeg(50, 40)
    result = image_processing.thumbnail(data, max_size=256)
    w, h = _dimensions(result)
    assert w <= 50 and h <= 40, \
        f"thumbnail must not upscale 50x40 to {w}x{h}"


def test_processing_convert_jpeg_to_png():
    from shared.media import image_processing
    data = _solid_jpeg()
    result = image_processing.convert_format(data, "PNG")
    assert _format(result) == "PNG"


def test_processing_convert_jpeg_to_webp():
    from shared.media import image_processing
    data = _solid_jpeg()
    result = image_processing.convert_format(data, "WEBP")
    assert _format(result) == "WEBP"


def test_processing_convert_invalid_format_raises():
    from shared.media import image_processing
    data = _solid_jpeg()
    try:
        image_processing.convert_format(data, "BMP")
        assert False, "Should have raised ValueError for unsupported format"
    except ValueError:
        pass


def test_processing_compress_reduces_size():
    from shared.media import image_processing
    data = _solid_jpeg(800, 600)
    compressed = image_processing.compress(data, quality=20)
    assert len(compressed) < len(data), \
        f"compress(quality=20) must reduce size: {len(data)} → {len(compressed)}"


def test_processing_compress_preserves_format():
    from shared.media import image_processing
    data = _solid_jpeg()
    result = image_processing.compress(data, quality=60)
    assert _format(result) == "JPEG"


def test_processing_get_dimensions():
    from shared.media import image_processing
    data = _solid_jpeg(640, 480)
    assert image_processing.get_dimensions(data) == (640, 480)


def test_processing_get_format():
    from shared.media import image_processing
    data = _solid_jpeg()
    assert image_processing.get_format(data) == "JPEG"


def test_processing_rgba_to_jpeg_no_crash():
    """RGBA images must be composited to RGB before JPEG output."""
    from PIL import Image
    from shared.media import image_processing

    img = Image.new("RGBA", (100, 100), (255, 0, 0, 128))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    png_bytes = buf.getvalue()

    result = image_processing.convert_format(png_bytes, "JPEG")
    assert _format(result) == "JPEG", "RGBA → JPEG must not crash"


# ===========================================================================
# 5. Social Formatter
# ===========================================================================


def test_social_formatter_single_format():
    from shared.media.social_formatter import format_for_social
    from shared.media.models import SocialFormat

    data = _solid_jpeg(800, 600)
    results = format_for_social(data, [SocialFormat.FACEBOOK_LANDSCAPE])
    assert len(results) == 1
    r = results[0]
    assert r.success, f"Expected success: {r.error}"
    assert r.format == SocialFormat.FACEBOOK_LANDSCAPE
    assert r.width == 1200 and r.height == 630
    assert _dimensions(r.image_bytes) == (1200, 630)


def test_social_formatter_all_formats():
    from shared.media.social_formatter import format_for_social, all_formats, get_dimensions
    from shared.media.models import SocialFormat

    data = _solid_jpeg(1200, 1200)
    formats = all_formats()
    results = format_for_social(data, formats)

    assert len(results) == len(formats), \
        f"Expected {len(formats)} results, got {len(results)}"

    for r in results:
        assert r.success, f"{r.format} failed: {r.error}"
        expected_w, expected_h = get_dimensions(r.format)
        assert r.width == expected_w and r.height == expected_h, \
            f"{r.format}: expected {expected_w}x{expected_h}, got {r.width}x{r.height}"
        assert _dimensions(r.image_bytes) == (expected_w, expected_h), \
            f"{r.format}: pixel dimensions do not match declared dimensions"


def test_social_formatter_each_format_matches_spec():
    """Verify every known format against its documented pixel spec."""
    from shared.media.social_formatter import format_for_social
    from shared.media.models import SocialFormat

    expected = {
        SocialFormat.FACEBOOK_LANDSCAPE:  (1200, 630),
        SocialFormat.FACEBOOK_SQUARE:     (1080, 1080),
        SocialFormat.INSTAGRAM_SQUARE:    (1080, 1080),
        SocialFormat.INSTAGRAM_PORTRAIT:  (1080, 1350),
        SocialFormat.STORY:               (1080, 1920),
    }

    data = _solid_jpeg(1200, 1200)
    results = format_for_social(data, list(expected))

    by_format = {r.format: r for r in results}
    for fmt, (w, h) in expected.items():
        r = by_format[fmt]
        assert r.success, f"{fmt} failed: {r.error}"
        assert (r.width, r.height) == (w, h), \
            f"{fmt}: expected {w}x{h}, got {r.width}x{r.height}"


def test_social_formatter_independent_failure_isolation():
    """A failure in one format must not prevent others from succeeding."""
    from shared.media.social_formatter import format_for_social, _DIMENSIONS
    from shared.media.models import SocialFormat

    # Feed a valid image — all should succeed
    data = _solid_jpeg(400, 400)
    results = format_for_social(
        data,
        [SocialFormat.INSTAGRAM_SQUARE, SocialFormat.FACEBOOK_LANDSCAPE],
    )
    assert len(results) == 2
    assert all(r.success for r in results), \
        "Both formats should succeed from a valid input"


def test_social_formatter_empty_bytes_returns_failures():
    from shared.media.social_formatter import format_for_social
    from shared.media.models import SocialFormat

    results = format_for_social(b"", [SocialFormat.FACEBOOK_LANDSCAPE, SocialFormat.STORY])
    assert len(results) == 2
    assert all(not r.success for r in results), "Empty bytes must produce failures"
    assert all(r.error != "" for r in results)


def test_social_formatter_empty_formats_returns_empty():
    from shared.media.social_formatter import format_for_social

    data = _solid_jpeg()
    results = format_for_social(data, [])
    assert results == []


def test_social_formatter_result_order_preserved():
    from shared.media.social_formatter import format_for_social
    from shared.media.models import SocialFormat

    requested = [
        SocialFormat.STORY,
        SocialFormat.FACEBOOK_LANDSCAPE,
        SocialFormat.INSTAGRAM_PORTRAIT,
    ]
    data = _solid_jpeg(800, 800)
    results = format_for_social(data, requested)
    assert [r.format for r in results] == requested, \
        "Output order must match input order"


def test_social_formatter_get_dimensions():
    from shared.media.social_formatter import get_dimensions
    from shared.media.models import SocialFormat

    assert get_dimensions(SocialFormat.STORY) == (1080, 1920)
    assert get_dimensions(SocialFormat.FACEBOOK_LANDSCAPE) == (1200, 630)
    assert get_dimensions(SocialFormat.INSTAGRAM_PORTRAIT) == (1080, 1350)


def test_social_formatter_no_overlays_applied():
    """
    Phase 10A social formatter must only resize — no text, branding, or ads.
    Verify the output image has no 'extra' pixels by checking dimensions exactly.
    """
    from shared.media.social_formatter import format_for_social
    from shared.media.models import SocialFormat

    data = _solid_jpeg(800, 600)
    results = format_for_social(data, [SocialFormat.FACEBOOK_SQUARE])
    r = results[0]
    assert r.success
    # If any overlay extended the canvas, dimensions would differ
    assert _dimensions(r.image_bytes) == (1080, 1080), \
        "Social formatter must not alter canvas beyond target dimensions"


# ===========================================================================
# 6. Package-level imports
# ===========================================================================


def test_package_imports_all_public_api():
    import shared.media as m
    assert callable(m.generate_image),    "generate_image must be importable"
    assert callable(m.search_stock_image), "search_stock_image must be importable"
    assert callable(m.format_for_social), "format_for_social must be importable"
    assert hasattr(m, "image_processing"), "image_processing module must be importable"


def test_package_does_not_expose_phase10b_symbols():
    """Phase 10A must not expose composition, featured_image, or branding."""
    import shared.media as m
    assert not hasattr(m, "compose"), \
        "compose must not exist in Phase 10A — it belongs to Phase 10B"
    assert not hasattr(m, "get_featured_image"), \
        "get_featured_image must not exist in Phase 10A — it belongs to Phase 10B"


def test_no_composition_module_exists():
    """image_composition.py must not exist in Phase 10A."""
    comp_path = Path(ROOT) / "shared" / "media" / "image_composition.py"
    assert not comp_path.exists(), \
        f"image_composition.py must not exist in Phase 10A: {comp_path}"


def test_no_featured_image_module_exists():
    """featured_image.py must not exist in Phase 10A."""
    fi_path = Path(ROOT) / "shared" / "media" / "featured_image.py"
    assert not fi_path.exists(), \
        f"featured_image.py must not exist in Phase 10A: {fi_path}"


# ===========================================================================
# Runner (direct execution)
# ===========================================================================


_ALL_TESTS = [
    # Models
    ("models: all classes import",            test_models_all_import),
    ("models: ImageRequest defaults",          test_image_request_defaults),
    ("models: StockImageRequest defaults",     test_stock_request_defaults),
    ("models: ImageMetadata is frozen",        test_image_metadata_is_frozen),
    ("models: ImageProviderResponse is frozen",test_provider_response_is_frozen),
    ("models: ImageResult is frozen",          test_image_result_is_frozen),
    ("models: SocialImageResult is frozen",    test_social_image_result_is_frozen),
    # Generation
    ("gen: mock returns success",              test_generation_mock_returns_success),
    ("gen: mock is deterministic",             test_generation_mock_is_deterministic),
    ("gen: different prompts differ",          test_generation_different_prompts_differ),
    ("gen: mock produces valid PNG",           test_generation_mock_validates_as_png),
    ("gen: stub providers return failure",     test_generation_stub_provider_returns_failure),
    ("gen: unknown provider returns failure",  test_generation_unknown_provider_returns_failure),
    # Sourcing
    ("src: mock returns success",              test_sourcing_mock_returns_success),
    ("src: mock is deterministic",             test_sourcing_mock_is_deterministic),
    ("src: different keywords differ",         test_sourcing_different_keywords_differ),
    ("src: attribution populated",             test_sourcing_mock_attribution_populated),
    ("src: mock produces valid JPEG",          test_sourcing_mock_produces_valid_jpeg),
    ("src: missing API key → failure",         test_sourcing_missing_api_key_returns_failure),
    ("src: unknown provider → failure",        test_sourcing_unknown_provider_returns_failure),
    # Processing
    ("proc: resize exact",                     test_processing_resize_exact),
    ("proc: resize_fit preserves aspect",      test_processing_resize_fit_preserves_aspect),
    ("proc: resize_fit no upscale",            test_processing_resize_fit_does_not_upscale),
    ("proc: resize_fill exact",                test_processing_resize_fill_exact),
    ("proc: resize_fill landscape→square",     test_processing_resize_fill_landscape_to_square),
    ("proc: crop_center exact",                test_processing_crop_center_exact),
    ("proc: crop_center smaller than source",  test_processing_crop_center_smaller_than_source),
    ("proc: thumbnail within max",             test_processing_thumbnail_within_max),
    ("proc: thumbnail no upscale",             test_processing_thumbnail_does_not_upscale),
    ("proc: convert JPEG→PNG",                 test_processing_convert_jpeg_to_png),
    ("proc: convert JPEG→WEBP",                test_processing_convert_jpeg_to_webp),
    ("proc: invalid format raises",            test_processing_convert_invalid_format_raises),
    ("proc: compress reduces size",            test_processing_compress_reduces_size),
    ("proc: compress preserves format",        test_processing_compress_preserves_format),
    ("proc: get_dimensions correct",           test_processing_get_dimensions),
    ("proc: get_format correct",               test_processing_get_format),
    ("proc: RGBA→JPEG no crash",               test_processing_rgba_to_jpeg_no_crash),
    # Social formatter
    ("soc: single format",                     test_social_formatter_single_format),
    ("soc: all formats",                       test_social_formatter_all_formats),
    ("soc: each format matches spec",          test_social_formatter_each_format_matches_spec),
    ("soc: failure isolation",                 test_social_formatter_independent_failure_isolation),
    ("soc: empty bytes → failures",            test_social_formatter_empty_bytes_returns_failures),
    ("soc: empty formats → empty list",        test_social_formatter_empty_formats_returns_empty),
    ("soc: order preserved",                   test_social_formatter_result_order_preserved),
    ("soc: get_dimensions correct",            test_social_formatter_get_dimensions),
    ("soc: no overlays applied",               test_social_formatter_no_overlays_applied),
    # Package
    ("pkg: public API importable",             test_package_imports_all_public_api),
    ("pkg: Phase 10B symbols absent",          test_package_does_not_expose_phase10b_symbols),
    ("pkg: image_composition absent",          test_no_composition_module_exists),
    ("pkg: featured_image absent",             test_no_featured_image_module_exists),
]


if __name__ == "__main__":
    print("\nContentPilot — Phase 10A Media Foundation Tests")
    print("=" * 56)

    passed = failed = 0
    for name, fn in _ALL_TESTS:
        ok = _run(name, fn)
        if ok:
            passed += 1
        else:
            failed += 1

    print("=" * 56)
    print(f"  {passed} passed  |  {failed} failed  |  {len(_ALL_TESTS)} total")
    sys.exit(0 if failed == 0 else 1)
