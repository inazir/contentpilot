# shared/social/models.py
"""
Data models for social publishing.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class PublishResult:
    platform: str
    success: bool
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    external_post_id: str | None = None
    error_message: str | None = None
    retryable: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        if self.success:
            return f"[{self.platform}] OK post_id={self.external_post_id}"
        flag = "retryable" if self.retryable else "permanent"
        return f"[{self.platform}] FAILED ({flag}): {self.error_message}"


@dataclass
class PublishSummary:
    results: list[PublishResult] = field(default_factory=list)
    module_name: str = ""

    @property
    def succeeded(self) -> list[PublishResult]:
        return [r for r in self.results if r.success]

    @property
    def failed(self) -> list[PublishResult]:
        return [r for r in self.results if not r.success]

    @property
    def all_succeeded(self) -> bool:
        return bool(self.results) and all(r.success for r in self.results)

    @property
    def any_succeeded(self) -> bool:
        return any(r.success for r in self.results)

    def __str__(self) -> str:
        total = len(self.results)
        ok = len(self.succeeded)
        fail = len(self.failed)
        return f"PublishSummary: {ok}/{total} succeeded, {fail} failed"
