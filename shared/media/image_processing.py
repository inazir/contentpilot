# shared/media/image_processing.py
"""
Stateless image processing utilities.

All functions take bytes in and return bytes out. No file I/O, no global
state, no side effects. Every function is a pure transformation.

Design contract
---------------
- Input:  raw image bytes (any Pillow-readable format)
- Output: raw image bytes in the requested format
- State:  none
- Raises: RuntimeError only when Pillow is not installed
          Never raises on malformed images — returns a descriptive error
          by letting Pillow surface the exception to the caller

Typical call chain
------------------
    raw     = generate_image(request).image_bytes
    cropped = image_processing.resize_fill(raw, 1200, 630)
    thumb   = image_processing.thumbnail(cropped, 256)
    final   = image_processing.compress(cropped, quality=80)
"""

from __future__ import annotations

import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _require_pillow():
    """Raise a clear error if Pillow is missing."""
    try:
        import PIL  # noqa: F401
    except ImportError:
        raise RuntimeError(
            "Pillow is required for image_processing. "
            "Install it with: pip install pillow"
        )


def _open(image_bytes: bytes):
    """Open image bytes as a PIL Image."""
    from PIL import Image
    return Image.open(io.BytesIO(image_bytes))


def _to_bytes(img, fmt: str, quality: int) -> bytes:
    """Serialise a PIL Image to bytes in the given format."""
    buf = io.BytesIO()
    save_kwargs: dict = {"format": fmt}
    if fmt in {"JPEG", "WEBP"}:
        save_kwargs["quality"] = quality
        save_kwargs["optimize"] = True
    elif fmt == "PNG":
        save_kwargs["optimize"] = True
    img.save(buf, **save_kwargs)
    return buf.getvalue()


def _ensure_rgb(img):
    """
    Convert image to RGB mode, compositing transparency onto white where needed.
    Required before saving as JPEG (which has no alpha channel).
    """
    if img.mode == "RGB":
        return img
    from PIL import Image
    if img.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        mask = img.split()[-1]
        bg.paste(img.convert("RGB"), mask=mask)
        return bg
    return img.convert("RGB")


def _validate_fmt(fmt: str) -> str:
    fmt = fmt.upper()
    supported = {"JPEG", "PNG", "WEBP"}
    if fmt not in supported:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {supported}")
    return fmt


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def resize(
    image_bytes: bytes,
    width: int,
    height: int,
    output_format: str = "JPEG",
    quality: int = 90,
) -> bytes:
    """
    Resize to exact (width, height). Aspect ratio is NOT preserved.
    Use resize_fit() or resize_fill() for aspect-preserving variants.
    """
    _require_pillow()
    from PIL import Image

    fmt = _validate_fmt(output_format)
    img = _open(image_bytes)
    if fmt == "JPEG":
        img = _ensure_rgb(img)
    img = img.resize((width, height), Image.LANCZOS)
    result = _to_bytes(img, fmt, quality)
    logger.debug("resize | %dx%d → %dx%d | fmt=%s | %d bytes", *_open(image_bytes).size, width, height, fmt, len(result))
    return result


def resize_fit(
    image_bytes: bytes,
    max_width: int,
    max_height: int,
    output_format: str = "JPEG",
    quality: int = 90,
) -> bytes:
    """
    Shrink image so it fits within (max_width, max_height), preserving aspect ratio.
    The image is never upscaled. One axis may be smaller than the bound.
    """
    _require_pillow()
    from PIL import Image

    fmt = _validate_fmt(output_format)
    img = _open(image_bytes)
    if fmt == "JPEG":
        img = _ensure_rgb(img)
    img.thumbnail((max_width, max_height), Image.LANCZOS)
    result = _to_bytes(img, fmt, quality)
    logger.debug("resize_fit | max=%dx%d | actual=%dx%d | fmt=%s", max_width, max_height, img.width, img.height, fmt)
    return result


def resize_fill(
    image_bytes: bytes,
    width: int,
    height: int,
    output_format: str = "JPEG",
    quality: int = 90,
) -> bytes:
    """
    Resize and center-crop image to exactly (width, height).
    Fills the entire canvas — no letterboxing. Edges may be cropped.
    Use this for social format thumbnails where exact dimensions are required.
    """
    _require_pillow()
    from PIL import Image, ImageOps

    fmt = _validate_fmt(output_format)
    img = _open(image_bytes)
    if fmt == "JPEG":
        img = _ensure_rgb(img)
    img = ImageOps.fit(img, (width, height), Image.LANCZOS)
    result = _to_bytes(img, fmt, quality)
    logger.debug("resize_fill | %dx%d | fmt=%s | %d bytes", width, height, fmt, len(result))
    return result


def crop_center(
    image_bytes: bytes,
    width: int,
    height: int,
    output_format: str = "JPEG",
    quality: int = 90,
) -> bytes:
    """
    Crop the centre of the image to (width, height).
    If the source is smaller than the target on either axis, that axis is
    used as-is (no padding added).
    """
    _require_pillow()
    from PIL import Image

    fmt = _validate_fmt(output_format)
    img = _open(image_bytes)
    if fmt == "JPEG":
        img = _ensure_rgb(img)

    src_w, src_h = img.size
    left   = max(0, (src_w - width)  // 2)
    top    = max(0, (src_h - height) // 2)
    right  = min(src_w, left + width)
    bottom = min(src_h, top + height)

    img = img.crop((left, top, right, bottom))
    result = _to_bytes(img, fmt, quality)
    logger.debug("crop_center | %dx%d | fmt=%s | %d bytes", img.width, img.height, fmt, len(result))
    return result


def thumbnail(
    image_bytes: bytes,
    max_size: int = 256,
    output_format: str = "JPEG",
    quality: int = 85,
) -> bytes:
    """
    Generate a thumbnail where neither dimension exceeds max_size px.
    Aspect ratio is preserved; the image is never upscaled.
    """
    return resize_fit(image_bytes, max_size, max_size, output_format, quality)


def convert_format(
    image_bytes: bytes,
    output_format: str,
    quality: int = 90,
) -> bytes:
    """
    Convert image bytes from any Pillow-readable format to output_format.
    Supported output formats: JPEG | PNG | WEBP
    """
    _require_pillow()
    fmt = _validate_fmt(output_format)
    img = _open(image_bytes)
    if fmt == "JPEG":
        img = _ensure_rgb(img)
    result = _to_bytes(img, fmt, quality)
    logger.debug("convert_format | %s → %s | %d bytes", img.format, fmt, len(result))
    return result


def compress(
    image_bytes: bytes,
    quality: int = 75,
    output_format: Optional[str] = None,
) -> bytes:
    """
    Re-compress image at the specified quality level to reduce file size.

    Args:
        image_bytes:   Source image bytes.
        quality:       Target quality (1–95). Lower = smaller file.
        output_format: Force output format; None preserves original format
                       (falls back to JPEG when original format is unknown).
    """
    _require_pillow()
    img = _open(image_bytes)
    fmt = _validate_fmt(output_format or img.format or "JPEG")
    if fmt == "JPEG":
        img = _ensure_rgb(img)
    result = _to_bytes(img, fmt, quality)
    logger.debug(
        "compress | quality=%d | fmt=%s | %d → %d bytes (%.0f%%)",
        quality, fmt, len(image_bytes), len(result),
        100 * len(result) / max(len(image_bytes), 1),
    )
    return result


def get_dimensions(image_bytes: bytes) -> tuple[int, int]:
    """
    Return (width, height) of image bytes without full pixel decode.
    """
    _require_pillow()
    return _open(image_bytes).size


def get_format(image_bytes: bytes) -> str:
    """
    Return the detected format string of image bytes (e.g. 'JPEG', 'PNG').
    Returns 'UNKNOWN' when Pillow cannot determine the format.
    """
    _require_pillow()
    fmt = _open(image_bytes).format
    return fmt if fmt else "UNKNOWN"
