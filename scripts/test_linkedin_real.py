#!/usr/bin/env python3
# scripts/test_linkedin_real.py
import sys
import os
import requests
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

def _build_author_urn(raw_page_id: str) -> str:
    raw_page_id = raw_page_id.strip()
    if raw_page_id.startswith("urn:li:organization:"):
        return raw_page_id
    return f"urn:li:organization:{raw_page_id}"

def test_real_publish():
    print("\n=== Test: Real Flat Schema LinkedIn Publish ===")

    page_id = os.getenv("SOCIAL__GS_LINKEDIN_MAIN__PAGE_ID", "").strip()
    token   = os.getenv("SOCIAL__GS_LINKEDIN_MAIN__ACCESS_TOKEN", "").strip()

    if not page_id or not token:
        print("SKIP: Missing credentials.")
        return

    author_urn = _build_author_urn(page_id)
    
    # Claude's verified modern flat payload structure
    payload = {
        "author": author_urn,
        "commentary": "🚀 ContentPilot Pipeline Integration Test. This update uses the flat /rest/posts schema layout.",
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
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": "202603",
    }

    print(f"Sending request to LinkedIn /rest/posts targeting {author_urn}...")
    response = requests.post("https://api.linkedin.com/rest/posts", json=payload, headers=headers, timeout=30)

    if response.ok:
        post_urn = response.headers.get("x-restli-id") or response.headers.get("X-RestLi-Id")
        print(f"  success=True")
        print(f"  post_urn={post_urn}")
        print("  PASS")
    else:
        print(f"  success=False")
        print(f"  HTTP {response.status_code}: {response.text}")

if __name__ == "__main__":
    test_real_publish()