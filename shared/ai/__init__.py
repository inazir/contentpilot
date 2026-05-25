# shared/ai/__init__.py
"""
shared.ai — AI provider clients for ContentPilot.

Public interface:
    from shared.ai import anthropic_complete, deepseek_complete, AIClientError

Modules should import from here, never from the internal files directly.
This lets us reorganize internals without touching every module.
"""

from .anthropic_client import anthropic_complete
from .deepseek_client import deepseek_complete
from .exceptions import AIClientError

__all__ = [
    "anthropic_complete",
    "deepseek_complete",
    "AIClientError",
]