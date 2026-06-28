# modules/dashboard/auth.py
"""
Single-admin session auth for the dashboard.

Deliberately minimal: one admin user, password hash from env,
signed session cookie. No user table, no OAuth — that's a later
phase if/when client self-login is needed.

Required env vars:
    DASHBOARD_ADMIN_PASSWORD_HASH   sha256 hex digest of the admin password
    DASHBOARD_SECRET_KEY            random secret used to sign session cookies

Generate a password hash:
    python3 -c "import hashlib; print(hashlib.sha256(b'your-password').hexdigest())"
"""
import hashlib
import hmac
import os
import time

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

SESSION_COOKIE_NAME = "cp_dashboard_session"
SESSION_MAX_AGE_SECONDS = 60 * 60 * 12  # 12 hours


def _get_secret_key() -> str:
    key = os.getenv("DASHBOARD_SECRET_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "DASHBOARD_SECRET_KEY is not set. Generate one with: "
            "python3 -c \"import secrets; print(secrets.token_hex(32))\""
        )
    return key


def _get_password_hash() -> str:
    hash_val = os.getenv("DASHBOARD_ADMIN_PASSWORD_HASH", "").strip()
    if not hash_val:
        raise RuntimeError("DASHBOARD_ADMIN_PASSWORD_HASH is not set.")
    return hash_val


def verify_password(password: str) -> bool:
    """Constant-time comparison against the configured password hash."""
    candidate = hashlib.sha256(password.encode("utf-8")).hexdigest()
    expected = _get_password_hash()
    return hmac.compare_digest(candidate, expected)


def create_session_token() -> str:
    serializer = URLSafeTimedSerializer(_get_secret_key())
    return serializer.dumps({"user": "admin", "issued_at": time.time()})


def verify_session_token(token: str) -> bool:
    """Returns True if token is valid and not expired. Never raises."""
    if not token:
        return False
    serializer = URLSafeTimedSerializer(_get_secret_key())
    try:
        serializer.loads(token, max_age=SESSION_MAX_AGE_SECONDS)
        return True
    except (BadSignature, SignatureExpired):
        return False
