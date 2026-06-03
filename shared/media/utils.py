# shared/media/utils.py
"""
Pillow layout utilities for ContentPilot media pipeline.

All coordinate calculations are relative (percentage of canvas dimensions)
so layouts scale correctly across social formats:
  - Facebook landscape  1200×630
  - Facebook square     1080×1080
  - Instagram square    1080×1080
  - Instagram portrait  1080×1350
  - Story               1080×1920

Never use hardcoded pixel values for layout — always derive from canvas size.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Font resolution
# ---------------------------------------------------------------------------

# Bundled font directory — lives inside the shared package so it's always
# present in the Docker image regardless of the base OS font set.
_ASSETS_DIR = Path(__file__).parent / "assets" / "fonts"

_FONT_CANDIDATES = {
    "semibold": [
        str(_ASSETS_DIR / "Inter-SemiBold.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ],
    "regular": [
        str(_ASSETS_DIR / "Inter-Regular.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ],
    "bold": [
        str(_ASSETS_DIR / "Inter-Bold.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
    ],
}


def load_font(size: int, weight: str = "semibold"):
    """
    Load the best available TrueType font at the requested size.

    Falls back gracefully to Pillow's built-in bitmap font if no
    TrueType font can be found — never raises.

    Args:
        size:   Font size in points.
        weight: "semibold" | "regular" | "bold"

    Returns:
        PIL ImageFont instance.
    """
    from PIL import ImageFont

    candidates = _FONT_CANDIDATES.get(weight, _FONT_CANDIDATES["semibold"])

    for path in candidates:
        if path and os.path.isfile(path):
            try:
                font = ImageFont.truetype(path, size)
                logger.debug("branding_font_loaded | path=%s | size=%d", path, size)
                return font
            except (IOError, OSError) as exc:
                logger.debug("branding_font_load_attempt_failed | path=%s | error=%s", path, exc)
                continue

    logger.warning(
        "branding_font_fallback | weight=%s | size=%d | reason=no_ttf_found",
        weight, size,
    )
    return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Relative coordinate helpers
# ---------------------------------------------------------------------------

def rel_x(canvas_width: int, fraction: float) -> int:
    """Convert a fraction of canvas width to pixels. E.g. rel_x(1200, 0.05) = 60."""
    return int(canvas_width * fraction)


def rel_y(canvas_height: int, fraction: float) -> int:
    """Convert a fraction of canvas height to pixels."""
    return int(canvas_height * fraction)


def rel_font_size(canvas_width: int, fraction: float, min_size: int = 12, max_size: int = 120) -> int:
    """
    Derive font size relative to canvas width so text scales across formats.

    Args:
        canvas_width: Pixel width of the canvas.
        fraction:     Fraction of canvas width (e.g. 0.035 = 3.5%).
        min_size:     Floor to avoid unreadably small text.
        max_size:     Ceiling to avoid oversized text on very wide canvases.
    """
    size = int(canvas_width * fraction)
    return max(min_size, min(size, max_size))


# ---------------------------------------------------------------------------
# Text wrapping
# ---------------------------------------------------------------------------

def wrap_text(
    draw,
    text: str,
    font,
    max_width: int,
) -> list[str]:
    """
    Break `text` into lines that each fit within `max_width` pixels.

    Uses PIL ImageDraw.textbbox for accurate per-character measurement.
    Returns a list of line strings.

    Args:
        draw:      PIL ImageDraw instance (needed for text measurement).
        text:      Input string (may contain newlines already).
        font:      PIL font instance.
        max_width: Maximum pixel width per line.
    """
    if not text:
        return []

    lines: list[str] = []

    for paragraph in text.splitlines():
        words = paragraph.split()
        if not words:
            lines.append("")
            continue

        current = ""
        for word in words:
            candidate = f"{current} {word}".strip() if current else word
            bbox = draw.textbbox((0, 0), candidate, font=font)
            line_width = bbox[2] - bbox[0]
            if line_width <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word

        if current:
            lines.append(current)

    return lines


def measure_text_block(
    draw,
    lines: list[str],
    font,
    line_spacing: float = 1.3,
) -> tuple[int, int]:
    """
    Return (max_width, total_height) of a list of text lines.

    Args:
        draw:         PIL ImageDraw instance.
        lines:        Text lines as returned by wrap_text().
        font:         PIL font instance.
        line_spacing: Multiplier on line height (1.0 = tight, 1.3 = comfortable).

    Returns:
        (width_px, height_px) of the entire block.
    """
    if not lines:
        return 0, 0

    max_w = 0
    total_h = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        max_w = max(max_w, w)
        total_h += int(h * line_spacing)

    return max_w, total_h


def draw_text_block(
    draw,
    lines: list[str],
    font,
    x: int,
    y: int,
    fill: tuple,
    line_spacing: float = 1.3,
    align: str = "left",
    max_width: int = 0,
) -> int:
    """
    Draw a list of text lines onto `draw` starting at (x, y).

    Args:
        draw:         PIL ImageDraw instance.
        lines:        Text lines.
        font:         PIL font.
        x:            Left edge (or centre anchor when align="center").
        y:            Top edge of first line.
        fill:         RGB(A) colour tuple.
        line_spacing: Multiplier on line height.
        align:        "left" | "center" | "right"
        max_width:    Used for centre/right alignment calculations.

    Returns:
        Y position after the last line (useful for stacking elements).
    """
    cy = y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        line_h = bbox[3] - bbox[1]

        if align == "center" and max_width:
            lx = x + (max_width - line_w) // 2
        elif align == "right" and max_width:
            lx = x + max_width - line_w
        else:
            lx = x

        draw.text((lx, cy), line, font=font, fill=fill)
        cy += int(line_h * line_spacing)

    return cy


# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------

def hex_to_rgb(hex_color: str, alpha: int = 255) -> tuple:
    """
    Convert a CSS hex colour string to an RGBA tuple.

    Accepts: "#RRGGBB", "#RGB", "RRGGBB"

    Args:
        hex_color: Hex string with or without leading #.
        alpha:     Alpha channel (0–255). Default 255 = fully opaque.

    Returns:
        (R, G, B, A) tuple of ints 0–255.
    """
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        r = int(h[0:2], 16)
        g = int(h[2:4], 16)
        b = int(h[4:6], 16)
        return (r, g, b, alpha)
    except (ValueError, IndexError):
        logger.warning("hex_to_rgb | invalid_hex=%r | falling_back_to_black", hex_color)
        return (0, 0, 0, alpha)


def darken(color: tuple, factor: float = 0.7) -> tuple:
    """Return a darkened version of an RGB(A) colour tuple."""
    rgb = tuple(min(255, max(0, int(c * factor))) for c in color[:3])
    return (*rgb, color[3]) if len(color) == 4 else rgb


def lighten(color: tuple, factor: float = 1.3) -> tuple:
    """Return a lightened version of an RGB(A) colour tuple."""
    rgb = tuple(min(255, max(0, int(c * factor))) for c in color[:3])
    return (*rgb, color[3]) if len(color) == 4 else rgb


# ---------------------------------------------------------------------------
# Logo loading
# ---------------------------------------------------------------------------

def load_logo(logo_path: Optional[str], max_height: int):
    """
    Load a logo image from disk and resize it to fit within max_height.

    Returns a PIL Image (RGBA) or None if loading fails.
    Never raises.

    Args:
        logo_path:  Absolute or relative path to logo file (PNG/JPEG).
        max_height: Maximum logo height in pixels.
    """
    if not logo_path:
        return None

    try:
        from PIL import Image
        if not os.path.isfile(logo_path):
            logger.warning("branding_logo_status | path=%s | status=not_found", logo_path)
            return None

        logo = Image.open(logo_path).convert("RGBA")
        if logo.height > max_height:
            ratio = max_height / logo.height
            new_w = max(1, int(logo.width * ratio))
            logo = logo.resize((new_w, max_height), Image.LANCZOS)

        logger.debug("branding_logo_status | path=%s | status=loaded | size=%dx%d",
                     logo_path, logo.width, logo.height)
        return logo

    except Exception as exc:
        logger.warning("branding_logo_status | path=%s | status=error | error=%s",
                       logo_path, exc)
        return None


# ---------------------------------------------------------------------------
# Gradient overlay
# ---------------------------------------------------------------------------

def draw_gradient_overlay(
    img,
    start_y_fraction: float = 0.55,
    alpha_top: int = 0,
    alpha_bottom: int = 210,
    color: tuple = (0, 0, 0),
):
    """
    Draw a vertical gradient (transparent → solid) over the bottom of img.

    Args:
        img:               PIL Image (will be converted to RGBA internally).
        start_y_fraction:  Where the gradient starts as fraction of height.
        alpha_top:         Alpha at the top of the gradient (0 = fully transparent).
        alpha_bottom:      Alpha at the bottom (210 = mostly opaque).
        color:             RGB base colour for the gradient.

    Returns:
        Composited PIL Image in original mode.
    """
    from PIL import Image

    original_mode = img.mode
    base = img.convert("RGBA")
    W, H = base.size
    gradient = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    start_y = int(H * start_y_fraction)
    gradient_height = H - start_y

    for y in range(start_y, H):
        progress = (y - start_y) / max(gradient_height, 1)
        alpha = int(alpha_top + (alpha_bottom - alpha_top) * progress)
        for x in range(W):
            gradient.putpixel((x, y), (*color, alpha))

    result = Image.alpha_composite(base, gradient)
    return result.convert(original_mode) if original_mode != "RGBA" else result
