# shared/media/__init__.py
"""
ContentPilot Media Layer — Phase 10 (10A + 10B combined).

Public API
----------

Phase 10A — Foundation:
    from shared.media import generate_image
    from shared.media import search_stock_image
    from shared.media import image_processing          # module-level import
    from shared.media import format_for_social
    from shared.media.models import (
        ImageRequest, ImageProvider,
        StockImageRequest, StockProvider,
        ImageMetadata, ImageProviderResponse, ImageResult,
        SocialFormat, SocialImageResult,
    )

Phase 10B — Composition engine:
    from shared.media import compose_image
    from shared.media import get_featured_image
    from shared.media.models import (
        BrandingConfig, AdConfig, AdType, LogoPosition,
        ImageCompositionConfig,
        ComposedImageResult,
        FeaturedImageResult,
    )
"""

# Phase 10A
from .image_generation import generate_image
from .image_sourcing import search_stock_image
from .social_formatter import format_for_social
from . import image_processing

# Phase 10B
# Phase 10B exports are intentionally omitted in Phase 10A.

__all__ = [
    # 10A
    "generate_image",
    "search_stock_image",
    "format_for_social",
    "image_processing",
]
