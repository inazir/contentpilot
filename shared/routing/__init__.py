# shared/routing/__init__.py
from .router import ArticleRouter, RouteDecision
from .strategies import keyword_match, ai_score

__all__ = ["ArticleRouter", "RouteDecision", "keyword_match", "ai_score"]
