#!/usr/bin/env python3
"""
Tests modules/dashboard/facebook_preview.py — pure logic, no AI calls,
no FastAPI. Confirms prompt-building and image-plan reporting are
correct, and that missing config fails clearly rather than silently.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "modules", "dashboard"))

from facebook_preview import (
    build_system_prompt,
    build_user_prompt,
    build_hashtag_line,
    build_first_comment,
    build_image_plan,
    build_preview_plan,
)


def test_system_prompt_uses_configured_tone():
    print("=== Test: system prompt includes configured tone ===")
    prompt = build_system_prompt("witty and concise")
    assert "witty and concise" in prompt
    print("  PASS")


def test_system_prompt_defaults_when_tone_blank():
    print("=== Test: blank tone falls back to a sensible default ===")
    prompt = build_system_prompt("")
    assert "helpful, modern, trustworthy" in prompt
    print("  PASS")


def test_user_prompt_picks_a_configured_topic():
    print("=== Test: user prompt picks one of the configured topics ===")
    config = {"caption_topics": ["Anmeldung", "health insurance"]}
    prompt, topic = build_user_prompt(config)
    assert topic in config["caption_topics"]
    assert topic in prompt
    print(f"  topic={topic!r}  PASS")


def test_user_prompt_includes_excluded_keywords_note():
    print("=== Test: excluded keywords appear as a constraint in the prompt ===")
    config = {"caption_topics": ["taxes"], "excluded_keywords": ["politics", "religion"]}
    prompt, _ = build_user_prompt(config)
    assert "politics" in prompt and "religion" in prompt
    print("  PASS")


def test_user_prompt_no_topics_raises_clear_error():
    print("=== Test: CRITICAL — no topics configured raises a clear error, not a crash ===")
    try:
        build_user_prompt({"caption_topics": []})
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "No caption topics configured" in str(exc)
        print(f"  raised correctly: {exc}  PASS")


def test_user_prompt_missing_key_raises_same_error():
    print("=== Test: missing caption_topics key (not just empty) also raises clearly ===")
    try:
        build_user_prompt({})
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "No caption topics configured" in str(exc)
        print("  PASS")


def test_hashtag_line_joins_with_spaces():
    print("=== Test: hashtag line joins list with spaces ===")
    line = build_hashtag_line({"hashtags": ["#a", "#b", "#c"]})
    assert line == "#a #b #c"
    assert build_hashtag_line({}) == ""
    print(f"  {line!r}  PASS")


def test_image_plan_substitutes_topic_into_templates():
    print("=== Test: image plan substitutes {topic} into title/subtitle templates ===")
    config = {
        "image_source": "pexels",
        "image_title_template": "{topic} — what you need to know",
        "image_subtitle_template": "A guide for expats",
    }
    plan = build_image_plan(config, topic="Anmeldung")
    assert plan["overlay_title"] == "Anmeldung — what you need to know"
    assert plan["overlay_subtitle"] == "A guide for expats"
    assert plan["search_query"] == "Anmeldung"
    assert plan["source"] == "pexels"
    print(f"  {plan}  PASS")


def test_image_plan_falls_back_to_topic_when_no_title_template():
    print("=== Test: image plan falls back to bare topic when no title template set ===")
    plan = build_image_plan({}, topic="taxes")
    assert plan["overlay_title"] == "taxes"
    assert plan["overlay_subtitle"] == ""
    assert plan["source"] == "pexels"  # default
    print("  PASS")


def test_image_plan_never_calls_a_real_image_api():
    print("=== Test: image plan note explicitly says fetch is not wired in ===")
    plan = build_image_plan({}, topic="x")
    assert "not wired into this preview" in plan["note"]
    print("  PASS")


def test_full_preview_plan_assembles_everything():
    print("=== Test: build_preview_plan assembles all fields together ===")
    config = {
        "caption_topics": ["Anmeldung"],
        "hashtags": ["#expat", "#germany"],
        "cta_text": "DM us",
        "first_comment_template": "Questions below!",
        "tone": "friendly",
        "image_source": "pexels",
        "image_title_template": "{topic}",
    }
    plan = build_preview_plan(config)
    assert plan["topic"] == "Anmeldung"
    assert plan["hashtag_line"] == "#expat #germany"
    assert plan["cta_text"] == "DM us"
    assert plan["first_comment"] == "Questions below!"
    assert "friendly" in plan["system_prompt"]
    assert plan["image_plan"]["overlay_title"] == "Anmeldung"
    print(f"  {plan}  PASS")


def test_full_preview_plan_propagates_missing_topics_error():
    print("=== Test: build_preview_plan raises the same clear error with no topics ===")
    try:
        build_preview_plan({"hashtags": ["#a"]})
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "No caption topics configured" in str(exc)
        print("  PASS")


if __name__ == "__main__":
    test_system_prompt_uses_configured_tone()
    test_system_prompt_defaults_when_tone_blank()
    test_user_prompt_picks_a_configured_topic()
    test_user_prompt_includes_excluded_keywords_note()
    test_user_prompt_no_topics_raises_clear_error()
    test_user_prompt_missing_key_raises_same_error()
    test_hashtag_line_joins_with_spaces()
    test_image_plan_substitutes_topic_into_templates()
    test_image_plan_falls_back_to_topic_when_no_title_template()
    test_image_plan_never_calls_a_real_image_api()
    test_full_preview_plan_assembles_everything()
    test_full_preview_plan_propagates_missing_topics_error()
    print("\nAll facebook preview logic tests passed.")
