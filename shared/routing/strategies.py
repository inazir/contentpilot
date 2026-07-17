# shared/routing/strategies.py
"""
Phase 14B: Routing strategy implementations.

Three strategies, all return a float score 0.0-1.0:
  0.0 = definitely do not route this article to this brand
  1.0 = definitely route this article to this brand

keyword_match:  Fast, free. Checks article title+summary against
                brand's caption_topics list. Case-insensitive.
                Score = fraction of topics that appear in the article.
                Threshold default: any match (score > 0).

ai_score:       Calls the AI layer to score relevance 0-100.
                Returns score / 100.0.
                Falls back to keyword_match on AI failure.

manual:         Always returns 1.0 — routing is controlled entirely
                by which feeds are assigned to which brands.
                No scoring needed; every article from the brand's
                own feeds is routed to that brand.
"""
from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)


def keyword_match(article_title: str, article_summary: str, topics: list[str]) -> float:
    """
    Score an article against a list of topic keywords.

    Returns fraction of topics found in title+summary (0.0–1.0).
    Empty topics list returns 0.0 (no config = no match).
    Single match is enough: threshold logic lives in the router.
    """
    if not topics:
        return 0.0

    text = f"{article_title} {article_summary}".lower()
    matched = sum(
        1 for topic in topics
        if _topic_in_text(topic.lower(), text)
    )
    return matched / len(topics)


def _topic_in_text(topic: str, text: str) -> bool:
    """Word-boundary aware topic matching — avoids 'bank' matching 'banking'."""
    # If topic is multi-word, do a simple substring match
    if " " in topic:
        return topic in text
    # Single word: require word boundary
    pattern = r"\b" + re.escape(topic) + r"\b"
    return bool(re.search(pattern, text))


def ai_score(
    article_title: str,
    article_summary: str,
    brand_name: str,
    topics: list[str],
    ai_cfg=None,
) -> float:
    """
    Use the AI layer to score article relevance for a brand.

    Returns a float 0.0-1.0.
    Falls back to keyword_match on any AI failure — never crashes the pipeline.

    Args:
        article_title:   Article title string.
        article_summary: Article summary string.
        brand_name:      Brand name for context.
        topics:          Brand's configured topics list.
        ai_cfg:          AIConfig object. If None, loads daily_news config.
    """
    try:
        from shared.ai import get_ai_config, ai_complete, AIClientError

        cfg = ai_cfg or get_ai_config("daily_news")

        topic_list = ", ".join(topics) if topics else "(not specified)"
        prompt = (
            f"Rate how relevant this article is for a brand called '{brand_name}' "
            f"that covers these topics: {topic_list}.\n\n"
            f"Article title: {article_title}\n"
            f"Article summary: {article_summary[:300]}\n\n"
            "Reply with ONLY a single integer from 0 to 100, where:\n"
            "  0   = completely irrelevant\n"
            "  50  = somewhat relevant\n"
            "  100 = highly relevant\n"
            "Do not explain. Just the number."
        )

        response = ai_complete(cfg, prompt=prompt)
        # Extract first integer from response
        match = re.search(r"\d+", response.strip())
        if match:
            score = int(match.group()) / 100.0
            score = max(0.0, min(1.0, score))
            logger.debug(
                "ai_score | brand=%s | title=%r | score=%.2f",
                brand_name, article_title[:50], score,
            )
            return score
        else:
            logger.warning(
                "ai_score_parse_failed | response=%r | falling_back_to_keyword",
                response[:100],
            )

    except Exception as exc:
        logger.warning(
            "ai_score_failed | error=%s | falling_back_to_keyword", exc
        )

    # Fallback: keyword matching
    return keyword_match(article_title, article_summary, topics)
