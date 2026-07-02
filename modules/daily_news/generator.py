# modules/daily_news/generator.py
"""
Phase 13C Step 7b: generate_news_post() now optionally accepts a
content_config dict (from brand_content_config, platform='facebook')
to drive tone, excluded keywords, and location — falling back to the
original hardcoded SYSTEM_PROMPT when no config is provided, so
existing callers (and brands with no dashboard config saved yet)
behave exactly as before.
"""
import logging
from shared.ai import get_ai_config, ai_complete, AIClientError

logger = logging.getLogger(__name__)

_AI_CONFIG = get_ai_config("daily_news")

_DEFAULT_SYSTEM_PROMPT = """You are a social media writer for an expat guide about Germany.
Write short, practical, engaging posts about daily life in Germany.
Tone: helpful, modern, trustworthy. No hashtags. No emojis unless natural."""


def _build_system_prompt(content_config: dict | None) -> str:
    """
    Builds the system prompt. Uses the brand's configured tone if
    present and non-empty; otherwise falls back to the original
    hardcoded prompt verbatim (byte-for-byte, so existing behavior
    for brands with no config is unchanged).
    """
    if not content_config:
        return _DEFAULT_SYSTEM_PROMPT

    tone = (content_config.get("tone") or "").strip()
    if not tone:
        return _DEFAULT_SYSTEM_PROMPT

    return (
        "You are a social media writer for an expat guide about Germany.\n"
        "Write short, practical, engaging posts about daily life in Germany.\n"
        f"Tone: {tone}. No hashtags. No emojis unless natural."
    )


def _build_user_prompt(topic: str, content_config: dict | None) -> str:
    """
    Builds the user prompt. Adds an excluded-keywords constraint and
    a location note when present in content_config — both are no-ops
    (empty string appended) when content_config is None or doesn't
    have those fields, so the prompt text for unconfigured brands is
    byte-for-byte identical to before this change.
    """
    excluded_note = ""
    location_note = ""

    if content_config:
        excluded = content_config.get("excluded_keywords") or []
        if excluded:
            excluded_note = f"\nDo not mention or reference: {', '.join(excluded)}."

        location = (content_config.get("location_text") or "").strip()
        if location:
            location_note = f"\nIf relevant, this content is aimed at: {location}."

    return f"""Write a short social media post (3-5 sentences) about this Germany topic:

{topic}

Focus on practical value for expats and foreigners living in Germany.{excluded_note}{location_note}
Return only the post text, nothing else."""


def generate_news_post(topic: str, content_config: dict | None = None) -> str:
    """
    Generate a news post for the given topic.

    Args:
        topic:          The topic to write about (unchanged behavior).
        content_config: Optional dict from brand_content_config
                         (platform='facebook'), e.g. {"tone": "...",
                         "excluded_keywords": [...], "location_text": "..."}.
                         None (the default) preserves exact prior behavior.
    """
    system_prompt = _build_system_prompt(content_config)
    prompt = _build_user_prompt(topic, content_config)

    return ai_complete(
        _AI_CONFIG,
        prompt=prompt,
        system=system_prompt,
    )

from shared.ingestion.models import Article

def summarize_article(article: Article, content_config: dict | None = None) -> str:
    """
    RSS-driven path. Summarizes a real article into a social media post.
    """
    system_prompt = _build_system_prompt(content_config)
    
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

    return ai_complete(_AI_CONFIG, prompt=prompt, system=system_prompt)
