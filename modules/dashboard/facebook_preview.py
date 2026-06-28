# modules/dashboard/facebook_preview.py
"""
Preview generation for Facebook content config (Step 6).

Builds the AI prompt/system message from saved brand_content_config
values — mirrors modules/daily_news/generator.py's prompt shape, but
parameterized by the dashboard's saved config instead of hardcoded
topics, so a brand's actual configured tone/topics/CTA show up in
the preview exactly as they would in a real run.

Image generation itself is NOT implemented here (shared/image/* was
not available to build against) — this module reports what WOULD be
fetched (search query + overlay text) without calling any image API.
That gap is reported explicitly in the result, not hidden.

No publish, no duplicate-check, no DB writes. Read-only preview only.
"""
from __future__ import annotations

import random


def build_system_prompt(tone: str) -> str:
    """
    Mirrors modules/daily_news/generator.py's SYSTEM_PROMPT shape,
    substituting the brand's configured tone for the hardcoded one.
    """
    tone = tone.strip() or "helpful, modern, trustworthy"
    return (
        "You are a social media writer for this brand's Facebook page.\n"
        "Write short, practical, engaging posts.\n"
        f"Tone: {tone}. No hashtags in the body text itself — hashtags "
        "are appended separately. No emojis unless natural."
    )


def build_user_prompt(content_config: dict) -> tuple[str, str]:
    """
    Builds the user prompt for caption generation from saved config.
    Returns (prompt, chosen_topic) — chosen_topic is surfaced in the
    preview output so it's clear which topic was used this time.

    Raises ValueError if no caption_topics are configured — a preview
    can't be generated from nothing, and this should surface as a
    clear error rather than silently generating about an empty topic.
    """
    topics = content_config.get("caption_topics") or []
    if not topics:
        raise ValueError(
            "No caption topics configured yet. Add at least one topic "
            "in the Facebook settings before generating a preview."
        )

    topic = random.choice(topics)

    excluded = content_config.get("excluded_keywords") or []
    excluded_note = ""
    if excluded:
        excluded_note = (
            f"\nDo not mention or reference: {', '.join(excluded)}."
        )

    location = content_config.get("location_text", "").strip()
    location_note = f"\nIf relevant, this content is aimed at: {location}." if location else ""

    prompt = (
        f"Write a short Facebook post (3-5 sentences) about this topic:\n\n"
        f"{topic}\n"
        f"{excluded_note}{location_note}\n\n"
        "Return only the post text, nothing else."
    )
    return prompt, topic


def build_hashtag_line(content_config: dict) -> str:
    hashtags = content_config.get("hashtags") or []
    return " ".join(hashtags)


def build_first_comment(content_config: dict) -> str:
    return content_config.get("first_comment_template", "").strip()


def build_image_plan(content_config: dict, topic: str) -> dict:
    """
    Reports what the image pipeline WOULD do, without calling any
    image API. Honest placeholder: shared/image/* internals weren't
    available to build against safely.
    """
    source = content_config.get("image_source", "pexels").strip() or "pexels"
    title_template = content_config.get("image_title_template", "").strip()
    subtitle_template = content_config.get("image_subtitle_template", "").strip()

    title = title_template.replace("{topic}", topic) if title_template else topic
    subtitle = subtitle_template.replace("{topic}", topic) if subtitle_template else ""

    return {
        "source": source,
        "search_query": topic,
        "overlay_title": title,
        "overlay_subtitle": subtitle,
        "note": (
            f"Image would be sourced from {source} using this query, "
            "with the title/subtitle overlaid. Actual image fetch is "
            "not wired into this preview yet."
        ),
    }


def build_preview_plan(content_config: dict) -> dict:
    """
    Top-level entry point. Returns everything needed to render the
    preview EXCEPT the generated caption text itself, which requires
    an AI call (kept separate so this function stays pure/testable).
    """
    user_prompt, topic = build_user_prompt(content_config)
    return {
        "topic": topic,
        "system_prompt": build_system_prompt(content_config.get("tone", "")),
        "user_prompt": user_prompt,
        "hashtag_line": build_hashtag_line(content_config),
        "first_comment": build_first_comment(content_config),
        "cta_text": content_config.get("cta_text", "").strip(),
        "image_plan": build_image_plan(content_config, topic),
    }
