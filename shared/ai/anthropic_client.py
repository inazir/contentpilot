# shared/ai/anthropic_client.py
"""
Thin HTTP wrapper for the Anthropic Messages API.

Responsibilities:
- authenticate using ANTHROPIC_KEY env var
- send messages to /v1/messages
- retry on 429 (rate limit) and 529 (overload) with exponential backoff
- extract and return the response text
- raise AIClientError on permanent failure

NOT responsible for:
- what the prompt says
- what model is best for a task
- parsing structured output (JSON, XML, etc.)
- anything about the business domain
"""

import logging
import os
import time

import requests

from .exceptions import AIClientError

logger = logging.getLogger(__name__)

# Anthropic API endpoint — stable, versioned
_API_URL = "https://api.anthropic.com/v1/messages"
_API_VERSION = "2023-06-01"

# Retry configuration
_MAX_RETRIES = 4
_BASE_BACKOFF_SECONDS = 2.0   # wait = base * (2 ** attempt) + small jitter
_REQUEST_TIMEOUT = 60         # seconds before we give up on a single HTTP call

# HTTP status codes we retry on — both mean "try again later"
_RETRYABLE_STATUS_CODES = {429, 529}


def anthropic_complete(
    *,
    prompt: str | None = None,
    messages: list[dict] | None = None,
    model: str = "claude-haiku-4-5",
    max_tokens: int = 1024,
    temperature: float = 0.7,
    system: str | None = None,
) -> str:
    """
    Send a completion request to the Anthropic Messages API.

    Accepts either:
    - prompt="your text here"  (convenience shortcut, becomes a single user message)
    - messages=[{"role": "user", "content": "..."}]  (full control)

    If both are provided, messages takes precedence.

    Args:
        prompt:      Shortcut for a single user message.
        messages:    Full messages list for multi-turn or system+user combos.
        model:       Anthropic model string. Default: claude-haiku-4-5 (cheapest).
        max_tokens:  Maximum tokens in the response.
        temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative).
        system:      Optional system prompt. Only used when prompt= shortcut is used.
                     When passing messages=, include system message yourself.

    Returns:
        The generated text as a plain string, stripped of leading/trailing whitespace.

    Raises:
        AIClientError: On permanent failure after all retries exhausted.
        ValueError:    If neither prompt nor messages is provided.
    """
    if messages is None and prompt is None:
        raise ValueError("Provide either prompt= or messages=")

    # Build the messages list from the prompt shortcut if needed
    if messages is None:
        messages = [{"role": "user", "content": prompt}]

    api_key = os.getenv("ANTHROPIC_KEY", "").strip()
    if not api_key:
        raise AIClientError(
            "ANTHROPIC_KEY environment variable is not set",
            provider="anthropic",
        )

    headers = {
        "x-api-key": api_key,
        "anthropic-version": _API_VERSION,
        "content-type": "application/json",
    }

    payload: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": messages,
    }

    # System prompt is a top-level field, not a message role in Anthropic's API
    if system:
        payload["system"] = system

    last_exception: Exception | None = None

    for attempt in range(_MAX_RETRIES + 1):
        try:
            response = requests.post(
                _API_URL,
                headers=headers,
                json=payload,
                timeout=_REQUEST_TIMEOUT,
            )

            # Handle retryable server-side errors
            if response.status_code in _RETRYABLE_STATUS_CODES:
                wait = _BASE_BACKOFF_SECONDS * (2 ** attempt)
                logger.warning(
                    "Anthropic returned %s (attempt %d/%d), retrying in %.1fs",
                    response.status_code,
                    attempt + 1,
                    _MAX_RETRIES + 1,
                    wait,
                )
                time.sleep(wait)
                last_exception = AIClientError(
                    f"HTTP {response.status_code} after {attempt + 1} attempts",
                    provider="anthropic",
                    status_code=response.status_code,
                )
                continue

            # Non-retryable HTTP errors (400, 401, 403, etc.)
            if not response.ok:
                raise AIClientError(
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    provider="anthropic",
                    status_code=response.status_code,
                )

            # Parse the response
            data = response.json()
            content_blocks = data.get("content", [])
            if not content_blocks:
                raise AIClientError(
                    "Response contained no content blocks",
                    provider="anthropic",
                )

            text = content_blocks[0].get("text", "")
            if not text:
                raise AIClientError(
                    "Response content block had empty text",
                    provider="anthropic",
                )

            return text.strip()

        except requests.Timeout:
            wait = _BASE_BACKOFF_SECONDS * (2 ** attempt)
            logger.warning(
                "Anthropic request timed out (attempt %d/%d), retrying in %.1fs",
                attempt + 1,
                _MAX_RETRIES + 1,
                wait,
            )
            time.sleep(wait)
            last_exception = AIClientError(
                f"Request timed out after {_REQUEST_TIMEOUT}s",
                provider="anthropic",
            )
            continue

        except requests.RequestException as exc:
            # Network-level failures (DNS, connection refused, etc.) — retryable
            wait = _BASE_BACKOFF_SECONDS * (2 ** attempt)
            logger.warning(
                "Anthropic network error (attempt %d/%d): %s, retrying in %.1fs",
                attempt + 1,
                _MAX_RETRIES + 1,
                exc,
                wait,
            )
            time.sleep(wait)
            last_exception = exc
            continue

        except AIClientError:
            # Already normalized — re-raise immediately (non-retryable path)
            raise

    # All retries exhausted
    raise AIClientError(
        f"All {_MAX_RETRIES + 1} attempts failed",
        provider="anthropic",
    ) from last_exception