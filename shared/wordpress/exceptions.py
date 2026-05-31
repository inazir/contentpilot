# shared/wordpress/exceptions.py
"""
Exception hierarchy for WordPress publishing.

Mirrors shared/social/exceptions.py pattern exactly.
Adapters raise these; callers catch WordPressError without
knowing which HTTP call failed.
"""


class WordPressError(Exception):
    """Base class for all WordPress client failures."""

    retryable: bool = False

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)


class RetryableWordPressError(WordPressError):
    """Transient failure — worth retrying. Examples: timeout, 503."""
    retryable = True


class PermanentWordPressError(WordPressError):
    """Non-recoverable failure. Examples: 400 bad request, auth failure."""
    retryable = False


class AuthError(PermanentWordPressError):
    """Authentication failure. Not retryable until credentials are fixed."""


class ValidationError(PermanentWordPressError):
    """Post data failed WordPress validation."""


class NotFoundError(PermanentWordPressError):
    """Post or resource not found (404)."""
