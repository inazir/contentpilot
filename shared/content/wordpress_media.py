# shared/content/wordpress_media.py
"""
WordPress Media Upload Service.

Uploads generated image assets to the WordPress media library
and returns the media attachment ID for use as a featured image.

Design:
- Stateless — one instance per upload session is fine
- Never raises — returns WordPressMediaResult
- Logs all outcomes with structured fields
- Retries transient failures using WordPressClient's built-in backoff

Phase 11B uses this to:
1. Upload bundle.featured_image bytes to WordPress
2. Receive the media attachment ID
3. Pass the ID into PostRequest.featured_media

Depends on:
- shared/wordpress/client.py  (existing, untouched)
- shared/content/models.py    (AssetFile, AssetBundle)
"""

from __future__ import annotations

import base64
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = 30
_MAX_RETRIES = 3
_BASE_BACKOFF = 2.0
_RETRYABLE_STATUS = {429, 500, 502, 503, 504}


@dataclass
class WordPressMediaResult:
    """Result of a single media upload attempt."""
    success: bool
    media_id: int | None = None
    url: str | None = None
    error_message: str | None = None
    retryable: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        if self.success:
            return f"[wp_media] OK media_id={self.media_id} url={self.url}"
        flag = "retryable" if self.retryable else "permanent"
        return f"[wp_media] FAILED ({flag}): {self.error_message}"


class WordPressMediaService:
    """
    Uploads image files to the WordPress media library.

    Usage:
        config = get_wordpress_config()
        svc = WordPressMediaService(config)
        result = svc.upload_image(image_bytes, filename="featured.jpg")
        if result.success:
            post_request.featured_media = result.media_id
    """

    def __init__(self, config) -> None:
        """
        Args:
            config: WordPressConfig from shared.config.get_wordpress_config()
        """
        self._config = config
        self._base_url = config.base_url.rstrip("/")
        self._api_base = f"{self._base_url}/wp-json/wp/v2"
        self._auth_header = self._build_auth_header(
            config.username, config.app_password
        )

    def upload_image(
        self,
        image_bytes: bytes,
        filename: str = "featured.jpg",
        alt_text: str = "",
        caption: str = "",
        title: str = "",
    ) -> WordPressMediaResult:
        """
        Upload image bytes to WordPress media library.

        Args:
            image_bytes: Raw JPEG/PNG bytes.
            filename:    Filename to use in WordPress.
            alt_text:    Accessibility alt text.
            caption:     Optional image caption.
            title:       Optional media title.

        Returns:
            WordPressMediaResult — never raises.
        """
        if not image_bytes:
            return WordPressMediaResult(
                success=False,
                error_message="image_bytes is empty",
                retryable=False,
            )

        logger.info(
            "wp_media_upload_start | filename=%s | size=%d | site=%s",
            filename, len(image_bytes), self._base_url,
        )

        url = f"{self._api_base}/media"
        headers = {
            "Authorization": self._auth_header,
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "image/jpeg",
        }

        last_exc: Exception | None = None

        for attempt in range(_MAX_RETRIES + 1):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    data=image_bytes,
                    timeout=_DEFAULT_TIMEOUT,
                )
            except requests.Timeout:
                wait = _BASE_BACKOFF * (2 ** attempt)
                logger.warning(
                    "wp_media_timeout | attempt=%d/%d | retry_in=%.1fs",
                    attempt + 1, _MAX_RETRIES + 1, wait,
                )
                time.sleep(wait)
                last_exc = Exception("Request timed out")
                continue
            except requests.RequestException as exc:
                wait = _BASE_BACKOFF * (2 ** attempt)
                logger.warning(
                    "wp_media_network_error | attempt=%d/%d | error=%s",
                    attempt + 1, _MAX_RETRIES + 1, exc,
                )
                time.sleep(wait)
                last_exc = exc
                continue

            if response.status_code in _RETRYABLE_STATUS:
                wait = _BASE_BACKOFF * (2 ** attempt)
                logger.warning(
                    "wp_media_server_error | http=%d | attempt=%d/%d | retry_in=%.1fs",
                    response.status_code, attempt + 1, _MAX_RETRIES + 1, wait,
                )
                time.sleep(wait)
                last_exc = Exception(f"HTTP {response.status_code}")
                continue

            return self._parse_upload_response(response, filename, alt_text, caption, title)

        return WordPressMediaResult(
            success=False,
            error_message=f"All {_MAX_RETRIES + 1} upload attempts failed: {last_exc}",
            retryable=True,
        )

    def upload_asset_file(
        self,
        asset_file,
        alt_text: str = "",
        title: str = "",
    ) -> WordPressMediaResult:
        """
        Upload an AssetFile directly.

        Args:
            asset_file: AssetFile with a valid .path
            alt_text:   Alt text for the media item.
            title:      Media title.

        Returns:
            WordPressMediaResult — never raises.
        """
        try:
            image_bytes = asset_file.path.read_bytes()
        except Exception as exc:
            return WordPressMediaResult(
                success=False,
                error_message=f"Could not read asset file {asset_file.path}: {exc}",
                retryable=False,
            )

        return self.upload_image(
            image_bytes=image_bytes,
            filename=asset_file.path.name,
            alt_text=alt_text,
            title=title,
        )

    def _parse_upload_response(
        self,
        response: requests.Response,
        filename: str,
        alt_text: str,
        caption: str,
        title: str,
    ) -> WordPressMediaResult:
        if response.status_code in {401, 403}:
            return WordPressMediaResult(
                success=False,
                error_message=f"Auth failed (HTTP {response.status_code}): {response.text[:200]}",
                retryable=False,
            )

        if response.status_code == 400:
            return WordPressMediaResult(
                success=False,
                error_message=f"Bad request (HTTP 400): {response.text[:200]}",
                retryable=False,
            )

        if not response.ok:
            return WordPressMediaResult(
                success=False,
                error_message=f"Unexpected HTTP {response.status_code}: {response.text[:200]}",
                retryable=True,
            )

        try:
            body = response.json()
        except Exception as exc:
            return WordPressMediaResult(
                success=False,
                error_message=f"Could not parse upload response: {exc}",
                retryable=True,
            )

        media_id = body.get("id")
        url = body.get("source_url") or body.get("guid", {}).get("rendered")

        if not media_id:
            return WordPressMediaResult(
                success=False,
                error_message=f"Upload response missing media ID: {str(body)[:200]}",
                retryable=False,
            )

        # Patch alt text and caption if provided
        if alt_text or caption or title:
            self._patch_media_meta(media_id, alt_text=alt_text, caption=caption, title=title)

        logger.info(
            "wp_media_upload_success | media_id=%d | filename=%s | url=%s",
            media_id, filename, url,
        )

        return WordPressMediaResult(
            success=True,
            media_id=int(media_id),
            url=url,
            metadata={"filename": filename},
        )

    def _patch_media_meta(
        self,
        media_id: int,
        alt_text: str = "",
        caption: str = "",
        title: str = "",
    ) -> None:
        """Update alt text / caption after upload. Best-effort, never raises."""
        url = f"{self._api_base}/media/{media_id}"
        payload: dict = {}
        if alt_text:
            payload["alt_text"] = alt_text
        if caption:
            payload["caption"] = caption
        if title:
            payload["title"] = title
        if not payload:
            return
        try:
            requests.post(
                url,
                json=payload,
                headers={
                    "Authorization": self._auth_header,
                    "Content-Type": "application/json",
                },
                timeout=_DEFAULT_TIMEOUT,
            )
        except Exception as exc:
            logger.debug("wp_media_meta_patch_failed | media_id=%d | error=%s", media_id, exc)

    @staticmethod
    def _build_auth_header(username: str, app_password: str) -> str:
        token = base64.b64encode(
            f"{username}:{app_password}".encode("utf-8")
        ).decode("utf-8")
        return f"Basic {token}"
