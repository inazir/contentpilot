# modules/daily_news/generator.py
import logging
from shared.ai import get_ai_config, ai_complete, AIClientError

logger = logging.getLogger(__name__)

_AI_CONFIG = get_ai_config("daily_news")

SYSTEM_PROMPT = """You are a social media writer for an expat guide about Germany.
Write short, practical, engaging posts about daily life in Germany.
Tone: helpful, modern, trustworthy. No hashtags. No emojis unless natural."""


def generate_news_post(topic: str) -> str:
    prompt = f"""Write a short social media post (3-5 sentences) about this Germany topic:

{topic}

Focus on practical value for expats and foreigners living in Germany.
Return only the post text, nothing else."""

    return ai_complete(
        _AI_CONFIG,
        prompt=prompt,
        system=SYSTEM_PROMPT,
    )