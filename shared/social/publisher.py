# shared/social/publisher.py
"""
Orchestrates publishing across social targets.

Phase 12A: supports image_bytes in content dict for image publishing.

content dict schema:
    {
        "title":       str,
        "text":        str,
        "image_url":   str | None,   # legacy, passed through
        "image_bytes": bytes | None, # Phase 12A: raw image for direct upload
        "image_name":  str | None,   # optional filename for logging
    }
"""

import logging

from shared.config import get_publish_mode, load_social_targets
from shared.store import already_published, compute_content_hash, record_publish

from .exceptions import PublishError
from .models import PublishResult, PublishSummary
from . import facebook, instagram

logger = logging.getLogger(__name__)

_ADAPTERS = {
    "facebook":  facebook,
    "instagram": instagram,
}


def publish_post(
    content: dict,
    targets: list[str],
    module_name: str,
) -> PublishSummary:
    """
    Publish content to all requested targets.

    Args:
        content:     {
                       "title": str,
                       "text": str,
                       "image_url": str | None,
                       "image_bytes": bytes | None,  # Phase 12A
                       "image_name": str | None,     # Phase 12A, for logging
                     }
        targets:     list of target keys
        module_name: used for store tracking and logging

    Returns:
        PublishSummary — never raises.
    """
    summary = PublishSummary(module_name=module_name)
    mode = get_publish_mode()

    if mode == "disabled":
        logger.info("PUBLISH_MODE=disabled — skipping all publishing")
        return summary

    text         = content.get("text", "")
    image_url    = content.get("image_url")
    image_bytes  = content.get("image_bytes")
    image_name   = content.get("image_name", "image.jpg")
    content_hash = compute_content_hash(text)

    if image_bytes:
        logger.info(
            "social_image_selected | filename=%s | size=%d",
            image_name, len(image_bytes),
        )

    all_targets = load_social_targets()

    for target_key in targets:
        target_key = target_key.strip().lower()
        result = _publish_one(
            target_key   = target_key,
            text         = text,
            image_url    = image_url,
            image_bytes  = image_bytes,
            image_name   = image_name,
            content_hash = content_hash,
            module_name  = module_name,
            mode         = mode,
            all_targets  = all_targets,
        )
        summary.results.append(result)

    return summary


def _publish_one(
    target_key:   str,
    text:         str,
    image_url:    str | None,
    image_bytes:  bytes | None,
    image_name:   str,
    content_hash: str,
    module_name:  str,
    mode:         str,
    all_targets:  dict,
) -> PublishResult:
    target = all_targets.get(target_key)
    if target is None:
        logger.error("Unknown target=%r", target_key)
        return PublishResult(
            platform="unknown",
            success=False,
            error_message=f"Unknown target '{target_key}'",
            metadata={"target": target_key},
        )

    adapter = _ADAPTERS.get(target.platform)
    if adapter is None:
        logger.error("Unknown platform=%r for target=%r", target.platform, target_key)
        return PublishResult(
            platform=target.platform,
            success=False,
            error_message=f"Unknown platform '{target.platform}'",
            metadata={"target": target_key},
        )

    if mode == "real" and not target.enabled:
        logger.info("Target %s is disabled — skipping", target_key)
        return PublishResult(
            platform=target.platform,
            success=False,
            error_message=f"Target {target_key} is disabled",
            metadata={"target": target_key, "skipped": True},
        )

    if already_published(content_hash, target_key):
        logger.info(
            "Duplicate skipped | target=%s | module=%s | hash=%s",
            target_key, module_name, content_hash[:12],
        )
        return PublishResult(
            platform=target.platform,
            success=True,
            external_post_id="[duplicate:skipped]",
            metadata={"target": target_key, "duplicate": True},
        )

    try:
        # Pass image_bytes to adapter — each adapter decides how to use it
        result = adapter.publish_post(
            content     = text,
            target      = target,
            image_url   = image_url,
            mode        = mode,
            image_bytes = image_bytes,
        )

        record_publish(
            content_hash     = content_hash,
            target_key       = target_key,
            platform         = target.platform,
            module_name      = module_name,
            status           = "success" if result.success else "failed",
            external_post_id = result.external_post_id,
        )

        return result

    except PublishError as exc:
        logger.error(
            "Publish failed | target=%s | retryable=%s | error=%s",
            target_key, exc.retryable, exc,
        )
        record_publish(
            content_hash = content_hash,
            target_key   = target_key,
            platform     = target.platform,
            module_name  = module_name,
            status       = "failed",
            error_message= str(exc),
        )
        return PublishResult(
            platform      = target.platform,
            success       = False,
            error_message = str(exc),
            retryable     = exc.retryable,
            metadata      = {"target": target_key},
        )

    except NotImplementedError as exc:
        logger.error("Platform %s not implemented: %s", target.platform, exc)
        return PublishResult(
            platform      = target.platform,
            success       = False,
            error_message = str(exc),
            retryable     = False,
            metadata      = {"target": target_key},
        )

    except Exception as exc:
        logger.exception(
            "Unexpected error publishing to target %s: %s", target_key, exc
        )
        return PublishResult(
            platform      = target.platform,
            success       = False,
            error_message = f"Unexpected: {exc}",
            retryable     = True,
            metadata      = {"target": target_key},
        )
