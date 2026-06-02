"""
Facebook Page publisher — Phase 12A.

Supports:
- PUBLISH_MODE=mock
- PUBLISH_MODE=real (text-only via /feed)
- PUBLISH_MODE=real (image+caption via /photos)

Image publishing uses the /photos endpoint.
Falls back to text-only /feed if image upload fails.
"""

import logging
import uuid

import requests

from shared.config import SocialTarget
from .exceptions import (
    AuthError,
    RateLimitError,
    RetryablePublishError,
    ValidationError,
)
from .models import PublishResult

logger = logging.getLogger(__name__)

_GRAPH_API_VERSION = "v23.0"
_TIMEOUT = 30


def publish_post(
    content: str,
    target: SocialTarget,
    image_url: str | None = None,
    mode: str = "mock",
    image_bytes: bytes | None = None,
) -> PublishResult:
    """
    Publish a post to a Facebook Page.

    Args:
        content:     Post text/caption.
        target:      SocialTarget with page_id and access_token.
        image_url:   Optional image URL (not used — kept for interface compat).
        mode:        "mock" or "real"
        image_bytes: Raw image bytes. When provided in real mode,
                     publishes via /photos endpoint instead of /feed.

    Returns:
        PublishResult — never raises.
    """
    if not content.strip():
        raise ValidationError("content is empty", platform="facebook")

    if mode == "mock":
        return _mock_publish(content, target, image_bytes)

    if mode == "real":
        if image_bytes:
            return _real_publish_with_photo(content, target, image_bytes)
        return _real_publish_text(content, target)

    raise ValueError(f"Unknown publish mode: {mode!r}")


# ---------------------------------------------------------------------------
# Mock
# ---------------------------------------------------------------------------

def _mock_publish(
    content: str,
    target: SocialTarget,
    image_bytes: bytes | None,
) -> PublishResult:
    fake_id = f"fb_mock_{uuid.uuid4().hex[:10]}"
    has_image = image_bytes is not None and len(image_bytes) > 0
    logger.debug(
        "Facebook mock publish | target=%s | post_id=%s | content_length=%d | has_image=%s",
        target.key, fake_id, len(content), has_image,
    )
    return PublishResult(
        platform="facebook",
        success=True,
        external_post_id=fake_id,
        metadata={
            "mode": "mock",
            "target": target.key,
            "has_image": has_image,
        },
    )


# ---------------------------------------------------------------------------
# Real — text only (/feed)
# ---------------------------------------------------------------------------

def _real_publish_text(content: str, target: SocialTarget) -> PublishResult:
    if not target.enabled:
        raise ValidationError(f"Target {target.key} is disabled", platform="facebook")
    if not target.page_id:
        raise ValidationError(f"Target {target.key} missing page_id", platform="facebook")
    if not target.access_token:
        raise AuthError(f"Target {target.key} missing access_token", platform="facebook")

    url = f"https://graph.facebook.com/{_GRAPH_API_VERSION}/{target.page_id}/feed"
    payload = {
        "message":      content,
        "access_token": target.access_token,
    }

    logger.info(
        "facebook_text_publish_start | target=%s | content_length=%d",
        target.key, len(content),
    )

    try:
        response = requests.post(url, data=payload, timeout=_TIMEOUT)
    except requests.Timeout:
        raise RetryablePublishError(f"Request timed out after {_TIMEOUT}s", platform="facebook")
    except requests.RequestException as exc:
        raise RetryablePublishError(f"Network error: {exc}", platform="facebook") from exc

    return _handle_feed_response(response, target)


# ---------------------------------------------------------------------------
# Real — image + caption (/photos)
# ---------------------------------------------------------------------------

def _real_publish_with_photo(
    content: str,
    target: SocialTarget,
    image_bytes: bytes,
) -> PublishResult:
    """
    Publish image + caption using the /photos endpoint.
    Falls back to text-only /feed if photo upload fails.
    """
    if not target.enabled:
        raise ValidationError(f"Target {target.key} is disabled", platform="facebook")
    if not target.page_id:
        raise ValidationError(f"Target {target.key} missing page_id", platform="facebook")
    if not target.access_token:
        raise AuthError(f"Target {target.key} missing access_token", platform="facebook")

    url = f"https://graph.facebook.com/{_GRAPH_API_VERSION}/{target.page_id}/photos"

    logger.info(
        "facebook_image_upload_start | target=%s | image_size=%d | content_length=%d",
        target.key, len(image_bytes), len(content),
    )

    try:
        response = requests.post(
            url,
            data={
                "caption":      content,
                "access_token": target.access_token,
            },
            files={
                "source": ("facebook_landscape.jpg", image_bytes, "image/jpeg"),
            },
            timeout=_TIMEOUT,
        )
    except requests.Timeout:
        logger.warning(
            "facebook_image_upload_timeout | target=%s | falling_back_to_text",
            target.key,
        )
        return _real_publish_text(content, target)
    except requests.RequestException as exc:
        logger.warning(
            "facebook_image_upload_network_error | target=%s | error=%s | falling_back_to_text",
            target.key, exc,
        )
        return _real_publish_text(content, target)

    # Auth / validation errors — do not fall back, these won't fix themselves
    if response.status_code in {400, 401, 403}:
        return _handle_feed_response(response, target)

    # Server errors — fall back to text
    if response.status_code >= 500 or not response.ok:
        logger.warning(
            "facebook_image_upload_failed | target=%s | http=%d | falling_back_to_text",
            target.key, response.status_code,
        )
        return _real_publish_text(content, target)

    # Success
    try:
        body = response.json()
        post_id = body.get("post_id") or body.get("id")
    except Exception:
        logger.warning(
            "facebook_image_upload_parse_error | target=%s | falling_back_to_text",
            target.key,
        )
        return _real_publish_text(content, target)

    if not post_id:
        logger.warning(
            "facebook_image_upload_missing_id | target=%s | falling_back_to_text",
            target.key,
        )
        return _real_publish_text(content, target)

    logger.info(
        "facebook_image_publish_success | target=%s | post_id=%s | image_size=%d",
        target.key, post_id, len(image_bytes),
    )

    return PublishResult(
        platform="facebook",
        success=True,
        external_post_id=str(post_id),
        metadata={
            "mode": "real",
            "target": target.key,
            "has_image": True,
            "image_size": len(image_bytes),
        },
    )


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------

def _handle_feed_response(
    response: requests.Response,
    target: SocialTarget,
) -> PublishResult:
    if response.status_code == 429:
        raise RateLimitError("Facebook rate limit hit", platform="facebook")

    if response.status_code in {400, 401, 403}:
        try:
            body = response.json()
            error = body.get("error", {})
            msg = error.get("message", response.text[:200])
            code = error.get("code", response.status_code)
        except Exception:
            msg = response.text[:200]
            code = response.status_code
        raise AuthError(
            f"Auth/permission error (code={code}): {msg}",
            platform="facebook",
        )

    if response.status_code >= 500:
        raise RetryablePublishError(
            f"Facebook server error: HTTP {response.status_code}",
            platform="facebook",
        )

    if not response.ok:
        raise RetryablePublishError(
            f"Unexpected HTTP {response.status_code}: {response.text[:200]}",
            platform="facebook",
        )

    try:
        body = response.json()
        post_id = body.get("id")
    except Exception:
        raise RetryablePublishError(
            "Could not parse success response as JSON",
            platform="facebook",
        )

    if not post_id:
        raise RetryablePublishError(
            f"Success response missing post ID: {response.text[:200]}",
            platform="facebook",
        )

    logger.info(
        "Facebook post published | target=%s | post_id=%s",
        target.key, post_id,
    )

    return PublishResult(
        platform="facebook",
        success=True,
        external_post_id=str(post_id),
        metadata={"mode": "real", "target": target.key, "has_image": False},
    )
