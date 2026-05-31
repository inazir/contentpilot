# shared/wordpress/client.py
"""
WordPress REST API client.

Responsibilities:
- authenticate via Application Passwords (Basic Auth over HTTPS)
- create posts
- update posts
- fetch posts by ID
- retry with exponential backoff on transient failures
- raise typed WordPressError subclasses only — never raw exceptions

This is a stateless adapter. It holds no mutable state beyond the config
it was constructed with. Safe to instantiate per-call or reuse across calls.
"""

import base64
import logging
import time

import requests

from .exceptions import (
    AuthError,
    NotFoundError,
    PermanentWordPressError,
    RetryableWordPressError,
    ValidationError,
    WordPressError,
)
from .models import PostRequest, PostResponse, WordPressConfig

logger = logging.getLogger(__name__)

_BASE_BACKOFF_SECONDS = 2.0
_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class WordPressClient:
    """
    Thin HTTP client for the WordPress REST API v2.

    Usage:
        config = get_wordpress_config()
        client = WordPressClient(config)
        response = client.create_post(post_request)
    """

    def __init__(self, config: WordPressConfig) -> None:
        self._config = config
        self._base_url = config.base_url.rstrip("/")
        self._api_base = f"{self._base_url}/wp-json/wp/v2"
        self._auth_header = self._build_auth_header(
            config.username, config.app_password
        )

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def create_post(self, post: PostRequest) -> PostResponse:
        """
        Create a new WordPress post.

        Args:
            post: PostRequest with title, content, and optional fields.

        Returns:
            PostResponse — never raises.
        """
        logger.info(
            "wordpress_publish_start | action=create | title=%r | status=%s",
            post.title[:60], post.status,
        )
        return self._execute_with_retry(
            method="POST",
            endpoint="/posts",
            payload=post.to_api_payload(),
            action="create",
        )

    def update_post(self, post_id: int, post: PostRequest) -> PostResponse:
        """
        Update an existing WordPress post by ID.

        Args:
            post_id: WordPress post ID to update.
            post:    PostRequest with updated fields.

        Returns:
            PostResponse — never raises.
        """
        logger.info(
            "wordpress_publish_start | action=update | post_id=%d | title=%r | status=%s",
            post_id, post.title[:60], post.status,
        )
        return self._execute_with_retry(
            method="POST",
            endpoint=f"/posts/{post_id}",
            payload=post.to_api_payload(),
            action="update",
        )

    def get_post(self, post_id: int) -> PostResponse:
        """
        Fetch a post by ID.

        Returns:
            PostResponse — never raises.
        """
        logger.info(
            "wordpress_publish_start | action=fetch | post_id=%d", post_id,
        )
        return self._execute_with_retry(
            method="GET",
            endpoint=f"/posts/{post_id}",
            payload=None,
            action="fetch",
        )

    def check_auth(self) -> bool:
        """
        Verify that credentials are valid by hitting /users/me.

        Returns:
            True if authenticated, False otherwise.
            Never raises.
        """
        url = f"{self._api_base}/users/me"
        try:
            response = requests.get(
                url,
                headers=self._headers(),
                timeout=self._config.timeout_seconds,
            )
            if response.status_code == 200:
                logger.info("wordpress_auth | status=ok | url=%s", self._base_url)
                return True
            logger.warning(
                "wordpress_auth | status=failed | http=%d | url=%s",
                response.status_code, self._base_url,
            )
            return False
        except Exception as exc:
            logger.warning("wordpress_auth | status=error | error=%s", exc)
            return False

    # -----------------------------------------------------------------------
    # Internal
    # -----------------------------------------------------------------------

    def _execute_with_retry(
        self,
        method: str,
        endpoint: str,
        payload: dict | None,
        action: str,
    ) -> PostResponse:
        """
        Execute an HTTP request with exponential backoff retry.
        Converts all outcomes to PostResponse — never raises.
        """
        url = f"{self._api_base}{endpoint}"
        last_exc: Exception | None = None

        for attempt in range(self._config.max_retries + 1):
            try:
                response = self._make_request(method, url, payload)
                result = self._parse_response(response, action)
                return result

            except RetryableWordPressError as exc:
                last_exc = exc
                if attempt < self._config.max_retries:
                    wait = _BASE_BACKOFF_SECONDS * (2 ** attempt)
                    logger.warning(
                        "wordpress_retry | action=%s | attempt=%d/%d | wait=%.1fs | error=%s",
                        action, attempt + 1, self._config.max_retries + 1, wait, exc,
                    )
                    time.sleep(wait)
                    continue

                # Exhausted retries
                logger.error(
                    "wordpress_publish_failure | action=%s | reason=retries_exhausted | error=%s",
                    action, exc,
                )
                return PostResponse(
                    success=False,
                    error_message=str(exc),
                    retryable=True,
                    metadata={"action": action, "url": url},
                )

            except WordPressError as exc:
                # Permanent failure — don't retry
                logger.error(
                    "wordpress_publish_failure | action=%s | reason=permanent | error=%s",
                    action, exc,
                )
                return PostResponse(
                    success=False,
                    error_message=str(exc),
                    retryable=False,
                    metadata={"action": action, "url": url},
                )

            except Exception as exc:
                logger.exception(
                    "wordpress_publish_failure | action=%s | reason=unexpected | error=%s",
                    action, exc,
                )
                return PostResponse(
                    success=False,
                    error_message=f"Unexpected: {exc}",
                    retryable=True,
                    metadata={"action": action, "url": url},
                )

        # Should never reach here, but satisfy type checker
        return PostResponse(
            success=False,
            error_message=str(last_exc),
            retryable=True,
        )

    def _make_request(
        self,
        method: str,
        url: str,
        payload: dict | None,
    ) -> requests.Response:
        """
        Execute the HTTP request. Raises typed WordPressError on failure.
        Network errors become RetryableWordPressError.
        """
        try:
            if method == "GET":
                response = requests.get(
                    url,
                    headers=self._headers(),
                    timeout=self._config.timeout_seconds,
                )
            else:
                response = requests.post(
                    url,
                    json=payload,
                    headers=self._headers(),
                    timeout=self._config.timeout_seconds,
                )
        except requests.Timeout:
            raise RetryableWordPressError(
                f"Request timed out after {self._config.timeout_seconds}s"
            )
        except requests.RequestException as exc:
            raise RetryableWordPressError(f"Network error: {exc}") from exc

        return response

    def _parse_response(
        self,
        response: requests.Response,
        action: str,
    ) -> PostResponse:
        """
        Parse HTTP response into PostResponse or raise typed exception.
        """
        # Auth failures
        if response.status_code == 401:
            raise AuthError(
                "Authentication failed — check WORDPRESS_USERNAME and "
                "WORDPRESS_APP_PASSWORD (HTTP 401)",
                status_code=401,
            )

        if response.status_code == 403:
            raise AuthError(
                "Permission denied — user may lack publishing rights (HTTP 403)",
                status_code=403,
            )

        # Not found
        if response.status_code == 404:
            raise NotFoundError(
                f"Resource not found (HTTP 404): {response.url}",
                status_code=404,
            )

        # Bad request — content or payload issue
        if response.status_code == 400:
            try:
                body = response.json()
                msg = body.get("message", response.text[:200])
            except Exception:
                msg = response.text[:200]
            raise ValidationError(
                f"WordPress rejected the request (HTTP 400): {msg}",
                status_code=400,
            )

        # Retryable server errors
        if response.status_code in _RETRYABLE_STATUS_CODES:
            raise RetryableWordPressError(
                f"WordPress server error (HTTP {response.status_code})",
                status_code=response.status_code,
            )

        # Other non-2xx
        if not response.ok:
            raise PermanentWordPressError(
                f"Unexpected HTTP {response.status_code}: {response.text[:200]}",
                status_code=response.status_code,
            )

        # Parse success response
        try:
            body = response.json()
        except Exception as exc:
            raise RetryableWordPressError(
                f"Could not parse response as JSON: {exc}"
            ) from exc

        post_id = body.get("id")
        url     = body.get("link") or body.get("guid", {}).get("rendered")
        status  = body.get("status")

        logger.info(
            "wordpress_publish_success | action=%s | post_id=%s | status=%s | url=%s",
            action, post_id, status, url,
        )

        return PostResponse(
            success=True,
            wordpress_post_id=post_id,
            url=url,
            status=status,
            metadata={"action": action},
        )

    def _headers(self) -> dict:
        return {
            "Authorization": self._auth_header,
            "Content-Type":  "application/json",
            "Accept":        "application/json",
        }

    @staticmethod
    def _build_auth_header(username: str, app_password: str) -> str:
        """Build HTTP Basic Auth header from username + application password."""
        token = base64.b64encode(
            f"{username}:{app_password}".encode("utf-8")
        ).decode("utf-8")
        return f"Basic {token}"
