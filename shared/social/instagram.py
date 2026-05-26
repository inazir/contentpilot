"""
Instagram publisher — mock implementation.

Real implementation will replace the mock block only.
Interface stays identical.
"""

import logging
import uuid

from .exceptions import ValidationError

logger = logging.getLogger(__name__)


def publish(content: dict, mode: str) -> tuple[bool, str | None, str | None]:
    """
    Publish content to Instagram.

    Args:
        content: {
            "title":     str,
            "text":      str,
            "image_url": str | None
        }
        mode: "mock" or "real"

    Returns:
        (success, external_post_id, error_message)
    """
    text = content.get("text", "").strip()
    if not text:
        raise ValidationError("text is empty", platform="instagram")

    if not content.get("image_url"):
        logger.warning(
            "Instagram publish has no image_url — real API will reject this"
        )

    if mode == "real":
        raise NotImplementedError(
            "Instagram real API not implemented yet. Set PUBLISH_MODE=mock."
        )

    fake_id = f"ig_mock_{uuid.uuid4().hex[:10]}"
    logger.info(
        "Instagram mock publish | post_id=%s | text_length=%d | has_image=%s",
        fake_id,
        len(text),
        content.get("image_url") is not None,
    )
    return True, fake_id, None
