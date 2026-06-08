# shared/social/publisher.py
"""
Orchestrates publishing across social targets.

Phase 13B: BrandContext-aware publishing.

Both call signatures are supported:

    publish_post(content, targets, module_name)                        # legacy
    publish_post(content, targets, module_name, brand_context=ctx)     # preferred

When brand_context is provided:
  - publish mode comes from ctx.publish_mode (falls back to PUBLISH_MODE env)
  - social targets are resolved using ctx.social_targets if targets list is empty
  - every log line includes brand_id and brand_slug

When brand_context is None:
  - behavior is identical to Phase 12 (fully env-driven)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from shared.config import (
    get_publish_mode,
    load_social_targets,
)
from shared.store import already_published, compute_content_hash, record_publish

from .exceptions import PublishError
from .models import PublishResult, PublishSummary
from . import facebook, instagram

if TYPE_CHECKING:
    from shared.brands.models import BrandContext

logger = logging.getLogger(__name__)

_ADAPTERS = {
    "facebook":  facebook,
    "instagram": instagram,
}


def publish_post(
    content: dict,
    targets: list[str],
    module_name: str,
    brand_context: Optional["BrandContext"] = None,
) -> PublishSummary:
    """
    Publish content to all requested targets.

    Args:
        content:       {"title": str, "text": str, "image_url": Optional[str], ...}
        targets:       list of target keys; if empty and brand_context provided,
                       uses brand_context.social_targets
        module_name:   used for store tracking and logging
        brand_context: optional BrandContext; when provided, enables brand-aware
                       publish mode resolution and logging

    Returns:
        PublishSummary — never raises.
    """
    summary = PublishSummary(module_name=module_name)

    # Resolve publish mode: BrandContext > env
    if brand_context and brand_context.publish_mode:
        mode = brand_context.publish_mode.strip().lower()
    else:
        mode = get_publish_mode()

    if mode == "disabled":
        logger.info(
            "publish_disabled | mode=disabled | module=%s%s",
            module_name,
            f" | brand_id={brand_context.brand_id} | brand_slug={brand_context.brand_slug}"
            if brand_context else "",
        )
        return summary

    # Resolve targets: explicit list > brand_context.social_targets > env
    resolved_targets = targets
    if not resolved_targets and brand_context and brand_context.social_targets:
        resolved_targets = brand_context.social_targets

    text         = content.get("text", "")
    image_url    = content.get("image_url")
    image_bytes  = content.get("image_bytes")
    image_name   = content.get("image_name", "")
    content_hash = compute_content_hash(text)

    all_targets = load_social_targets()

    for target_key in resolved_targets:
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
            brand_context = brand_context,
        )
        summary.results.append(result)

    return summary


def _publish_one(
    target_key:    str,
    text:          str,
    image_url:     Optional[str],
    image_bytes:   Optional[bytes],
    image_name:    str,
    content_hash:  str,
    module_name:   str,
    mode:          str,
    all_targets:   dict,
    brand_context: Optional["BrandContext"],
) -> PublishResult:
    """Publish to a single target. Always returns a PublishResult."""

    brand_log = ""
    if brand_context:
        brand_log = f" | brand_id={brand_context.brand_id} | brand_slug={brand_context.brand_slug}"

    target = all_targets.get(target_key)
    if target is None:
        logger.error("Unknown target=%r%s", target_key, brand_log)
        return PublishResult(
            platform="unknown",
            success=False,
            error_message=f"Unknown target '{target_key}'",
            metadata={"target": target_key},
        )

    adapter = _ADAPTERS.get(target.platform)
    if adapter is None:
        logger.error(
            "Unknown platform=%r for target=%r%s", target.platform, target_key, brand_log
        )
        return PublishResult(
            platform=target.platform,
            success=False,
            error_message=f"Unknown platform '{target.platform}'",
            metadata={"target": target_key},
        )

    if mode == "real" and not target.enabled:
        logger.info("Target %s is disabled — skipping%s", target_key, brand_log)
        return PublishResult(
            platform=target.platform,
            success=False,
            error_message=f"Target {target_key} is disabled",
            metadata={"target": target_key, "skipped": True},
        )

    if already_published(content_hash, target_key):
        logger.info(
            "duplicate_skipped | target=%s | module=%s | hash=%s%s",
            target_key, module_name, content_hash[:12], brand_log,
        )
        return PublishResult(
            platform=target.platform,
            success=True,
            external_post_id="[duplicate:skipped]",
            metadata={"target": target_key, "duplicate": True},
        )

    try:
        result = adapter.publish_post(
            content     = text,
            target      = target,
            image_url   = image_url,
            mode        = mode,
            image_bytes = image_bytes,
        )

        if result.success:
            logger.info(
                "publish_success | target=%s | platform=%s | post_id=%s%s",
                target_key, target.platform, result.external_post_id, brand_log,
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
            "publish_failed | target=%s | retryable=%s | error=%s%s",
            target_key, exc.retryable, exc, brand_log,
        )
        record_publish(
            content_hash = content_hash,
            target_key   = target_key,
            platform     = target.platform,
            module_name  = module_name,
            status       = "failed",
            error_message = str(exc),
        )
        return PublishResult(
            platform      = target.platform,
            success       = False,
            error_message = str(exc),
            retryable     = exc.retryable,
            metadata      = {"target": target_key},
        )

    except NotImplementedError as exc:
        logger.error("Platform %s not implemented: %s%s", target.platform, exc, brand_log)
        return PublishResult(
            platform      = target.platform,
            success       = False,
            error_message = str(exc),
            retryable     = False,
            metadata      = {"target": target_key},
        )

    except Exception as exc:
        logger.exception(
            "publish_unexpected_error | target=%s | error=%s%s", target_key, exc, brand_log
        )
        return PublishResult(
            platform      = target.platform,
            success       = False,
            error_message = f"Unexpected: {exc}",
            retryable     = True,
            metadata      = {"target": target_key},
        )
