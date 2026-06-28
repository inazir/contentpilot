#!/usr/bin/env python3
"""
Tests auth.py directly — password verification and session token
creation/verification. No FastAPI needed for these checks.
"""
import hashlib
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

os.environ["DASHBOARD_SECRET_KEY"] = "test-secret-key-do-not-use-in-prod"
os.environ["DASHBOARD_ADMIN_PASSWORD_HASH"] = hashlib.sha256(b"correct-password").hexdigest()

import auth


def test_correct_password_verifies():
    print("=== Test: correct password verifies ===")
    assert auth.verify_password("correct-password") is True
    print("  PASS")


def test_wrong_password_rejected():
    print("=== Test: wrong password rejected ===")
    assert auth.verify_password("wrong-password") is False
    print("  PASS")


def test_session_token_roundtrip():
    print("=== Test: session token created and verified ===")
    token = auth.create_session_token()
    assert auth.verify_session_token(token) is True
    print("  PASS")


def test_garbage_token_rejected():
    print("=== Test: garbage/tampered token rejected, no exception ===")
    assert auth.verify_session_token("not-a-real-token") is False
    assert auth.verify_session_token("") is False
    print("  PASS")


def test_tampered_token_rejected():
    print("=== Test: tampered valid-looking token rejected ===")
    token = auth.create_session_token()
    tampered = token[:-2] + "xx"
    assert auth.verify_session_token(tampered) is False
    print("  PASS")


def test_missing_secret_key_raises():
    print("=== Test: missing DASHBOARD_SECRET_KEY raises clearly ===")
    saved = os.environ.pop("DASHBOARD_SECRET_KEY")
    try:
        try:
            auth.create_session_token()
            assert False, "Expected RuntimeError"
        except RuntimeError as exc:
            assert "DASHBOARD_SECRET_KEY" in str(exc)
            print(f"  raised correctly: {exc}  PASS")
    finally:
        os.environ["DASHBOARD_SECRET_KEY"] = saved


if __name__ == "__main__":
    test_correct_password_verifies()
    test_wrong_password_rejected()
    test_session_token_roundtrip()
    test_garbage_token_rejected()
    test_tampered_token_rejected()
    test_missing_secret_key_raises()
    print("\nAll auth logic tests passed.")
