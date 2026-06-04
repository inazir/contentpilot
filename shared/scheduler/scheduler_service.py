# shared/scheduler/scheduler_service.py
"""
ContentPilot Scheduler Daemon — Phase 13B update.

Changes from Phase 13A:
  - Calls init_brand_db() on boot (runs migrations for brand_id columns)
  - Calls seed_default_brand() to ensure GermanySupport exists
  - Passes brand_id-aware Schedule objects to execute_with_retry
  - Heartbeat remains unchanged

All Phase 13A functionality (retry, heartbeat, scheduling model) is preserved.
"""

from __future__ import annotations

import logging
import os
import signal
import sys
import time
from typing import Optional

sys.path.insert(0, "/app")

from shared.logging import configure_logging

configure_logging(module_name="scheduler")

from shared.scheduler.models import (
    Schedule,
    init_scheduler_db,
    load_enabled_schedules,
    seed_default_schedule,
)
from shared.scheduler.job_executor import execute_with_retry
from shared.scheduler.heartbeat import HeartbeatService
from shared.scheduler.retry_manager import RetryManager

logger = logging.getLogger(__name__)

_scheduler: Optional[object] = None


def get_scheduler():
    return _scheduler


def _is_enabled() -> bool:
    return os.getenv("SCHEDULER_ENABLED", "true").strip().lower() in {"1", "true", "yes"}


def _register_schedule(scheduler, schedule: Schedule, retry_manager: RetryManager) -> None:
    job_id = f"module_{schedule.module_name}_{schedule.id}_brand_{schedule.brand_id}"

    if schedule.trigger_type == "interval":
        scheduler.add_job(
            func             = execute_with_retry,
            trigger          = "interval",
            hours            = schedule.interval_hours,
            args             = [schedule, retry_manager],
            id               = job_id,
            replace_existing = True,
            coalesce         = True,
            max_instances    = 1,
        )
        logger.info(
            "schedule_registered | module=%s | brand_id=%d | trigger=interval | hours=%d | job_id=%s",
            schedule.module_name, schedule.brand_id, schedule.interval_hours, job_id,
        )

    elif schedule.trigger_type == "cron":
        parts = schedule.cron_expression.split()
        if len(parts) != 5:
            logger.error(
                "schedule_invalid_cron | module=%s | brand_id=%d | expr=%r",
                schedule.module_name, schedule.brand_id, schedule.cron_expression,
            )
            return

        minute, hour, day, month, day_of_week = parts
        scheduler.add_job(
            func             = execute_with_retry,
            trigger          = "cron",
            minute           = minute,
            hour             = hour,
            day              = day,
            month            = month,
            day_of_week      = day_of_week,
            args             = [schedule, retry_manager],
            id               = job_id,
            replace_existing = True,
            coalesce         = True,
            max_instances    = 1,
        )
        logger.info(
            "schedule_registered | module=%s | brand_id=%d | trigger=cron | expr=%r | job_id=%s",
            schedule.module_name, schedule.brand_id, schedule.cron_expression, job_id,
        )


def run() -> None:
    global _scheduler

    if not _is_enabled():
        logger.info("SCHEDULER_ENABLED=false — exiting immediately")
        return

    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.executors.pool import ThreadPoolExecutor
    except ImportError:
        logger.critical("APScheduler not installed. Run: pip install apscheduler>=3.10.0")
        sys.exit(1)

    # ------------------------------------------------------------------
    # Phase 13B: initialize brand tables + seed default brand first
    # ------------------------------------------------------------------
    try:
        from shared.brands.models import init_brand_db, seed_default_brand
        init_brand_db()
        seed_default_brand()
    except Exception as exc:
        logger.warning("Brand DB initialization failed (non-fatal): %s", exc)

    init_scheduler_db()
    seed_default_schedule()

    schedules = load_enabled_schedules()
    logger.info("scheduler_boot | schedules_loaded=%d", len(schedules))

    if not schedules:
        logger.warning("No enabled schedules found — check DAILY_NEWS_SCHEDULE_HOURS")

    executors = {"default": ThreadPoolExecutor(max_workers=4)}
    job_defaults = {
        "coalesce": True,
        "max_instances": 1,
        "misfire_grace_time": 60,
    }

    scheduler = BackgroundScheduler(
        executors    = executors,
        job_defaults = job_defaults,
        timezone     = "UTC",
    )
    _scheduler = scheduler

    retry_manager = RetryManager()
    start_time = time.monotonic()

    for schedule in schedules:
        _register_schedule(scheduler, schedule, retry_manager)

    heartbeat = HeartbeatService(scheduler, start_time)
    scheduler.add_job(
        func             = heartbeat.emit,
        trigger          = "interval",
        seconds          = HeartbeatService.interval_seconds(),
        id               = "heartbeat",
        replace_existing = True,
    )

    scheduler.start()
    logger.info(
        "scheduler_running | jobs=%d | heartbeat_interval=%ds",
        len(scheduler.get_jobs()), HeartbeatService.interval_seconds(),
    )

    def _shutdown(signum, frame):
        logger.info("scheduler_shutdown | signal=%d", signum)
        scheduler.shutdown(wait=True)
        sys.exit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("scheduler_stopping")
        scheduler.shutdown(wait=True)


if __name__ == "__main__":
    run()
