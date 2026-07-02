#!/usr/bin/env python3
"""
Tests for Step 7b's updated generator.py. Most critical assertion:
calling generate_news_post(topic) with NO content_config produces
byte-for-byte identical prompts to the original implementation —
this is what every brand with no dashboard config relies on, and a
silent prompt change here would alter live published content for
existing brands without anyone touching the dashboard.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "modules", "daily_news"))

os.environ.setdefault("AI_DEFAULT_PROVIDER", "anthropic")

from generator import _build_system_prompt, _build_user_prompt, _DEFAULT_SYSTEM_PROMPT


# Original prompt strings, copied verbatim from the pre-Step-7b generator.py
# (the version shared earlier in this conversation), to compare against.
_ORIGINAL_SYSTEM_PROMPT = """You are a social media writer for an expat guide about Germany.
Write short, practical, engaging posts about daily life in Germany.
Tone: helpful, modern, trustworthy. No hashtags. No emojis unless natural."""


def _original_user_prompt(topic: str) -> str:
    return f"""Write a short social media post (3-5 sentences) about this Germany topic:

{topic}

Focus on practical value for expats and foreigners living in Germany.
Return only the post text, nothing else."""


def test_system_prompt_none_config_matches_original_exactly():
    print("=== Test: CRITICAL — system prompt with content_config=None is byte-identical to original ===")
    result = _build_system_prompt(None)
    assert result == _ORIGINAL_SYSTEM_PROMPT, (
        f"MISMATCH!\nExpected: {_ORIGINAL_SYSTEM_PROMPT!r}\nGot: {result!r}"
    )
    print("  byte-identical  PASS")


def test_system_prompt_empty_dict_falls_back_to_original():
    print("=== Test: system prompt with content_config={} (no tone key) falls back to original ===")
    result = _build_system_prompt({})
    assert result == _ORIGINAL_SYSTEM_PROMPT
    print("  PASS")


def test_system_prompt_blank_tone_falls_back_to_original():
    print("=== Test: system prompt with tone='' (blank, not missing) falls back to original ===")
    result = _build_system_prompt({"tone": "   "})
    assert result == _ORIGINAL_SYSTEM_PROMPT
    print("  PASS")


def test_system_prompt_real_tone_overrides():
    print("=== Test: a real configured tone changes the prompt ===")
    result = _build_system_prompt({"tone": "witty and concise"})
    assert "witty and concise" in result
    assert result != _ORIGINAL_SYSTEM_PROMPT
    print(f"  {result!r}  PASS")


def test_user_prompt_none_config_matches_original_exactly():
    print("=== Test: CRITICAL — user prompt with content_config=None is byte-identical to original ===")
    topic = "registering your address in Germany (Anmeldung)"
    result = _build_user_prompt(topic, None)
    expected = _original_user_prompt(topic)
    assert result == expected, f"MISMATCH!\nExpected: {expected!r}\nGot: {result!r}"
    print("  byte-identical  PASS")


def test_user_prompt_empty_dict_matches_original():
    print("=== Test: user prompt with content_config={} matches original ===")
    topic = "opening a bank account"
    result = _build_user_prompt(topic, {})
    assert result == _original_user_prompt(topic)
    print("  PASS")


def test_user_prompt_excluded_keywords_appended():
    print("=== Test: excluded keywords appear as a constraint when configured ===")
    result = _build_user_prompt("taxes", {"excluded_keywords": ["politics", "religion"]})
    assert "politics" in result and "religion" in result
    assert "Do not mention or reference" in result
    print("  PASS")


def test_user_prompt_location_appended():
    print("=== Test: location text appears when configured ===")
    result = _build_user_prompt("health insurance", {"location_text": "Stuttgart"})
    assert "Stuttgart" in result
    print("  PASS")


def test_user_prompt_no_excluded_or_location_keys_matches_original():
    print("=== Test: content_config present but without excluded_keywords/location_text matches original ===")
    topic = "public transport"
    result = _build_user_prompt(topic, {"tone": "friendly", "cta_text": "DM us"})
    assert result == _original_user_prompt(topic), (
        "Unrelated content_config keys should not alter the user prompt"
    )
    print("  PASS")


if __name__ == "__main__":
    test_system_prompt_none_config_matches_original_exactly()
    test_system_prompt_empty_dict_falls_back_to_original()
    test_system_prompt_blank_tone_falls_back_to_original()
    test_system_prompt_real_tone_overrides()
    test_user_prompt_none_config_matches_original_exactly()
    test_user_prompt_empty_dict_matches_original()
    test_user_prompt_excluded_keywords_appended()
    test_user_prompt_location_appended()
    test_user_prompt_no_excluded_or_location_keys_matches_original()
    print("\nAll generator content config tests passed.")
