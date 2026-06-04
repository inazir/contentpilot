# shared/scheduler/job_executor.py
"""
In-process job executor for the ContentPilot scheduler.

Phase 13B additions:
  - Resolves BrandContext from schedule.brand_id before execution
  - Passes BrandContext into module's run() function
  - Records brand_id in job_runs
  - Every log line includes brand_id and brand_slug

Dual-layer locking is preserved from Phase 13A:
  Layer 1: threading.Lock per module (in-process)
  Layer 2: file-based lock via managed_run() (cross-process / cross-container)

Exit code semantics:
  SystemExit(0) → 'locked'   (managed_run file-lock conflict)
  SystemExit(1+) → 'failed'
  Exception → 'failed' with full traceback
"""

from __future__ import annotations

import importlib
import logging
import sys
import threading
import time
import traceback
from typing import Optional

from .models import (
    Schedule,
    insert_job_run,
    update_job_run,
)
from .retry_manager import RetryManager

logger = logging.getLogger(__name__)

# In-process thread locks — one per module name
_module_locks: dict[str, threading.Lock] = {}
_module_locks_mutex = threading.Lock()


def _get_module_lock(module_name: str) -> threading.Lock:
    with _module_locks_mutex:
        if module_name not in _module_locks:
            _module_locks[module_name] = threading.Lock()
        return _module_locks[module_name]


_MODULE_REGISTRY: dict[str, str] = {
    "daily_news": "modules.daily_news.main",
}


def _resolve_main(module_name: str):
    dotted = _MODULE_REGISTRY.get(module_name)
    if not dotted:
        raise ImportError(
            f"No entry point registered for module '{module_name}'. "
            f"Known: {list(_MODULE_REGISTRY.keys())}"
        )
    mod = importlib.import_module(dotted)
    if not hasattr(mod, "main"):
        raise ImportError(f"Module {dotted!r} has no main() function")
    return mod.main


def _resolve_brand_context(schedule: Schedule):
    """
    Build BrandContext for schedule.brand_id.
    Returns None if brand resolution fails (logs a warning, doesn't crash).
    """
    try:
        from shared.brands.service import get_brand_context
        return get_brand_context(schedule.brand_id)
    except Exception as exc:
        logger.warning(
            "brand_context_resolution_failed | brand_id=%d | error=%s — falling back to no brand context",
            schedule.brand_id, exc,
        )
        return None


def execute_job(schedule: Schedule, retry_count: int = 0) -> str:
    """
    Execute a scheduled job in-process with BrandContext injection.

    Returns: 'completed' | 'failed' | 'locked'
    Never raises.
    """
    module_name = schedule.module_name
    thread_lock = _get_module_lock(module_name)

    # Layer 1: in-process thread lock
    acquired = thread_lock.acquire(blocking=False)
    if not acquired:
        logger.warning(
            "job_thread_locked | module=%s | schedule_id=%s | brand_id=%d",
            module_name, schedule.id, schedule.brand_id,
        )
        return "locked"

    # Resolve brand before inserting job_run
    brand_context = _resolve_brand_context(schedule)
    brand_id = brand_context.brand_id if brand_context else schedule.brand_id
    brand_slug = brand_context.brand_slug if brand_context else "unknown"

    run_id = insert_job_run(schedule.id, module_name, brand_id=brand_id)
    start_time = time.monotonic()
    status = "failed"
    tb_str: Optional[str] = None

    try:
        logger.info(
            "job_execution_start | module=%s | schedule_id=%s | run_id=%d | brand_id=%d | brand_slug=%s | retry=%d",
            module_name, schedule.id, run_id, brand_id, brand_slug, retry_count,
        )

        main_fn = _resolve_main(module_name)

        orig_argv = sys.argv[:]
        sys.argv = ["scheduler"]

        try:
            # Phase 13B: call main(brand_context=...) if supported
            # Falls back to main() for modules not yet updated
            import inspect
            sig = inspect.signature(main_fn)
            if "brand_context" in sig.parameters:
                main_fn(brand_context=brand_context)
            else:
                main_fn()
            status = "completed"

        except SystemExit as exc:
            code = int(exc.code) if exc.code is not None else 1
            if code == 0:
                status = "locked"
                logger.info(
                    "job_lock_conflict | module=%s | run_id=%d | brand_id=%d | brand_slug=%s",
                    module_name, run_id, brand_id, brand_slug,
                )
            else:
                status = "failed"
                tb_str = f"SystemExit({code})"
                logger.error(
                    "job_exit_nonzero | module=%s | run_id=%d | brand_id=%d | brand_slug=%s | exit=%d",
                    module_name, run_id, brand_id, brand_slug, code,
                )
        finally:
            sys.argv = orig_argv

    except ImportError as exc:
        status = "failed"
        tb_str = traceback.format_exc()
        logger.error(
            "job_import_error | module=%s | brand_id=%d | brand_slug=%s | error=%s",
            module_name, brand_id, brand_slug, exc,
        )

    except Exception as exc:
        status = "failed"
        tb_str = traceback.format_exc()
        logger.error(
            "job_unexpected_error | module=%s | brand_id=%d | brand_slug=%s | error=%s",
            module_name, brand_id, brand_slug, exc,
        )

    finally:
        duration = time.monotonic() - start_time
        update_job_run(
            run_id          = run_id,
            status          = status,
            duration_seconds = duration,
            retry_count     = retry_count,
            error_traceback = tb_str,
        )
        thread_lock.release()

        log_fn = logger.info if status == "completed" else logger.warning
        log_fn(
            "job_execution_%s | module=%s | run_id=%d | brand_id=%d | brand_slug=%s | duration=%.2fs",
            status, module_name, run_id, brand_id, brand_slug, duration,
        )

    return status


def execute_with_retry(schedule: Schedule, retry_manager: RetryManager) -> None:
    """Execute a job and schedule automatic retries on failure."""
    from .models import count_retries_for_schedule
    current_retries = count_retries_for_schedule(schedule.id)

    status = execute_job(schedule, retry_count=current_retries)

    if status in {"completed", "locked"}:
        return

    next_retry_count = current_retries + 1
    if retry_manager.is_exhausted(next_retry_count):
        retry_manager.log_retry_plan(schedule.module_name, next_retry_count)
        logger.error(
            "job_permanently_failed | module=%s | schedule_id=%s | brand_id=%d | total_retries=%d",
            schedule.module_name, schedule.id, schedule.brand_id, next_retry_count,
        )
        return

    retry_at = retry_manager.next_retry_at(next_retry_count)
    retry_manager.log_retry_plan(schedule.module_name, next_retry_count)

    try:
        from .scheduler_service import get_scheduler
        apscheduler = get_scheduler()
        if apscheduler and apscheduler.running:
            apscheduler.add_job(
                func            = execute_with_retry,
                trigger         = "date",
                run_date        = retry_at,
                args            = [schedule, retry_manager],
                id              = f"retry_{schedule.module_name}_{schedule.id}_{next_retry_count}",
                replace_existing = True,
            )
            logger.info(
                "retry_job_queued | module=%s | brand_id=%d | retry_count=%d | run_date=%s",
                schedule.module_name, schedule.brand_id, next_retry_count, retry_at.isoformat(),
            )
    except Exception as exc:
        logger.error(
            "retry_queue_failed | module=%s | brand_id=%d | error=%s",
            schedule.module_name, schedule.brand_id, exc,
        )
