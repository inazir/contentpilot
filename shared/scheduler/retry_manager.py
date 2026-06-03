"""
Retry manager for ContentPilot scheduler.

Implements exponential backoff:
  - Retry 0 → 15 minutes
  - Retry 1 →  1 hour
  - Retry 2 →  6 hours
  - Retry 3+ → exhausted (raises ValueError)
"""

from datetime import datetime, timedelta, timezone


_BACKOFF_MINUTES = [15, 60, 360]   # 15 min, 1 h, 6 h


class RetryManager:
    """Encapsulates retry delay and exhaustion logic."""

    def __init__(self, max_retries: int = 3) -> None:
        self._max = max_retries

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def next_delay_seconds(self, retry_count: int) -> float:
        """Return the delay in seconds before the next retry attempt."""
        if self.is_exhausted(retry_count):
            raise ValueError(
                f"Retry count {retry_count} exceeds max {self._max}"
            )
        return _BACKOFF_MINUTES[retry_count] * 60.0

    def is_exhausted(self, retry_count: int) -> bool:
        """Return True if retry_count has reached the max."""
        return retry_count >= self._max

    def next_retry_at(self, retry_count: int) -> datetime:
        """Return the UTC datetime when the next retry should fire."""
        seconds = self.next_delay_seconds(retry_count)
        return datetime.now(timezone.utc) + timedelta(seconds=seconds)