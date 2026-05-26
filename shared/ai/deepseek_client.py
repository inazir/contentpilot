# shared/ai/deepseek_client.py
import logging
import os
import time

import requests

from .exceptions import AIClientError

logger = logging.getLogger(__name__)

_API_URL = "https://api.deepseek.com/v1/chat/completions"
_MAX_RETRIES = 4
_BASE_BACKOFF_SECONDS = 2.0
_REQUEST_TIMEOUT = 60
_RETRYABLE_STATUS_CODES = {429, 529, 503}


def deepseek_complete(
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

    if system:
        messages = [{"role": "system", "content": system}, *messages]

    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise AIClientError("DEEPSEEK_API_KEY is not set", provider="deepseek")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": messages,
    }

    last_exception: Exception | None = None

    for attempt in range(_MAX_RETRIES + 1):
        try:
            response = requests.post(
                _API_URL, headers=headers, json=payload, timeout=_REQUEST_TIMEOUT
            )

            if response.status_code in _RETRYABLE_STATUS_CODES:
                wait = _BASE_BACKOFF_SECONDS * (2 ** attempt)
                logger.warning(
                    "DeepSeek %s (attempt %d/%d), retrying in %.1fs",
                    response.status_code, attempt + 1, _MAX_RETRIES + 1, wait,
                )
                time.sleep(wait)
                last_exception = AIClientError(
                    f"HTTP {response.status_code}", provider="deepseek",
                    status_code=response.status_code,
                )
                continue

            if not response.ok:
                raise AIClientError(
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    provider="deepseek", status_code=response.status_code,
                )

            data = response.json()
            try:
                text = data["choices"][0]["message"]["content"]
            except (KeyError, IndexError) as exc:
                raise AIClientError(
                    f"Unexpected response structure: {str(data)[:200]}",
                    provider="deepseek",
                ) from exc

            if not text:
                raise AIClientError("Empty response content", provider="deepseek")

            return text.strip()

        except requests.Timeout:
            wait = _BASE_BACKOFF_SECONDS * (2 ** attempt)
            logger.warning("DeepSeek timeout (attempt %d/%d), retrying in %.1fs",
                           attempt + 1, _MAX_RETRIES + 1, wait)
            time.sleep(wait)
            last_exception = AIClientError("Request timed out", provider="deepseek")
            continue

        except requests.RequestException as exc:
            wait = _BASE_BACKOFF_SECONDS * (2 ** attempt)
            logger.warning("DeepSeek network error (attempt %d/%d): %s",
                           attempt + 1, _MAX_RETRIES + 1, exc)
            time.sleep(wait)
            last_exception = exc
            continue

        except AIClientError:
            raise

    raise AIClientError(
        f"All {_MAX_RETRIES + 1} attempts failed", provider="deepseek"
    ) from last_exception