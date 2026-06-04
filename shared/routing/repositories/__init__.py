# shared/routing/repositories/__init__.py
"""
Client configuration repository layer.

Architecture decision: The router depends on ClientRepository (the abstract
base), never on a concrete implementation. This means the storage backend
(JSON → SQLite → PostgreSQL → Vault) can be swapped without touching
router or publisher code.

Current implementations:
    JsonClientRepository  — reads from clients_config.json (MVP / dev)

Planned:
    SqliteClientRepository
    PostgresClientRepository
    EnvClientRepository   — for single-client deploys via env vars only
"""

from __future__ import annotations

import json
import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from shared.routing.models.client import (
    ClientConfig,
    FacebookClientConfig,
    ImagePostConfig,
    PublishingPreferences,
    ReelConfig,
    WordPressClientConfig,
)
from shared.routing.exceptions import (
    ClientNotFoundError,
    ClientConfigError,
    RepositoryError,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------

class ClientRepository(ABC):
    """
    Abstract interface for client configuration storage.

    All router and publisher code depends on this interface only.
    Concrete implementations handle I/O and parsing.
    """

    @abstractmethod
    def get_all(self) -> list[ClientConfig]:
        """Return all enabled clients."""

    @abstractmethod
    def get_by_id(self, client_id: str) -> ClientConfig:
        """
        Return a specific client by ID.
        Raises ClientNotFoundError if not found.
        """

    @abstractmethod
    def get_by_business_type(self, business_type: str) -> list[ClientConfig]:
        """
        Return all enabled clients of a given business type.
        Note: business_type is metadata — the primary key is client_id.
        """

    @abstractmethod
    def reload(self) -> None:
        """
        Reload configuration from storage.
        Used for hot-reload without restarting the process.
        """


# ---------------------------------------------------------------------------
# JSON implementation (MVP)
# ---------------------------------------------------------------------------

_DEFAULT_CONFIG_PATH = "clients_config.json"


class JsonClientRepository(ClientRepository):
    """
    Reads client configuration from a JSON file.

    This is the MVP implementation. The JSON file must follow the schema
    defined in clients_config.json. Credentials are NOT resolved here —
    only env var names are stored in the config objects.

    Thread safety: Not thread-safe for concurrent writes. For production
    multi-threaded use, implement a lock around reload() or migrate to
    a proper database backend.

    Usage:
        repo = JsonClientRepository()                      # uses default path
        repo = JsonClientRepository("/path/to/clients.json")
        clients = repo.get_all()
    """

    def __init__(self, config_path: str | None = None) -> None:
        self._path = Path(
            config_path
            or os.getenv("CLIENTS_CONFIG_PATH", _DEFAULT_CONFIG_PATH)
        )
        self._clients: dict[str, ClientConfig] = {}
        self._loaded = False
        logger.debug("JsonClientRepository | path=%s", self._path)

    # ---- ClientRepository interface ----------------------------------------

    def get_all(self) -> list[ClientConfig]:
        self._ensure_loaded()
        return [c for c in self._clients.values() if c.enabled]

    def get_by_id(self, client_id: str) -> ClientConfig:
        self._ensure_loaded()
        client = self._clients.get(client_id)
        if client is None:
            raise ClientNotFoundError(client_id)
        return client

    def get_by_business_type(self, business_type: str) -> list[ClientConfig]:
        self._ensure_loaded()
        return [
            c for c in self._clients.values()
            if c.business_type == business_type and c.enabled
        ]

    def reload(self) -> None:
        self._clients = {}
        self._loaded = False
        self._load()
        logger.info(
            "JsonClientRepository.reload | path=%s | clients=%d",
            self._path, len(self._clients),
        )

    # ---- Internal ----------------------------------------------------------

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self._load()

    def _load(self) -> None:
        if not self._path.exists():
            raise RepositoryError(
                f"Client config file not found: {self._path}. "
                f"Set CLIENTS_CONFIG_PATH or create {_DEFAULT_CONFIG_PATH}."
            )

        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RepositoryError(
                f"Failed to parse client config JSON: {self._path}: {exc}"
            ) from exc

        clients_raw: list[dict] = raw.get("clients", [])
        loaded: dict[str, ClientConfig] = {}

        for entry in clients_raw:
            try:
                client = self._parse_client(entry)
                loaded[client.client_id] = client
                logger.debug(
                    "client_loaded | id=%s | name=%r | enabled=%s",
                    client.client_id, client.client_name, client.enabled,
                )
            except Exception as exc:
                client_id = entry.get("client_id", "<unknown>")
                logger.warning(
                    "client_parse_error | id=%s | error=%s | skipping",
                    client_id, exc,
                )
                # Skip malformed entries rather than crashing the whole load.
                # Production systems should alert on this.

        self._clients = loaded
        self._loaded = True
        logger.info(
            "JsonClientRepository.load | path=%s | total=%d | loaded=%d",
            self._path, len(clients_raw), len(loaded),
        )

    def _parse_client(self, data: dict[str, Any]) -> ClientConfig:
        """Parse one client dict into a ClientConfig. Raises ClientConfigError on bad data."""
        required = ["client_id", "client_name", "business_type", "wordpress", "facebook"]
        for field in required:
            if field not in data:
                raise ClientConfigError(f"Missing required field: {field!r}")

        wp_data = data["wordpress"]
        fb_data = data["facebook"]
        prefs_data = data.get("publishing_preferences", {})

        wordpress = WordPressClientConfig(
            base_url=wp_data["base_url"],
            username=wp_data["username"],
            app_password_env=wp_data["app_password_env"],
            default_status=wp_data.get("default_status", "draft"),
            default_categories=list(wp_data.get("default_categories", [])),
            default_tags=list(wp_data.get("default_tags", [])),
            timeout_seconds=int(wp_data.get("timeout_seconds", 30)),
        )

        facebook = FacebookClientConfig(
            page_id_env=fb_data["page_id_env"],
            access_token_env=fb_data["access_token_env"],
            enabled=bool(fb_data.get("enabled", True)),
        )

        img_data = prefs_data.get("image_post", {})
        reel_data = prefs_data.get("reel", {})

        preferences = PublishingPreferences(
            formats=tuple(prefs_data.get("formats", ["text_link"])),
            image_post=ImagePostConfig(
                enabled=bool(img_data.get("enabled", False)),
                image_provider=img_data.get("image_provider", "mock"),
            ),
            reel=ReelConfig(
                enabled=bool(reel_data.get("enabled", False)),
                video_url_env=reel_data.get("video_url_env", ""),
            ),
            max_posts_per_day=int(prefs_data.get("max_posts_per_day", 5)),
        )

        return ClientConfig(
            client_id=data["client_id"],
            client_name=data["client_name"],
            business_type=data["business_type"],
            enabled=bool(data.get("enabled", True)),
            routing_keywords=list(data.get("routing_keywords", [])),
            routing_priority=int(data.get("routing_priority", 5)),
            wordpress=wordpress,
            facebook=facebook,
            publishing_preferences=preferences,
        )
