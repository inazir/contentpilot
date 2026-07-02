# modules/dashboard/hostname.py
"""
Hostname-to-brand-slug resolution for subdomain routing (Step 8).

Kept in its own module so it can be tested without importing FastAPI,
and imported by app.py without circular dependencies.
"""
import os


def get_base_domain() -> str:
    return os.getenv("DASHBOARD_BASE_DOMAIN", "mycontentpilot.de").lower()


def slug_from_host(host: str | None) -> str | None:
    """
    Extract brand slug from a subdomain Host header.

    'germanysupport.mycontentpilot.de'      -> 'germanysupport'
    'germanysupport.mycontentpilot.de:8090' -> 'germanysupport'
    'mycontentpilot.de'                     -> None
    'localhost:8090'                         -> None
    '127.0.0.1'                             -> None
    ''  / None                              -> None
    """
    if not host:
        return None

    host = host.split(":")[0].lower().strip()
    base = get_base_domain()

    if not host.endswith(f".{base}"):
        return None

    slug = host[: -len(f".{base}")]
    return slug if slug else None
