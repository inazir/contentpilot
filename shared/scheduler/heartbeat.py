# shared/scheduler/heartbeat.py
"""
Periodic heartbeat logging for the ContentPilot scheduler daemon.

Emits a structured log line every SCHEDULER_HEARTBEAT_SECONDS (default: 60)
containing live scheduler status:
  scheduler_heartbeat | active_jobs=X | pending_retries=Y | uptime_seconds=Z
"""

from __future__ import annotations

import logging
import os
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)


class HeartbeatService:
    def __init__(self, scheduler: "BackgroundScheduler", start_time: float) -> None:
        self._scheduler = scheduler
        self._start_time = start_time

    def emit(self) -> None:
        """Emit a single heartbeat log line."""
        try:
            all_jobs = self._scheduler.get_jobs()

            # Count retry jobs (named with retry_ prefix) as pending retries
            active_jobs = sum(
                1 for j in all_jobs
                if not (j.id or "").startswith("retry_")
                and not (j.id or "").startswith("heartbeat")
            )
            pending_retries = sum(
                1 for j in all_jobs
                if (j.id or "").startswith("retry_")
            )

            uptime = time.monotonic() - self._start_time

            logger.info(
                "scheduler_heartbeat | active_jobs=%d | pending_retries=%d | uptime_seconds=%.0f",
                active_jobs, pending_retries, uptime,
            )
        except Exception as exc:
            logger.warning("heartbeat_error | error=%s", exc)

    @staticmethod
    def interval_seconds() -> int:
        return int(os.getenv("SCHEDULER_HEARTBEAT_SECONDS", "60"))
