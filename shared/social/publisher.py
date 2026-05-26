# shared/social/publisher.py
"""
Unified social publishing entry point.

Modules call publish_post() without knowing which platform
implementation is used. Adding a new platform means:
  1. Create shared/social/newplatform.py with publish(content) -> bool
  2. Add one entry to _PUBLISHERS below

Nothing else changes.
"""

import logging
from typing import Optional

from .exceptions import PublishError
from . import facebook, instagram

logger = logging.getLogger(__name__)

# Registry: platform name → module with publish(content) -> bool
_PUBLISHERS = {
    "facebook": facebook,
    "instagram": instagram,
}


def publish_post(
    platform: str,
    content: dict,
) -> bool:
    """
    Publish content to a social platform.

    Args:
        platform: "facebook" or "instagram"
        content: {
            "title":     str,
            "text":      str,
            "image_url": Optional[str]
        }

    Returns:
        True on success, False on failure.

    Raises:
        ValueError: If platform is not registered.
    """
    platform = platform.strip().lower()

    publisher = _PUBLISHERS.get(platform)
    if publisher is None:
        raise ValueError(
            f"Unknown platform '{platform}'. "
            f"Registered: {list(_PUBLISHERS.keys())}"
        )

    _validate_content(content)

    try:
        success = publisher.publish(content)
        if success:
            logger.info("Published to %s successfully", platform)
        else:
            logger.warning("Publish to %s returned False", platform)
        return success

    except Exception as exc:
        logger.error("Publish to %s failed: %s", platform, exc)
        raise PublishError(str(exc), platform=platform) from exc


def _validate_content(content: dict) -> None:
    """Fail fast on missing required fields before hitting any API."""
    if not content.get("text", "").strip():
        raise ValueError("content['text'] is required and cannot be empty")
