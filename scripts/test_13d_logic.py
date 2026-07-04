#!/usr/bin/env python3
"""
Phase 13D logic tests — schedule config and CSV parsing.
Pure Python, no FastAPI, no DB, no network needed.
"""
import os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "modules", "dashboard"))

from facebook_schedule import (
    parse_schedule_form, validate_schedule, schedule_to_display,
    merge_schedule_into_config, _is_valid_time, _parse_times, _parse_days,
)
from facebook_csv import parse_csv_bytes, merge_topics, validate_topics_list

# ── Schedule tests ─────────────────────────────────────────────────────────

def test_parse_schedule_form_daily():
    print("=== Test: parse daily schedule from form ===")
    s = parse_schedule_form({"schedule_frequency": "daily",
                              "schedule_times": "09:00",
                              "schedule_active_days": "0,1,2,3,4",
                              "schedule_max_posts": "1"})
    assert s["frequency"] == "daily"
    assert s["times"] == ["09:00"]
    assert s["active_days"] == [0,1,2,3,4]
    assert s["max_posts_per_day"] == 1
    print("  PASS")

def test_parse_schedule_form_twice_daily():
    print("=== Test: parse twice_daily schedule ===")
    s = parse_schedule_form({"schedule_frequency": "twice_daily",
                              "schedule_times": "09:00, 17:00",
                              "schedule_active_days": "0,1,2,3,4",
                              "schedule_max_posts": "2"})
    assert s["times"] == ["09:00", "17:00"]
    assert s["max_posts_per_day"] == 2
    print("  PASS")

def test_parse_schedule_defaults_on_empty():
    print("=== Test: empty form fields fall back to frequency defaults ===")
    s = parse_schedule_form({"schedule_frequency": "weekly"})
    assert s["frequency"] == "weekly"
    assert s["times"] == ["09:00"]
    assert s["active_days"] == [0]
    print("  PASS")

def test_validate_schedule_valid():
    print("=== Test: valid schedule passes validation ===")
    s = {"frequency": "daily", "times": ["09:00"],
         "active_days": [0,1,2,3,4], "max_posts_per_day": 1}
    assert validate_schedule(s) == []
    print("  PASS")

def test_validate_schedule_daily_rejects_two_times():
    print("=== Test: daily frequency with two times is rejected ===")
    s = {"frequency": "daily", "times": ["09:00", "17:00"],
         "active_days": [0], "max_posts_per_day": 1}
    errors = validate_schedule(s)
    assert any("twice_daily" in e for e in errors)
    print(f"  {errors}  PASS")

def test_validate_schedule_bad_time_format():
    print("=== Test: invalid time format caught ===")
    s = {"frequency": "daily", "times": ["9am"],
         "active_days": [0], "max_posts_per_day": 1}
    errors = validate_schedule(s)
    assert any("9am" in e for e in errors)
    print(f"  {errors}  PASS")

def test_validate_schedule_no_active_days():
    print("=== Test: no active days rejected ===")
    s = {"frequency": "daily", "times": ["09:00"],
         "active_days": [], "max_posts_per_day": 1}
    errors = validate_schedule(s)
    assert any("active day" in e for e in errors)
    print("  PASS")

def test_merge_schedule_into_config():
    print("=== Test: schedule merged into existing content_config ===")
    config = {"caption_topics": ["topic1"], "cta_text": "DM us"}
    schedule = {"frequency": "daily", "times": ["09:00"],
                "active_days": [0,1,2,3,4], "max_posts_per_day": 1}
    merged = merge_schedule_into_config(config, schedule)
    assert merged["schedule"] == schedule
    assert merged["caption_topics"] == ["topic1"]  # unchanged
    assert merged["cta_text"] == "DM us"           # unchanged
    print("  PASS")

def test_schedule_to_display_none():
    print("=== Test: None schedule returns safe defaults ===")
    d = schedule_to_display(None)
    assert d["frequency"] == "daily"
    assert "Mon" in d["active_day_labels"]
    print("  PASS")

def test_max_posts_clamped():
    print("=== Test: max_posts_per_day clamped to 1-10 ===")
    s = parse_schedule_form({"schedule_frequency": "daily",
                              "schedule_times": "09:00",
                              "schedule_active_days": "0",
                              "schedule_max_posts": "999"})
    assert s["max_posts_per_day"] == 10
    s2 = parse_schedule_form({"schedule_frequency": "daily",
                               "schedule_times": "09:00",
                               "schedule_active_days": "0",
                               "schedule_max_posts": "-5"})
    assert s2["max_posts_per_day"] == 1
    print("  PASS")

# ── CSV tests ──────────────────────────────────────────────────────────────

def test_csv_simple_one_per_row():
    print("=== Test: simple CSV one topic per row ===")
    raw = b"Anmeldung process\nHealth insurance for expats\nBank account"
    topics, errors = parse_csv_bytes(raw)
    assert topics == ["Anmeldung process", "Health insurance for expats", "Bank account"]
    assert errors == []
    print(f"  {topics}  PASS")

def test_csv_header_row_skipped():
    print("=== Test: header row 'topic' auto-detected and skipped ===")
    raw = b"topic\nAnmeldung process\nHealth insurance"
    topics, errors = parse_csv_bytes(raw)
    assert "topic" not in topics
    assert "Anmeldung process" in topics
    print("  PASS")

def test_csv_empty_file_raises():
    print("=== Test: empty file raises ValueError ===")
    try:
        parse_csv_bytes(b"")
        assert False, "Expected ValueError"
    except ValueError as e:
        print(f"  raised: {e}  PASS")

def test_csv_merge_adds_new_keeps_existing():
    print("=== Test: merge adds new topics, preserves existing, deduplicates ===")
    existing = ["topic A", "topic B"]
    uploaded = ["topic B", "topic C", "topic D"]
    merged = merge_topics(existing, uploaded, replace=False)
    assert merged == ["topic A", "topic B", "topic C", "topic D"]
    print(f"  {merged}  PASS")

def test_csv_merge_replace_mode():
    print("=== Test: replace=True fully replaces existing topics ===")
    existing = ["old topic 1", "old topic 2"]
    uploaded = ["new topic A", "new topic B"]
    merged = merge_topics(existing, uploaded, replace=True)
    assert "old topic 1" not in merged
    assert merged == ["new topic A", "new topic B"]
    print("  PASS")

def test_csv_deduplicates_within_upload():
    print("=== Test: duplicate topics within uploaded file are deduplicated ===")
    raw = b"topic A\ntopic A\ntopic B"
    topics, _ = parse_csv_bytes(raw)
    merged = merge_topics([], topics, replace=True)
    assert merged.count("topic A") == 1
    print("  PASS")

def test_csv_long_topic_truncated():
    print("=== Test: topic over 300 chars is truncated with a warning ===")
    long_topic = ("x" * 350).encode()
    raw = b"topic\n" + long_topic
    topics, errors = parse_csv_bytes(raw)
    assert len(topics[0]) == 300
    assert any("truncated" in e for e in errors)
    print("  PASS")

def test_csv_utf8_encoding():
    print("=== Test: UTF-8 topics with German characters parse correctly ===")
    raw = "Anmeldung\nKrankenversicherung\nSteuererklärung".encode("utf-8")
    topics, errors = parse_csv_bytes(raw)
    assert "Steuererklärung" in topics
    assert errors == []
    print("  PASS")

if __name__ == "__main__":
    test_parse_schedule_form_daily()
    test_parse_schedule_form_twice_daily()
    test_parse_schedule_defaults_on_empty()
    test_validate_schedule_valid()
    test_validate_schedule_daily_rejects_two_times()
    test_validate_schedule_bad_time_format()
    test_validate_schedule_no_active_days()
    test_merge_schedule_into_config()
    test_schedule_to_display_none()
    test_max_posts_clamped()
    test_csv_simple_one_per_row()
    test_csv_header_row_skipped()
    test_csv_empty_file_raises()
    test_csv_merge_adds_new_keeps_existing()
    test_csv_merge_replace_mode()
    test_csv_deduplicates_within_upload()
    test_csv_long_topic_truncated()
    test_csv_utf8_encoding()
    print("\nAll Phase 13D logic tests passed.")
