# shared/routing/__init__.py
"""
ContentPilot multi-client routing layer.

Public API:
    from shared.routing import AutoPublisherRouter
    from shared.routing import MultiClientPublisher
    from shared.routing.repositories import JsonClientRepository, ClientRepository
    from shared.routing.classifiers import KeywordClassifier, BaseClassifier
    from shared.routing.models import (
        ClientConfig, RoutingDecision, PublishRequest, PublishSummary
    )
    from shared.routing.exceptions import (
        NoClientMatchedError, ClientNotFoundError, CredentialMissingError
    )
"""

from .router import AutoPublisherRouter
from .publisher import MultiClientPublisher
from .repositories import ClientRepository, JsonClientRepository
from .classifiers import BaseClassifier, KeywordClassifier
from .exceptions import (
    RoutingError,
    NoClientMatchedError,
    ClientNotFoundError,
    ClientConfigError,
    RepositoryError,
    CredentialMissingError,
    PublishRoutingError,
)
from .models import (
    ClientConfig,
    RoutingDecision,
    RoutingResult,
    PublishRequest,
    PublishSummary,
    PublishOutcome,
)

__all__ = [
    "AutoPublisherRouter",
    "MultiClientPublisher",
    "ClientRepository",
    "JsonClientRepository",
    "BaseClassifier",
    "KeywordClassifier",
    "RoutingError",
    "NoClientMatchedError",
    "ClientNotFoundError",
    "ClientConfigError",
    "RepositoryError",
    "CredentialMissingError",
    "PublishRoutingError",
    "ClientConfig",
    "RoutingDecision",
    "RoutingResult",
    "PublishRequest",
    "PublishSummary",
    "PublishOutcome",
]
