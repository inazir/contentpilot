#!/usr/bin/env python3
# scripts/test_runtime_failure.py (updated to use temp workspace paths)
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, "/app")

_TMPDIR = tempfile.TemporaryDirectory(prefix="cp_rt_fail_")
os.environ["STORE_DB_PATH"] = os.path.join(_TMPDIR.name, "contentpilot.db")
os.environ["RUNTIME_DB_PATH"] = os.environ["STORE_DB_PATH"]

from shared.logging import configure_logging, get_logger
import shared.runtime as runtime

configure_logging()
logger = get_logger("test_failure")


def test_exception_releases_lock() -> None:
    print("\n=== Test: Exception inside managed_run releases lock ===")
    runtime.init_runtime_db()
    runtime._LOCK_DIR = os.path.join(_TMPDIR.name, "locks")
    module = "test_fail_mod"
    runtime._lock_path(module).unlink(missing_ok=True)

    try:
        with runtime.managed_run(module) as ctx:
            raise RuntimeError("Simulated failure")
    except SystemExit:
        pass

    assert runtime._acquire_lock(module), "Lock should be released after failure"
    runtime._release_lock(module)
    print("  Lock released after exception  PASS")


def test_failed_run_written_to_db() -> None:
    print("\n=== Test: Failed run written to DB ===")
    runtime.init_runtime_db()
    runtime._LOCK_DIR = os.path.join(_TMPDIR.name, "locks")
    module = "test_fail_db"
    runtime._lock_path(module).unlink(missing_ok=True)

    try:
        with runtime.managed_run(module) as ctx:
            raise ValueError("DB write failure test")
    except SystemExit:
        pass

    conn = runtime._connect()
    row = conn.execute(
        "SELECT * FROM runtime_executions WHERE module_name = ? ORDER BY id DESC LIMIT 1",
        (module,)
    ).fetchone()
    conn.close()

    assert row is not None, "Run should be recorded"
    assert row["success"] == 0, "Should be marked as failed"
    assert row["error_message"] is not None
    print(f"  error={row['error_message']}  PASS")


def test_lock_held_exits_cleanly() -> None:
    print("\n=== Test: Already-running job exits with code 0 (not an error) ===")
    runtime.init_runtime_db()
    runtime._LOCK_DIR = os.path.join(_TMPDIR.name, "locks")
    module = "test_held_lock"
    runtime._lock_path(module).unlink(missing_ok=True)

    runtime._acquire_lock(module)

    exit_code = None
    try:
        with runtime.managed_run(module) as ctx:
            pass
    except SystemExit as exc:
        exit_code = exc.code

    runtime._release_lock(module)

    assert exit_code == 0, f"Should exit 0 when lock is held, got {exit_code}"
    print("  Exited cleanly with code 0  PASS")


if __name__ == "__main__":
    test_exception_releases_lock()
    test_failed_run_written_to_db()
    test_lock_held_exits_cleanly()
    print("\nAll failure tests passed.")
