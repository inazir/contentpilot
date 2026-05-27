#!/usr/bin/env python3
# scripts/test_runtime_lock.py (updated to use temp workspace paths)
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, "/app")

# Use an isolated temporary directory for DB and lock files so tests don't
# require /app or Docker mounts. The TemporaryDirectory is kept alive for
# the duration of the script via the _TMPDIR variable.
_TMPDIR = tempfile.TemporaryDirectory(prefix="cp_rt_")
os.environ["STORE_DB_PATH"] = os.path.join(_TMPDIR.name, "contentpilot.db")
os.environ["RUNTIME_DB_PATH"] = os.environ["STORE_DB_PATH"]

from shared.logging import configure_logging, get_logger
import shared.runtime as runtime

configure_logging()
logger = get_logger("test_lock")


def test_lock_acquire_and_release() -> None:
    print("\n=== Test: Basic lock acquire/release ===")
    runtime.init_runtime_db()
    # point runtime locks into our tempdir
    runtime._LOCK_DIR = os.path.join(_TMPDIR.name, "locks")

    module = "test_module_lock"

    runtime._lock_path(module).unlink(missing_ok=True)

    assert runtime._acquire_lock(module), "Should acquire lock on clean state"
    assert not runtime._acquire_lock(module), "Should fail — lock already held"

    runtime._release_lock(module)
    assert runtime._acquire_lock(module), "Should acquire again after release"
    runtime._release_lock(module)

    print("  PASS")


def test_stale_lock_cleanup() -> None:
    print("\n=== Test: Stale lock is cleaned up ===")
    import time

    runtime.init_runtime_db()
    runtime._LOCK_DIR = os.path.join(_TMPDIR.name, "locks")
    module = "test_stale_lock"
    lock_file = runtime._lock_path(module)

    lock_file.write_text("99999")
    old_time = time.time() - 7200
    os.utime(lock_file, (old_time, old_time))

    assert runtime._acquire_lock(module), "Stale lock should be removed and new lock acquired"
    runtime._release_lock(module)

    print("  PASS")


def test_lock_contention_simulation() -> None:
    print("\n=== Test: Concurrent lock contention ===")

    runtime._LOCK_DIR = os.path.join(_TMPDIR.name, "locks")
    module = "test_contention"
    runtime._lock_path(module).unlink(missing_ok=True)

    assert runtime._acquire_lock(module), "First acquire should succeed"

    result = not runtime._acquire_lock(module)
    assert result, "Second acquire should fail while first holds lock"

    runtime._release_lock(module)
    print("  PASS")


if __name__ == "__main__":
    test_lock_acquire_and_release()
    test_stale_lock_cleanup()
    test_lock_contention_simulation()
    print("\nAll lock tests passed.")
