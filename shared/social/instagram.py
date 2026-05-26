"""
Instagram publisher — mock implementation.

Real implementation will replace the mock block only.
Interface stays identical.
"""

import logging

logger = logging.getLogger(__name__)


def publish(content: dict) -> bool:
    """
    Publish content to Instagram.

    Args:
        content: {
            "title":     str,
            "text":      str,
            "image_url": str | None
        }

    Returns:
        True on success, False on failure.
    """
    title = content.get("title", "")
    text = content.get("text", "")
    image_url = content.get("image_url")

    # Instagram requires an image for feed posts — warn but don't hard-fail
    # so mock behavior stays clean during development
    if not image_url:
        logger.warning("Instagram publish called without image_url — real API will reject this")

    logger.info(
        "Instagram publish | title=%r | text_length=%d | has_image=%s",
        title,
        len(text),
        image_url is not None,
    )

    # --- MOCK: replace this block with real Graph API call ---
    logger.info("Instagram mock: post published successfully")
    return True
    # ---------------------------------------------------------
