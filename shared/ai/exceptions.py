# shared/ai/exceptions.py
"""
Normalized exception for all AI provider failures.

Modules catch AIClientError without knowing which provider was used.
The original exception is always attached as __cause__ for debugging.
"""


class AIClientError(Exception):
    """
    Raised when an AI provider call fails permanently.

    Permanent means:
    - exhausted all retries on transient errors (429, 529, timeout)
    - received a non-retryable error (400 bad request, 401 auth failure)
    - response was structurally unexpected (missing content field)

    Always check str(exc) for a human-readable summary.
    Always check exc.__cause__ for the original low-level exception.
    """

    def __init__(self, message: str, provider: str, status_code: int | None = None):
        self.provider = provider
        self.status_code = status_code
        super().__init__(f"[{provider}] {message}")