# shared/social/publisher.py
"""
Orchestrates publishing across social targets.

Responsibilities:
- read publish mode from environment
- load all social targets from config
- check duplicates via shared/store
- call platform adapters with target info
- catch and classify exceptions
- record publish attempts in SQLite
- return aggregated results without crashing the caller
"""

import logging

from shared.config import (
    get_publish_mode,
    load_social_targets,
)
from shared.store import already_published, compute_content_hash, record_publish

from .exceptions import PublishError
from .models import PublishResult, PublishSummary
from . import facebook, instagram

logger = logging.getLogger(__name__)

# Registry maps platform name → adapter module
# Each adapter must expose: publish_post(content, target, image_url, mode) -> PublishResult
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
        content:     {"title": str, "text": str, "image_url": Optional[str]}
        targets:     list of target keys, e.g. ["gs_facebook_main", "gs_instagram_main"]
        module_name: used for store tracking and logging

    Returns:
        PublishSummary — never raises.
    """
    summary = PublishSummary(module_name=module_name)
    mode = get_publish_mode()

    if mode == "disabled":
        logger.info("PUBLISH_MODE=disabled — skipping all publishing")
        return summary

    text      = content.get("text", "")
    image_url = content.get("image_url")
    content_hash = compute_content_hash(text)

    # Load all available targets from config
    all_targets = load_social_targets()

    for target_key in targets:
        target_key = target_key.strip().lower()
        result   = _publish_one(
            target_key=target_key,
            text=text,
            image_url=image_url,
            content_hash=content_hash,
            module_name=module_name,
            mode=mode,
            all_targets=all_targets,
        )
        summary.results.append(result)

    return summary


def _publish_one(
    target_key: str,
    text: str,
    image_url: str | None,
    content_hash: str,
    module_name: str,
    mode: str,
    all_targets: dict,
) -> PublishResult:
    """Publish to a single target. Always returns a PublishResult."""

    # Resolve target from registry
    target = all_targets.get(target_key)
    if target is None:
        logger.error("Unknown target=%r", target_key)
        return PublishResult(
            platform="unknown",
            success=False,
            error_message=f"Unknown target '{target_key}'",
            metadata={"target": target_key},
        )

    # Get adapter for platform
    adapter = _ADAPTERS.get(target.platform)
    if adapter is None:
        logger.error("Unknown platform=%r for target=%r", target.platform, target_key)
        return PublishResult(
            platform=target.platform,
            success=False,
            error_message=f"Unknown platform '{target.platform}'",
            metadata={"target": target_key},
        )

    # Check target enabled flag (only enforced in real mode)
    if mode == "real" and not target.enabled:
        logger.info("Target %s is disabled — skipping", target_key)
        return PublishResult(
            platform=target.platform,
            success=False,
            error_message=f"Target {target_key} is disabled",
            metadata={"target": target_key, "skipped": True},
        )

    # Duplicate check
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

    # Call adapter with target
    try:
        result = adapter.publish_post(
            content=text, 
            target=target,
            image_url=image_url, 
            mode=mode
        )

        record_publish(
            content_hash=content_hash,
            target_key=target_key,
            platform=target.platform,
            module_name=module_name,
            status="success" if result.success else "failed",
            external_post_id=result.external_post_id,
        )

        return result

    except PublishError as exc:
        logger.error(
            "Publish failed | target=%s | retryable=%s | error=%s",
            target_key, exc.retryable, exc,
        )
        record_publish(
            content_hash=content_hash,
            target_key=target_key,
            platform=target.platform,
            module_name=module_name,
            status="failed",
            error_message=str(exc),
        )
        return PublishResult(
            platform=target.platform,
            success=False,
            error_message=str(exc),
            retryable=exc.retryable,
            metadata={"target": target_key},
        )

    except NotImplementedError as exc:
        logger.error("Platform %s not implemented: %s", target.platform, exc)
        return PublishResult(
            platform=target.platform,
            success=False,
            error_message=str(exc),
            retryable=False,
            metadata={"target": target_key},
        )

    except Exception as exc:
        logger.exception("Unexpected error publishing to target %s: %s", target_key, exc)
        return PublishResult(
            platform=target.platform,
            success=False,
            error_message=f"Unexpected: {exc}",
            retryable=True,
            metadata={"target": target_key},
        )
