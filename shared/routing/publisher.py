# shared/routing/publisher.py
"""
Multi-client publisher — dispatches content to all configured destinations
for a given client.

This publisher is called AFTER routing — it receives a routed ClientConfig
and a PublishRequest, and fires off all configured publish formats.

Supported publish formats:
    text_link   — WordPress REST API article + optional Facebook text+link post
    image_post  — Facebook image post (image URL required)
    reel        — Facebook Reel (two-step: create container → publish)

Architecture:
    - Each format has an isolated _publish_* method.
    - All methods return PublishOutcome (never raise).
    - Credentials are resolved at publish time, not config load time.
    - PUBLISH_MODE env var controls mock vs real behaviour (inherits from
      shared ContentPilot convention).

Usage:
    publisher = MultiClientPublisher()
    summary = publisher.publish(request, client)
    for outcome in summary.outcomes:
        logger.info(str(outcome))
"""

from __future__ import annotations

import logging
import os
import uuid
from typing import Any

import requests as req

from .exceptions import CredentialMissingError, PublishRoutingError
from .models.client import ClientConfig
from .models.publishing import (
    PublishFormat,
    PublishOutcome,
    PublishPlatform,
    PublishRequest,
    PublishSummary,
)

logger = logging.getLogger(__name__)

_FB_GRAPH_VERSION = "v23.0"
_FB_BASE = f"https://graph.facebook.com/{_FB_GRAPH_VERSION}"
_DEFAULT_TIMEOUT = 30


def _get_publish_mode() -> str:
    return os.getenv("PUBLISH_MODE", "mock").strip().lower()


class MultiClientPublisher:
    """
    Publishes content to all configured destinations for one client.

    Each publish format is an isolated method. Failures in one format
    do not prevent other formats from being attempted.

    Instantiate once and reuse across calls — the class is stateless.
    """

    def publish(
        self,
        request: PublishRequest,
        client: ClientConfig,
    ) -> PublishSummary:
        """
        Execute all configured publish formats for this client.

        Args:
            request: Article content and metadata.
            client:  Routed ClientConfig (from AutoPublisherRouter).

        Returns:
            PublishSummary — never raises.
        """
        mode = _get_publish_mode()
        prefs = client.publishing_preferences

        summary = PublishSummary(
            article_id=request.article_id,
            client_id=client.client_id,
            routing_score=0.0,   # filled in by caller if needed
            routed=True,
        )

        logger.info(
            "publisher_start | article=%s | client=%s | formats=%s | mode=%s",
            request.article_id, client.client_id, list(prefs.formats), mode,
        )

        for fmt_str in prefs.formats:
            try:
                fmt = PublishFormat(fmt_str)
            except ValueError:
                logger.warning(
                    "publisher_unknown_format | client=%s | format=%r | skipping",
                    client.client_id, fmt_str,
                )
                continue

            if fmt == PublishFormat.TEXT_LINK:
                outcomes = self._publish_text_link(request, client, mode)
            elif fmt == PublishFormat.IMAGE_POST:
                outcomes = self._publish_image_post(request, client, mode)
            elif fmt == PublishFormat.REEL:
                outcomes = self._publish_reel(request, client, mode)
            else:
                logger.warning(
                    "publisher_unhandled_format | client=%s | format=%s",
                    client.client_id, fmt,
                )
                continue

            summary.outcomes.extend(outcomes)

        ok = sum(1 for o in summary.outcomes if o.success)
        logger.info(
            "publisher_complete | article=%s | client=%s | outcomes=%d | ok=%d",
            request.article_id, client.client_id, len(summary.outcomes), ok,
        )
        return summary

    # -----------------------------------------------------------------------
    # text_link: WordPress post + Facebook text+link
    # -----------------------------------------------------------------------

    def _publish_text_link(
        self,
        request: PublishRequest,
        client: ClientConfig,
        mode: str,
    ) -> list[PublishOutcome]:
        outcomes: list[PublishOutcome] = []

        # 1. WordPress
        wp_outcome = self._publish_wordpress(request, client, mode)
        outcomes.append(wp_outcome)

        # 2. Facebook text+link (only if FB is enabled for this client)
        if client.facebook.enabled:
            fb_text = f"{request.summary}\n\n{request.url}" if request.url else request.summary
            fb_outcome = self._facebook_post_text(
                content=fb_text,
                client=client,
                mode=mode,
                fmt=PublishFormat.TEXT_LINK,
            )
            outcomes.append(fb_outcome)

        return outcomes

    # -----------------------------------------------------------------------
    # image_post: Facebook image post
    # -----------------------------------------------------------------------

    def _publish_image_post(
        self,
        request: PublishRequest,
        client: ClientConfig,
        mode: str,
    ) -> list[PublishOutcome]:
        prefs = client.publishing_preferences.image_post

        if not prefs.enabled:
            logger.debug(
                "publisher_image_post_disabled | client=%s", client.client_id,
            )
            return []

        if not client.facebook.enabled:
            return []

        caption = f"{request.summary}\n\n{request.url}" if request.url else request.summary
        return [
            self._facebook_post_photo(
                caption=caption,
                image_url=request.image_url,
                client=client,
                mode=mode,
            )
        ]

    # -----------------------------------------------------------------------
    # reel: Facebook Reel (two-step upload)
    # -----------------------------------------------------------------------

    def _publish_reel(
        self,
        request: PublishRequest,
        client: ClientConfig,
        mode: str,
    ) -> list[PublishOutcome]:
        reel_cfg = client.publishing_preferences.reel

        if not reel_cfg.enabled:
            logger.debug(
                "publisher_reel_disabled | client=%s", client.client_id,
            )
            return []

        if not client.facebook.enabled:
            return []

        # Resolve video URL: prefer request.video_url, fall back to client env var
        video_url = request.video_url
        if not video_url:
            try:
                video_url = reel_cfg.resolve_video_url()
            except CredentialMissingError as exc:
                return [
                    self._outcome_error(
                        client_id=client.client_id,
                        platform=PublishPlatform.FACEBOOK,
                        fmt=PublishFormat.REEL,
                        error=str(exc),
                        retryable=False,
                    )
                ]

        return [
            self._facebook_publish_reel(
                video_url=video_url,
                description=request.summary,
                client=client,
                mode=mode,
            )
        ]

    # -----------------------------------------------------------------------
    # WordPress REST API
    # -----------------------------------------------------------------------

    def _publish_wordpress(
        self,
        request: PublishRequest,
        client: ClientConfig,
        mode: str,
    ) -> PublishOutcome:
        wp = client.wordpress

        if mode == "mock":
            fake_id = f"wp_mock_{uuid.uuid4().hex[:10]}"
            logger.debug(
                "wp_mock_publish | client=%s | article=%s | post_id=%s",
                client.client_id, request.article_id, fake_id,
            )
            return PublishOutcome(
                client_id=client.client_id,
                platform=PublishPlatform.WORDPRESS,
                format=PublishFormat.TEXT_LINK,
                success=True,
                external_id=fake_id,
                url=f"{wp.base_url}/?p=mock_{fake_id}",
                metadata={"mode": "mock"},
            )

        # Resolve credential
        try:
            app_password = wp.resolve_app_password()
        except CredentialMissingError as exc:
            return self._outcome_error(
                client_id=client.client_id,
                platform=PublishPlatform.WORDPRESS,
                fmt=PublishFormat.TEXT_LINK,
                error=str(exc),
                retryable=False,
            )

        import base64
        auth = base64.b64encode(
            f"{wp.username}:{app_password}".encode()
        ).decode()

        payload: dict[str, Any] = {
            "title":      request.title,
            "content":    request.body,
            "status":     wp.default_status,
            "excerpt":    request.summary,
        }
        if wp.default_categories:
            payload["categories"] = wp.default_categories
        if wp.default_tags:
            payload["tags"] = wp.default_tags

        url = f"{wp.base_url.rstrip('/')}/wp-json/wp/v2/posts"

        try:
            response = req.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Basic {auth}",
                    "Content-Type": "application/json",
                },
                timeout=wp.timeout_seconds,
            )
        except req.Timeout:
            return self._outcome_error(
                client_id=client.client_id,
                platform=PublishPlatform.WORDPRESS,
                fmt=PublishFormat.TEXT_LINK,
                error=f"Request timed out after {wp.timeout_seconds}s",
                retryable=True,
            )
        except req.RequestException as exc:
            return self._outcome_error(
                client_id=client.client_id,
                platform=PublishPlatform.WORDPRESS,
                fmt=PublishFormat.TEXT_LINK,
                error=f"Network error: {exc}",
                retryable=True,
            )

        return self._handle_wp_response(response, client.client_id)

    def _handle_wp_response(self, response: req.Response, client_id: str) -> PublishOutcome:
        if response.status_code in {401, 403}:
            return self._outcome_error(
                client_id=client_id,
                platform=PublishPlatform.WORDPRESS,
                fmt=PublishFormat.TEXT_LINK,
                error=f"Auth failed (HTTP {response.status_code}): {response.text[:200]}",
                retryable=False,
            )
        if response.status_code >= 500:
            return self._outcome_error(
                client_id=client_id,
                platform=PublishPlatform.WORDPRESS,
                fmt=PublishFormat.TEXT_LINK,
                error=f"Server error (HTTP {response.status_code})",
                retryable=True,
            )
        if not response.ok:
            return self._outcome_error(
                client_id=client_id,
                platform=PublishPlatform.WORDPRESS,
                fmt=PublishFormat.TEXT_LINK,
                error=f"HTTP {response.status_code}: {response.text[:200]}",
                retryable=False,
            )

        body = response.json()
        post_id = str(body.get("id", ""))
        post_url = body.get("link") or body.get("guid", {}).get("rendered", "")

        logger.info(
            "wp_publish_success | client=%s | post_id=%s | url=%s",
            client_id, post_id, post_url,
        )
        return PublishOutcome(
            client_id=client_id,
            platform=PublishPlatform.WORDPRESS,
            format=PublishFormat.TEXT_LINK,
            success=True,
            external_id=post_id,
            url=post_url,
            metadata={"status": body.get("status")},
        )

    # -----------------------------------------------------------------------
    # Facebook: text post
    # -----------------------------------------------------------------------

    def _facebook_post_text(
        self,
        content: str,
        client: ClientConfig,
        mode: str,
        fmt: PublishFormat,
    ) -> PublishOutcome:
        if mode == "mock":
            fake_id = f"fb_mock_{uuid.uuid4().hex[:10]}"
            logger.debug(
                "fb_mock_text_post | client=%s | post_id=%s",
                client.client_id, fake_id,
            )
            return PublishOutcome(
                client_id=client.client_id,
                platform=PublishPlatform.FACEBOOK,
                format=fmt,
                success=True,
                external_id=fake_id,
                metadata={"mode": "mock"},
            )

        try:
            page_id = client.facebook.resolve_page_id()
            access_token = client.facebook.resolve_access_token()
        except CredentialMissingError as exc:
            return self._outcome_error(
                client_id=client.client_id,
                platform=PublishPlatform.FACEBOOK,
                fmt=fmt,
                error=str(exc),
                retryable=False,
            )

        url = f"{_FB_BASE}/{page_id}/feed"
        try:
            response = req.post(
                url,
                data={"message": content, "access_token": access_token},
                timeout=_DEFAULT_TIMEOUT,
            )
        except req.Timeout:
            return self._outcome_error(
                client_id=client.client_id,
                platform=PublishPlatform.FACEBOOK,
                fmt=fmt,
                error="Request timed out",
                retryable=True,
            )
        except req.RequestException as exc:
            return self._outcome_error(
                client_id=client.client_id,
                platform=PublishPlatform.FACEBOOK,
                fmt=fmt,
                error=f"Network error: {exc}",
                retryable=True,
            )

        return self._handle_fb_response(response, client.client_id, fmt)

    # -----------------------------------------------------------------------
    # Facebook: photo post
    # -----------------------------------------------------------------------

    def _facebook_post_photo(
        self,
        caption: str,
        image_url: str | None,
        client: ClientConfig,
        mode: str,
    ) -> PublishOutcome:
        if mode == "mock":
            fake_id = f"fb_photo_mock_{uuid.uuid4().hex[:8]}"
            logger.debug(
                "fb_mock_photo_post | client=%s | post_id=%s | image_url=%s",
                client.client_id, fake_id, image_url,
            )
            return PublishOutcome(
                client_id=client.client_id,
                platform=PublishPlatform.FACEBOOK,
                format=PublishFormat.IMAGE_POST,
                success=True,
                external_id=fake_id,
                metadata={"mode": "mock", "image_url": image_url},
            )

        if not image_url:
            return self._outcome_error(
                client_id=client.client_id,
                platform=PublishPlatform.FACEBOOK,
                fmt=PublishFormat.IMAGE_POST,
                error="image_url is required for image_post format",
                retryable=False,
            )

        try:
            page_id = client.facebook.resolve_page_id()
            access_token = client.facebook.resolve_access_token()
        except CredentialMissingError as exc:
            return self._outcome_error(
                client_id=client.client_id,
                platform=PublishPlatform.FACEBOOK,
                fmt=PublishFormat.IMAGE_POST,
                error=str(exc),
                retryable=False,
            )

        url = f"{_FB_BASE}/{page_id}/photos"
        try:
            response = req.post(
                url,
                data={
                    "url":          image_url,
                    "caption":      caption,
                    "access_token": access_token,
                },
                timeout=_DEFAULT_TIMEOUT,
            )
        except (req.Timeout, req.RequestException) as exc:
            return self._outcome_error(
                client_id=client.client_id,
                platform=PublishPlatform.FACEBOOK,
                fmt=PublishFormat.IMAGE_POST,
                error=str(exc),
                retryable=True,
            )

        return self._handle_fb_response(response, client.client_id, PublishFormat.IMAGE_POST)

    # -----------------------------------------------------------------------
    # Facebook: Reel (two-step upload → publish)
    # -----------------------------------------------------------------------

    def _facebook_publish_reel(
        self,
        video_url: str,
        description: str,
        client: ClientConfig,
        mode: str,
    ) -> PublishOutcome:
        """
        Facebook Reels two-step process:
          Step 1 — POST /{page_id}/video_reels  → container_id
          Step 2 — POST /{page_id}/video_reels  with video_id + PUBLISH status
        """
        if mode == "mock":
            fake_id = f"fb_reel_mock_{uuid.uuid4().hex[:8]}"
            logger.debug(
                "fb_mock_reel | client=%s | reel_id=%s", client.client_id, fake_id,
            )
            return PublishOutcome(
                client_id=client.client_id,
                platform=PublishPlatform.FACEBOOK,
                format=PublishFormat.REEL,
                success=True,
                external_id=fake_id,
                metadata={"mode": "mock", "video_url": video_url},
            )

        try:
            page_id = client.facebook.resolve_page_id()
            access_token = client.facebook.resolve_access_token()
        except CredentialMissingError as exc:
            return self._outcome_error(
                client_id=client.client_id,
                platform=PublishPlatform.FACEBOOK,
                fmt=PublishFormat.REEL,
                error=str(exc),
                retryable=False,
            )

        # Step 1: Create media container
        container_id = self._fb_create_reel_container(
            page_id=page_id,
            access_token=access_token,
            video_url=video_url,
            description=description,
            client_id=client.client_id,
        )
        if container_id is None:
            return self._outcome_error(
                client_id=client.client_id,
                platform=PublishPlatform.FACEBOOK,
                fmt=PublishFormat.REEL,
                error="Failed to create Reel container (Step 1)",
                retryable=True,
            )

        # Step 2: Publish the container
        return self._fb_publish_reel_container(
            page_id=page_id,
            access_token=access_token,
            container_id=container_id,
            client_id=client.client_id,
        )

    def _fb_create_reel_container(
        self,
        page_id: str,
        access_token: str,
        video_url: str,
        description: str,
        client_id: str,
    ) -> str | None:
        """
        Step 1: POST to /{page_id}/video_reels to create a media container.
        Returns the container ID, or None on failure.
        """
        url = f"{_FB_BASE}/{page_id}/video_reels"
        try:
            response = req.post(
                url,
                data={
                    "upload_phase":  "start",
                    "access_token":  access_token,
                    "video_url":     video_url,
                    "description":   description,
                },
                timeout=_DEFAULT_TIMEOUT,
            )
        except (req.Timeout, req.RequestException) as exc:
            logger.error(
                "fb_reel_container_create_failed | client=%s | error=%s",
                client_id, exc,
            )
            return None

        if not response.ok:
            logger.error(
                "fb_reel_container_create_failed | client=%s | http=%d | body=%s",
                client_id, response.status_code, response.text[:200],
            )
            return None

        container_id = response.json().get("video_id") or response.json().get("id")
        logger.info(
            "fb_reel_container_created | client=%s | container_id=%s",
            client_id, container_id,
        )
        return str(container_id) if container_id else None

    def _fb_publish_reel_container(
        self,
        page_id: str,
        access_token: str,
        container_id: str,
        client_id: str,
    ) -> PublishOutcome:
        """
        Step 2: POST to /{page_id}/video_reels with upload_phase=finish to publish.
        """
        url = f"{_FB_BASE}/{page_id}/video_reels"
        try:
            response = req.post(
                url,
                data={
                    "upload_phase":   "finish",
                    "access_token":   access_token,
                    "video_id":       container_id,
                    "video_state":    "PUBLISHED",
                },
                timeout=_DEFAULT_TIMEOUT,
            )
        except (req.Timeout, req.RequestException) as exc:
            return self._outcome_error(
                client_id=client_id,
                platform=PublishPlatform.FACEBOOK,
                fmt=PublishFormat.REEL,
                error=f"Reel publish step 2 network error: {exc}",
                retryable=True,
            )

        return self._handle_fb_response(response, client_id, PublishFormat.REEL)

    # -----------------------------------------------------------------------
    # Shared FB response handler
    # -----------------------------------------------------------------------

    def _handle_fb_response(
        self,
        response: req.Response,
        client_id: str,
        fmt: PublishFormat,
    ) -> PublishOutcome:
        if response.status_code == 429:
            return self._outcome_error(
                client_id=client_id,
                platform=PublishPlatform.FACEBOOK,
                fmt=fmt,
                error="Rate limited (HTTP 429)",
                retryable=True,
            )
        if response.status_code in {400, 401, 403}:
            try:
                err = response.json().get("error", {})
                msg = err.get("message", response.text[:200])
            except Exception:
                msg = response.text[:200]
            return self._outcome_error(
                client_id=client_id,
                platform=PublishPlatform.FACEBOOK,
                fmt=fmt,
                error=f"Auth/permission error: {msg}",
                retryable=False,
            )
        if response.status_code >= 500:
            return self._outcome_error(
                client_id=client_id,
                platform=PublishPlatform.FACEBOOK,
                fmt=fmt,
                error=f"Server error (HTTP {response.status_code})",
                retryable=True,
            )
        if not response.ok:
            return self._outcome_error(
                client_id=client_id,
                platform=PublishPlatform.FACEBOOK,
                fmt=fmt,
                error=f"HTTP {response.status_code}: {response.text[:200]}",
                retryable=False,
            )

        body = response.json()
        post_id = str(body.get("id", ""))

        logger.info(
            "fb_publish_success | client=%s | format=%s | post_id=%s",
            client_id, fmt.value, post_id,
        )
        return PublishOutcome(
            client_id=client_id,
            platform=PublishPlatform.FACEBOOK,
            format=fmt,
            success=True,
            external_id=post_id,
            metadata={"mode": "real"},
        )

    # -----------------------------------------------------------------------
    # Helper: build a failed outcome without raising
    # -----------------------------------------------------------------------

    @staticmethod
    def _outcome_error(
        client_id: str,
        platform: PublishPlatform,
        fmt: PublishFormat,
        error: str,
        retryable: bool,
    ) -> PublishOutcome:
        logger.warning(
            "publish_failed | client=%s | platform=%s | format=%s | retryable=%s | error=%s",
            client_id, platform.value, fmt.value, retryable, error,
        )
        return PublishOutcome(
            client_id=client_id,
            platform=platform,
            format=fmt,
            success=False,
            error_message=error,
            retryable=retryable,
        )
