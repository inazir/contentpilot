# shared/social/publisher.py
"""
Orchestrates publishing across social platforms.

Responsibilities:
- read publish mode from environment
- check duplicates via shared/store
- call platform adapters safely
- catch and classify exceptions
- record publish attempts in SQLite
- return aggregated results without crashing the caller
"""

import logging
import os

from shared.store import (
    already_published,
    compute_content_hash,
    record_publish,
)

from .exceptions import PublishError
from .models import PublishResult, PublishSummary
from . import facebook, instagram

logger = logging.getLogger(__name__)

# Registry: platform name → module with publish(content, mode)
_ADAPTERS = {
    "facebook": facebook,
    "instagram": instagram,
}


def get_publish_mode() -> str:
    """Return the configured publish mode."""
    mode = os.getenv("PUBLISH_MODE", "").strip().lower()
    if mode:
        return mode

    # backward compatibility with older PUBLISH_ENABLED flag
    if os.getenv("PUBLISH_ENABLED", "false").strip().lower() in {"1", "true", "yes"}:
        return "mock"
    return "disabled"


def publish_post(
    content: dict,
    platforms: list[str],
    module_name: str,
) -> PublishSummary:
    """
    Publish content to requested platforms and return aggregated results.

    This function never raises, even when one platform fails.
    """
    summary = PublishSummary(module_name=module_name)
    mode = get_publish_mode()

    if mode == "disabled":
        logger.info("PUBLISH_MODE=disabled — skipping publishing")
        return summary

    text = content.get("text", "")
    content_hash = compute_content_hash(text)

    for platform in platforms:
        key = platform.strip().lower()
        adapter = _ADAPTERS.get(key)
        if adapter is None:
            error_message = f"Unknown platform '{platform}'"
            logger.error(error_message)
            summary.results.append(PublishResult(
                platform=platform,
                success=False,
                error_message=error_message,
                retryable=False,
            ))
            continue

        if already_published(content_hash, key):
            logger.info(
                "Duplicate content detected — skipping publish | platform=%s | module=%s | hash=%s",
                key, module_name, content_hash[:12],
            )
            summary.results.append(PublishResult(
                platform=key,
                success=True,
                external_post_id="[duplicate:skipped]",
                metadata={"duplicate": True},
            ))
            continue

        try:
            success, external_post_id, error_message = adapter.publish(content, mode)
            status = "success" if success else "failed"
            record_publish(
                content_hash=content_hash,
                platform=key,
                module_name=module_name,
                status=status,
                external_post_id=external_post_id,
                error_message=error_message,
            )
            summary.results.append(PublishResult(
                platform=key,
                success=success,
                external_post_id=external_post_id,
                error_message=error_message,
                retryable=False,
            ))

        except PublishError as exc:
            logger.error(
                "Publish failed | platform=%s | retryable=%s | error=%s",
                key, exc.retryable, exc,
            )
            record_publish(
                content_hash=content_hash,
                platform=key,
                module_name=module_name,
                status="failed",
                error_message=str(exc),
            )
            summary.results.append(PublishResult(
                platform=key,
                success=False,
                error_message=str(exc),
                retryable=exc.retryable,
            ))

        except NotImplementedError as exc:
            logger.error("Platform %s real mode not implemented: %s", key, exc)
            summary.results.append(PublishResult(
                platform=key,
                success=False,
                error_message=str(exc),
                retryable=False,
            ))

        except Exception as exc:
            logger.exception("Unexpected error publishing to %s", key)
            record_publish(
                content_hash=content_hash,
                platform=key,
                module_name=module_name,
                status="failed",
                error_message=str(exc),
            )
            summary.results.append(PublishResult(
                platform=key,
                success=False,
                error_message=f"Unexpected: {exc}",
                retryable=True,
            ))

    return summary
