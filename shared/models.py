# shared/models.py
"""
Shared data models used across ContentPilot modules.

ExecutionSummary is the standard return shape from any module run.
It feeds into structured logs, runtime metadata, and future dashboards.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ExecutionSummary:
    """
    Produced at the end of every module execution.

    Modules populate this and pass it back to managed_run() so the
    runtime layer can log and persist it consistently.
    """
    module: str
    duration_sec: float = 0.0
    posts_generated: int = 0
    published: int = 0
    duplicates_skipped: int = 0
    failures: int = 0
    dry_run: bool = False
    extra: dict = field(default_factory=dict)
    completed_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "module": self.module,
            "duration_sec": round(self.duration_sec, 2),
            "posts_generated": self.posts_generated,
            "published": self.published,
            "duplicates_skipped": self.duplicates_skipped,
            "failures": self.failures,
            "dry_run": self.dry_run,
            "completed_at": self.completed_at,
            **self.extra,
        }

    def log_summary(self, logger) -> None:
        """Emit the summary as a single structured log line."""
        fields = " ".join(f"{k}={v!r}" for k, v in self.to_dict().items())
        logger.info("execution_summary | %s", fields)
