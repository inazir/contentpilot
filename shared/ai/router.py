# shared/ai/router.py
"""
Routes a completion request through primary + fallback providers.

Modules call ai_complete() instead of calling providers directly.
Provider/model selection comes entirely from AIConfig (i.e. from .env).
"""

import logging

from .anthropic_client import anthropic_complete
from .deepseek_client import deepseek_complete
from .config import AIConfig
from .exceptions import AIClientError

logger = logging.getLogger(__name__)

_PROVIDERS = {
    "anthropic": anthropic_complete,
    "deepseek":  deepseek_complete,
}


def ai_complete(
    cfg: AIConfig,
    *,
    prompt: str | None = None,
    messages: list[dict] | None = None,
    system: str | None = None,
) -> str:
    """
    Call the primary provider. If it fails, try the fallback provider.
    If both fail, raise AIClientError.

    Args:
        cfg:      AIConfig from get_ai_config("module_name")
        prompt:   Shortcut for single user message.
        messages: Full messages list (takes precedence over prompt).
        system:   Optional system prompt.

    Raises:
        AIClientError: When all available providers fail.
        ValueError:    When cfg.provider is not a known provider name.
    """
    primary_fn = _PROVIDERS.get(cfg.provider)
    if primary_fn is None:
        raise ValueError(
            f"Unknown AI provider '{cfg.provider}'. "
            f"Valid options: {list(_PROVIDERS.keys())}"
        )

    # Try primary
    try:
        return primary_fn(
            prompt=prompt,
            messages=messages,
            system=system,
            model=cfg.model,
            max_tokens=cfg.max_tokens,
            temperature=cfg.temperature,
        )
    except AIClientError as primary_exc:
        if not cfg.fallback_provider:
            raise

        logger.warning(
            "Primary provider '%s' failed (%s), trying fallback '%s'",
            cfg.provider, primary_exc, cfg.fallback_provider,
        )

    # Try fallback
    fallback_fn = _PROVIDERS.get(cfg.fallback_provider)
    if fallback_fn is None:
        raise ValueError(
            f"Unknown fallback provider '{cfg.fallback_provider}'"
        )

    return fallback_fn(
        prompt=prompt,
        messages=messages,
        system=system,
        model=cfg.fallback_model or cfg.model,
        max_tokens=cfg.max_tokens,
        temperature=cfg.temperature,
    )