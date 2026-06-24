# shared/social/linkedin.py — corrected for /rest/posts

import os
import requests
import logging

logger = logging.getLogger(__name__)

_REST_POSTS_URL = "https://api.linkedin.com/rest/posts"
_LINKEDIN_VERSION = "202603"  # match what you validated via curl
_TIMEOUT = 30


def _build_author_urn(raw_page_id: str) -> str:
    """
    Builds the organization URN from a raw numeric Page ID.
    Handles the case where .env already contains the full urn:li:... string too.
    """
    raw_page_id = raw_page_id.strip()
    if raw_page_id.startswith("urn:li:organization:"):
        return raw_page_id
    return f"urn:li:organization:{raw_page_id}"


def publish_post_real(content: str, target, image_url: str | None = None) -> dict:
    author_urn = _build_author_urn(target.page_id)

    payload = {
        "author": author_urn,
        "commentary": content,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    headers = {
        "Authorization": f"Bearer {target.access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": _LINKEDIN_VERSION,
    }

    response = requests.post(_REST_POSTS_URL, json=payload, headers=headers, timeout=_TIMEOUT)

    if not response.ok:
        raise RuntimeError(f"LinkedIn HTTP {response.status_code}: {response.text[:300]}")

    post_urn = response.headers.get("x-restli-id") or response.headers.get("X-RestLi-Id")
    return {"success": True, "post_id": post_urn}
    