# modules/daily_news/generator.py
"""
Content generation for daily_news.

Two paths:
  generate_news_post(topic)     — original static topic path (kept for tests/fallback)
  summarize_article(article)    — new RSS-driven path (Phase 7)

Both use shared.ai only. No direct Anthropic or DeepSeek imports here.
"""

import logging

from shared.ai import get_ai_config, ai_complete, AIClientError
from shared.ingestion.models import Article

logger = logging.getLogger(__name__)

_AI_CONFIG = get_ai_config("daily_news")

_SYSTEM_PROMPT = """You are a social media writer for an expat guide about Germany.
Write short, practical, engaging posts about daily life in Germany.
Tone: helpful, modern, trustworthy. No hashtags. No emojis unless natural."""


def generate_news_post(topic: str) -> str:
    """
    Original static-topic path. Kept for dry-run fallback and tests.
    """
    prompt = f"""Write a short social media post (3-5 sentences) about this Germany topic:

{topic}

Focus on practical value for expats and foreigners living in Germany.
Return only the post text, nothing else."""

    return ai_complete(_AI_CONFIG, prompt=prompt, system=_SYSTEM_PROMPT)


def summarize_article(article: Article) -> str:
    """
    RSS-driven path. Summarizes a real article into a social media post.

    Uses only RSS metadata (title + summary + link).
    Does NOT fetch or scrape the article body.
    """
    # Build context from what RSS provides
    context_parts = [f"Title: {article.title}"]
    if article.summary:
        context_parts.append(f"Summary: {article.summary}")
    context_parts.append(f"Source: {article.source}")
    context = "\n".join(context_parts)

    prompt = f"""You are writing a social media post for GermanySupport.de, an expat guide for people living in Germany.

Based on this news article, write a short social media post (3-5 sentences) that is relevant and useful for expats in Germany.

{context}

Requirements:
- Focus on practical impact for expats or foreigners living in Germany
- If the article is not relevant to life in Germany, still write a brief informative post
- Return only the post text, no preamble, no explanation
- Do not include the URL in the post text"""

    return ai_complete(_AI_CONFIG, prompt=prompt, system=_SYSTEM_PROMPT)
