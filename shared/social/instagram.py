"""
Instagram publisher — mock only for now.

Adapter contract:
    publish_post(content, target, image_url, mode) -> PublishResult
"""

import logging
import uuid

from shared.config import SocialTarget
from .exceptions import ValidationError
from .models import PublishResult

logger = logging.getLogger(__name__)


def publish_post(
    content: str,
    target: SocialTarget,
    image_url: str | None = None,
    mode: str = "mock",
) -> PublishResult:
    if not content.strip():
        raise ValidationError("content is empty", platform="instagram")

    if not image_url:
        logger.warning(
            "Instagram publish called without image_url — real API will reject this | target=%s",
            target.key,
        )

    if mode == "real":
        raise NotImplementedError(
            "Instagram real publishing not implemented yet. "
            "Set PUBLISH_MODE=mock or target.enabled=false."
        )

    return _mock_publish(content, target, image_url)


def _mock_publish(content: str, target: SocialTarget, image_url: str | None) -> PublishResult:
    fake_id = f"ig_mock_{uuid.uuid4().hex[:10]}"
    logger.debug(
        "Instagram mock publish | target=%s | post_id=%s | content_length=%d | has_image=%s",
        target.key, fake_id, len(content), image_url is not None,
    )
    return PublishResult(
        platform="instagram",
        success=True,
        external_post_id=fake_id,
        metadata={"mode": "mock", "target": target.key},
    )
