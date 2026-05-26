"""
Facebook publisher — mock implementation.

Real implementation will replace _publish() body only.
Interface stays identical.
"""

import logging

logger = logging.getLogger(__name__)


def publish(content: dict) -> bool:
    """
    Publish content to Facebook.

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

    logger.info(
        "Facebook publish | title=%r | text_length=%d | has_image=%s",
        title,
        len(text),
        image_url is not None,
    )

    # --- MOCK: replace this block with real Graph API call ---
    logger.info("Facebook mock: post published successfully")
    return True
    # ---------------------------------------------------------
