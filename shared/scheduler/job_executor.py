"""
Job executor for ContentPilot scheduler.

Responsible for:
  - thread-level locking per module (prevents concurrent in-process runs)
  - invoking module main() via managed_run
  - writing job_runs rows on every execution outcome
  - returning a status string: 'completed', 'failed', or 'locked'
"""

import importlib
import logging
import threading
import time
import traceback
from typing import TYPE_CHECKING

from shared.scheduler.models import (
    Schedule,
    insert_job_run,
    update_job_run,
)

if TYPE_CHECKING:
    from shared.runtime import managed_run

logger = logging.getLogger(__name__)

# Maps module name → dotted import path for its main entry point.
# The test suite patches this dict to inject mock modules.
_MODULE_REGISTRY: dict[str, str] = {
    "daily_news": "modules.daily_news.main",
}

# Per-module thread locks (module_name → threading.Lock)
_module_locks: dict[str, threading.Lock] = {}
_module_locks_lock = threading.Lock()


def _get_module_lock(module_name: str) -> threading.Lock:
    """Return (or create) the per-module threading.Lock."""
    with _module_locks_lock:
        if module_name not in _module_locks:
            _module_locks[module_name] = threading.Lock()
        return _module_locks[module_name]


def execute_job(schedule: Schedule) -> str:
    """
    Execute a scheduled job.

    Steps:
      1. Acquire per-module thread lock (non-blocking → 'locked' if held).
      2. Insert job_runs row.
      3. Import and call module main() inside managed_run().
      4. Update job_runs row with outcome.
      5. Return 'completed', 'failed', or 'locked'.

    Args:
        schedule: The Schedule to execute.

    Returns:
        One of 'completed', 'failed', 'locked'.
    """
    lock = _get_module_lock(schedule.module_name)
    if not lock.acquire(blocking=False):
        logger.warning(
            "In-process lock held for %s — skipping", schedule.module_name
        )
        return "locked"

    try:
        run_id = insert_job_run(schedule.id, schedule.module_name)

        import_path = _MODULE_REGISTRY.get(schedule.module_name)
        if not import_path:
            logger.error(
                "No module entry in registry for %s — treating as failed",
                schedule.module_name,
            )
            update_job_run(run_id, "failed", 0.0, 0, "Module not in registry")
            return "failed"

        mod = importlib.import_module(import_path)
        start = time.monotonic()
        try:
            mod.main()
            duration = time.monotonic() - start
            update_job_run(run_id, "completed", duration)
            return "completed"

        except SystemExit as exc:
            duration = time.monotonic() - start
            code = int(exc.code) if exc.code is not None else 1
            if code == 0:
                # SystemExit(0) from the module's own managed_run means file lock was held
                update_job_run(run_id, "locked", duration)
                return "locked"
            else:
                update_job_run(
                    run_id, "failed", duration, error_traceback=traceback.format_exc()
                )
                return "failed"

        except Exception:
            duration = time.monotonic() - start
            update_job_run(
                run_id, "failed", duration, error_traceback=traceback.format_exc()
            )
            return "failed"

    finally:
        lock.release()