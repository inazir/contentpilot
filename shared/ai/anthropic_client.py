# shared/ai/anthropic_client.py
import logging
import os
import time

import requests

from .exceptions import AIClientError

logger = logging.getLogger(__name__)

_API_URL = "https://api.anthropic.com/v1/messages"
_API_VERSION = "2023-06-01"
_MAX_RETRIES = 4
_BASE_BACKOFF_SECONDS = 2.0
_REQUEST_TIMEOUT = 60
_RETRYABLE_STATUS_CODES = {429, 529}


def anthropic_complete(
    *,
    prompt: str | None = None,
    messages: list[dict] | None = None,
    model: str,                  # ← no default; caller must pass explicitly
    max_tokens: int = 1024,
    temperature: float = 0.7,
    system: str | None = None,
) -> str:
    if messages is None and prompt is None:
        raise ValueError("Provide either prompt= or messages=")

    if messages is None:
        messages = [{"role": "user", "content": prompt}]

    api_key = os.getenv("ANTHROPIC_KEY", "").strip()
    if not api_key:
        raise AIClientError("ANTHROPIC_KEY is not set", provider="anthropic")

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
    if system:
        payload["system"] = system

    last_exception: Exception | None = None

    for attempt in range(_MAX_RETRIES + 1):
        try:
            response = requests.post(
                _API_URL, headers=headers, json=payload, timeout=_REQUEST_TIMEOUT
            )

            if response.status_code in _RETRYABLE_STATUS_CODES:
                wait = _BASE_BACKOFF_SECONDS * (2 ** attempt)
                logger.warning(
                    "Anthropic %s (attempt %d/%d), retrying in %.1fs",
                    response.status_code, attempt + 1, _MAX_RETRIES + 1, wait,
                )
                time.sleep(wait)
                last_exception = AIClientError(
                    f"HTTP {response.status_code}", provider="anthropic",
                    status_code=response.status_code,
                )
                continue

            if not response.ok:
                raise AIClientError(
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    provider="anthropic", status_code=response.status_code,
                )

            data = response.json()
            content_blocks = data.get("content", [])
            if not content_blocks:
                raise AIClientError("No content blocks in response", provider="anthropic")

            text = content_blocks[0].get("text", "")
            if not text:
                raise AIClientError("Empty text in response", provider="anthropic")

            return text.strip()

        except requests.Timeout:
            wait = _BASE_BACKOFF_SECONDS * (2 ** attempt)
            logger.warning("Anthropic timeout (attempt %d/%d), retrying in %.1fs",
                           attempt + 1, _MAX_RETRIES + 1, wait)
            time.sleep(wait)
            last_exception = AIClientError("Request timed out", provider="anthropic")
            continue

        except requests.RequestException as exc:
            wait = _BASE_BACKOFF_SECONDS * (2 ** attempt)
            logger.warning("Anthropic network error (attempt %d/%d): %s",
                           attempt + 1, _MAX_RETRIES + 1, exc)
            time.sleep(wait)
            last_exception = exc
            continue

        except AIClientError:
            raise

    raise AIClientError(
        f"All {_MAX_RETRIES + 1} attempts failed", provider="anthropic"
    ) from last_exception