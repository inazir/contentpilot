# shared/routing/router.py
"""
AutoPublisherRouter — routes articles to the best-matching client.

This is the single entry point for all routing decisions. It depends only
on abstractions (ClientRepository, BaseClassifier), never on concrete
storage or classification implementations.

Usage:
    from shared.routing import AutoPublisherRouter
    from shared.routing.repositories import JsonClientRepository
    from shared.routing.classifiers import KeywordClassifier

    router = AutoPublisherRouter(
        repository=JsonClientRepository(),
        classifier=KeywordClassifier(),
    )

    decision = router.route(
        article_id="abc123",
        article_text="The Federal Reserve raised interest rates...",
        tags=["finance", "Federal Reserve", "interest rates"],
    )

    if decision.routed:
        client = decision.matched_client
        # → finance_client_a (or whichever scored highest)
"""

from __future__ import annotations

import logging
import os

from .classifiers import BaseClassifier, KeywordClassifier
from .exceptions import NoClientMatchedError
from .models.routing import RoutingDecision, RoutingResult
from .repositories import ClientRepository

logger = logging.getLogger(__name__)

_DEFAULT_MIN_SCORE = 0.05   # articles below this score are not routed


class AutoPublisherRouter:
    """
    Routes articles to the best-matching client.

    Responsibilities:
      1. Load all enabled clients from the repository.
      2. Score each client against the article via the classifier.
      3. Select the highest-scoring client above the minimum threshold.
      4. Return a RoutingDecision with full audit trail.

    Design notes:
      - The router is stateless between calls. Client configs are loaded
        from the repository on each call (or cached — see reload_on_call).
      - Multiple clients with identical scores are broken by routing_priority.
      - If no client meets the threshold, the decision has routed=False and
        matched_client=None. The caller decides whether to skip or raise.
    """

    def __init__(
        self,
        repository: ClientRepository,
        classifier: BaseClassifier | None = None,
        min_score: float | None = None,
        reload_on_call: bool = False,
    ) -> None:
        """
        Args:
            repository:      Storage backend for client configs.
            classifier:      Scoring implementation. Defaults to KeywordClassifier.
            min_score:       Minimum score required to route. Reads
                             ROUTING_MIN_SCORE env var if not provided.
                             Defaults to 0.05.
            reload_on_call:  If True, reload client configs from storage on
                             every route() call. Useful for hot-reload in
                             long-running services.
        """
        self._repository = repository
        self._classifier = classifier or KeywordClassifier()
        self._min_score = min_score if min_score is not None else float(
            os.getenv("ROUTING_MIN_SCORE", str(_DEFAULT_MIN_SCORE))
        )
        self._reload_on_call = reload_on_call

        logger.info(
            "AutoPublisherRouter init | classifier=%s | min_score=%.3f | reload=%s",
            self._classifier.name, self._min_score, reload_on_call,
        )

    def route(
        self,
        article_id: str,
        article_text: str,
        tags: list[str] | None = None,
        raise_on_no_match: bool = False,
    ) -> RoutingDecision:
        """
        Route one article to the best-matching client.

        Args:
            article_id:         Unique identifier for logging and deduplication.
            article_text:       Combined article text (title + body + summary).
            tags:               AI-generated or feed-provided tags.
            raise_on_no_match:  If True, raises NoClientMatchedError when no
                                client meets the minimum score threshold.
                                If False (default), returns decision with routed=False.

        Returns:
            RoutingDecision — always returned, never raises unless raise_on_no_match.

        Raises:
            NoClientMatchedError: Only when raise_on_no_match=True and no match.
        """
        tags = tags or []

        if self._reload_on_call:
            self._repository.reload()

        clients = self._repository.get_all()

        if not clients:
            logger.warning(
                "routing_no_clients | article=%s | reason=no_enabled_clients",
                article_id,
            )
            return RoutingDecision(
                article_id=article_id,
                matched_client=None,
                score=0.0,
                routed=False,
                reason="No enabled clients in repository",
            )

        logger.info(
            "routing_start | article=%s | clients=%d | classifier=%s | tags=%s",
            article_id, len(clients), self._classifier.name, tags[:5],
        )

        # Score all clients
        all_results: list[RoutingResult] = self._classifier.classify_all(
            article_text=article_text,
            tags=tags,
            clients=clients,
        )

        # Log all scores for auditability
        for result in all_results:
            logger.debug(
                "routing_score | article=%s | client=%s | score=%.4f | terms=%s",
                article_id, result.client_id, result.score,
                list(result.matched_terms)[:5],
            )

        # Find best match above threshold
        best = self._select_best(all_results)

        if best is None or best.score < self._min_score:
            reason = (
                f"Best score {best.score:.4f} below threshold {self._min_score}"
                if best else "No results from classifier"
            )
            logger.info(
                "routing_no_match | article=%s | threshold=%.3f | best_score=%s",
                article_id, self._min_score,
                f"{best.score:.4f}" if best else "none",
            )

            if raise_on_no_match:
                raise NoClientMatchedError(article_id, self._min_score)

            return RoutingDecision(
                article_id=article_id,
                matched_client=None,
                score=best.score if best else 0.0,
                all_results=all_results,
                routed=False,
                reason=reason,
            )

        # Resolve the winning client config
        matched_client = self._repository.get_by_id(best.client_id)

        logger.info(
            "routing_matched | article=%s | client=%s | score=%.4f | terms=%s",
            article_id, matched_client.client_id, best.score,
            list(best.matched_terms)[:8],
        )

        return RoutingDecision(
            article_id=article_id,
            matched_client=matched_client,
            score=best.score,
            all_results=all_results,
            routed=True,
            reason=f"Matched {matched_client.client_id} (score={best.score:.4f})",
        )

    @staticmethod
    def _select_best(results: list[RoutingResult]) -> RoutingResult | None:
        """
        Select the highest-scoring result.

        Results are already sorted descending by score from classify_all().
        If two results have identical scores, the one returned first from
        classify_all() wins (which uses routing_priority as a tiebreaker
        inside KeywordClassifier).
        """
        return results[0] if results else None
