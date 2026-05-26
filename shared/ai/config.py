# shared/ai/config.py
"""
Reads AI provider/model configuration from environment variables.

Global defaults:
    AI_DEFAULT_PROVIDER   (default: anthropic)
    AI_DEFAULT_MODEL      (default: per-provider fallback)

Module-specific overrides (replace MODULE with module name in uppercase):
    {MODULE}_AI_PROVIDER
    {MODULE}_AI_MODEL
    {MODULE}_AI_FALLBACK_PROVIDER
    {MODULE}_AI_FALLBACK_MODEL

Usage:
    from shared.ai.config import get_ai_config
    cfg = get_ai_config("daily_news")
    # cfg.provider, cfg.model, cfg.fallback_provider, cfg.fallback_model
"""

import os
from dataclasses import dataclass

# Per-provider default models if nothing is set in .env
_PROVIDER_DEFAULT_MODELS = {
    "anthropic": "claude-haiku-4-5",
    "deepseek":  "deepseek-chat",
}


@dataclass(frozen=True)
class AIConfig:
    provider:          str
    model:             str
    fallback_provider: str | None
    fallback_model:    str | None
    max_tokens:        int
    temperature:       float


def get_ai_config(module_name: str) -> AIConfig:
    """
    Build AIConfig for a given module by reading env vars.

    Priority for provider:
        1. {MODULE}_AI_PROVIDER
        2. AI_DEFAULT_PROVIDER
        3. "anthropic"

    Priority for model:
        1. {MODULE}_AI_MODEL
        2. AI_DEFAULT_MODEL
        3. hardcoded per-provider default
    """
    prefix = module_name.upper()

    provider = (
        os.getenv(f"{prefix}_AI_PROVIDER")
        or os.getenv("AI_DEFAULT_PROVIDER")
        or "anthropic"
    ).strip().lower()

    model = (
        os.getenv(f"{prefix}_AI_MODEL")
        or os.getenv("AI_DEFAULT_MODEL")
        or _PROVIDER_DEFAULT_MODELS.get(provider, "claude-haiku-4-5")
    ).strip()

    fallback_provider_raw = (
        os.getenv(f"{prefix}_AI_FALLBACK_PROVIDER")
        or os.getenv("AI_DEFAULT_FALLBACK_PROVIDER")
        or ""
    ).strip().lower()

    fallback_provider = fallback_provider_raw or None

    fallback_model = (
        os.getenv(f"{prefix}_AI_FALLBACK_MODEL")
        or _PROVIDER_DEFAULT_MODELS.get(fallback_provider or "", "")
        or None
    )
    if fallback_model:
        fallback_model = fallback_model.strip()

    max_tokens = int(
        os.getenv(f"{prefix}_AI_MAX_TOKENS")
        or os.getenv("AI_DEFAULT_MAX_TOKENS")
        or 1024
    )

    temperature = float(
        os.getenv(f"{prefix}_AI_TEMPERATURE")
        or os.getenv("AI_DEFAULT_TEMPERATURE")
        or 0.7
    )

    return AIConfig(
        provider=provider,
        model=model,
        fallback_provider=fallback_provider,
        fallback_model=fallback_model,
        max_tokens=max_tokens,
        temperature=temperature,
    )