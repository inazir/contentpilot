"""
Facebook Page publisher.

Supports PUBLISH_MODE=mock and PUBLISH_MODE=real.

Adapter contract:
    publish_post(content, target, image_url, mode) -> PublishResult

Never returns raw dicts or booleans.
Never raises generic exceptions.
Raises typed exceptions from shared.social.exceptions only.
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
_TIMEOUT = 30  # seconds


def publish_post(
    content: str,
    target: SocialTarget,
    image_url: str | None = None,
    mode: str = "mock",
) -> PublishResult:
    """
    Publish a text post to a Facebook Page.

    Args:
        content:   Post text. Required and non-empty.
        target:    SocialTarget with page_id and access_token.
        image_url: Optional image URL. Not used in v1 text-only posts.
        mode:      "mock" or "real"

    Returns:
        PublishResult with success status and post ID.
    """
    if not content.strip():
        raise ValidationError("content is empty", platform="facebook")

    if mode == "mock":
        return _mock_publish(content, target, image_url)

    if mode == "real":
        return _real_publish(content, target, image_url)

    raise ValueError(f"Unknown publish mode: {mode!r}")


# ---------------------------------------------------------------------------
# Mock
# ---------------------------------------------------------------------------


def _mock_publish(content: str, target: SocialTarget, image_url: str | None) -> PublishResult:
    fake_id = f"fb_mock_{uuid.uuid4().hex[:10]}"
    logger.debug(
        "Facebook mock publish | target=%s | post_id=%s | content_length=%d | has_image=%s",
        target.key, fake_id, len(content), image_url is not None,
    )
    return PublishResult(
        platform="facebook",
        success=True,
        external_post_id=fake_id,
        metadata={"mode": "mock", "target": target.key},
    )


# ---------------------------------------------------------------------------
# Real
# ---------------------------------------------------------------------------


def _real_publish(content: str, target: SocialTarget, image_url: str | None) -> PublishResult:
    if not target.enabled:
        raise ValidationError(
            f"Target {target.key} is disabled",
            platform="facebook",
        )
    if not target.page_id:
        raise ValidationError(
            f"Target {target.key} missing page_id",
            platform="facebook",
        )
    if not target.access_token:
        raise AuthError(
            f"Target {target.key} missing access_token",
            platform="facebook",
        )

    url = f"https://graph.facebook.com/{_GRAPH_API_VERSION}/{target.page_id}/feed"
    payload = {
        "message":      content,
        "access_token": target.access_token,
    }

    try:
        response = requests.post(url, data=payload, timeout=_TIMEOUT)
    except requests.Timeout:
        raise RetryablePublishError(
            f"Request timed out after {_TIMEOUT}s",
            platform="facebook",
        )
    except requests.RequestException as exc:
        raise RetryablePublishError(
            f"Network error: {exc}",
            platform="facebook",
        ) from exc

    return _handle_response(response, target)


def _handle_response(response: requests.Response, target: SocialTarget) -> PublishResult:
    """Parse Graph API response into a PublishResult or raise a typed exception."""

    # Rate limit
    if response.status_code == 429:
        raise RateLimitError(
            "Facebook rate limit hit",
            platform="facebook",
        )

    # Auth failures — not retryable
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

    # Server errors — retryable
    if response.status_code >= 500:
        raise RetryablePublishError(
            f"Facebook server error: HTTP {response.status_code}",
            platform="facebook",
        )

    # Non-200 catch-all
    if not response.ok:
        raise RetryablePublishError(
            f"Unexpected HTTP {response.status_code}: {response.text[:200]}",
            platform="facebook",
        )

    # Success
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
        metadata={"mode": "real", "target": target.key},
    )
