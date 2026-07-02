#!/usr/bin/env python3
"""
Regression check: confirms load_social_targets() (the existing,
unmodified function) behaves identically to before Step 7a. The new
function is additive — this proves the old one wasn't touched.
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

_TMPDIR = tempfile.TemporaryDirectory(prefix="cp_regress_7a_")
os.environ["STORE_DB_PATH"] = os.path.join(_TMPDIR.name, "contentpilot.db")

os.environ["SOCIAL_TARGETS"] = "test_main"
os.environ["SOCIAL__TEST_MAIN__PLATFORM"] = "facebook"
os.environ["SOCIAL__TEST_MAIN__ENABLED"] = "true"
os.environ["SOCIAL__TEST_MAIN__PAGE_ID"] = "123"
os.environ["SOCIAL__TEST_MAIN__ACCESS_TOKEN"] = "tok"

from shared.config import load_social_targets


def test_load_social_targets_unchanged():
    print("=== Regression: load_social_targets() behaves exactly as before ===")
    result = load_social_targets()
    assert "test_main" in result
    target = result["test_main"]
    assert target.platform == "facebook"
    assert target.page_id == "123"
    assert target.access_token == "tok"
    assert target.enabled is True
    print(f"  {target}  PASS")


def test_empty_social_targets_returns_empty_dict():
    print("=== Regression: empty SOCIAL_TARGETS still returns {} ===")
    saved = os.environ.pop("SOCIAL_TARGETS")
    try:
        result = load_social_targets()
        assert result == {}
        print("  PASS")
    finally:
        os.environ["SOCIAL_TARGETS"] = saved


if __name__ == "__main__":
    test_load_social_targets_unchanged()
    test_empty_social_targets_returns_empty_dict()
    print("\nNo regression in existing load_social_targets() behavior.")
