# shared/brands/validation.py
"""
Brand input validation for create_brand.py and service layer.
"""

from __future__ import annotations

import re


_SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9\-]{1,48}[a-z0-9]$")


def validate_slug(slug: str) -> str:
    """
    Normalize and validate a brand slug.

    Rules:
    - Lowercase letters, digits, hyphens only
    - Must start and end with alphanumeric
    - 3–50 characters

    Returns the normalized slug or raises ValueError.
    """
    normalized = slug.strip().lower().replace(" ", "-").replace("_", "-")
    if not _SLUG_PATTERN.match(normalized):
        raise ValueError(
            f"Invalid slug {slug!r}. Must be 3-50 characters, "
            "lowercase alphanumeric and hyphens, start/end with alphanumeric."
        )
    return normalized


def validate_name(name: str) -> str:
    name = name.strip()
    if not name or len(name) < 2:
        raise ValueError("Brand name must be at least 2 characters.")
    if len(name) > 100:
        raise ValueError("Brand name must be 100 characters or fewer.")
    return name


def validate_url(url: str) -> str:
    url = url.strip()
    if url and not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError(f"URL must start with http:// or https://: {url!r}")
    return url
