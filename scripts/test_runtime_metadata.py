#!/usr/bin/env python3
# scripts/test_runtime_metadata.py (updated to use temp workspace paths)
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, "/app")

_TMPDIR = tempfile.TemporaryDirectory(prefix="cp_rt_meta_")
os.environ["STORE_DB_PATH"] = os.path.join(_TMPDIR.name, "contentpilot.db")
os.environ["RUNTIME_DB_PATH"] = os.environ["STORE_DB_PATH"]

from shared.logging import configure_logging, get_logger
import shared.runtime as runtime

configure_logging()
logger = get_logger("test_metadata")


def test_run_record() -> None:
    print("\n=== Test: Run metadata recorded correctly ===")
    runtime.init_runtime_db()

    row_id = runtime.record_run_start("test_module", "run_abc123")
    assert row_id > 0, "Expected valid row id"

    runtime.record_run_end(
        row_id=row_id,
        success=True,
        exit_code=0,
        duration=1.23,
        publish_count=2,
    )

    conn = runtime._connect()
    row = conn.execute(
        "SELECT * FROM runtime_executions WHERE id = ?", (row_id,)
    ).fetchone()
    conn.close()

    assert row["module_name"] == "test_module"
    assert row["success"] == 1
    assert row["exit_code"] == 0
    assert row["publish_count"] == 2
    assert abs(row["duration_seconds"] - 1.23) < 0.01
    assert row["completed_at"] is not None
    print(f"  run_id={row['run_id']} duration={row['duration_seconds']}s  PASS")


def test_failed_run_record() -> None:
    print("\n=== Test: Failed run recorded correctly ===")
    runtime.init_runtime_db()

    row_id = runtime.record_run_start("test_fail_module", "run_fail_xyz")
    runtime.record_run_end(
        row_id=row_id,
        success=False,
        exit_code=1,
        duration=0.5,
        error_message="Something went wrong",
    )

    conn = runtime._connect()
    row = conn.execute(
        "SELECT * FROM runtime_executions WHERE id = ?", (row_id,)
    ).fetchone()
    conn.close()

    assert row["success"] == 0
    assert row["exit_code"] == 1
    assert row["error_message"] == "Something went wrong"
    print(f"  error_message={row['error_message']}  PASS")


if __name__ == "__main__":
    test_run_record()
    test_failed_run_record()
    print("\nAll metadata tests passed.")
