# shared/brands/__init__.py
from .models import (
    Brand,
    BrandProfile,
    BrandCredential,
    BrandContext,
    init_brand_db,
    seed_default_brand,
)
from .service import (
    get_brand_context,
    get_brand_context_by_slug,
    get_default_brand_context,
    CRED_FACEBOOK,
    CRED_INSTAGRAM,
    CRED_WORDPRESS,
    CRED_AI_OVERRIDE,
    CRED_SOCIAL_TARGETS,
)
from .repository import (
    get_brand_by_id,
    get_brand_by_slug,
    get_all_enabled_brands,
    create_brand,
    upsert_profile,
    upsert_credential,
    get_credentials,
)

__all__ = [
    "Brand",
    "BrandProfile",
    "BrandCredential",
    "BrandContext",
    "init_brand_db",
    "seed_default_brand",
    "get_brand_context",
    "get_brand_context_by_slug",
    "get_default_brand_context",
    "CRED_FACEBOOK",
    "CRED_INSTAGRAM",
    "CRED_WORDPRESS",
    "CRED_AI_OVERRIDE",
    "CRED_SOCIAL_TARGETS",
    "get_brand_by_id",
    "get_brand_by_slug",
    "get_all_enabled_brands",
    "create_brand",
    "upsert_profile",
    "upsert_credential",
    "get_credentials",
]
