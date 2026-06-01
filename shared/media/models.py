# shared/media/models.py
"""
Data models for the ContentPilot Media Foundation Layer (Phase 10A).

Design rules:
  - Dataclasses only (no external dependencies)
  - All fields explicitly typed
  - Immutable result types (frozen=True)
  - Mutable request/config types (frozen=False, for ergonomic construction)

Phase 10B will extend this file with:
  - BrandingConfig
  - AdConfig
  - ImageCompositionConfig
  - FeaturedImageRequest / FeaturedImageResult
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ImageProvider(str, Enum):
    """Registered AI image generation providers."""
    MOCK       = "mock"
    OPENAI     = "openai"
    STABILITY  = "stability"
    IDEOGRAM   = "ideogram"
    FLUX       = "flux"


class StockProvider(str, Enum):
    """Registered stock image sourcing providers."""
    MOCK     = "mock"
    UNSPLASH = "unsplash"
    PEXELS   = "pexels"
    PIXABAY  = "pixabay"


class SocialFormat(str, Enum):
    """
    Platform-specific image format targets.

    Each value maps to a (width, height) pair in social_formatter.py.
    """
    FACEBOOK_LANDSCAPE  = "facebook_landscape"   # 1200 x 630
    FACEBOOK_SQUARE     = "facebook_square"       # 1080 x 1080
    INSTAGRAM_SQUARE    = "instagram_square"      # 1080 x 1080
    INSTAGRAM_PORTRAIT  = "instagram_portrait"    # 1080 x 1350
    STORY               = "story"                 # 1080 x 1920


# ---------------------------------------------------------------------------
# Request models  (mutable — callers build these)
# ---------------------------------------------------------------------------


@dataclass
class ImageRequest:
    """
    Input descriptor for AI image generation.

    Fields:
        prompt:          Text prompt sent to the provider.
        width / height:  Requested output dimensions in pixels.
        provider:        Which generation backend to use.
        negative_prompt: Things to avoid (provider-dependent support).
        seed:            Optional fixed seed for reproducibility.
        extra:           Provider-specific pass-through parameters.
    """
    prompt:          str
    width:           int           = 1024
    height:          int           = 1024
    provider:        ImageProvider = ImageProvider.MOCK
    negative_prompt: str           = ""
    seed:            Optional[int] = None
    extra:           dict          = field(default_factory=dict)


@dataclass
class StockImageRequest:
    """
    Input descriptor for stock image keyword search.

    Fields:
        keywords:    Search terms (joined with spaces for API queries).
        provider:    Which stock source to query.
        orientation: "landscape" | "portrait" | "square"
        min_width:   Minimum acceptable image width.
        min_height:  Minimum acceptable image height.
        per_page:    How many results to request from the API (first is used).
    """
    keywords:    list[str]
    provider:    StockProvider = StockProvider.MOCK
    orientation: str           = "landscape"
    min_width:   int           = 800
    min_height:  int           = 600
    per_page:    int           = 10


# ---------------------------------------------------------------------------
# Metadata — attached to every image result
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ImageMetadata:
    """
    Descriptive metadata attached to a sourced or generated image.

    For stock images: always populate attribution + photographer + license.
    For generated images: populate source="generated" and provider.
    """
    source:       str   # "stock" | "generated" | "mock"
    provider:     str
    original_url: str   = ""
    attribution:  str   = ""   # Required for stock; display where license demands it
    photographer: str   = ""
    license:      str   = ""
    width:        int   = 0
    height:       int   = 0
    extra:        dict  = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Response / result models  (frozen — callers must not mutate)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ImageProviderResponse:
    """
    Raw response from any image provider (generation or stock) before processing.

    image_bytes:  Raw image data (set when the image was downloaded/generated).
    image_url:    Remote URL (set when the provider returns a URL instead of bytes).
    One of the two will be populated on success.
    """
    success:     bool
    provider:    str
    image_bytes: Optional[bytes]        = None
    image_url:   str                    = ""
    error:       str                    = ""
    metadata:    Optional[ImageMetadata] = None


@dataclass(frozen=True)
class ImageResult:
    """
    Final result after all processing has been applied to an image.

    This is what callers receive from image_processing utilities.
    Phase 10B will extend this with composition flags.
    """
    success:         bool
    image_bytes:     Optional[bytes]        = None
    width:           int                    = 0
    height:          int                    = 0
    format:          str                    = ""      # "JPEG" | "PNG" | "WEBP"
    file_size_bytes: int                    = 0
    metadata:        Optional[ImageMetadata] = None
    error:           str                    = ""


@dataclass(frozen=True)
class SocialImageResult:
    """
    Result of formatting an image for one specific social platform target.
    One instance is returned per requested SocialFormat.
    """
    format:      SocialFormat
    success:     bool
    image_bytes: Optional[bytes] = None
    width:       int             = 0
    height:      int             = 0
    error:       str             = ""


# ===========================================================================
# Phase 10B extensions — Composition Engine
# ===========================================================================
#
# These types are appended here per the 10A README's Phase 10B extension guide.
# No existing 10A type is modified.


class AdType(str, Enum):
    """Ad strip content type."""
    TEXT  = "text"
    IMAGE = "image"


class LogoPosition(str, Enum):
    """Where to pin the logo within the branding bar."""
    TOP_LEFT     = "top_left"
    BOTTOM_RIGHT = "bottom_right"


@dataclass
class BrandingConfig:
    """
    Optional branding overlay for the composition pipeline.

    All settings have safe defaults — enable=False skips the stage entirely.
    font_path: absolute path to a .ttf font file, or None to use Pillow's default.
    """
    enable:        bool                       = False
    brand_name:    str                        = ""
    logo_path:     Optional[str]              = None          # local path
    logo_position: LogoPosition               = LogoPosition.BOTTOM_RIGHT
    cta_text:      str                        = ""
    bar_color:     tuple[int, int, int, int]  = (0, 0, 0, 180)   # RGBA
    text_color:    tuple[int, int, int]       = (255, 255, 255)   # RGB
    font_size:     int                        = 28
    font_path:     Optional[str]              = None


@dataclass
class AdConfig:
    """
    Optional advertisement strip for the composition pipeline.

    Ads always appear at the very bottom of the final image.
    ad_content: text string (AdType.TEXT) or local image path (AdType.IMAGE).
    """
    enable:           bool                   = False
    ad_type:          AdType                 = AdType.TEXT
    ad_content:       str                    = ""
    ad_height_ratio:  float                  = 0.10   # fraction of total image height
    background_color: tuple[int, int, int]   = (240, 240, 240)
    text_color:       tuple[int, int, int]   = (30, 30, 30)
    font_size:        int                    = 22
    font_path:        Optional[str]          = None


@dataclass
class ImageCompositionConfig:
    """
    Full configuration for the composition pipeline.

    Passed to compose_image(). All overlay stages are optional.
    output_dir: directory where the composed file is written.
                Defaults to /app/data/media/composed at runtime.
    """
    output_width:   int             = 1200
    output_height:  int             = 630
    output_format:  str             = "JPEG"    # JPEG | PNG | WEBP
    output_quality: int             = 88
    output_dir:     Optional[str]   = None
    branding:       BrandingConfig  = field(default_factory=BrandingConfig)
    ads:            AdConfig        = field(default_factory=AdConfig)


@dataclass(frozen=True)
class ComposedImageResult:
    """
    Result of compose_image().

    image_bytes: the fully composed image as raw bytes.
    local_path:  path where the file was written (if save_to_disk=True).
    width/height: always equal to ImageCompositionConfig.output_width/height on success.
    stages_applied: ordered list of pipeline stages that ran (e.g. ["base","branding","ads"]).
    """
    success:        bool
    image_bytes:    Optional[bytes]          = None
    local_path:     Optional[str]            = None
    width:          int                      = 0
    height:         int                      = 0
    format:         str                      = ""
    file_size_bytes: int                     = 0
    stages_applied: tuple[str, ...]          = field(default_factory=tuple)
    metadata:       Optional[ImageMetadata]  = None
    error:          str                      = ""


@dataclass
class FeaturedImageResult:
    """
    Result of the full featured-image pipeline.

    Mutable so pipeline stages can be appended during execution.
    composed: the final ComposedImageResult (frozen) once the pipeline completes.
    """
    success:         bool
    composed:        Optional[ComposedImageResult] = None
    source_used:     str                           = ""   # "stock" | "generated" | "mock"
    pipeline_stages: list[str]                     = field(default_factory=list)
    error:           str                           = ""
