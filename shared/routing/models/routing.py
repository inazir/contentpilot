# shared/routing/models/routing.py
"""
Data models for routing decisions.

RoutingResult is what the classifier returns per-client.
RoutingDecision is the final output of the router — which client won and why.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import ClientConfig


@dataclass(frozen=True)
class RoutingResult:
    """
    Score produced by a classifier for one client against one article.

    score:         Relevance score (0.0–1.0). Higher = better match.
    matched_terms: Which keywords/signals triggered the match (for audit logging).
    classifier:    Name of the classifier that produced this result.
    """
    client_id: str
    score: float
    matched_terms: tuple[str, ...] = field(default_factory=tuple)
    classifier: str = "unknown"

    def __repr__(self) -> str:
        return (
            f"RoutingResult(client={self.client_id!r}, score={self.score:.3f}, "
            f"terms={list(self.matched_terms)[:5]}, classifier={self.classifier!r})"
        )


@dataclass
class RoutingDecision:
    """
    Final routing output from AutoPublisherRouter.

    matched_client: The winning ClientConfig, or None if no match found.
    score:          Score of the winning match.
    all_results:    Scores for all evaluated clients (useful for debugging).
    article_id:     Identifier of the article being routed (for logging).
    routed:         True if a suitable client was found.
    reason:         Human-readable explanation of the decision.
    """
    article_id: str
    matched_client: "ClientConfig | None"
    score: float
    all_results: list[RoutingResult] = field(default_factory=list)
    routed: bool = False
    reason: str = ""

    def __repr__(self) -> str:
        client_id = self.matched_client.client_id if self.matched_client else "none"
        return (
            f"RoutingDecision(article={self.article_id!r}, client={client_id!r}, "
            f"score={self.score:.3f}, routed={self.routed})"
        )
