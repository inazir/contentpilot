#!/usr/bin/env python3
"""
ContentPilot system health check.

Exit codes:
  0 — all checks passed
  1 — one or more checks failed
"""

import os
import shutil
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, "/app")

from shared.config import get_db_path

PASS = "\033[92m PASS\033[0m"
FAIL = "\033[91m FAIL\033[0m"
WARN = "\033[93m WARN\033[0m"
SKIP = "\033[94m SKIP\033[0m"

failures = []
warnings = []


def check(name: str, fn) -> None:
    try:
        result = fn()
        if result is True:
            print(f"  [{PASS}] {name}")
        elif result is False:
            print(f"  [{FAIL}] {name}")
            failures.append(name)
        elif isinstance(result, str) and result.startswith("WARN"):
            print(f"  [{WARN}] {name}: {result[5:]}")
            warnings.append(name)
        elif isinstance(result, str) and result.startswith("SKIP"):
            print(f"  [{SKIP}] {name}: {result[5:]}")
        else:
            print(f"  [{PASS}] {name}: {result}")
    except Exception as exc:
        print(f"  [{FAIL}] {name}: {exc}")
        failures.append(name)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_db_writable() -> bool:
    db_path = Path(get_db_path())
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE IF NOT EXISTS _healthcheck (id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()
    return True


def check_locks_dir() -> bool:
    p = Path("/app/data/locks")
    p.mkdir(parents=True, exist_ok=True)
    test = p / ".write_test"
    test.write_text("ok")
    test.unlink()
    return True


def check_logs_dir() -> bool:
    p = Path(os.getenv("LOG_DIR", "/app/data/logs"))
    p.mkdir(parents=True, exist_ok=True)
    test = p / ".write_test"
    test.write_text("ok")
    test.unlink()
    return True


def check_disk_space() -> str:
    total, used, free = shutil.disk_usage("/app/data")
    free_gb = free / (1024 ** 3)
    pct_used = (used / total) * 100
    if pct_used > 90:
        return f"WARN disk {pct_used:.0f}% used ({free_gb:.1f}GB free)"
    return f"{pct_used:.0f}% used, {free_gb:.1f}GB free"


def check_required_env_vars() -> bool:
    required = [
        "ANTHROPIC_KEY",
        "STORE_DB_PATH",
        "PUBLISH_MODE",
    ]
    missing = [v for v in required if not os.getenv(v, "").strip()]
    if missing:
        raise ValueError(f"Missing: {', '.join(missing)}")
    return True


def check_facebook_config() -> str:
    mode = os.getenv("PUBLISH_MODE", "disabled")
    if mode != "real":
        return f"SKIP not in real mode (PUBLISH_MODE={mode})"

    fb_enabled = os.getenv("FACEBOOK_ENABLED", "false").lower()
    if fb_enabled != "true":
        return "SKIP FACEBOOK_ENABLED=false"

    page_id = os.getenv("FACEBOOK_PAGE_ID", "").strip()
    token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "").strip()
    if not page_id or not token:
        raise ValueError("FACEBOOK_PAGE_ID or FACEBOOK_PAGE_ACCESS_TOKEN not set")
    return True


def check_ai_provider_reachable() -> str:
    import urllib.error
    import urllib.request

    key = os.getenv("ANTHROPIC_KEY", "").strip()
    if not key:
        return "SKIP ANTHROPIC_KEY not set"

    try:
        req = urllib.request.Request(
            "https://api.anthropic.com",
            headers={"User-Agent": "ContentPilot-healthcheck"},
            method="HEAD",
        )
        with urllib.request.urlopen(req, timeout=5):
            pass
        return True
    except urllib.error.HTTPError:
        return True
    except Exception as exc:
        raise ConnectionError(f"Cannot reach api.anthropic.com: {exc}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("\nContentPilot Health Check")
    print("=" * 40)

    check("Database writable", check_db_writable)
    check("Locks directory writable", check_locks_dir)
    check("Logs directory writable", check_logs_dir)
    check("Disk space", check_disk_space)
    check("Required env vars", check_required_env_vars)
    check("Facebook config", check_facebook_config)
    check("AI provider reachable", check_ai_provider_reachable)

    print("=" * 40)
    if failures:
        print(f"\n  {len(failures)} check(s) failed: {', '.join(failures)}")
        sys.exit(1)
    elif warnings:
        print(f"\n  All checks passed ({len(warnings)} warning(s))")
        sys.exit(0)
    else:
        print("\n  All checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
