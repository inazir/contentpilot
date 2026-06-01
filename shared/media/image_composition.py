# shared/media/image_composition.py
"""
Media Composition Pipeline Engine — Phase 10B.

Applies optional overlay layers to a base image in strict, deterministic order:

    1. Base image   — scale-fill crop to target dimensions
    2. Branding     — semi-transparent bar + brand name + CTA + logo   (optional)
    3. Ad strip     — text or image strip at the bottom                (optional)
    4. Export       — encode to JPEG / PNG / WEBP bytes

Architecture contract (matching Phase 10A style):
    - Input:  raw image bytes  (any Pillow-readable format)
    - Output: ComposedImageResult  (image_bytes + optional local_path)
    - State:  none (pure transformation)
    - File I/O: only when save_to_disk=True — handled at the call site in featured_image.py

Usage:
    from shared.media.image_composition import compose_image
    from shared.media.models import ImageCompositionConfig, BrandingConfig, AdConfig, AdType

    config = ImageCompositionConfig(
        output_width=1200, output_height=630,
        branding=BrandingConfig(enable=True, brand_name="GermanStudies.de", cta_text="Read more"),
        ads=AdConfig(enable=True, ad_type=AdType.TEXT, ad_content="Sponsored by ExpatBank"),
    )
    result = compose_image(image_bytes, config)
    if result.success:
        Path("output.jpg").write_bytes(result.image_bytes)

Extending this system:
    Add a new stage as a private function _apply_*(img, cfg) -> PIL.Image.
    Call it in compose_image() in the desired position.
    Register its config field in ImageCompositionConfig (models.py).
"""

from __future__ import annotations

import io
import logging
import os
import uuid
from pathlib import Path
from typing import Optional

from .models import (
    AdConfig,
    AdType,
    BrandingConfig,
    ComposedImageResult,
    ImageCompositionConfig,
    ImageMetadata,
    LogoPosition,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------

_MIN_BAR_HEIGHT  = 40     # px — branding bar minimum height
_LOGO_BAR_FRAC   = 0.80   # logo height as fraction of bar height
_LOGO_PADDING    = 10     # px from edge
_TEXT_PAD_X      = 14     # px horizontal text padding
_TEXT_PAD_Y      = 8      # px vertical text padding
_CTA_PAD_X       = 20
_CTA_PAD_Y       = 6
_AD_MIN_HEIGHT   = 30     # px — ad strip minimum height
_AD_MAX_RATIO    = 1 / 3  # ad strip never exceeds 1/3 of image height


# ---------------------------------------------------------------------------
# Pillow lazy import
# ---------------------------------------------------------------------------

def _pil():
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageOps
        return Image, ImageDraw, ImageFont, ImageOps
    except ImportError as exc:
        raise RuntimeError(
            "Pillow is required for image_composition. "
            "Install via: pip install Pillow"
        ) from exc


# ---------------------------------------------------------------------------
# Font helper
# ---------------------------------------------------------------------------

def _load_font(font_path: Optional[str], size: int):
    """Load a TrueType font or fall back to Pillow's built-in default."""
    _, _, ImageFont, _ = _pil()
    candidates = [
        font_path,
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if path:
            try:
                return ImageFont.truetype(path, size)
            except (IOError, OSError):
                continue
    return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Stage helpers
# ---------------------------------------------------------------------------

def _bar_height(cfg: BrandingConfig) -> int:
    return max(_MIN_BAR_HEIGHT, cfg.font_size + _TEXT_PAD_Y * 2)


def _ad_strip_height(img_height: int, cfg: AdConfig) -> int:
    raw = int(img_height * cfg.ad_height_ratio)
    return max(_AD_MIN_HEIGHT, min(raw, int(img_height * _AD_MAX_RATIO)))


# ---------------------------------------------------------------------------
# Stage 1 — Base image preparation
# ---------------------------------------------------------------------------

def _prepare_base(image_bytes: bytes, width: int, height: int, fmt: str):
    """
    Load and cover-fit image_bytes to exactly width×height.
    No letterboxing — short edge scales to meet target, long edge crops from centre.
    """
    Image, _, _, ImageOps = _pil()

    img = Image.open(io.BytesIO(image_bytes))

    if fmt == "JPEG" and img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")
    elif fmt in ("PNG", "WEBP") and img.mode == "P":
        img = img.convert("RGBA")

    img = ImageOps.fit(img, (width, height), Image.LANCZOS)
    logger.debug("base_prepared | %dx%d | fmt=%s", width, height, fmt)
    return img


# ---------------------------------------------------------------------------
# Stage 2 — Branding overlay
# ---------------------------------------------------------------------------

def _apply_branding(img, cfg: BrandingConfig):
    """
    Draw branding overlay on a copy of img.

    Layers (applied in order):
        1. Semi-transparent colour bar at bottom
        2. Brand name text — left-aligned in bar
        3. CTA box — centred in bar
        4. Logo — top-left or bottom-right (inside bar height)
    Returns a new PIL Image. Input img is never mutated.
    """
    Image, ImageDraw, _, _ = _pil()

    if not cfg.enable:
        return img

    base = img.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    W, H = base.size
    bar_h = _bar_height(cfg)
    bar_top = H - bar_h

    # Bar
    r, g, b, a = cfg.bar_color
    draw.rectangle([(0, bar_top), (W, H)], fill=(r, g, b, a))

    # Fonts
    font_main  = _load_font(cfg.font_path, cfg.font_size)
    font_small = _load_font(cfg.font_path, max(cfg.font_size - 6, 14))

    tc = (*cfg.text_color, 255)   # text colour with full alpha

    # Brand name
    if cfg.brand_name:
        draw.text((_TEXT_PAD_X, bar_top + _TEXT_PAD_Y), cfg.brand_name,
                  font=font_main, fill=tc)

    # CTA box
    if cfg.cta_text:
        bbox = draw.textbbox((0, 0), cfg.cta_text, font=font_small)
        cta_w = bbox[2] - bbox[0] + _CTA_PAD_X * 2
        cta_h = bbox[3] - bbox[1] + _CTA_PAD_Y * 2
        cta_x = (W - cta_w) // 2
        cta_y = bar_top + (bar_h - cta_h) // 2
        cta_fill = (min(r + 60, 255), min(g + 60, 255), min(b + 60, 255), 220)
        draw.rectangle([(cta_x, cta_y), (cta_x + cta_w, cta_y + cta_h)], fill=cta_fill)
        draw.text((cta_x + _CTA_PAD_X, cta_y + _CTA_PAD_Y), cfg.cta_text,
                  font=font_small, fill=tc)

    result = Image.alpha_composite(base, overlay)

    # Logo
    if cfg.logo_path:
        result = _place_logo(result, cfg, W, H, bar_h)

    result = result.convert("RGB") if img.mode == "RGB" else result
    logger.debug("branding_applied | brand=%r | cta=%r | logo=%s",
                 cfg.brand_name, cfg.cta_text, bool(cfg.logo_path))
    return result


def _place_logo(canvas, cfg: BrandingConfig, W: int, H: int, bar_h: int):
    """Paste logo onto canvas at the configured position."""
    Image, _, _, _ = _pil()

    try:
        logo = Image.open(cfg.logo_path).convert("RGBA")
    except Exception as exc:
        logger.warning("logo_load_failed | path=%s | error=%s", cfg.logo_path, exc)
        return canvas  # graceful degradation — continue without logo

    max_h = max(1, int(bar_h * _LOGO_BAR_FRAC))
    if logo.height > max_h:
        ratio = max_h / logo.height
        logo = logo.resize((max(1, int(logo.width * ratio)), max_h), Image.LANCZOS)

    lw, lh = logo.size

    if cfg.logo_position == LogoPosition.TOP_LEFT:
        pos = (_LOGO_PADDING, _LOGO_PADDING)
    else:  # BOTTOM_RIGHT — inside the branding bar
        pos = (W - lw - _LOGO_PADDING, H - bar_h + (bar_h - lh) // 2)

    result = canvas.convert("RGBA")
    result.paste(logo, pos, mask=logo)
    return result.convert("RGB") if canvas.mode == "RGB" else result


# ---------------------------------------------------------------------------
# Stage 3 — Advertisement strip
# ---------------------------------------------------------------------------

def _apply_ads(img, cfg: AdConfig):
    """
    Draw an advertisement strip at the bottom of img.

    Two ad types:
        TEXT  — renders cfg.ad_content as centred text on a solid background
        IMAGE — loads cfg.ad_content as an image path, resizes into strip

    Returns a new PIL Image. Input img is never mutated.
    """
    Image, ImageDraw, _, _ = _pil()

    if not cfg.enable:
        return img

    W, H = img.size
    strip_h = _ad_strip_height(H, cfg)
    strip_top = H - strip_h

    result = img.copy()
    draw = ImageDraw.Draw(result)
    draw.rectangle([(0, strip_top), (W, H)], fill=cfg.background_color)

    if cfg.ad_type == AdType.TEXT:
        _draw_text_ad(draw, cfg, W, strip_top, strip_h)
    elif cfg.ad_type == AdType.IMAGE:
        result = _draw_image_ad(result, cfg, W, H, strip_top, strip_h)

    logger.debug("ads_applied | type=%s | strip_h=%dpx | content=%.40r",
                 cfg.ad_type, strip_h, cfg.ad_content)
    return result


def _draw_text_ad(draw, cfg: AdConfig, W: int, strip_top: int, strip_h: int) -> None:
    font = _load_font(cfg.font_path, cfg.font_size)
    text = cfg.ad_content or ""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = max(0, (W - tw) // 2)
    y = strip_top + max(0, (strip_h - th) // 2)
    draw.text((x, y), text, font=font, fill=cfg.text_color)


def _draw_image_ad(base, cfg: AdConfig, W: int, H: int,
                   strip_top: int, strip_h: int):
    """Proportionally resize ad image into strip, centred horizontally."""
    Image, _, _, _ = _pil()

    try:
        ad_img = Image.open(cfg.ad_content).convert("RGBA")
    except Exception as exc:
        logger.warning("ad_image_load_failed | path=%s | error=%s", cfg.ad_content, exc)
        return base  # graceful degradation — strip background already drawn

    ratio = strip_h / max(ad_img.height, 1)
    new_w = min(int(ad_img.width * ratio), W)
    new_h = strip_h
    ad_img = ad_img.resize((new_w, new_h), Image.LANCZOS)

    x = (W - new_w) // 2
    canvas = base.convert("RGBA")
    canvas.paste(ad_img, (x, strip_top), mask=ad_img)
    return canvas.convert("RGB") if base.mode == "RGB" else canvas


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def _to_bytes(img, fmt: str, quality: int) -> bytes:
    buf = io.BytesIO()
    save_kwargs: dict = {"format": fmt}
    if fmt in ("JPEG", "WEBP"):
        save_kwargs["quality"] = quality
        save_kwargs["optimize"] = True
    elif fmt == "PNG":
        save_kwargs["optimize"] = True

    if fmt == "JPEG" and img.mode != "RGB":
        img = img.convert("RGB")

    img.save(buf, **save_kwargs)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def compose_image(
    image_bytes: bytes,
    config: ImageCompositionConfig,
    save_to_disk: bool = False,
) -> ComposedImageResult:
    """
    Run the full composition pipeline on raw image bytes.

    Pipeline (strict order):
        1. Base fit    — cover-fill to output_width × output_height
        2. Branding    — if config.branding.enable
        3. Ad strip    — if config.ads.enable
        4. Export      — encode to output_format bytes

    Args:
        image_bytes:  Raw bytes of any Pillow-readable image.
        config:       Full composition configuration.
        save_to_disk: If True, write the output bytes to a file under
                      config.output_dir (or /app/data/media/composed).
                      The path is returned in ComposedImageResult.local_path.

    Returns:
        ComposedImageResult — never raises.
        On failure: success=False, error describes what went wrong.
    """
    if not image_bytes:
        return ComposedImageResult(success=False, error="image_bytes is empty")

    fmt = config.output_format.upper()
    stages: list[str] = []

    try:
        # Stage 1
        img = _prepare_base(image_bytes, config.output_width, config.output_height, fmt)
        stages.append("base")
        logger.info("compose_start | target=%dx%d | fmt=%s | branding=%s | ads=%s",
                    config.output_width, config.output_height, fmt,
                    config.branding.enable, config.ads.enable)

        # Stage 2
        if config.branding.enable:
            img = _apply_branding(img, config.branding)
            stages.append("branding")

        # Stage 3
        if config.ads.enable:
            img = _apply_ads(img, config.ads)
            stages.append("ads")

        # Stage 4 — encode
        out_bytes = _to_bytes(img, fmt, config.output_quality)
        stages.append("export")
        file_size = len(out_bytes)

        logger.info("compose_ok | stages=%s | %dx%d | %d bytes",
                    stages, img.width, img.height, file_size)

        # Optional disk write
        local_path: Optional[str] = None
        if save_to_disk:
            out_dir = Path(config.output_dir or os.getenv("MEDIA_OUTPUT_DIR", "/app/data/media")) / "composed"
            out_dir.mkdir(parents=True, exist_ok=True)
            ext = fmt.lower().replace("jpeg", "jpg")
            out_path = out_dir / f"composed_{uuid.uuid4().hex[:10]}.{ext}"
            out_path.write_bytes(out_bytes)
            local_path = str(out_path)
            logger.debug("compose_saved | path=%s", local_path)

        return ComposedImageResult(
            success=True,
            image_bytes=out_bytes,
            local_path=local_path,
            width=img.width,
            height=img.height,
            format=fmt,
            file_size_bytes=file_size,
            stages_applied=tuple(stages),
        )

    except Exception as exc:
        logger.exception("compose_error | stages_completed=%s | error=%s", stages, exc)
        return ComposedImageResult(
            success=False,
            error=f"Composition error after stages {stages}: {exc}",
        )
