#!/usr/bin/env python3
"""
Phase 15 logic tests — user_auth.py
Pure Python, no FastAPI needed. DB tests use isolated temp DB.
"""
import os, sys, tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "modules", "dashboard"))

_TMPDIR = tempfile.TemporaryDirectory(prefix="cp_users_")
os.environ["STORE_DB_PATH"] = os.path.join(_TMPDIR.name, "contentpilot.db")
os.environ["DASHBOARD_SECRET_KEY"] = "test-secret-phase15"

# Bootstrap brands table so FK works
import sqlite3
conn = sqlite3.connect(os.environ["STORE_DB_PATH"])
conn.execute("""CREATE TABLE IF NOT EXISTS brands (
    id INTEGER PRIMARY KEY, name TEXT, slug TEXT UNIQUE,
    enabled INTEGER DEFAULT 1, created_at TEXT, updated_at TEXT)""")
conn.execute("INSERT INTO brands VALUES (1,'GermanySupport','germanysupport',1,'2026-01-01','2026-01-01')")
conn.commit()
conn.close()

from user_auth import (
    init_user_db, hash_password, verify_user_password_hash,
    create_user, delete_user, get_users_for_brand,
    authenticate_user, create_user_session_token,
    verify_user_session_token, validate_new_user_form, USER_COOKIE_NAME,
)
from admin_auth import ADMIN_COOKIE_NAME
import auth as auth_mod

init_user_db()


def test_cookie_names_all_distinct():
    print("=== Test: all three cookie names are distinct ===")
    names = {auth_mod.SESSION_COOKIE_NAME, ADMIN_COOKIE_NAME, USER_COOKIE_NAME}
    assert len(names) == 3, f"Expected 3 distinct names, got {names}"
    print(f"  brand={auth_mod.SESSION_COOKIE_NAME!r} admin={ADMIN_COOKIE_NAME!r} user={USER_COOKIE_NAME!r}  PASS")


def test_password_hash_roundtrip():
    print("=== Test: hash_password + verify roundtrip ===")
    h = hash_password("my-secret-password")
    assert verify_user_password_hash("my-secret-password", h) is True
    assert verify_user_password_hash("wrong-password", h) is False
    print("  PASS")


def test_password_hashes_are_unique():
    print("=== Test: two hashes of same password are different (random salt) ===")
    h1 = hash_password("same-password")
    h2 = hash_password("same-password")
    assert h1 != h2, "Same password should produce different hashes (salt)"
    assert verify_user_password_hash("same-password", h1)
    assert verify_user_password_hash("same-password", h2)
    print("  PASS")


def test_create_and_get_user():
    print("=== Test: create_user + get_users_for_brand ===")
    user_id = create_user(brand_id=1, email="test@example.com", password="password123")
    assert user_id > 0
    users = get_users_for_brand(brand_id=1)
    assert any(u["email"] == "test@example.com" for u in users)
    print(f"  user_id={user_id}  PASS")


def test_duplicate_email_raises():
    print("=== Test: duplicate email for same brand raises ValueError ===")
    try:
        create_user(brand_id=1, email="test@example.com", password="other123")
        assert False, "Expected ValueError"
    except ValueError as e:
        print(f"  raised: {e}  PASS")


def test_authenticate_correct_password():
    print("=== Test: authenticate_user succeeds with correct password ===")
    result = authenticate_user(brand_id=1, email="test@example.com", password="password123")
    assert result is not None
    assert result["email"] == "test@example.com"
    assert result["brand_id"] == 1
    print("  PASS")


def test_authenticate_wrong_password():
    print("=== Test: authenticate_user returns None with wrong password ===")
    result = authenticate_user(brand_id=1, email="test@example.com", password="wrong!")
    assert result is None
    print("  PASS")


def test_authenticate_wrong_brand():
    print("=== Test: authenticate_user returns None for wrong brand_id ===")
    result = authenticate_user(brand_id=99, email="test@example.com", password="password123")
    assert result is None
    print("  PASS")


def test_session_token_roundtrip():
    print("=== Test: session token created and verified ===")
    token = create_user_session_token(user_id=1, brand_id=1, email="test@example.com")
    payload = verify_user_session_token(token)
    assert payload is not None
    assert payload["user_id"] == 1
    assert payload["brand_id"] == 1
    assert payload["email"] == "test@example.com"
    print("  PASS")


def test_garbage_token_returns_none():
    print("=== Test: garbage token returns None (not raises) ===")
    assert verify_user_session_token("garbage") is None
    assert verify_user_session_token("") is None
    assert verify_user_session_token(None) is None
    print("  PASS")


def test_delete_user():
    print("=== Test: delete_user removes the user ===")
    uid = create_user(brand_id=1, email="todelete@example.com", password="pass1234")
    delete_user(user_id=uid, brand_id=1)
    users = get_users_for_brand(brand_id=1)
    assert not any(u["email"] == "todelete@example.com" for u in users)
    print("  PASS")


def test_delete_user_wrong_brand_does_nothing():
    print("=== Test: delete_user with wrong brand_id doesn't delete ===")
    uid = create_user(brand_id=1, email="safe@example.com", password="pass1234")
    delete_user(user_id=uid, brand_id=99)  # wrong brand
    users = get_users_for_brand(brand_id=1)
    assert any(u["email"] == "safe@example.com" for u in users), "Should NOT have been deleted"
    print("  PASS")


def test_validate_form_valid():
    print("=== Test: valid form passes ===")
    errors = validate_new_user_form("client@brand.de", "goodpassword", "goodpassword")
    assert errors == []
    print("  PASS")


def test_validate_form_bad_email():
    print("=== Test: invalid email rejected ===")
    errors = validate_new_user_form("not-an-email", "pass1234", "pass1234")
    assert any("valid" in e.lower() for e in errors)
    print(f"  {errors}  PASS")


def test_validate_form_short_password():
    print("=== Test: password under 8 chars rejected ===")
    errors = validate_new_user_form("a@b.com", "short", "short")
    assert any("8 characters" in e for e in errors)
    print(f"  {errors}  PASS")


def test_validate_form_password_mismatch():
    print("=== Test: mismatched passwords rejected ===")
    errors = validate_new_user_form("a@b.com", "password123", "different123")
    assert any("match" in e.lower() for e in errors)
    print(f"  {errors}  PASS")


if __name__ == "__main__":
    test_cookie_names_all_distinct()
    test_password_hash_roundtrip()
    test_password_hashes_are_unique()
    test_create_and_get_user()
    test_duplicate_email_raises()
    test_authenticate_correct_password()
    test_authenticate_wrong_password()
    test_authenticate_wrong_brand()
    test_session_token_roundtrip()
    test_garbage_token_returns_none()
    test_delete_user()
    test_delete_user_wrong_brand_does_nothing()
    test_validate_form_valid()
    test_validate_form_bad_email()
    test_validate_form_short_password()
    test_validate_form_password_mismatch()
    print("\nAll Phase 15 user auth tests passed.")
