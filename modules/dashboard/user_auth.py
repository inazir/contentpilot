# modules/dashboard/user_auth.py
"""
Phase 15: Per-brand client user authentication.

Manages the `users` table — one row per (email, brand_id) pair.
Admin creates users via the admin panel; clients log in with email+password.

Deliberately separate from:
  - auth.py         (single-password brand admin, kept for backward compat)
  - admin_auth.py   (admin panel, ADMIN_PANEL_PASSWORD_HASH env var)

Cookie name: cp_user_session
Session payload: {"user_id": int, "brand_id": int, "email": str}

DB table created by init_user_db() — called on dashboard startup.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
import os
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

logger = logging.getLogger(__name__)

USER_COOKIE_NAME = "cp_user_session"
USER_SESSION_MAX_AGE = 60 * 60 * 24  # 24 hours

_DEFAULT_DB_PATH = "/app/data/db/contentpilot.db"


def _get_db_path() -> str:
    return os.getenv("STORE_DB_PATH", _DEFAULT_DB_PATH)


def _connect() -> sqlite3.Connection:
    db_path = _get_db_path()
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=10.0, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    return conn


def init_user_db() -> None:
    conn = _connect()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_id      INTEGER NOT NULL,
            email         TEXT    NOT NULL,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    NOT NULL,
            last_login    TEXT,
            UNIQUE(brand_id, email),
            FOREIGN KEY(brand_id) REFERENCES brands(id)
        )
    """)
    conn.commit()
    conn.close()
    logger.debug("User DB initialized | path=%s", _get_db_path())


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"),
        salt.encode("utf-8"), iterations=260_000,
    ).hex()
    return f"{salt}:{hashed}"


def verify_user_password_hash(password: str, stored_hash: str) -> bool:
    try:
        salt, expected = stored_hash.split(":", 1)
        candidate = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"),
            salt.encode("utf-8"), iterations=260_000,
        ).hex()
        return hmac.compare_digest(candidate, expected)
    except Exception:
        return False


def create_user(brand_id: int, email: str, password: str) -> int:
    now = datetime.now(timezone.utc).isoformat()
    conn = _connect()
    try:
        cursor = conn.execute(
            "INSERT INTO users (brand_id, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (brand_id, email.strip().lower(), hash_password(password), now),
        )
        conn.commit()
        user_id = cursor.lastrowid
        logger.info("user_created | brand_id=%d | email=%s | user_id=%d", brand_id, email, user_id)
        return user_id
    except sqlite3.IntegrityError:
        raise ValueError(f"A user with email '{email}' already exists for this brand.")
    finally:
        conn.close()


def delete_user(user_id: int, brand_id: int) -> None:
    conn = _connect()
    conn.execute("DELETE FROM users WHERE id = ? AND brand_id = ?", (user_id, brand_id))
    conn.commit()
    conn.close()
    logger.info("user_deleted | user_id=%d | brand_id=%d", user_id, brand_id)


def get_users_for_brand(brand_id: int) -> list[dict]:
    conn = _connect()
    rows = conn.execute(
        "SELECT id, email, created_at, last_login FROM users WHERE brand_id = ? ORDER BY created_at",
        (brand_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def authenticate_user(brand_id: int, email: str, password: str) -> Optional[dict]:
    conn = _connect()
    row = conn.execute(
        "SELECT * FROM users WHERE brand_id = ? AND email = ?",
        (brand_id, email.strip().lower()),
    ).fetchone()
    if not row:
        conn.close()
        return None
    if not verify_user_password_hash(password, row["password_hash"]):
        conn.close()
        return None
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("UPDATE users SET last_login = ? WHERE id = ?", (now, row["id"]))
    conn.commit()
    conn.close()
    logger.info("user_login_success | brand_id=%d | email=%s | user_id=%d", brand_id, email, row["id"])
    return {"id": row["id"], "brand_id": row["brand_id"], "email": row["email"]}


def _get_secret_key() -> str:
    key = os.getenv("DASHBOARD_SECRET_KEY", "").strip()
    if not key:
        raise RuntimeError("DASHBOARD_SECRET_KEY is not set.")
    return key


def create_user_session_token(user_id: int, brand_id: int, email: str) -> str:
    serializer = URLSafeTimedSerializer(_get_secret_key())
    return serializer.dumps({"user_id": user_id, "brand_id": brand_id, "email": email})


def verify_user_session_token(token: str) -> Optional[dict]:
    if not token:
        return None
    serializer = URLSafeTimedSerializer(_get_secret_key())
    try:
        return serializer.loads(token, max_age=USER_SESSION_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None


def validate_new_user_form(email: str, password: str, confirm: str) -> list[str]:
    import re
    errors = []
    email = email.strip()
    if not email:
        errors.append("Email is required.")
    elif not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        errors.append("Email address is not valid.")
    if not password:
        errors.append("Password is required.")
    elif len(password) < 8:
        errors.append("Password must be at least 8 characters.")
    if password and confirm and password != confirm:
        errors.append("Passwords do not match.")
    return errors
