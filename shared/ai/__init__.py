# shared/ai/__init__.py  (final version)
from .anthropic_client import anthropic_complete
from .deepseek_client import deepseek_complete
from .exceptions import AIClientError
from .config import get_ai_config, AIConfig
from .router import ai_complete

__all__ = [
    "anthropic_complete",
    "deepseek_complete",
    "AIClientError",
    "get_ai_config",
    "AIConfig",
    "ai_complete",
]