#!/usr/bin/env python3
"""
Tests for Phase 13D-Ext: schedule_config.py

Critical properties to verify:
1. Cron expressions are correct for APScheduler (not Unix cron)
2. Multiple times produce multiple expressions (one per time)
3. active_days maps correctly (0=Mon -> 'mon', not Sunday)
4. sync_schedule_to_db disables old rows and creates new ones
5. Edge cases (empty times, empty days) fall back safely
"""
import os, sys, tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

_TMPDIR = tempfile.TemporaryDirectory(prefix="cp_sched_ext_")
os.environ["STORE_DB_PATH"] = os.path.join(_TMPDIR.name, "contentpilot.db")

# Bootstrap the DB with real scheduler schema before importing schedule_config
import sqlite3
db_path = os.environ["STORE_DB_PATH"]
conn = sqlite3.connect(db_path)
conn.execute("""
    CREATE TABLE IF NOT EXISTS schedules (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        module_name      TEXT    NOT NULL,
        enabled          INTEGER NOT NULL DEFAULT 1,
        interval_hours   INTEGER,
        cron_expression  TEXT,
        brand_id         INTEGER NOT NULL DEFAULT 1,
        created_at       TEXT    NOT NULL,
        updated_at       TEXT    NOT NULL
    )
""")
conn.commit()
conn.close()

sys.path.insert(0, os.path.join(ROOT, "shared", "scheduler"))
from schedule_config import (
    schedule_config_to_cron_expressions,
    sync_schedule_to_db,
    get_active_schedules_for_brand,
    disable_schedules_for_brand,
)


def test_daily_single_time_weekdays():
    print("=== Test: daily 09:00 Mon-Fri -> single cron expression ===")
    schedule = {
        "frequency": "daily",
        "times": ["09:00"],
        "active_days": [0, 1, 2, 3, 4],
        "max_posts_per_day": 1,
    }
    exprs = schedule_config_to_cron_expressions(schedule)
    assert len(exprs) == 1, f"Expected 1, got {len(exprs)}"
    assert exprs[0] == "0 9 * * mon,tue,wed,thu,fri", f"Got: {exprs[0]}"
    print(f"  {exprs}  PASS")


def test_twice_daily_produces_two_expressions():
    print("=== Test: twice_daily at 09:00 and 17:00 -> two cron expressions ===")
    schedule = {
        "frequency": "twice_daily",
        "times": ["09:00", "17:00"],
        "active_days": [0, 1, 2, 3, 4],
        "max_posts_per_day": 2,
    }
    exprs = schedule_config_to_cron_expressions(schedule)
    assert len(exprs) == 2, f"Expected 2, got {len(exprs)}"
    assert "0 9 * * mon,tue,wed,thu,fri" in exprs
    assert "0 17 * * mon,tue,wed,thu,fri" in exprs
    print(f"  {exprs}  PASS")


def test_weekly_monday_only():
    print("=== Test: weekly on Monday at 09:00 ===")
    schedule = {
        "frequency": "weekly",
        "times": ["09:00"],
        "active_days": [0],
        "max_posts_per_day": 1,
    }
    exprs = schedule_config_to_cron_expressions(schedule)
    assert exprs[0] == "0 9 * * mon", f"Got: {exprs[0]}"
    print(f"  {exprs}  PASS")


def test_day_mapping_is_monday_based_not_sunday():
    print("=== Test: CRITICAL — day 0 maps to 'mon' not 'sun' ===")
    schedule = {"times": ["09:00"], "active_days": [0]}
    exprs = schedule_config_to_cron_expressions(schedule)
    assert "mon" in exprs[0], f"Day 0 should be 'mon', got: {exprs[0]}"
    assert "sun" not in exprs[0], f"Day 0 must not be 'sun', got: {exprs[0]}"

    # Day 6 should be Sunday
    schedule6 = {"times": ["09:00"], "active_days": [6]}
    exprs6 = schedule_config_to_cron_expressions(schedule6)
    assert "sun" in exprs6[0], f"Day 6 should be 'sun', got: {exprs6[0]}"
    print(f"  day0={exprs[0]}  day6={exprs6[0]}  PASS")


def test_all_days_including_weekend():
    print("=== Test: all 7 days active ===")
    schedule = {"times": ["09:00"], "active_days": [0,1,2,3,4,5,6]}
    exprs = schedule_config_to_cron_expressions(schedule)
    assert "mon,tue,wed,thu,fri,sat,sun" in exprs[0], f"Got: {exprs[0]}"
    print(f"  {exprs}  PASS")


def test_empty_times_falls_back_safely():
    print("=== Test: empty times list falls back to safe default ===")
    schedule = {"times": [], "active_days": [0,1,2,3,4]}
    exprs = schedule_config_to_cron_expressions(schedule)
    assert len(exprs) == 1
    assert "9" in exprs[0]  # default 09:00
    print(f"  {exprs}  PASS")


def test_empty_active_days_falls_back_safely():
    print("=== Test: empty active_days falls back to safe default ===")
    schedule = {"times": ["09:00"], "active_days": []}
    exprs = schedule_config_to_cron_expressions(schedule)
    assert len(exprs) == 1
    assert "mon" in exprs[0]
    print(f"  {exprs}  PASS")


def test_sync_creates_schedule_rows():
    print("=== Test: sync_schedule_to_db creates rows in schedules table ===")
    schedule = {
        "frequency": "daily",
        "times": ["10:00"],
        "active_days": [0,1,2,3,4],
        "max_posts_per_day": 1,
    }
    ids = sync_schedule_to_db(brand_id=1, module_name="daily_news", schedule=schedule)
    assert len(ids) == 1
    assert ids[0] > 0

    rows = get_active_schedules_for_brand(brand_id=1, module_name="daily_news")
    assert len(rows) == 1
    assert rows[0]["cron_expression"] == "0 10 * * mon,tue,wed,thu,fri"
    assert rows[0]["enabled"] == 1
    print(f"  row_id={ids[0]} cron={rows[0]['cron_expression']}  PASS")


def test_sync_disables_old_rows_not_deletes():
    print("=== Test: re-syncing disables old rows, creates new ones ===")
    schedule_v2 = {
        "frequency": "twice_daily",
        "times": ["08:00", "18:00"],
        "active_days": [0,1,2,3,4],
        "max_posts_per_day": 2,
    }
    ids = sync_schedule_to_db(brand_id=1, module_name="daily_news", schedule=schedule_v2)
    assert len(ids) == 2

    # Old row should be disabled, not deleted
    conn = sqlite3.connect(os.environ["STORE_DB_PATH"])
    conn.row_factory = sqlite3.Row
    all_rows = conn.execute(
        "SELECT * FROM schedules WHERE brand_id=1 AND module_name='daily_news'"
    ).fetchall()
    conn.close()

    enabled = [r for r in all_rows if r["enabled"] == 1]
    disabled = [r for r in all_rows if r["enabled"] == 0]
    assert len(enabled) == 2, f"Expected 2 new enabled rows, got {len(enabled)}"
    assert len(disabled) >= 1, "Expected at least 1 old row disabled"
    print(f"  enabled={len(enabled)} disabled={len(disabled)}  PASS")


def test_disable_schedules_for_brand():
    print("=== Test: disable_schedules_for_brand disables without deleting ===")
    disable_schedules_for_brand(brand_id=1, module_name="daily_news")
    rows = get_active_schedules_for_brand(brand_id=1, module_name="daily_news")
    assert rows == [], f"Expected no active rows, got {rows}"

    # Rows still exist in DB
    conn = sqlite3.connect(os.environ["STORE_DB_PATH"])
    count = conn.execute(
        "SELECT COUNT(*) FROM schedules WHERE brand_id=1"
    ).fetchone()[0]
    conn.close()
    assert count > 0, "Rows should still exist after disable"
    print(f"  active=0, total={count} rows preserved  PASS")


if __name__ == "__main__":
    test_daily_single_time_weekdays()
    test_twice_daily_produces_two_expressions()
    test_weekly_monday_only()
    test_day_mapping_is_monday_based_not_sunday()
    test_all_days_including_weekend()
    test_empty_times_falls_back_safely()
    test_empty_active_days_falls_back_safely()
    test_sync_creates_schedule_rows()
    test_sync_disables_old_rows_not_deletes()
    test_disable_schedules_for_brand()
    print("\nAll Phase 13D-Ext schedule config tests passed.")
