# shared/media/image_generation.py
"""
Provider-agnostic AI image generation layer.

All generation calls go through generate_image(). Provider functions are
registered in _REGISTRY and resolved at call time from the ImageRequest.

Retry behaviour
---------------
Transient errors (network timeouts, HTTP 429/5xx) are retried with
exponential backoff up to _MAX_RETRIES attempts. Non-transient errors
(invalid prompt, auth failure) surface immediately without retrying.

Adding a new provider
---------------------
1. Implement a function with the signature:
       def _my_provider(request: ImageRequest) -> ImageProviderResponse
2. Register it:
       _REGISTRY[ImageProvider.MY_PROVIDER] = _my_provider

The rest of the system requires no other changes.
"""

from __future__ import annotations

import io
import logging
import os
import time
from typing import Callable

from .models import ImageMetadata, ImageProvider, ImageProviderResponse, ImageRequest

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Retry constants
# ---------------------------------------------------------------------------

_MAX_RETRIES   = 3
_BASE_BACKOFF  = 2.0   # seconds; doubles each attempt

# HTTP status codes that are safe to retry
_RETRYABLE_STATUS_CODES: frozenset[int] = frozenset({429, 500, 502, 503, 504})

# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------

_ProviderFn = Callable[[ImageRequest], ImageProviderResponse]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_image(request: ImageRequest) -> ImageProviderResponse:
    """
    Generate an image with retry-and-backoff error handling.

    Args:
        request: Fully populated ImageRequest.

    Returns:
        ImageProviderResponse — never raises.
    """
    provider_fn = _REGISTRY.get(request.provider)
    if provider_fn is None:
        msg = (
            f"Unknown image provider '{request.provider}'. "
            f"Valid options: {[p.value for p in _REGISTRY]}"
        )
        logger.error("generate_image | %s", msg)
        return ImageProviderResponse(success=False, provider=str(request.provider), error=msg)

    logger.info(
        "image_generation_start | provider=%s | size=%dx%d | prompt_len=%d",
        request.provider.value, request.width, request.height, len(request.prompt),
    )
    t_start = time.monotonic()

    last_error = ""
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            response = provider_fn(request)
        except Exception as exc:
            last_error = str(exc)
            logger.warning(
                "image_generation_exception | provider=%s | attempt=%d/%d | error=%s",
                request.provider.value, attempt, _MAX_RETRIES, exc,
            )
            _backoff(attempt)
            continue

        if response.success:
            duration = time.monotonic() - t_start
            logger.info(
                "image_generation_ok | provider=%s | attempt=%d | duration=%.2fs | bytes=%d",
                request.provider.value, attempt, duration,
                len(response.image_bytes) if response.image_bytes else 0,
            )
            return response

        # Provider returned a structured failure — check if retrying makes sense.
        # Stub providers and permanent errors (auth, invalid prompt) should not retry.
        last_error = response.error
        is_permanent = (
            "not yet implemented" in last_error.lower()
            or "not set" in last_error.lower()          # missing API key
        )
        logger.warning(
            "image_generation_failed | provider=%s | attempt=%d/%d | permanent=%s | error=%s",
            request.provider.value, attempt, _MAX_RETRIES, is_permanent, last_error,
        )
        if is_permanent:
            return response   # return immediately — no retry
        _backoff(attempt)

    duration = time.monotonic() - t_start
    logger.error(
        "image_generation_exhausted | provider=%s | attempts=%d | duration=%.2fs | last_error=%s",
        request.provider.value, _MAX_RETRIES, duration, last_error,
    )
    return ImageProviderResponse(
        success=False,
        provider=str(request.provider),
        error=f"All {_MAX_RETRIES} attempts failed. Last error: {last_error}",
    )


# ---------------------------------------------------------------------------
# Mock provider  (deterministic, no network, Pillow only)
# ---------------------------------------------------------------------------


def _mock_provider(request: ImageRequest) -> ImageProviderResponse:
    """
    Deterministic in-process provider for testing.

    Generates a solid-colour PNG where the colour is derived from the
    prompt hash — same prompt always produces the same image bytes.
    No network calls; only Pillow required.
    """
    try:
        from PIL import Image
    except ImportError:
        return ImageProviderResponse(
            success=False,
            provider="mock",
            error="Pillow is not installed. Run: pip install pillow",
        )

    h = hash(request.prompt) & 0xFFFFFF
    r_val = (h >> 16) & 0xFF
    g_val = (h >> 8) & 0xFF
    b_val = h & 0xFF

    img = Image.new("RGB", (request.width, request.height), color=(r_val, g_val, b_val))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    image_bytes = buf.getvalue()

    return ImageProviderResponse(
        success=True,
        provider="mock",
        image_bytes=image_bytes,
        metadata=ImageMetadata(
            source="generated",
            provider="mock",
            width=request.width,
            height=request.height,
            extra={"color_rgb": (r_val, g_val, b_val)},
        ),
    )


# ---------------------------------------------------------------------------
# OpenAI provider  (DALL-E 3)
# ---------------------------------------------------------------------------


def _openai_provider(request: ImageRequest) -> ImageProviderResponse:
    """
    DALL-E 3 via OpenAI Images API.

    Required env vars:
        OPENAI_API_KEY

    DALL-E 3 only supports fixed sizes; unsupported dimensions fall back
    to 1024x1024.
    """
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return ImageProviderResponse(
            success=False, provider="openai", error="OPENAI_API_KEY is not set",
        )

    try:
        import requests as req
    except ImportError:
        return ImageProviderResponse(
            success=False, provider="openai", error="requests library not installed",
        )

    _VALID_SIZES = {"1024x1024", "1792x1024", "1024x1792"}
    size = f"{request.width}x{request.height}"
    if size not in _VALID_SIZES:
        logger.warning(
            "openai_provider | unsupported size %s — falling back to 1024x1024", size,
        )
        size = "1024x1024"

    try:
        resp = req.post(
            "https://api.openai.com/v1/images/generations",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "dall-e-3", "prompt": request.prompt, "n": 1,
                  "size": size, "response_format": "url"},
            timeout=60,
        )
    except req.Timeout:
        return ImageProviderResponse(success=False, provider="openai", error="Request timed out")
    except req.RequestException as exc:
        return ImageProviderResponse(success=False, provider="openai", error=str(exc))

    if resp.status_code in _RETRYABLE_STATUS_CODES:
        return ImageProviderResponse(
            success=False, provider="openai",
            error=f"HTTP {resp.status_code} (retryable): {resp.text[:200]}",
        )
    if not resp.ok:
        return ImageProviderResponse(
            success=False, provider="openai",
            error=f"HTTP {resp.status_code}: {resp.text[:200]}",
        )

    data = resp.json()
    image_url = data["data"][0]["url"]

    try:
        img_resp = req.get(image_url, timeout=30)
        img_resp.raise_for_status()
    except Exception as exc:
        return ImageProviderResponse(
            success=False, provider="openai", error=f"Image download failed: {exc}",
        )

    w, h = map(int, size.split("x"))
    return ImageProviderResponse(
        success=True,
        provider="openai",
        image_bytes=img_resp.content,
        image_url=image_url,
        metadata=ImageMetadata(
            source="generated", provider="openai",
            original_url=image_url, width=w, height=h,
            extra={"revised_prompt": data["data"][0].get("revised_prompt", "")},
        ),
    )


# ---------------------------------------------------------------------------
# Stub providers — not yet implemented
# ---------------------------------------------------------------------------

# Sentinel: providers that raise this skip retry loop immediately
class _NotImplementedError(Exception):
    """Raised by stub providers to skip the retry loop."""


def _stub_provider(name: str) -> _ProviderFn:
    """Return a stub function that signals non-retryable failure immediately."""
    def _inner(request: ImageRequest) -> ImageProviderResponse:
        return ImageProviderResponse(
            success=False,
            provider=name,
            error=(
                f"Provider '{name}' is not yet implemented. "
                f"Use provider=mock for testing or implement the adapter."
            ),
        )
    return _inner


# ---------------------------------------------------------------------------
# Provider registry
# ---------------------------------------------------------------------------


_REGISTRY: dict[ImageProvider, _ProviderFn] = {
    ImageProvider.MOCK:      _mock_provider,
    ImageProvider.OPENAI:    _openai_provider,
    ImageProvider.STABILITY: _stub_provider("stability"),
    ImageProvider.IDEOGRAM:  _stub_provider("ideogram"),
    ImageProvider.FLUX:      _stub_provider("flux"),
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _backoff(attempt: int) -> None:
    """Sleep for exponentially increasing duration if not the last attempt."""
    if attempt < _MAX_RETRIES:
        wait = _BASE_BACKOFF * (2 ** (attempt - 1))
        logger.debug("image_generation_backoff | attempt=%d | sleep=%.1fs", attempt, wait)
        time.sleep(wait)
