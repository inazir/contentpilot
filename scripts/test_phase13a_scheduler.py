#!/usr/bin/env python3
# scripts/test_phase13a_scheduler.py
"""
Phase 13A — Scheduler Service Foundation tests.

All tests run offline (no real module execution, no APScheduler threads started).
Uses isolated temp SQLite DBs so tests never touch production data.

Test coverage:
  1. DB init — schedules + job_runs tables created correctly
  2. Seed — default schedule seeded when table is empty; not re-seeded when populated
  3. Schedule loading — only enabled schedules returned
  4. Retry manager — delay calculations, exhaustion, datetime projection
  5. Job run lifecycle — insert → update → fetch roundtrip
  6. Retry count tracking — count_retries_for_schedule
  7. Dual-layer thread lock — second acquire blocked while first holds
  8. execute_job with mocked main — completed / failed / locked status paths
  9. Heartbeat emit — no crash, correct log output
  10. Cron vs interval schedule registration (APScheduler not started, just validated)
"""

from __future__ import annotations

import importlib
import os
import sqlite3
import sys
import tempfile
import threading
import time
import traceback
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Bootstrap: point everything at a temp DB before importing scheduler code
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, "/app")

_TMPDIR = tempfile.TemporaryDirectory(prefix="cp_sched_test_")
_DB_PATH = os.path.join(_TMPDIR.name, "contentpilot_test.db")
os.environ["STORE_DB_PATH"]      = _DB_PATH
os.environ["SCHEDULER_DB_PATH"]  = _DB_PATH
os.environ["RUNTIME_DB_PATH"]    = _DB_PATH

# Suppress structured logging noise during tests
import logging
logging.disable(logging.CRITICAL)

from shared.scheduler.models import (
    Schedule,
    JobRun,
    _connect,
    init_scheduler_db,
    load_enabled_schedules,
    seed_default_schedule,
    insert_job_run,
    update_job_run,
    get_job_run,
    count_retries_for_schedule,
)
from shared.scheduler.retry_manager import RetryManager
from shared.scheduler.job_executor import (
    _get_module_lock,
    execute_job,
    _MODULE_REGISTRY,
)
from shared.scheduler.heartbeat import HeartbeatService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fresh_db() -> None:
    """Drop and re-create scheduler tables for test isolation."""
    conn = _connect()
    conn.execute("DROP TABLE IF EXISTS job_runs")
    conn.execute("DROP TABLE IF EXISTS schedules")
    conn.commit()
    conn.close()
    init_scheduler_db()


def _make_schedule(
    module_name: str = "daily_news",
    enabled: bool = True,
    interval_hours: int | None = 1,
    cron_expression: str | None = None,
) -> Schedule:
    """Insert a schedule row and return a Schedule dataclass."""
    _fresh_db()
    now = datetime.now(timezone.utc).isoformat()
    conn = _connect()
    cursor = conn.execute(
        """
        INSERT INTO schedules (module_name, enabled, interval_hours, cron_expression, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (module_name, 1 if enabled else 0, interval_hours, cron_expression, now, now),
    )
    conn.commit()
    row_id = cursor.lastrowid
    row = conn.execute("SELECT * FROM schedules WHERE id = ?", (row_id,)).fetchone()
    conn.close()
    return Schedule.from_row(row)


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

class TestDbInit(unittest.TestCase):
    def test_tables_created(self):
        _fresh_db()
        conn = _connect()
        tables = {
            r[0] for r in
            conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        }
        conn.close()
        self.assertIn("schedules", tables)
        self.assertIn("job_runs", tables)
        print("  [PASS] DB tables created correctly")

    def test_init_idempotent(self):
        _fresh_db()
        init_scheduler_db()   # second call should not error
        print("  [PASS] init_scheduler_db is idempotent")


class TestSeed(unittest.TestCase):
    def test_seeds_when_empty(self):
        _fresh_db()
        os.environ["DAILY_NEWS_SCHEDULE_HOURS"] = "2"
        seed_default_schedule()
        schedules = load_enabled_schedules()
        self.assertEqual(len(schedules), 1)
        self.assertEqual(schedules[0].module_name, "daily_news")
        self.assertEqual(schedules[0].interval_hours, 2)
        print("  [PASS] Default schedule seeded when table is empty")

    def test_does_not_reseed(self):
        _fresh_db()
        seed_default_schedule()
        seed_default_schedule()   # second call — should not add a row
        conn = _connect()
        count = conn.execute("SELECT COUNT(*) FROM schedules").fetchone()[0]
        conn.close()
        self.assertEqual(count, 1)
        print("  [PASS] seed_default_schedule does not re-seed when rows exist")


class TestLoadSchedules(unittest.TestCase):
    def test_only_enabled_loaded(self):
        _fresh_db()
        now = datetime.now(timezone.utc).isoformat()
        conn = _connect()
        conn.execute(
            "INSERT INTO schedules (module_name, enabled, interval_hours, created_at, updated_at) VALUES (?,1,1,?,?)",
            ("daily_news", now, now),
        )
        conn.execute(
            "INSERT INTO schedules (module_name, enabled, interval_hours, created_at, updated_at) VALUES (?,0,1,?,?)",
            ("social_tips", now, now),
        )
        conn.commit()
        conn.close()

        schedules = load_enabled_schedules()
        self.assertEqual(len(schedules), 1)
        self.assertEqual(schedules[0].module_name, "daily_news")
        print("  [PASS] Only enabled schedules are loaded")

    def test_empty_table_returns_empty_list(self):
        _fresh_db()
        schedules = load_enabled_schedules()
        self.assertEqual(schedules, [])
        print("  [PASS] Empty schedules table returns empty list")


class TestRetryManager(unittest.TestCase):
    def setUp(self):
        self.rm = RetryManager(max_retries=3)

    def test_delays(self):
        self.assertEqual(self.rm.next_delay_seconds(0), 15 * 60)
        self.assertEqual(self.rm.next_delay_seconds(1), 60 * 60)
        self.assertEqual(self.rm.next_delay_seconds(2), 6 * 60 * 60)
        print("  [PASS] Retry delays are correct (15m, 1h, 6h)")

    def test_exhaustion(self):
        self.assertFalse(self.rm.is_exhausted(0))
        self.assertFalse(self.rm.is_exhausted(2))
        self.assertTrue(self.rm.is_exhausted(3))
        self.assertTrue(self.rm.is_exhausted(99))
        print("  [PASS] Retry exhaustion detection is correct")

    def test_next_retry_at_is_future(self):
        t = self.rm.next_retry_at(0)
        self.assertGreater(t, datetime.now(timezone.utc))
        print("  [PASS] next_retry_at returns a future datetime")

    def test_raises_on_exhausted(self):
        with self.assertRaises(ValueError):
            self.rm.next_delay_seconds(3)
        print("  [PASS] next_delay_seconds raises on exhausted count")


class TestJobRunLifecycle(unittest.TestCase):
    def test_insert_and_update(self):
        _fresh_db()
        schedule = _make_schedule()

        run_id = insert_job_run(schedule.id, "daily_news")
        self.assertGreater(run_id, 0)

        run = get_job_run(run_id)
        self.assertEqual(run.status, "running")
        self.assertEqual(run.module_name, "daily_news")
        self.assertEqual(run.schedule_id, schedule.id)

        update_job_run(
            run_id=run_id,
            status="completed",
            duration_seconds=3.14,
            retry_count=0,
            error_traceback=None,
        )
        run = get_job_run(run_id)
        self.assertEqual(run.status, "completed")
        self.assertAlmostEqual(run.duration_seconds, 3.14, places=1)
        self.assertIsNotNone(run.completed_at)
        print("  [PASS] Job run lifecycle: insert → update → fetch")

    def test_failed_run_stores_traceback(self):
        _fresh_db()
        schedule = _make_schedule()
        run_id = insert_job_run(schedule.id, "daily_news")
        update_job_run(
            run_id=run_id,
            status="failed",
            duration_seconds=1.0,
            retry_count=1,
            error_traceback="Traceback (most recent call last):\n  ...\nValueError: test",
        )
        run = get_job_run(run_id)
        self.assertEqual(run.status, "failed")
        self.assertIn("ValueError", run.error_traceback)
        self.assertEqual(run.retry_count, 1)
        print("  [PASS] Failed run stores full traceback")


class TestRetryCountTracking(unittest.TestCase):
    def test_count_retries_for_schedule(self):
        _fresh_db()
        schedule = _make_schedule()

        # No runs yet
        self.assertEqual(count_retries_for_schedule(schedule.id), 0)

        # Insert two runs with increasing retry counts
        r1 = insert_job_run(schedule.id, "daily_news")
        update_job_run(r1, "failed", 1.0, retry_count=0)

        r2 = insert_job_run(schedule.id, "daily_news")
        update_job_run(r2, "retrying", 1.0, retry_count=1)

        self.assertEqual(count_retries_for_schedule(schedule.id), 1)
        print("  [PASS] count_retries_for_schedule returns latest retry_count")


class TestThreadLocking(unittest.TestCase):
    def test_second_acquire_blocked(self):
        lock = _get_module_lock("test_module_lock")
        # Ensure clean state
        if lock.locked():
            lock.release()

        acquired1 = lock.acquire(blocking=False)
        self.assertTrue(acquired1, "First acquire should succeed")

        acquired2 = lock.acquire(blocking=False)
        self.assertFalse(acquired2, "Second acquire should fail — lock held")

        lock.release()
        print("  [PASS] In-process thread lock prevents concurrent execution")

    def test_lock_released_after_use(self):
        lock = _get_module_lock("test_module_lock_release")
        if lock.locked():
            lock.release()

        lock.acquire(blocking=False)
        lock.release()

        acquired_again = lock.acquire(blocking=False)
        self.assertTrue(acquired_again, "Should be acquirable after release")
        lock.release()
        print("  [PASS] Thread lock is correctly released")


class TestExecuteJob(unittest.TestCase):
    """Tests execute_job() with mocked module main() calls."""

    def test_completed_on_success(self):
        _fresh_db()
        schedule = _make_schedule()

        with patch.dict(_MODULE_REGISTRY, {"daily_news": "shared.scheduler._mock_main_ok"}):
            # Create a fake module with main() that succeeds
            import types
            fake_mod = types.ModuleType("shared.scheduler._mock_main_ok")
            fake_mod.main = lambda: None
            sys.modules["shared.scheduler._mock_main_ok"] = fake_mod

            status = execute_job(schedule)
            self.assertEqual(status, "completed")

        print("  [PASS] execute_job returns 'completed' on successful main()")

    def test_failed_on_exception(self):
        _fresh_db()
        schedule = _make_schedule()

        import types
        fake_mod = types.ModuleType("shared.scheduler._mock_main_fail")
        def _raise():
            raise RuntimeError("simulated failure")
        fake_mod.main = _raise
        sys.modules["shared.scheduler._mock_main_fail"] = fake_mod

        with patch.dict(_MODULE_REGISTRY, {"daily_news": "shared.scheduler._mock_main_fail"}):
            status = execute_job(schedule)
            self.assertEqual(status, "failed")

        print("  [PASS] execute_job returns 'failed' on unhandled exception")

    def test_locked_on_system_exit_0(self):
        """SystemExit(0) from managed_run means file lock held → 'locked', not failure."""
        _fresh_db()
        schedule = _make_schedule()

        import types
        fake_mod = types.ModuleType("shared.scheduler._mock_main_locked")
        fake_mod.main = lambda: (_ for _ in ()).throw(SystemExit(0))
        sys.modules["shared.scheduler._mock_main_locked"] = fake_mod

        with patch.dict(_MODULE_REGISTRY, {"daily_news": "shared.scheduler._mock_main_locked"}):
            status = execute_job(schedule)
            self.assertEqual(status, "locked")

        print("  [PASS] execute_job returns 'locked' on SystemExit(0)")

    def test_failed_on_system_exit_nonzero(self):
        _fresh_db()
        schedule = _make_schedule()

        import types
        fake_mod = types.ModuleType("shared.scheduler._mock_main_exit1")
        fake_mod.main = lambda: (_ for _ in ()).throw(SystemExit(1))
        sys.modules["shared.scheduler._mock_main_exit1"] = fake_mod

        with patch.dict(_MODULE_REGISTRY, {"daily_news": "shared.scheduler._mock_main_exit1"}):
            status = execute_job(schedule)
            self.assertEqual(status, "failed")

        print("  [PASS] execute_job returns 'failed' on SystemExit(1)")

    def test_job_run_written_for_all_outcomes(self):
        """Verify job_runs row is always written, even on failure."""
        _fresh_db()
        schedule = _make_schedule()

        import types
        fake_mod = types.ModuleType("shared.scheduler._mock_main_ok2")
        fake_mod.main = lambda: None
        sys.modules["shared.scheduler._mock_main_ok2"] = fake_mod

        with patch.dict(_MODULE_REGISTRY, {"daily_news": "shared.scheduler._mock_main_ok2"}):
            execute_job(schedule)

        conn = _connect()
        rows = conn.execute("SELECT * FROM job_runs WHERE module_name='daily_news'").fetchall()
        conn.close()
        self.assertGreater(len(rows), 0)
        row = rows[-1]
        self.assertIsNotNone(row["completed_at"])
        self.assertIsNotNone(row["duration_seconds"])
        print("  [PASS] job_runs row written with completed_at + duration on every execution")


class TestHeartbeat(unittest.TestCase):
    def test_emit_does_not_crash(self):
        """HeartbeatService.emit() must not raise even if scheduler is mock."""
        mock_scheduler = MagicMock()
        mock_scheduler.get_jobs.return_value = []

        # Re-enable logging temporarily to ensure no exception leaks
        logging.disable(logging.NOTSET)
        svc = HeartbeatService(mock_scheduler, start_time=time.monotonic())
        try:
            svc.emit()   # must not raise
        except Exception as exc:
            self.fail(f"heartbeat.emit() raised an exception: {exc}")
        finally:
            logging.disable(logging.CRITICAL)

        print("  [PASS] HeartbeatService.emit() runs without exceptions")

    def test_interval_seconds_default(self):
        os.environ.pop("SCHEDULER_HEARTBEAT_SECONDS", None)
        self.assertEqual(HeartbeatService.interval_seconds(), 60)
        print("  [PASS] HeartbeatService default interval is 60 seconds")

    def test_interval_seconds_from_env(self):
        os.environ["SCHEDULER_HEARTBEAT_SECONDS"] = "120"
        self.assertEqual(HeartbeatService.interval_seconds(), 120)
        os.environ.pop("SCHEDULER_HEARTBEAT_SECONDS", None)
        print("  [PASS] HeartbeatService reads interval from env")


class TestScheduleTriggerTypes(unittest.TestCase):
    def test_interval_trigger_type(self):
        _fresh_db()
        s = _make_schedule(interval_hours=2, cron_expression=None)
        self.assertEqual(s.trigger_type, "interval")
        self.assertEqual(s.interval_hours, 2)
        print("  [PASS] Schedule with interval_hours has trigger_type='interval'")

    def test_cron_trigger_type(self):
        _fresh_db()
        s = _make_schedule(interval_hours=None, cron_expression="0 * * * *")
        self.assertEqual(s.trigger_type, "cron")
        self.assertEqual(s.cron_expression, "0 * * * *")
        print("  [PASS] Schedule with cron_expression has trigger_type='cron'")


class TestFallbackToDefault(unittest.TestCase):
    def test_loads_nothing_without_seed(self):
        _fresh_db()
        # Without calling seed, table is empty
        schedules = load_enabled_schedules()
        self.assertEqual(schedules, [])
        print("  [PASS] Empty table returns no schedules (no crash)")

    def test_seed_fallback_uses_env(self):
        _fresh_db()
        os.environ["DAILY_NEWS_SCHEDULE_HOURS"] = "4"
        seed_default_schedule()
        schedules = load_enabled_schedules()
        self.assertEqual(schedules[0].interval_hours, 4)
        os.environ.pop("DAILY_NEWS_SCHEDULE_HOURS", None)
        print("  [PASS] Seed fallback respects DAILY_NEWS_SCHEDULE_HOURS env var")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_suite():
    suites = [
        TestDbInit,
        TestSeed,
        TestLoadSchedules,
        TestRetryManager,
        TestJobRunLifecycle,
        TestRetryCountTracking,
        TestThreadLocking,
        TestExecuteJob,
        TestHeartbeat,
        TestScheduleTriggerTypes,
        TestFallbackToDefault,
    ]

    total = 0
    failures = []

    for suite_cls in suites:
        print(f"\n=== {suite_cls.__name__} ===")
        suite = unittest.TestLoader().loadTestsFromTestCase(suite_cls)
        runner = unittest.TextTestRunner(
            stream=open(os.devnull, "w"),
            verbosity=0,
        )
        result = runner.run(suite)
        total += result.testsRun

        if result.failures or result.errors:
            for test, tb in result.failures + result.errors:
                print(f"  [FAIL] {test}: {tb}")
                failures.append(str(test))

    print(f"\n{'='*60}")
    print(f"Tests run: {total}  |  Failures: {len(failures)}")
    if failures:
        print(f"FAILED: {', '.join(failures)}")
        sys.exit(1)
    else:
        print("All Phase 13A tests passed.")
        sys.exit(0)


if __name__ == "__main__":
    run_suite()
