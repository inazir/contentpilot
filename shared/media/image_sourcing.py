# shared/media/image_sourcing.py
"""
Stock image sourcing abstraction.

All sourcing calls go through search_stock_image(). Providers are
registered in _REGISTRY. The mock provider requires only Pillow and
makes no network calls.

Attribution requirement
-----------------------
Stock image providers require attribution in many contexts. Always
preserve ImageMetadata.attribution and ImageMetadata.photographer in
publish flows and display them wherever the license demands it.

Adding a new provider
---------------------
1. Implement a function:
       def _my_provider(request: StockImageRequest) -> ImageProviderResponse
2. Register it:
       _REGISTRY[StockProvider.MY_PROVIDER] = _my_provider
"""

from __future__ import annotations

import io
import logging
import os
import time
from typing import Callable

from .models import (
    ImageMetadata,
    ImageProviderResponse,
    StockImageRequest,
    StockProvider,
)

logger = logging.getLogger(__name__)

_REQUEST_TIMEOUT = 20  # seconds for HTTP calls

_ProviderFn = Callable[[StockImageRequest], ImageProviderResponse]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def search_stock_image(request: StockImageRequest) -> ImageProviderResponse:
    """
    Search for a stock image matching the given keywords.

    Args:
        request: StockImageRequest with keywords, provider, and optional filters.

    Returns:
        ImageProviderResponse — never raises.
    """
    provider_fn = _REGISTRY.get(request.provider)
    if provider_fn is None:
        msg = (
            f"Unknown stock provider '{request.provider}'. "
            f"Valid options: {[p.value for p in _REGISTRY]}"
        )
        logger.error("search_stock_image | %s", msg)
        return ImageProviderResponse(success=False, provider=str(request.provider), error=msg)

    logger.info(
        "stock_image_search_start | provider=%s | keywords=%s",
        request.provider, request.keywords,
    )
    t_start = time.monotonic()

    try:
        response = provider_fn(request)
    except Exception as exc:
        duration = time.monotonic() - t_start
        logger.error(
            "stock_image_search_error | provider=%s | duration=%.2fs | error=%s",
            request.provider, duration, exc,
        )
        return ImageProviderResponse(
            success=False, provider=str(request.provider), error=str(exc),
        )

    duration = time.monotonic() - t_start
    if response.success:
        logger.info(
            "stock_image_search_ok | provider=%s | duration=%.2fs | bytes=%d",
            request.provider, duration,
            len(response.image_bytes) if response.image_bytes else 0,
        )
    else:
        logger.warning(
            "stock_image_search_failed | provider=%s | duration=%.2fs | error=%s",
            request.provider, duration, response.error,
        )
    return response


# ---------------------------------------------------------------------------
# Mock provider  (no network, Pillow only)
# ---------------------------------------------------------------------------


def _mock_provider(request: StockImageRequest) -> ImageProviderResponse:
    """
    Deterministic in-process mock provider.

    Generates a horizontal gradient PNG. The gradient colours are derived
    from the sorted keyword list so the same keywords always produce the
    same image bytes.
    """
    try:
        from PIL import Image
    except ImportError:
        return ImageProviderResponse(
            success=False, provider="mock",
            error="Pillow is not installed. Run: pip install pillow",
        )

    kw_hash = hash(tuple(sorted(request.keywords))) & 0xFFFFFF
    r1 = (kw_hash >> 16) & 0xFF
    g1 = (kw_hash >> 8) & 0xFF
    b1 = kw_hash & 0xFF
    # Simple complementary colour for the right edge of the gradient
    r2 = (r1 + 100) % 256
    g2 = (g1 + 80) % 256
    b2 = (b1 + 60) % 256

    W, H = 1200, 800
    img = Image.new("RGB", (W, H))
    px = img.load()
    for x in range(W):
        t = x / W
        col = (
            int(r1 + (r2 - r1) * t),
            int(g1 + (g2 - g1) * t),
            int(b1 + (b2 - b1) * t),
        )
        for y in range(H):
            px[x, y] = col

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)

    kw_str = " ".join(request.keywords)
    return ImageProviderResponse(
        success=True,
        provider="mock",
        image_bytes=buf.getvalue(),
        image_url=f"https://mock.contentpilot.local/stock?q={kw_str.replace(' ', '+')}",
        metadata=ImageMetadata(
            source="stock",
            provider="mock",
            original_url="https://mock.contentpilot.local/stock",
            attribution="Mock Stock Images — ContentPilot Test",
            photographer="Mock Photographer",
            license="ContentPilot Internal Test License",
            width=W,
            height=H,
            extra={"keywords": request.keywords},
        ),
    )


# ---------------------------------------------------------------------------
# Pexels provider
# ---------------------------------------------------------------------------


def _pexels_provider(request: StockImageRequest) -> ImageProviderResponse:
    """
    Pexels API — requires PEXELS_API_KEY environment variable.
    Returns the first matching result.
    """
    api_key = os.getenv("PEXELS_API_KEY", "").strip()
    if not api_key:
        return ImageProviderResponse(
            success=False, provider="pexels", error="PEXELS_API_KEY is not set",
        )

    try:
        import requests as req
    except ImportError:
        return ImageProviderResponse(
            success=False, provider="pexels", error="requests library not installed",
        )

    _ORIENTATION_MAP = {"landscape": "landscape", "portrait": "portrait", "square": "square"}
    orientation = _ORIENTATION_MAP.get(request.orientation, "landscape")

    try:
        resp = req.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": api_key},
            params={
                "query": " ".join(request.keywords),
                "orientation": orientation,
                "per_page": request.per_page,
                "size": "large",
            },
            timeout=_REQUEST_TIMEOUT,
        )
    except Exception as exc:
        return ImageProviderResponse(success=False, provider="pexels", error=str(exc))

    if not resp.ok:
        return ImageProviderResponse(
            success=False, provider="pexels",
            error=f"HTTP {resp.status_code}: {resp.text[:200]}",
        )

    photos = resp.json().get("photos", [])
    if not photos:
        return ImageProviderResponse(
            success=False, provider="pexels",
            error=f"No results for keywords: {request.keywords}",
        )

    photo = photos[0]
    image_url = photo["src"].get("large2x") or photo["src"].get("original", "")

    try:
        img_resp = req.get(image_url, timeout=30)
        img_resp.raise_for_status()
    except Exception as exc:
        return ImageProviderResponse(
            success=False, provider="pexels", error=f"Image download failed: {exc}",
        )

    photographer = photo.get("photographer", "")
    return ImageProviderResponse(
        success=True,
        provider="pexels",
        image_bytes=img_resp.content,
        image_url=image_url,
        metadata=ImageMetadata(
            source="stock",
            provider="pexels",
            original_url=image_url,
            attribution=f"Photo by {photographer} on Pexels",
            photographer=photographer,
            license="Pexels License",
            width=photo.get("width", 0),
            height=photo.get("height", 0),
            extra={"pexels_id": photo.get("id"), "pexels_url": photo.get("url", "")},
        ),
    )


# ---------------------------------------------------------------------------
# Unsplash provider
# ---------------------------------------------------------------------------


def _unsplash_provider(request: StockImageRequest) -> ImageProviderResponse:
    """
    Unsplash API — requires UNSPLASH_ACCESS_KEY environment variable.
    """
    access_key = os.getenv("UNSPLASH_ACCESS_KEY", "").strip()
    if not access_key:
        return ImageProviderResponse(
            success=False, provider="unsplash", error="UNSPLASH_ACCESS_KEY is not set",
        )

    try:
        import requests as req
    except ImportError:
        return ImageProviderResponse(
            success=False, provider="unsplash", error="requests library not installed",
        )

    _ORIENTATION_MAP = {"landscape": "landscape", "portrait": "portrait", "square": "squarish"}
    orientation = _ORIENTATION_MAP.get(request.orientation, "landscape")

    try:
        resp = req.get(
            "https://api.unsplash.com/search/photos",
            params={
                "query": " ".join(request.keywords),
                "orientation": orientation,
                "per_page": request.per_page,
                "client_id": access_key,
            },
            timeout=_REQUEST_TIMEOUT,
        )
    except Exception as exc:
        return ImageProviderResponse(success=False, provider="unsplash", error=str(exc))

    if not resp.ok:
        return ImageProviderResponse(
            success=False, provider="unsplash",
            error=f"HTTP {resp.status_code}: {resp.text[:200]}",
        )

    results = resp.json().get("results", [])
    if not results:
        return ImageProviderResponse(
            success=False, provider="unsplash",
            error=f"No results for keywords: {request.keywords}",
        )

    photo = results[0]
    image_url = photo["urls"].get("regular") or photo["urls"].get("full", "")

    try:
        img_resp = req.get(image_url, timeout=30)
        img_resp.raise_for_status()
    except Exception as exc:
        return ImageProviderResponse(
            success=False, provider="unsplash", error=f"Image download failed: {exc}",
        )

    user = photo.get("user", {})
    photographer = user.get("name", "")
    return ImageProviderResponse(
        success=True,
        provider="unsplash",
        image_bytes=img_resp.content,
        image_url=image_url,
        metadata=ImageMetadata(
            source="stock",
            provider="unsplash",
            original_url=image_url,
            attribution=f"Photo by {photographer} on Unsplash",
            photographer=photographer,
            license="Unsplash License",
            width=photo.get("width", 0),
            height=photo.get("height", 0),
            extra={
                "unsplash_id": photo.get("id"),
                "unsplash_url": photo.get("links", {}).get("html", ""),
            },
        ),
    )


# ---------------------------------------------------------------------------
# Pixabay provider
# ---------------------------------------------------------------------------


def _pixabay_provider(request: StockImageRequest) -> ImageProviderResponse:
    """
    Pixabay API — requires PIXABAY_API_KEY environment variable.
    """
    api_key = os.getenv("PIXABAY_API_KEY", "").strip()
    if not api_key:
        return ImageProviderResponse(
            success=False, provider="pixabay", error="PIXABAY_API_KEY is not set",
        )

    try:
        import requests as req
    except ImportError:
        return ImageProviderResponse(
            success=False, provider="pixabay", error="requests library not installed",
        )

    _ORIENTATION_MAP = {"landscape": "horizontal", "portrait": "vertical", "square": "all"}
    orientation = _ORIENTATION_MAP.get(request.orientation, "horizontal")

    try:
        resp = req.get(
            "https://pixabay.com/api/",
            params={
                "key": api_key,
                "q": "+".join(request.keywords),
                "orientation": orientation,
                "per_page": min(request.per_page, 20),
                "image_type": "photo",
                "safesearch": "true",
            },
            timeout=_REQUEST_TIMEOUT,
        )
    except Exception as exc:
        return ImageProviderResponse(success=False, provider="pixabay", error=str(exc))

    if not resp.ok:
        return ImageProviderResponse(
            success=False, provider="pixabay",
            error=f"HTTP {resp.status_code}: {resp.text[:200]}",
        )

    hits = resp.json().get("hits", [])
    if not hits:
        return ImageProviderResponse(
            success=False, provider="pixabay",
            error=f"No results for keywords: {request.keywords}",
        )

    photo = hits[0]
    image_url = photo.get("largeImageURL") or photo.get("webformatURL", "")

    try:
        img_resp = req.get(image_url, timeout=30)
        img_resp.raise_for_status()
    except Exception as exc:
        return ImageProviderResponse(
            success=False, provider="pixabay", error=f"Image download failed: {exc}",
        )

    user = photo.get("user", "")
    return ImageProviderResponse(
        success=True,
        provider="pixabay",
        image_bytes=img_resp.content,
        image_url=image_url,
        metadata=ImageMetadata(
            source="stock",
            provider="pixabay",
            original_url=image_url,
            attribution=f"Image by {user} on Pixabay",
            photographer=user,
            license="Pixabay License",
            width=photo.get("imageWidth", 0),
            height=photo.get("imageHeight", 0),
            extra={"pixabay_id": photo.get("id"), "tags": photo.get("tags", "")},
        ),
    )


# ---------------------------------------------------------------------------
# Provider registry
# ---------------------------------------------------------------------------


_REGISTRY: dict[StockProvider, _ProviderFn] = {
    StockProvider.MOCK:     _mock_provider,
    StockProvider.PEXELS:   _pexels_provider,
    StockProvider.UNSPLASH: _unsplash_provider,
    StockProvider.PIXABAY:  _pixabay_provider,
}
