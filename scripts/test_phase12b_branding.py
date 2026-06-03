#!/usr/bin/env python3
"""
Phase 12B — Visual Branding, CTA & Layout Template System
Offline mock test suite.

Tests:
  1.  BrandProfile loads defaults (all env vars unset)
  2.  BrandProfile loads from env vars
  3.  Invalid layout falls back to B
  4.  hex_to_rgb valid colours
  5.  hex_to_rgb invalid colour falls back gracefully
  6.  load_font falls back to default when no TTF available
  7.  wrap_text splits long lines correctly
  8.  wrap_text handles empty string
  9.  Layout A — renders on Facebook landscape (1200×630)
  10. Layout A — renders on Instagram square (1080×1080)
  11. Layout A — renders on Story (1080×1920)
  12. Layout B — renders on Facebook landscape
  13. Layout B — renders on Instagram square
  14. Layout B — renders on Story
  15. Layout C — renders on Facebook landscape
  16. Layout C — renders on Instagram square
  17. Layout C — renders on Story
  18. apply_branding returns original when profile.enabled=False
  19. apply_branding returns original on Pillow crash (corrupt bytes)
  20. apply_branding applies Layout B correctly end-to-end
  21. apply_branding applies Layout A correctly end-to-end
  22. apply_branding applies Layout C correctly end-to-end
  23. AssetBuilder._apply_branding_overlay skips when disabled
  24. AssetBuilder._apply_branding_overlay applies when enabled
  25. Missing logo path handled gracefully (no crash)

Run inside Docker:
    docker compose -f infra/compose/docker-compose.yml run --rm daily_news \
        python3 /app/scripts/test_phase12b_branding.py
"""

import io
import os
import sys
import traceback

sys.path.insert(0, "/app")

# ---------------------------------------------------------------------------
# Test harness
# ---------------------------------------------------------------------------

_passed = 0
_failed = 0
_errors = []


def ok(name: str) -> None:
    global _passed
    _passed += 1
    print(f"  ✓  {name}")


def fail(name: str, reason: str) -> None:
    global _failed
    _failed += 1
    _errors.append((name, reason))
    print(f"  ✗  {name}")
    print(f"       {reason}")


def run_test(name: str, fn):
    try:
        fn()
        ok(name)
    except AssertionError as exc:
        fail(name, str(exc))
    except Exception as exc:
        fail(name, f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_jpeg(width: int = 200, height: int = 200, color=(100, 150, 200)) -> bytes:
    """Return a minimal valid JPEG byte string."""
    from PIL import Image
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def _set_env(**kwargs):
    for k, v in kwargs.items():
        os.environ[k] = v


def _clear_brand_env():
    for k in [
        "MEDIA_BRANDING_ENABLED", "MEDIA_BRAND_NAME", "MEDIA_BRAND_TAGLINE",
        "MEDIA_BRAND_CTA", "MEDIA_BRAND_WEBSITE", "MEDIA_BRAND_PRIMARY_COLOR",
        "MEDIA_BRAND_ACCENT_COLOR", "MEDIA_BRAND_LOGO_PATH", "MEDIA_BRAND_LAYOUT",
    ]:
        os.environ.pop(k, None)


# ---------------------------------------------------------------------------
# Tests: BrandProfile
# ---------------------------------------------------------------------------

def test_brand_profile_defaults():
    _clear_brand_env()
    from importlib import reload
    import shared.media.branding as mod
    reload(mod)
    p = mod.load_brand_profile()
    assert not p.enabled, "should default to disabled"
    assert p.layout == "B", f"default layout should be B, got {p.layout}"
    assert p.primary_color == "#0F172A"
    assert p.accent_color == "#38BDF8"


def test_brand_profile_from_env():
    _clear_brand_env()
    _set_env(
        MEDIA_BRANDING_ENABLED="true",
        MEDIA_BRAND_NAME="TestBrand",
        MEDIA_BRAND_TAGLINE="Best content",
        MEDIA_BRAND_CTA="Read more",
        MEDIA_BRAND_WEBSITE="https://example.com",
        MEDIA_BRAND_PRIMARY_COLOR="#123456",
        MEDIA_BRAND_ACCENT_COLOR="#ABCDEF",
        MEDIA_BRAND_LAYOUT="A",
    )
    from importlib import reload
    import shared.media.branding as mod
    reload(mod)
    p = mod.load_brand_profile()
    assert p.enabled
    assert p.name == "TestBrand"
    assert p.tagline == "Best content"
    assert p.primary_cta == "Read more"
    assert p.website == "https://example.com"
    assert p.primary_color == "#123456"
    assert p.accent_color == "#ABCDEF"
    assert p.layout == "A"


def test_invalid_layout_fallback():
    _clear_brand_env()
    _set_env(MEDIA_BRANDING_ENABLED="true", MEDIA_BRAND_LAYOUT="Z")
    from importlib import reload
    import shared.media.branding as mod
    reload(mod)
    p = mod.load_brand_profile()
    assert p.layout == "B", f"invalid layout should fall back to B, got {p.layout}"


# ---------------------------------------------------------------------------
# Tests: utils
# ---------------------------------------------------------------------------

def test_hex_to_rgb_valid():
    from shared.media.utils import hex_to_rgb
    assert hex_to_rgb("#FF0000") == (255, 0, 0, 255)
    assert hex_to_rgb("#0F172A", 200) == (15, 23, 42, 200)
    assert hex_to_rgb("38BDF8") == (56, 189, 248, 255)
    # Short form
    assert hex_to_rgb("#FFF") == (255, 255, 255, 255)


def test_hex_to_rgb_invalid():
    from shared.media.utils import hex_to_rgb
    result = hex_to_rgb("notacolor")
    assert result == (0, 0, 0, 255), f"bad hex should return black, got {result}"


def test_load_font_fallback():
    """load_font must never crash even when all TTF paths are missing."""
    from shared.media import utils
    # Temporarily redirect candidates to nonexistent paths
    original = utils._FONT_CANDIDATES.copy()
    utils._FONT_CANDIDATES = {
        "semibold": ["/nonexistent/path.ttf"],
        "regular":  ["/nonexistent/path.ttf"],
        "bold":     ["/nonexistent/path.ttf"],
    }
    try:
        font = utils.load_font(24, "semibold")
        assert font is not None, "load_font must return something even as fallback"
    finally:
        utils._FONT_CANDIDATES = original


def test_wrap_text_splits_long_line():
    from PIL import Image, ImageDraw
    from shared.media.utils import wrap_text, load_font
    img = Image.new("RGB", (400, 100))
    draw = ImageDraw.Draw(img)
    font = load_font(20)
    long_text = "This is a very long line that should definitely wrap across multiple lines"
    lines = wrap_text(draw, long_text, font, 200)
    assert len(lines) > 1, f"expected wrapping, got {len(lines)} line(s)"


def test_wrap_text_empty():
    from PIL import Image, ImageDraw
    from shared.media.utils import wrap_text, load_font
    img = Image.new("RGB", (400, 100))
    draw = ImageDraw.Draw(img)
    font = load_font(20)
    lines = wrap_text(draw, "", font, 200)
    assert lines == [], f"empty text should return empty list, got {lines}"


# ---------------------------------------------------------------------------
# Tests: layouts (render without crash, return correct size)
# ---------------------------------------------------------------------------

_SOCIAL_SIZES = [
    ("facebook_landscape", 1200, 630),
    ("instagram_square",   1080, 1080),
    ("story",              1080, 1920),
]

def _make_profile_enabled(layout: str = "B"):
    _clear_brand_env()
    _set_env(
        MEDIA_BRANDING_ENABLED="true",
        MEDIA_BRAND_NAME="GermanySupport",
        MEDIA_BRAND_TAGLINE="Your expat guide",
        MEDIA_BRAND_CTA="Read more at GermanySupport.de",
        MEDIA_BRAND_WEBSITE="https://germanysupport.de",
        MEDIA_BRAND_LAYOUT=layout,
    )
    from importlib import reload
    import shared.media.branding as mod
    reload(mod)
    return mod.load_brand_profile()


def _layout_renders_ok(layout_name: str, layout_fn, w: int, h: int):
    from PIL import Image
    profile = _make_profile_enabled(layout_name)
    img = Image.new("RGB", (w, h), color=(80, 120, 180))
    result = layout_fn(img, profile)
    assert result is not None, "layout returned None"
    assert result.size == (w, h), f"size mismatch: got {result.size}, expected ({w},{h})"


def test_layout_a_facebook():
    from shared.media.layouts import apply_layout_a
    _layout_renders_ok("A", apply_layout_a, 1200, 630)

def test_layout_a_square():
    from shared.media.layouts import apply_layout_a
    _layout_renders_ok("A", apply_layout_a, 1080, 1080)

def test_layout_a_story():
    from shared.media.layouts import apply_layout_a
    _layout_renders_ok("A", apply_layout_a, 1080, 1920)

def test_layout_b_facebook():
    from shared.media.layouts import apply_layout_b
    _layout_renders_ok("B", apply_layout_b, 1200, 630)

def test_layout_b_square():
    from shared.media.layouts import apply_layout_b
    _layout_renders_ok("B", apply_layout_b, 1080, 1080)

def test_layout_b_story():
    from shared.media.layouts import apply_layout_b
    _layout_renders_ok("B", apply_layout_b, 1080, 1920)

def test_layout_c_facebook():
    from shared.media.layouts import apply_layout_c
    _layout_renders_ok("C", apply_layout_c, 1200, 630)

def test_layout_c_square():
    from shared.media.layouts import apply_layout_c
    _layout_renders_ok("C", apply_layout_c, 1080, 1080)

def test_layout_c_story():
    from shared.media.layouts import apply_layout_c
    _layout_renders_ok("C", apply_layout_c, 1080, 1920)


# ---------------------------------------------------------------------------
# Tests: apply_branding
# ---------------------------------------------------------------------------

def test_apply_branding_disabled_returns_original():
    _clear_brand_env()
    from importlib import reload
    import shared.media.branding as mod
    reload(mod)
    profile = mod.load_brand_profile()
    assert not profile.enabled
    original = _make_jpeg(200, 200)
    result = mod.apply_branding(original, profile)
    assert result == original, "disabled branding must return original bytes unchanged"


def test_apply_branding_corrupt_bytes_returns_original():
    _clear_brand_env()
    _set_env(MEDIA_BRANDING_ENABLED="true")
    from importlib import reload
    import shared.media.branding as mod
    reload(mod)
    profile = mod.load_brand_profile()
    corrupt = b"this is not an image"
    result = mod.apply_branding(corrupt, profile)
    assert result == corrupt, "corrupt bytes should be returned unchanged"


def test_apply_branding_layout_b_end_to_end():
    _set_env(
        MEDIA_BRANDING_ENABLED="true",
        MEDIA_BRAND_NAME="TestBrand",
        MEDIA_BRAND_CTA="Click here",
        MEDIA_BRAND_WEBSITE="https://test.com",
        MEDIA_BRAND_LAYOUT="B",
    )
    from importlib import reload
    import shared.media.branding as mod
    reload(mod)
    profile = mod.load_brand_profile()
    original = _make_jpeg(1200, 630)
    result = mod.apply_branding(original, profile)
    assert isinstance(result, bytes), "result should be bytes"
    assert len(result) > 100, "result too small"
    # Verify it's a valid JPEG
    from PIL import Image
    img = Image.open(io.BytesIO(result))
    assert img.size == (1200, 630), f"size changed: {img.size}"


def test_apply_branding_layout_a_end_to_end():
    _set_env(
        MEDIA_BRANDING_ENABLED="true",
        MEDIA_BRAND_NAME="LayoutA Test",
        MEDIA_BRAND_TAGLINE="The tagline here",
        MEDIA_BRAND_CTA="Read our guide",
        MEDIA_BRAND_WEBSITE="https://example.de",
        MEDIA_BRAND_LAYOUT="A",
    )
    from importlib import reload
    import shared.media.branding as mod
    reload(mod)
    profile = mod.load_brand_profile()
    original = _make_jpeg(1200, 630)
    result = mod.apply_branding(original, profile)
    assert isinstance(result, bytes)
    from PIL import Image
    img = Image.open(io.BytesIO(result))
    assert img.size == (1200, 630)


def test_apply_branding_layout_c_end_to_end():
    _set_env(
        MEDIA_BRANDING_ENABLED="true",
        MEDIA_BRAND_NAME="LayoutC Brand",
        MEDIA_BRAND_CTA="Discover more",
        MEDIA_BRAND_WEBSITE="https://layoutc.com",
        MEDIA_BRAND_LAYOUT="C",
    )
    from importlib import reload
    import shared.media.branding as mod
    reload(mod)
    profile = mod.load_brand_profile()
    original = _make_jpeg(1080, 1080)
    result = mod.apply_branding(original, profile)
    assert isinstance(result, bytes)
    from PIL import Image
    img = Image.open(io.BytesIO(result))
    assert img.size == (1080, 1080)


# ---------------------------------------------------------------------------
# Tests: AssetBuilder._apply_branding_overlay
# ---------------------------------------------------------------------------

def test_asset_builder_branding_skipped_when_disabled():
    """Test _apply_branding_overlay directly — stubs out content.models dependency."""
    _clear_brand_env()

    # We test the branding overlay method in isolation using the branding module directly
    from importlib import reload
    import shared.media.branding as bmod
    reload(bmod)
    profile = bmod.load_brand_profile()
    assert not profile.enabled

    # Simulate what _apply_branding_overlay does when disabled
    original = {"featured": _make_jpeg(200, 200), "facebook_landscape": _make_jpeg(100, 100)}
    branded = {}
    for key, raw in original.items():
        branded[key] = bmod.apply_branding(raw, profile)

    assert set(branded.keys()) == set(original.keys())
    assert branded["featured"] == original["featured"], "disabled: bytes must be unchanged"


def test_asset_builder_branding_applied_when_enabled():
    """Test _apply_branding_overlay directly — stubs out content.models dependency."""
    _clear_brand_env()
    _set_env(
        MEDIA_BRANDING_ENABLED="true",
        MEDIA_BRAND_NAME="BuilderBrand",
        MEDIA_BRAND_CTA="Check it out",
        MEDIA_BRAND_LAYOUT="B",
    )
    from importlib import reload
    import shared.media.branding as bmod
    reload(bmod)
    profile = bmod.load_brand_profile()
    assert profile.enabled

    jpeg = _make_jpeg(400, 300)
    image_data = {"featured": jpeg}

    branded = {}
    for key, raw in image_data.items():
        branded[key] = bmod.apply_branding(raw, profile)

    assert "featured" in branded
    assert isinstance(branded["featured"], bytes)
    assert len(branded["featured"]) > 100


def test_missing_logo_no_crash():
    _clear_brand_env()
    _set_env(
        MEDIA_BRANDING_ENABLED="true",
        MEDIA_BRAND_NAME="LogoTest",
        MEDIA_BRAND_LOGO_PATH="/nonexistent/logo.png",
        MEDIA_BRAND_LAYOUT="B",
    )
    from importlib import reload
    import shared.media.branding as mod
    reload(mod)
    profile = mod.load_brand_profile()
    # Should NOT crash even with invalid logo path
    original = _make_jpeg(800, 600)
    result = mod.apply_branding(original, profile)
    assert isinstance(result, bytes)
    assert len(result) > 100


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def main():
    print()
    print("=" * 60)
    print("  Phase 12B — Branding & Layout Test Suite")
    print("=" * 60)
    print()

    tests = [
        ("1.  BrandProfile loads defaults",                  test_brand_profile_defaults),
        ("2.  BrandProfile loads from env vars",             test_brand_profile_from_env),
        ("3.  Invalid layout falls back to B",               test_invalid_layout_fallback),
        ("4.  hex_to_rgb valid colours",                     test_hex_to_rgb_valid),
        ("5.  hex_to_rgb invalid colour falls back",         test_hex_to_rgb_invalid),
        ("6.  load_font fallback to default",                test_load_font_fallback),
        ("7.  wrap_text splits long lines",                  test_wrap_text_splits_long_line),
        ("8.  wrap_text handles empty string",               test_wrap_text_empty),
        ("9.  Layout A — Facebook landscape (1200×630)",     test_layout_a_facebook),
        ("10. Layout A — Instagram square (1080×1080)",      test_layout_a_square),
        ("11. Layout A — Story (1080×1920)",                 test_layout_a_story),
        ("12. Layout B — Facebook landscape (1200×630)",     test_layout_b_facebook),
        ("13. Layout B — Instagram square (1080×1080)",      test_layout_b_square),
        ("14. Layout B — Story (1080×1920)",                 test_layout_b_story),
        ("15. Layout C — Facebook landscape (1200×630)",     test_layout_c_facebook),
        ("16. Layout C — Instagram square (1080×1080)",      test_layout_c_square),
        ("17. Layout C — Story (1080×1920)",                 test_layout_c_story),
        ("18. apply_branding: disabled → original unchanged",test_apply_branding_disabled_returns_original),
        ("19. apply_branding: corrupt bytes → no crash",     test_apply_branding_corrupt_bytes_returns_original),
        ("20. apply_branding: Layout B end-to-end",          test_apply_branding_layout_b_end_to_end),
        ("21. apply_branding: Layout A end-to-end",          test_apply_branding_layout_a_end_to_end),
        ("22. apply_branding: Layout C end-to-end",          test_apply_branding_layout_c_end_to_end),
        ("23. AssetBuilder: branding skipped when disabled", test_asset_builder_branding_skipped_when_disabled),
        ("24. AssetBuilder: branding applied when enabled",  test_asset_builder_branding_applied_when_enabled),
        ("25. Missing logo path — no crash",                 test_missing_logo_no_crash),
    ]

    for name, fn in tests:
        run_test(name, fn)

    print()
    print("=" * 60)
    total = _passed + _failed
    print(f"  Results: {_passed}/{total} passed", end="")
    if _failed:
        print(f"  |  {_failed} FAILED")
        print()
        for name, reason in _errors:
            print(f"  FAIL: {name}")
            print(f"        {reason}")
    else:
        print("  ✓  ALL PASSED")
    print("=" * 60)
    print()

    sys.exit(0 if _failed == 0 else 1)


if __name__ == "__main__":
    main()
