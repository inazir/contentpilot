# modules/dashboard/admin_auth.py
"""
Phase 14A: Admin authentication — deliberately separate from brand auth.

Uses a different cookie name and a different env var so:
  - Being logged into a brand dashboard does NOT grant admin access
  - Admin credentials can be rotated without affecting brand logins
  - A future per-brand client login (Phase 15) won't conflict

Required env vars:
    ADMIN_PANEL_PASSWORD_HASH   sha256 hex digest of the admin password
    DASHBOARD_SECRET_KEY            same secret used for brand sessions
                                    (reused — one secret, two cookie names)

Generate a new admin password hash:
    python3 -c "import hashlib; print(hashlib.sha256(b'your-password').hexdigest())"
"""
import hashlib
import hmac
import os
import time

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

ADMIN_COOKIE_NAME = "cp_admin_session"
ADMIN_SESSION_MAX_AGE = 60 * 60 * 8  # 8 hours (shorter than brand session)


def _get_secret_key() -> str:
    key = os.getenv("DASHBOARD_SECRET_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "DASHBOARD_SECRET_KEY is not set. Generate one with: "
            "python3 -c \"import secrets; print(secrets.token_hex(32))\""
        )
    return key


def _get_admin_password_hash() -> str:
    h = os.getenv("ADMIN_PANEL_PASSWORD_HASH", "").strip()
    if not h:
        raise RuntimeError(
            "ADMIN_PANEL_PASSWORD_HASH is not set. "
            "Generate with: python3 -c \"import hashlib; "
            "print(hashlib.sha256(b'your-password').hexdigest())\""
        )
    return h


def verify_admin_password(password: str) -> bool:
    """Constant-time comparison against the configured admin password hash."""
    try:
        expected = _get_admin_password_hash()
    except RuntimeError:
        return False
    candidate = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(candidate, expected)


def create_admin_session_token() -> str:
    serializer = URLSafeTimedSerializer(_get_secret_key())
    return serializer.dumps({"role": "admin", "issued_at": time.time()})


def verify_admin_session_token(token: str) -> bool:
    """Returns True if token is valid and not expired. Never raises."""
    if not token:
        return False
    serializer = URLSafeTimedSerializer(_get_secret_key())
    try:
        serializer.loads(token, max_age=ADMIN_SESSION_MAX_AGE)
        return True
    except (BadSignature, SignatureExpired):
        return False
