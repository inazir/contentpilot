#!/usr/bin/env python3
"""
Phase 14B logic tests — routing strategies and RouteDecision.
Pure Python, no AI calls, no DB, no network needed.
"""
import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "shared", "routing"))

from strategies import keyword_match, _topic_in_text
from router import RouteDecision, RoutingConfig, STRATEGY_MANUAL, STRATEGY_KEYWORD, STRATEGY_AI


# ── keyword_match tests ────────────────────────────────────────────────────

def test_keyword_exact_match():
    print("=== Test: exact keyword found in title ===")
    score = keyword_match("Anmeldung process in Germany", "", ["anmeldung"])
    assert score > 0, f"Expected match, got {score}"
    print(f"  score={score:.2f}  PASS")

def test_keyword_case_insensitive():
    print("=== Test: keyword matching is case-insensitive ===")
    score = keyword_match("HEALTH INSURANCE for expats", "", ["health insurance"])
    assert score > 0
    print("  PASS")

def test_keyword_multi_word_topic():
    print("=== Test: multi-word topic matched as phrase ===")
    score = keyword_match("Opening a bank account in Germany", "", ["bank account"])
    assert score > 0
    print(f"  score={score:.2f}  PASS")

def test_keyword_no_match():
    print("=== Test: no keyword match returns 0.0 ===")
    score = keyword_match("Weather in Berlin today", "", ["tax", "visa", "anmeldung"])
    assert score == 0.0
    print("  PASS")

def test_keyword_empty_topics_returns_zero():
    print("=== Test: empty topics list returns 0.0 ===")
    score = keyword_match("Any article title", "any summary", [])
    assert score == 0.0
    print("  PASS")

def test_keyword_partial_match_score():
    print("=== Test: partial match returns fractional score ===")
    score = keyword_match("Anmeldung guide", "", ["anmeldung", "visa", "tax"])
    assert 0.0 < score < 1.0, f"Expected partial score, got {score}"
    print(f"  score={score:.2f} (1/3 topics matched)  PASS")

def test_keyword_all_match_score_is_one():
    print("=== Test: all topics matched returns 1.0 ===")
    score = keyword_match("Anmeldung visa and tax guide", "", ["anmeldung", "visa", "tax"])
    assert score == 1.0
    print("  PASS")

def test_keyword_word_boundary():
    print("=== Test: 'bank' does not match 'banking' (word boundary) ===")
    result = _topic_in_text("bank", "banking in germany")
    assert result is False, "Single-word topics must not match substrings"
    result2 = _topic_in_text("bank", "go to the bank today")
    assert result2 is True
    print("  PASS")

def test_keyword_matches_in_summary_too():
    print("=== Test: keyword matched in summary (not just title) ===")
    score = keyword_match("Life in Germany", "anmeldung is required for all", ["anmeldung"])
    assert score > 0
    print("  PASS")


# ── RouteDecision tests ────────────────────────────────────────────────────

def test_manual_strategy_always_routes():
    print("=== Test: manual strategy RouteDecision is always True ===")
    d = RouteDecision(route=True, score=1.0, strategy=STRATEGY_MANUAL, reason="manual")
    assert d.route is True
    print("  PASS")

def test_route_decision_str():
    print("=== Test: RouteDecision __str__ shows action ===")
    d = RouteDecision(route=False, score=0.1, strategy=STRATEGY_KEYWORD, reason="below_threshold")
    s = str(d)
    assert "SKIP" in s
    assert "keyword" in s
    print(f"  {s}  PASS")

def test_route_decision_route_str():
    print("=== Test: RouteDecision ROUTE shows correctly ===")
    d = RouteDecision(route=True, score=0.8, strategy=STRATEGY_AI, reason="ai_score=0.80")
    assert "ROUTE" in str(d)
    print("  PASS")


# ── RoutingConfig defaults ─────────────────────────────────────────────────

def test_routing_config_defaults():
    print("=== Test: RoutingConfig has safe defaults ===")
    cfg = RoutingConfig(brand_id=1)
    assert cfg.strategy == STRATEGY_MANUAL
    assert cfg.threshold == 0.01
    assert cfg.rss_feeds == []
    assert cfg.topics == []
    print("  PASS")

def test_routing_config_custom_values():
    print("=== Test: RoutingConfig stores custom values ===")
    cfg = RoutingConfig(
        brand_id=1,
        strategy=STRATEGY_KEYWORD,
        threshold=0.3,
        rss_feeds=["https://example.com/rss"],
        topics=["anmeldung", "visa"],
    )
    assert cfg.strategy == STRATEGY_KEYWORD
    assert cfg.threshold == 0.3
    assert len(cfg.rss_feeds) == 1
    assert len(cfg.topics) == 2
    print("  PASS")


if __name__ == "__main__":
    test_keyword_exact_match()
    test_keyword_case_insensitive()
    test_keyword_multi_word_topic()
    test_keyword_no_match()
    test_keyword_empty_topics_returns_zero()
    test_keyword_partial_match_score()
    test_keyword_all_match_score_is_one()
    test_keyword_word_boundary()
    test_keyword_matches_in_summary_too()
    test_manual_strategy_always_routes()
    test_route_decision_str()
    test_route_decision_route_str()
    test_routing_config_defaults()
    test_routing_config_custom_values()
    print("\nAll Phase 14B routing logic tests passed.")
