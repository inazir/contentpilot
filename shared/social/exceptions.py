# shared/social/exceptions.py
"""
Exception hierarchy for social publishing.

Platform adapters raise specific subclasses so publisher.py can classify
retryable vs permanent failures without crashing the entire module.
"""


class PublishError(Exception):
    """Base class for all publish failures."""

    retryable: bool = False

    def __init__(self, message: str, platform: str):
        self.platform = platform
        super().__init__(f"[{platform}] {message}")


class RetryablePublishError(PublishError):
    """Transient failure — worth retrying. Examples: timeout, 503."""
    retryable = True


class PermanentPublishError(PublishError):
    """Non-recoverable failure. Examples: invalid content, auth failure."""
    retryable = False


class RateLimitError(RetryablePublishError):
    """API rate limit hit. Retryable after a wait."""


class AuthError(PermanentPublishError):
    """Authentication failure. Not retryable until credentials are fixed."""


class ValidationError(PermanentPublishError):
    """Content failed platform validation. Not retryable without changes."""
