#!/usr/bin/env python3
"""
Tests for Step 8's hostname-based brand slug resolution.
Pure logic — no FastAPI, no DB, no network needed.
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "..", "modules", "dashboard"))

os.environ["DASHBOARD_BASE_DOMAIN"] = "mycontentpilot.de"

from hostname import slug_from_host


def test_known_subdomain_extracts_slug():
    print("=== Test: germanysupport.mycontentpilot.de -> 'germanysupport' ===")
    assert slug_from_host("germanysupport.mycontentpilot.de") == "germanysupport"
    print("  PASS")


def test_subdomain_with_port_strips_port():
    print("=== Test: germanysupport.mycontentpilot.de:8090 -> 'germanysupport' ===")
    assert slug_from_host("germanysupport.mycontentpilot.de:8090") == "germanysupport"
    print("  PASS")


def test_root_domain_returns_none():
    print("=== Test: mycontentpilot.de -> None (no slug) ===")
    assert slug_from_host("mycontentpilot.de") is None
    assert slug_from_host("mycontentpilot.de:8090") is None
    print("  PASS")


def test_localhost_returns_none():
    print("=== Test: localhost / 127.0.0.1 -> None ===")
    assert slug_from_host("localhost") is None
    assert slug_from_host("localhost:8090") is None
    assert slug_from_host("127.0.0.1:8090") is None
    print("  PASS")


def test_empty_host_returns_none():
    print("=== Test: empty/missing host -> None, no crash ===")
    assert slug_from_host("") is None
    assert slug_from_host(None) is None
    print("  PASS")


def test_different_brand_subdomain():
    print("=== Test: technewshub.mycontentpilot.de -> 'technewshub' ===")
    assert slug_from_host("technewshub.mycontentpilot.de") == "technewshub"
    print("  PASS")


def test_unrelated_domain_returns_none():
    print("=== Test: other domain -> None (not our subdomain) ===")
    assert slug_from_host("other-domain.com") is None
    assert slug_from_host("evil.mycontentpilot.de.attacker.com") is None
    print("  PASS")


def test_base_domain_env_override():
    print("=== Test: DASHBOARD_BASE_DOMAIN env var is respected ===")
    os.environ["DASHBOARD_BASE_DOMAIN"] = "example.com"
    import importlib, hostname as hm
    importlib.reload(hm)
    assert hm.slug_from_host("mybrand.example.com") == "mybrand"
    assert hm.slug_from_host("mybrand.mycontentpilot.de") is None
    os.environ["DASHBOARD_BASE_DOMAIN"] = "mycontentpilot.de"
    importlib.reload(hm)
    print("  PASS")


if __name__ == "__main__":
    test_known_subdomain_extracts_slug()
    test_subdomain_with_port_strips_port()
    test_root_domain_returns_none()
    test_localhost_returns_none()
    test_empty_host_returns_none()
    test_different_brand_subdomain()
    test_unrelated_domain_returns_none()
    test_base_domain_env_override()
    print("\nAll subdomain routing tests passed.")
