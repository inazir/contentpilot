#!/usr/bin/env python3
# scripts/test_wordpress.py
"""
WordPress client tests — no real network calls required.
All HTTP is intercepted with unittest.mock.

Run locally:  PYTHONPATH=. python3 scripts/test_wordpress.py
Run in Docker:
    docker compose -f infra/compose/docker-compose.yml run --rm daily_news \
        python /app/scripts/test_wordpress.py
"""

import os
import sys
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, "/app")

# Minimal env so config doesn't raise
os.environ.setdefault("WORDPRESS_BASE_URL",     "https://example.com")
os.environ.setdefault("WORDPRESS_USERNAME",     "testuser")
os.environ.setdefault("WORDPRESS_APP_PASSWORD", "test app password")

from shared.logging import configure_logging, get_logger
from shared.wordpress import WordPressClient, PostRequest, PostResponse
from shared.wordpress.exceptions import AuthError, ValidationError
from shared.wordpress.models import WordPressConfig

configure_logging()
logger = get_logger("test_wordpress")

PASS = "PASS"
FAIL = "FAIL"
failures: list[str] = []


def check(name: str, fn) -> None:
    try:
        fn()
        print(f"  [{PASS}] {name}")
    except AssertionError as exc:
        print(f"  [{FAIL}] {name}: {exc}")
        failures.append(name)
    except Exception as exc:
        print(f"  [{FAIL}] {name}: {type(exc).__name__}: {exc}")
        failures.append(name)


def _make_client(max_retries: int = 0) -> WordPressClient:
    config = WordPressConfig(
        base_url        = "https://example.com",
        username        = "testuser",
        app_password    = "abcd efgh ijkl mnop",
        default_status  = "draft",
        timeout_seconds = 5,
        max_retries     = max_retries,
    )
    return WordPressClient(config)


def _mock_response(status_code: int, body: dict) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.ok = status_code < 400
    mock.json.return_value = body
    mock.text = json.dumps(body)
    mock.url = "https://example.com/wp-json/wp/v2/posts"
    return mock


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_create_post_success():
    client = _make_client()
    mock_resp = _mock_response(201, {
        "id": 42,
        "link": "https://example.com/my-post/",
        "status": "draft",
    })
    with patch("requests.post", return_value=mock_resp):
        result = client.create_post(PostRequest(
            title="Test Post",
            content="<p>Hello world</p>",
            status="draft",
        ))
    assert result.success,                   "Expected success"
    assert result.wordpress_post_id == 42,   f"Expected post_id=42, got {result.wordpress_post_id}"
    assert result.status == "draft",         f"Expected draft, got {result.status}"
    assert result.url == "https://example.com/my-post/"


def test_create_post_publish_status():
    client = _make_client()
    mock_resp = _mock_response(201, {
        "id": 99,
        "link": "https://example.com/live-post/",
        "status": "publish",
    })
    with patch("requests.post", return_value=mock_resp):
        result = client.create_post(PostRequest(
            title="Live Post",
            content="<p>Published</p>",
            status="publish",
        ))
    assert result.success
    assert result.status == "publish"
    assert result.wordpress_post_id == 99


def test_auth_failure_401():
    client = _make_client()
    mock_resp = _mock_response(401, {"message": "Incorrect password."})
    mock_resp.ok = False
    with patch("requests.post", return_value=mock_resp):
        result = client.create_post(PostRequest(
            title="Will fail",
            content="content",
        ))
    assert not result.success,              "Expected failure on 401"
    assert not result.retryable,            "Auth errors must not be retryable"
    assert "401" in result.error_message or "Authentication" in result.error_message


def test_validation_failure_400():
    client = _make_client()
    mock_resp = _mock_response(400, {"message": "Invalid post title."})
    mock_resp.ok = False
    with patch("requests.post", return_value=mock_resp):
        result = client.create_post(PostRequest(
            title="",
            content="content",
        ))
    assert not result.success
    assert not result.retryable


def test_server_error_retries_then_fails():
    client = _make_client(max_retries=2)
    mock_resp = _mock_response(503, {"message": "Service unavailable"})
    mock_resp.ok = False
    call_count = [0]

    def fake_post(*args, **kwargs):
        call_count[0] += 1
        return mock_resp

    with patch("requests.post", side_effect=fake_post):
        with patch("time.sleep"):   # skip real waiting
            result = client.create_post(PostRequest(
                title="Retry test",
                content="content",
            ))

    assert not result.success
    assert result.retryable,    "503 should be retryable"
    assert call_count[0] == 3,  f"Expected 3 attempts (1 + 2 retries), got {call_count[0]}"


def test_timeout_is_retryable():
    import requests as req_lib
    client = _make_client(max_retries=1)
    call_count = [0]

    def fake_post(*args, **kwargs):
        call_count[0] += 1
        raise req_lib.Timeout()

    with patch("requests.post", side_effect=fake_post):
        with patch("time.sleep"):
            result = client.create_post(PostRequest(
                title="Timeout test",
                content="content",
            ))

    assert not result.success
    assert result.retryable
    assert call_count[0] == 2   # 1 attempt + 1 retry


def test_update_post():
    client = _make_client()
    mock_resp = _mock_response(200, {
        "id": 42,
        "link": "https://example.com/my-post/",
        "status": "publish",
    })
    with patch("requests.post", return_value=mock_resp):
        result = client.update_post(42, PostRequest(
            title="Updated Title",
            content="<p>Updated</p>",
            status="publish",
        ))
    assert result.success
    assert result.wordpress_post_id == 42


def test_post_request_payload_omits_none_fields():
    post = PostRequest(title="T", content="C", status="draft")
    payload = post.to_api_payload()
    assert "excerpt"        not in payload
    assert "categories"     not in payload
    assert "tags"           not in payload
    assert "featured_media" not in payload
    assert payload["title"]   == "T"
    assert payload["content"] == "C"
    assert payload["status"]  == "draft"


def test_post_request_payload_includes_optional_fields():
    post = PostRequest(
        title="T",
        content="C",
        status="publish",
        excerpt="short excerpt",
        categories=[1, 2],
        tags=[5],
    )
    payload = post.to_api_payload()
    assert payload["excerpt"]    == "short excerpt"
    assert payload["categories"] == [1, 2]
    assert payload["tags"]       == [5]


def test_check_auth_success():
    client = _make_client()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    with patch("requests.get", return_value=mock_resp):
        assert client.check_auth() is True


def test_check_auth_failure():
    client = _make_client()
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    with patch("requests.get", return_value=mock_resp):
        assert client.check_auth() is False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("\nPhase 9 — WordPress Client Tests")
    print("=" * 45)

    check("create post — draft success",            test_create_post_success)
    check("create post — publish status",           test_create_post_publish_status)
    check("auth failure 401 — not retryable",       test_auth_failure_401)
    check("validation failure 400 — not retryable", test_validation_failure_400)
    check("503 retries exhausted",                  test_server_error_retries_then_fails)
    check("timeout is retryable",                   test_timeout_is_retryable)
    check("update post",                            test_update_post)
    check("payload omits None fields",              test_post_request_payload_omits_none_fields)
    check("payload includes optional fields",       test_post_request_payload_includes_optional_fields)
    check("check_auth — success",                   test_check_auth_success)
    check("check_auth — failure",                   test_check_auth_failure)

    print("=" * 45)
    if failures:
        print(f"\n  {len(failures)} test(s) failed: {', '.join(failures)}")
        sys.exit(1)
    else:
        print("\n  All tests passed.")


if __name__ == "__main__":
    main()
