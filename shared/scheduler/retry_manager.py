# shared/scheduler/retry_manager.py
"""
Retry backoff calculator for failed scheduler jobs.

Retry schedule (fixed linear backoff):
  Attempt 1: +15 minutes
  Attempt 2: +1 hour
  Attempt 3: +6 hours
  Attempt 4+: Permanently failed — no more retries

Usage:
    from shared.scheduler.retry_manager import RetryManager
    rm = RetryManager(max_retries=3)
    delay = rm.next_delay_seconds(retry_count=1)  # → 900
    rm.is_exhausted(retry_count=4)                # → True
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

# Fixed retry delays in seconds
_RETRY_DELAYS: list[int] = [
    15 * 60,      # Retry 1: 15 minutes
    60 * 60,      # Retry 2: 1 hour
    6 * 60 * 60,  # Retry 3: 6 hours
]


class RetryManager:
    def __init__(self, max_retries: int | None = None) -> None:
        self.max_retries: int = max_retries or int(
            os.getenv("SCHEDULER_MAX_RETRIES", "3")
        )

    def is_exhausted(self, retry_count: int) -> bool:
        """Return True when no more retries should be attempted."""
        return retry_count >= self.max_retries

    def next_delay_seconds(self, retry_count: int) -> int:
        """
        Return the delay in seconds before the next retry attempt.
        retry_count is 0-based (0 = first failure, not yet retried).
        """
        if self.is_exhausted(retry_count):
            raise ValueError(
                f"Retry count {retry_count} exceeds max_retries {self.max_retries}"
            )
        idx = min(retry_count, len(_RETRY_DELAYS) - 1)
        return _RETRY_DELAYS[idx]

    def next_retry_at(self, retry_count: int) -> datetime:
        """Return the UTC datetime for the next retry attempt."""
        delay = self.next_delay_seconds(retry_count)
        return datetime.now(timezone.utc) + timedelta(seconds=delay)

    def log_retry_plan(self, module_name: str, retry_count: int) -> None:
        if self.is_exhausted(retry_count):
            logger.error(
                "retry_exhausted | module=%s | retry_count=%d | max_retries=%d",
                module_name, retry_count, self.max_retries,
            )
        else:
            delay = self.next_delay_seconds(retry_count)
            next_at = self.next_retry_at(retry_count)
            logger.warning(
                "retry_scheduled | module=%s | attempt=%d | delay_seconds=%d | next_at=%s",
                module_name, retry_count + 1, delay, next_at.isoformat(),
            )
