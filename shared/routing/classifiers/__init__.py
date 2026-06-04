# shared/routing/classifiers/__init__.py
"""
Article classifier layer.

Architecture decision: The router depends on BaseClassifier (the abstract
interface), never on a concrete implementation. This allows the classification
strategy to be upgraded from keyword matching → embedding similarity →
LLM-based classification without modifying the router.

Current implementations:
    KeywordClassifier  — token-overlap scoring (zero dependencies, fast)

Planned:
    EmbeddingClassifier  — cosine similarity via sentence-transformers
    LLMClassifier        — AI-powered topic extraction and matching

Usage:
    classifier = KeywordClassifier()
    results = classifier.classify_all(article_text, tags, clients)
    # → list[RoutingResult] sorted by score descending
"""

from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod

from shared.routing.models.client import ClientConfig
from shared.routing.models.routing import RoutingResult

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------

class BaseClassifier(ABC):
    """
    Abstract interface for article-to-client classification.

    Implementations score how well an article matches each client's
    routing keywords / profile. The router uses these scores to pick
    the best-matching client.

    All implementations must be stateless and thread-safe.
    """

    @abstractmethod
    def classify(
        self,
        article_text: str,
        tags: list[str],
        client: ClientConfig,
    ) -> RoutingResult:
        """
        Produce a relevance score for one article against one client.

        Args:
            article_text: Combined title + body + summary of the article.
            tags:         AI-generated or RSS-provided tags.
            client:       Client to score against.

        Returns:
            RoutingResult with score 0.0–1.0.
        """

    def classify_all(
        self,
        article_text: str,
        tags: list[str],
        clients: list[ClientConfig],
    ) -> list[RoutingResult]:
        """
        Score all clients and return results sorted by score descending.

        Tiebreaker: clients with equal scores are ordered by routing_priority
        (higher priority wins). This ensures deterministic output and lets
        operators influence routing without changing keywords.

        Default implementation calls classify() per client. Override for
        batch-optimised backends (e.g. single embedding model pass).
        """
        # Build a lookup so we can access routing_priority during sort
        priority_by_id = {c.client_id: c.routing_priority for c in clients}

        results = [
            self.classify(article_text, tags, client)
            for client in clients
        ]
        return sorted(
            results,
            key=lambda r: (r.score, priority_by_id.get(r.client_id, 0)),
            reverse=True,
        )

    @property
    def name(self) -> str:
        return self.__class__.__name__


# ---------------------------------------------------------------------------
# Keyword classifier
# ---------------------------------------------------------------------------

class KeywordClassifier(BaseClassifier):
    """
    Score articles by keyword token overlap against client routing_keywords.

    Scoring algorithm:
        1. Normalise article text (lowercase, strip punctuation).
        2. For each routing keyword of the client:
             - Check if the keyword (or its individual tokens) appear in
               the article text or tag list.
             - Phrase matches score higher than individual token matches.
        3. Final score = weighted_matches / total_keywords, clamped to [0, 1].
           Priority bonus: client.routing_priority adds a small tiebreaker boost.

    This is intentionally simple and dependency-free. It performs well
    enough for O(10s) of clients and O(100s) of keywords per client.

    Thread safety: Fully stateless — safe to share across threads.
    """

    # Weight of a full-phrase match vs individual token match
    PHRASE_WEIGHT = 2.0
    TOKEN_WEIGHT  = 1.0

    # Small additive boost per routing_priority point (max priority ≈ 10)
    PRIORITY_BONUS_PER_POINT = 0.002

    def classify(
        self,
        article_text: str,
        tags: list[str],
        client: ClientConfig,
    ) -> RoutingResult:
        if not client.routing_keywords:
            return RoutingResult(
                client_id=client.client_id,
                score=0.0,
                matched_terms=(),
                classifier=self.name,
            )

        # Normalised search corpus: article text + tags joined together
        corpus = self._normalise(article_text + " " + " ".join(tags))

        matched_terms: list[str] = []
        weighted_score = 0.0
        max_possible = len(client.routing_keywords) * self.PHRASE_WEIGHT

        for keyword in client.routing_keywords:
            kw_norm = self._normalise(keyword)

            if kw_norm in corpus:
                # Full phrase match — highest confidence
                weighted_score += self.PHRASE_WEIGHT
                matched_terms.append(keyword)
            else:
                # Token-level fallback — partial match
                tokens = kw_norm.split()
                matching_tokens = [t for t in tokens if t in corpus and len(t) > 2]
                if len(matching_tokens) >= max(1, len(tokens) // 2):
                    weighted_score += self.TOKEN_WEIGHT * (len(matching_tokens) / len(tokens))
                    matched_terms.append(keyword)

        # Normalise to [0, 1]
        raw_score = weighted_score / max_possible if max_possible > 0 else 0.0

        # Priority tiebreaker — tiny additive bonus, never dominates
        priority_bonus = client.routing_priority * self.PRIORITY_BONUS_PER_POINT
        final_score = min(1.0, raw_score + priority_bonus)

        logger.debug(
            "keyword_classify | client=%s | keywords=%d | matched=%d | score=%.4f",
            client.client_id, len(client.routing_keywords), len(matched_terms), final_score,
        )

        return RoutingResult(
            client_id=client.client_id,
            score=final_score,
            matched_terms=tuple(matched_terms),
            classifier=self.name,
        )

    @staticmethod
    def _normalise(text: str) -> str:
        """Lowercase and strip punctuation, preserving spaces."""
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        return re.sub(r"\s+", " ", text).strip()


# ---------------------------------------------------------------------------
# Stubs for future classifiers (illustrate the extension point)
# ---------------------------------------------------------------------------

class EmbeddingClassifier(BaseClassifier):
    """
    Planned: cosine similarity between article embedding and client keyword embeddings.

    Would use sentence-transformers or OpenAI embeddings. Not yet implemented.
    """

    def classify(
        self,
        article_text: str,
        tags: list[str],
        client: ClientConfig,
    ) -> RoutingResult:
        raise NotImplementedError(
            "EmbeddingClassifier is not yet implemented. Use KeywordClassifier."
        )


class LLMClassifier(BaseClassifier):
    """
    Planned: LLM-based relevance scoring via the shared AI router.

    Sends article + client description to the AI and receives a 0–1 relevance score.
    More accurate than keyword matching but slower and costs tokens.
    Not yet implemented.
    """

    def classify(
        self,
        article_text: str,
        tags: list[str],
        client: ClientConfig,
    ) -> RoutingResult:
        raise NotImplementedError(
            "LLMClassifier is not yet implemented. Use KeywordClassifier."
        )
