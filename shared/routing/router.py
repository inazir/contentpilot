# shared/routing/router.py
"""
Phase 14B: ArticleRouter — decides which brands receive which articles.

Usage in runner.py:
    router = ArticleRouter()
    for brand in get_all_enabled_brands():
        ctx = get_brand_context(brand.id)
        routing_cfg = router.get_routing_config(brand.id)
        articles = router.fetch_articles_for_brand(routing_cfg)
        for article in articles:
            decision = router.should_route(article, ctx, routing_cfg)
            if decision.route:
                # publish article to this brand
                ...

RouteDecision carries the reason, so it can be logged/audited.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

STRATEGY_MANUAL = "manual"
STRATEGY_KEYWORD = "keyword"
STRATEGY_AI = "ai"

VALID_STRATEGIES = {STRATEGY_MANUAL, STRATEGY_KEYWORD, STRATEGY_AI}
DEFAULT_STRATEGY = STRATEGY_MANUAL
DEFAULT_THRESHOLD = 0.01  # for keyword: any match; for AI: 1% relevance


@dataclass
class RouteDecision:
    """Result of routing one article to one brand."""
    route: bool
    score: float = 0.0
    strategy: str = STRATEGY_MANUAL
    reason: str = ""

    def __str__(self) -> str:
        action = "ROUTE" if self.route else "SKIP"
        return f"[{action}] strategy={self.strategy} score={self.score:.2f} reason={self.reason}"


@dataclass
class RoutingConfig:
    """Per-brand routing configuration, read from brand_content_config."""
    brand_id: int
    strategy: str = STRATEGY_MANUAL
    threshold: float = DEFAULT_THRESHOLD
    rss_feeds: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)


class ArticleRouter:
    """
    Central routing coordinator.

    Reads routing config from brand_content_config(platform='routing')
    and applies the configured strategy to decide which articles
    each brand should receive.
    """

    def get_routing_config(self, brand_id: int) -> RoutingConfig:
        """
        Load routing config for a brand from brand_content_config.
        Falls back to safe defaults if no routing config is saved yet.

        Routing config is stored in brand_content_config with
        platform='routing' (a new platform key, not facebook/instagram).
        """
        try:
            from shared.brands.repository import get_content_config, get_all_content_config

            routing_row = get_content_config(brand_id, "routing")
            if routing_row:
                data = routing_row.as_dict()
                strategy = data.get("routing_strategy", DEFAULT_STRATEGY)
                if strategy not in VALID_STRATEGIES:
                    logger.warning(
                        "invalid_routing_strategy | brand_id=%d | strategy=%r | "
                        "falling_back_to=%s", brand_id, strategy, DEFAULT_STRATEGY
                    )
                    strategy = DEFAULT_STRATEGY

                return RoutingConfig(
                    brand_id=brand_id,
                    strategy=strategy,
                    threshold=float(data.get("routing_threshold", DEFAULT_THRESHOLD)),
                    rss_feeds=[f.strip() for f in data.get("rss_feeds", []) if f.strip()],
                    topics=data.get("topics_override") or self._get_brand_topics(brand_id),
                )

        except Exception as exc:
            logger.warning(
                "routing_config_load_failed | brand_id=%d | error=%s | using_defaults",
                brand_id, exc,
            )

        # No routing config saved yet — use safe defaults
        return RoutingConfig(
            brand_id=brand_id,
            strategy=DEFAULT_STRATEGY,
            threshold=DEFAULT_THRESHOLD,
            rss_feeds=self._get_global_feeds(),
            topics=self._get_brand_topics(brand_id),
        )

    def _get_brand_topics(self, brand_id: int) -> list[str]:
        """Get brand's caption_topics from facebook content config as routing topics."""
        try:
            from shared.brands.repository import get_content_config
            fb_config = get_content_config(brand_id, "facebook")
            if fb_config:
                return fb_config.as_dict().get("caption_topics") or []
        except Exception:
            pass
        return []

    def _get_global_feeds(self) -> list[str]:
        """Fallback: read global feed URLs from env (existing behavior)."""
        raw = os.getenv("DAILY_NEWS_RSS_FEEDS", "").strip()
        if not raw:
            return []
        return [u.strip() for u in raw.split(",") if u.strip()]

    def fetch_articles_for_brand(self, routing_cfg: RoutingConfig) -> list:
        """
        Fetch RSS articles for a brand based on its routing config.

        Uses brand-specific feed URLs if configured, falls back to
        global DAILY_NEWS_RSS_FEEDS env var.
        """
        from shared.ingestion import fetch_feeds, get_max_articles, get_feed_timeout

        feed_urls = routing_cfg.rss_feeds or self._get_global_feeds()
        if not feed_urls:
            logger.warning(
                "no_feeds_configured | brand_id=%d", routing_cfg.brand_id
            )
            return []

        max_articles = get_max_articles()
        timeout = get_feed_timeout()

        logger.info(
            "fetching_articles_for_brand | brand_id=%d | feeds=%d | strategy=%s",
            routing_cfg.brand_id, len(feed_urls), routing_cfg.strategy,
        )

        return fetch_feeds(feed_urls, max_articles=max_articles, timeout=timeout)

    def should_route(
        self,
        article,
        brand_context,
        routing_cfg: RoutingConfig,
        ai_cfg=None,
    ) -> RouteDecision:
        """
        Decide whether to route an article to a brand.

        Args:
            article:       Article dataclass from shared.ingestion
            brand_context: BrandContext for the target brand
            routing_cfg:   RoutingConfig for this brand
            ai_cfg:        Optional AIConfig override for AI strategy

        Returns:
            RouteDecision — always returns something, never raises.
        """
        strategy = routing_cfg.strategy

        try:
            if strategy == STRATEGY_MANUAL:
                return RouteDecision(
                    route=True,
                    score=1.0,
                    strategy=STRATEGY_MANUAL,
                    reason="manual_strategy_always_routes",
                )

            elif strategy == STRATEGY_KEYWORD:
                from .strategies import keyword_match
                score = keyword_match(
                    article.title, article.summary, routing_cfg.topics
                )
                route = score > routing_cfg.threshold
                return RouteDecision(
                    route=route,
                    score=score,
                    strategy=STRATEGY_KEYWORD,
                    reason=f"keyword_score={score:.2f} threshold={routing_cfg.threshold:.2f}",
                )

            elif strategy == STRATEGY_AI:
                from .strategies import ai_score
                score = ai_score(
                    article.title,
                    article.summary,
                    brand_name=brand_context.brand_name,
                    topics=routing_cfg.topics,
                    ai_cfg=ai_cfg,
                )
                route = score > routing_cfg.threshold
                return RouteDecision(
                    route=route,
                    score=score,
                    strategy=STRATEGY_AI,
                    reason=f"ai_score={score:.2f} threshold={routing_cfg.threshold:.2f}",
                )

            else:
                logger.warning(
                    "unknown_routing_strategy | strategy=%r | defaulting_to_route",
                    strategy,
                )
                return RouteDecision(
                    route=True,
                    score=1.0,
                    strategy=strategy,
                    reason="unknown_strategy_default_route",
                )

        except Exception as exc:
            logger.error(
                "routing_decision_failed | brand_id=%d | strategy=%s | error=%s | defaulting_to_route",
                routing_cfg.brand_id, strategy, exc,
            )
            return RouteDecision(
                route=True,
                score=1.0,
                strategy=strategy,
                reason=f"routing_error_default_route: {exc}",
            )
