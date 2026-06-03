"""
Heartbeat service for ContentPilot scheduler.

Emits periodic log lines so monitoring tools can detect
whether the scheduler process is alive and processing jobs.
"""

import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)


class HeartbeatService:
    """Periodic heartbeat emitter tied to an APScheduler instance."""

    def __init__(
        self,
        scheduler: Any,
        start_time: float | None = None,
    ) -> None:
        """
        Args:
            scheduler: APScheduler scheduler instance (used to query job info).
            start_time: monotonic timestamp from scheduler start (optional).
        """
        self._scheduler = scheduler
        self._start_time = start_time or time.monotonic()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @staticmethod
    def interval_seconds() -> int:
        """Return the heartbeat interval from env, defaulting to 60."""
        return int(os.getenv("SCHEDULER_HEARTBEAT_SECONDS", "60"))

    def emit(self) -> None:
        """Emit a structured heartbeat log line.

        Must not raise even if scheduler is a mock / not fully initialised.
        """
        try:
            jobs = self._scheduler.get_jobs()  # type: ignore[union-attr]
            job_count = len(jobs)
        except Exception:
            job_count = -1

        uptime = time.monotonic() - self._start_time
        logger.info(
            "heartbeat | uptime=%.0fs | registered_jobs=%d",
            uptime,
            job_count,
        )