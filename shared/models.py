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

    # Phase 11B — media asset metrics
    assets_generated: int = 0
    bundles_created: int = 0
    images_generated: int = 0
    images_uploaded: int = 0
    wordpress_media_failures: int = 0

    extra: dict = field(default_factory=dict)
    completed_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "module":                   self.module,
            "duration_sec":             round(self.duration_sec, 2),
            "posts_generated":          self.posts_generated,
            "published":                self.published,
            "duplicates_skipped":       self.duplicates_skipped,
            "failures":                 self.failures,
            "dry_run":                  self.dry_run,
            "assets_generated":         self.assets_generated,
            "bundles_created":          self.bundles_created,
            "images_generated":         self.images_generated,
            "images_uploaded":          self.images_uploaded,
            "wordpress_media_failures": self.wordpress_media_failures,
            "completed_at":             self.completed_at,
            **self.extra,
        }

    def log_summary(self, logger) -> None:
        """Emit the summary as a single structured log line."""
        fields = " ".join(f"{k}={v!r}" for k, v in self.to_dict().items())
        logger.info("execution_summary | %s", fields)
