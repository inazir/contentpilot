#!/usr/bin/env python3
"""
Integration test: confirms the preview route's AI-calling logic
(get_ai_config + ai_complete + AIClientError handling) works correctly
against the REAL shared.ai package (reconstructed from source, not a
mock). API keys are deliberately unset, so calls fail fast via
AIClientError -- proving the error path app.py relies on actually
triggers correctly, without making any real network call.
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "modules", "dashboard"))

_TMPDIR = tempfile.TemporaryDirectory(prefix="cp_preview_ai_")
os.environ["STORE_DB_PATH"] = os.path.join(_TMPDIR.name, "contentpilot.db")
os.environ.pop("ANTHROPIC_KEY", None)
os.environ.pop("DEEPSEEK_API_KEY", None)

from shared.ai import get_ai_config, ai_complete, AIClientError
from facebook_preview import build_preview_plan


def test_ai_config_loads_for_daily_news():
    print("=== Test: get_ai_config('daily_news') loads without error ===")
    cfg = get_ai_config("daily_news")
    assert cfg.provider in {"anthropic", "deepseek"}
    print(f"  provider={cfg.provider} model={cfg.model}  PASS")


def test_ai_complete_raises_aiclienterror_without_keys():
    print("=== Test: ai_complete raises AIClientError cleanly when no API key set ===")
    cfg = get_ai_config("daily_news")
    try:
        ai_complete(cfg, prompt="test", system="test")
        assert False, "Expected AIClientError"
    except AIClientError as exc:
        print(f"  raised correctly: {exc}  PASS")


def test_full_preview_flow_with_ai_failure_path():
    print("=== Test: full flow — build plan, then AI call fails predictably ===")
    config = {
        "caption_topics": ["Anmeldung"],
        "hashtags": ["#expat"],
        "tone": "friendly",
    }
    plan = build_preview_plan(config)
    cfg = get_ai_config("daily_news")

    caption_text = None
    ai_error = None
    try:
        caption_text = ai_complete(cfg, prompt=plan["user_prompt"], system=plan["system_prompt"])
    except AIClientError as exc:
        ai_error = str(exc)

    # Mirrors app.py's exact branching logic
    assert caption_text is None
    assert ai_error is not None
    print(f"  caption_text=None, ai_error={ai_error!r}  PASS (app.py would show error banner, not crash)")


if __name__ == "__main__":
    test_ai_config_loads_for_daily_news()
    test_ai_complete_raises_aiclienterror_without_keys()
    test_full_preview_flow_with_ai_failure_path()
    print("\nAll preview AI integration tests passed.")
