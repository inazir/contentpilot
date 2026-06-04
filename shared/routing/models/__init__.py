# shared/routing/models/__init__.py
from .client import ClientConfig, WordPressClientConfig, FacebookClientConfig
from .client import PublishingPreferences, ImagePostConfig, ReelConfig
from .routing import RoutingResult, RoutingDecision
from .publishing import PublishTarget, PublishRequest, PublishOutcome, PublishSummary

__all__ = [
    "ClientConfig",
    "WordPressClientConfig",
    "FacebookClientConfig",
    "PublishingPreferences",
    "ImagePostConfig",
    "ReelConfig",
    "RoutingResult",
    "RoutingDecision",
    "PublishTarget",
    "PublishRequest",
    "PublishOutcome",
    "PublishSummary",
]
