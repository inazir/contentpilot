# shared/routing/exceptions/__init__.py
"""
Exception hierarchy for the routing and multi-client publishing layer.

Follows the same pattern as shared/social/exceptions.py and
shared/wordpress/exceptions.py — typed exceptions so callers can
classify failures without inspecting error strings.
"""


class RoutingError(Exception):
    """Base class for all routing failures."""


class NoClientMatchedError(RoutingError):
    """No client scored above the minimum threshold for the given article."""

    def __init__(self, article_id: str, threshold: float):
        self.article_id = article_id
        self.threshold = threshold
        super().__init__(
            f"No client matched article {article_id!r} above threshold {threshold}"
        )


class ClientNotFoundError(RoutingError):
    """A requested client_id does not exist in the repository."""

    def __init__(self, client_id: str):
        self.client_id = client_id
        super().__init__(f"Client not found: {client_id!r}")


class ClientConfigError(RoutingError):
    """A client configuration is malformed or missing required fields."""


class RepositoryError(RoutingError):
    """Storage backend failure (file not found, parse error, DB error, etc.)."""


class CredentialMissingError(RoutingError):
    """
    A required credential env var is not set.

    Raised at publish time, not at config load time — credentials are
    resolved lazily so the system starts even if some env vars are absent.
    """


class PublishRoutingError(RoutingError):
    """
    Error during the publish step after routing succeeded.

    Wraps platform-specific failures so callers can handle them uniformly.
    """

    def __init__(self, message: str, client_id: str, platform: str, retryable: bool = False):
        self.client_id = client_id
        self.platform = platform
        self.retryable = retryable
        super().__init__(f"[{client_id}:{platform}] {message}")
