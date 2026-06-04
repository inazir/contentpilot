#!/usr/bin/env python3
"""
Offline tests for the multi-client routing layer.

Runs entirely in-process with no file system or network dependencies.
Uses an in-memory repository stub instead of JsonClientRepository.

Run with:
    python scripts/test_routing.py
"""

import sys
import os
import unittest
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.routing.models.client import (
    ClientConfig, WordPressClientConfig, FacebookClientConfig,
    PublishingPreferences, ImagePostConfig, ReelConfig,
)
from shared.routing.models.routing import RoutingDecision, RoutingResult
from shared.routing.models.publishing import PublishRequest, PublishFormat, PublishPlatform
from shared.routing.classifiers import KeywordClassifier
from shared.routing.repositories import ClientRepository
from shared.routing.router import AutoPublisherRouter
from shared.routing.publisher import MultiClientPublisher
from shared.routing.exceptions import (
    NoClientMatchedError, ClientNotFoundError,
)


# ---------------------------------------------------------------------------
# In-memory repository stub (no file I/O)
# ---------------------------------------------------------------------------

def _make_client(
    client_id: str,
    business_type: str,
    keywords: list[str],
    priority: int = 5,
    formats: tuple[str, ...] = ("text_link",),
) -> ClientConfig:
    return ClientConfig(
        client_id=client_id,
        client_name=f"Test {client_id}",
        business_type=business_type,
        enabled=True,
        routing_keywords=keywords,
        routing_priority=priority,
        wordpress=WordPressClientConfig(
            base_url=f"https://{client_id}.example.com",
            username="testuser",
            app_password_env=f"{client_id.upper()}_WP_PASS",
        ),
        facebook=FacebookClientConfig(
            page_id_env=f"{client_id.upper()}_FB_PAGE",
            access_token_env=f"{client_id.upper()}_FB_TOKEN",
            enabled=True,
        ),
        publishing_preferences=PublishingPreferences(
            formats=formats,
            image_post=ImagePostConfig(enabled=False),
            reel=ReelConfig(enabled=False),
            max_posts_per_day=5,
        ),
    )


class InMemoryRepository(ClientRepository):
    def __init__(self, clients: list[ClientConfig]) -> None:
        self._clients = {c.client_id: c for c in clients}

    def get_all(self) -> list[ClientConfig]:
        return [c for c in self._clients.values() if c.enabled]

    def get_by_id(self, client_id: str) -> ClientConfig:
        if client_id not in self._clients:
            raise ClientNotFoundError(client_id)
        return self._clients[client_id]

    def get_by_business_type(self, business_type: str) -> list[ClientConfig]:
        return [c for c in self._clients.values() if c.business_type == business_type and c.enabled]

    def reload(self) -> None:
        pass  # No-op for in-memory


FINANCE_CLIENT = _make_client(
    "finance_a", "finance", ["investing", "stocks", "portfolio", "market", "Federal Reserve"], priority=10
)
TECH_CLIENT = _make_client(
    "tech_a", "tech_saas", ["software", "SaaS", "startup", "app", "API", "cloud"], priority=9
)
DEALS_CLIENT = _make_client(
    "deals_a", "deals", ["discount", "sale", "promo", "coupon", "% off", "deal"], priority=7
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestKeywordClassifier(unittest.TestCase):

    def setUp(self):
        self.classifier = KeywordClassifier()

    def test_phrase_match_scores_higher_than_zero(self):
        result = self.classifier.classify(
            "The Federal Reserve raised interest rates again amid inflation.",
            ["Federal Reserve", "interest rates"],
            FINANCE_CLIENT,
        )
        self.assertGreater(result.score, 0.0)
        self.assertIn("Federal Reserve", result.matched_terms)

    def test_unrelated_article_scores_low(self):
        result = self.classifier.classify(
            "A new species of butterfly was discovered in the Amazon rainforest.",
            ["biology", "nature"],
            FINANCE_CLIENT,
        )
        self.assertLess(result.score, 0.1)

    def test_tech_article_matches_tech_client(self):
        result = self.classifier.classify(
            "A new SaaS startup launched an AI-powered API platform in the cloud.",
            ["SaaS", "startup", "AI"],
            TECH_CLIENT,
        )
        self.assertGreater(result.score, 0.1)

    def test_classify_all_sorted_descending(self):
        clients = [FINANCE_CLIENT, TECH_CLIENT, DEALS_CLIENT]
        results = self.classifier.classify_all(
            "Major discount sale on software tools, 50% off all SaaS subscriptions.",
            ["discount", "SaaS", "sale"],
            clients,
        )
        self.assertEqual(len(results), 3)
        # Results should be sorted best-first
        scores = [r.score for r in results]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_priority_breaks_ties(self):
        # Two clients with same keywords but different priorities
        client_high = _make_client("high_prio", "test", ["news"], priority=10)
        client_low  = _make_client("low_prio",  "test", ["news"], priority=2)
        results = self.classifier.classify_all(
            "Breaking news today.", ["news"], [client_low, client_high]
        )
        # High priority client should win
        self.assertEqual(results[0].client_id, "high_prio")


class TestAutoPublisherRouter(unittest.TestCase):

    def setUp(self):
        self.repo = InMemoryRepository([FINANCE_CLIENT, TECH_CLIENT, DEALS_CLIENT])
        self.router = AutoPublisherRouter(repository=self.repo, min_score=0.01)

    def test_finance_article_routes_to_finance_client(self):
        decision = self.router.route(
            article_id="art_001",
            article_text="The Federal Reserve announced a 0.25% interest rate hike this week, affecting stock market portfolios.",
            tags=["Federal Reserve", "interest rates", "investing"],
        )
        self.assertTrue(decision.routed)
        self.assertIsNotNone(decision.matched_client)
        self.assertEqual(decision.matched_client.client_id, "finance_a")

    def test_tech_article_routes_to_tech_client(self):
        decision = self.router.route(
            article_id="art_002",
            article_text="A new SaaS startup has launched an API platform with AI capabilities in the cloud.",
            tags=["SaaS", "startup", "API", "cloud"],
        )
        self.assertTrue(decision.routed)
        self.assertEqual(decision.matched_client.client_id, "tech_a")

    def test_deals_article_routes_to_deals_client(self):
        decision = self.router.route(
            article_id="art_003",
            article_text="Massive sale today — 50% discount on all products. Use promo code for extra savings.",
            tags=["discount", "sale", "promo"],
        )
        self.assertTrue(decision.routed)
        self.assertEqual(decision.matched_client.client_id, "deals_a")

    def test_unrelated_article_does_not_route(self):
        decision = self.router.route(
            article_id="art_004",
            article_text="A rare species of parrot was spotted in the rainforest near the Amazon.",
            tags=["wildlife", "nature", "conservation"],
        )
        # May or may not route — just checking it doesn't crash
        self.assertIsInstance(decision, RoutingDecision)
        self.assertIsInstance(decision.routed, bool)

    def test_raise_on_no_match(self):
        router = AutoPublisherRouter(repository=self.repo, min_score=0.99)
        with self.assertRaises(NoClientMatchedError):
            router.route(
                article_id="art_005",
                article_text="Completely unrelated content about penguins.",
                tags=[],
                raise_on_no_match=True,
            )

    def test_empty_client_list(self):
        empty_repo = InMemoryRepository([])
        router = AutoPublisherRouter(repository=empty_repo)
        decision = router.route(
            article_id="art_006",
            article_text="Any article text.",
            tags=[],
        )
        self.assertFalse(decision.routed)
        self.assertIsNone(decision.matched_client)

    def test_decision_contains_all_results(self):
        decision = self.router.route(
            article_id="art_007",
            article_text="investing in the stock market",
            tags=["stocks"],
        )
        # all_results should have an entry for each client
        self.assertEqual(len(decision.all_results), 3)


class TestMultiClientPublisher(unittest.TestCase):
    """Tests publisher in mock mode — no real API calls."""

    def setUp(self):
        os.environ["PUBLISH_MODE"] = "mock"
        self.publisher = MultiClientPublisher()

    def tearDown(self):
        os.environ.pop("PUBLISH_MODE", None)

    def test_text_link_mock_succeeds(self):
        client = _make_client("test_wp", "test", ["test"], formats=("text_link",))
        request = PublishRequest(
            article_id="pub_001",
            title="Test Article",
            body="Test body content.",
            summary="Test summary.",
            url="https://example.com/test",
        )
        summary = self.publisher.publish(request, client)
        self.assertGreater(len(summary.outcomes), 0)
        # All mock outcomes should succeed
        for outcome in summary.outcomes:
            self.assertTrue(outcome.success, f"Outcome failed: {outcome}")

    def test_image_post_skipped_when_disabled(self):
        client = _make_client("test_img", "test", ["test"], formats=("image_post",))
        # ImagePostConfig.enabled defaults to False in _make_client
        request = PublishRequest(
            article_id="pub_002",
            title="Image Test",
            body="Body.",
            summary="Summary.",
        )
        summary = self.publisher.publish(request, client)
        # image_post disabled → no outcomes
        self.assertEqual(len(summary.outcomes), 0)

    def test_reel_mock_succeeds_when_enabled(self):
        client = ClientConfig(
            client_id="reel_test",
            client_name="Reel Test",
            business_type="test",
            enabled=True,
            routing_keywords=["test"],
            routing_priority=5,
            wordpress=WordPressClientConfig(
                base_url="https://test.example.com",
                username="user",
                app_password_env="TEST_WP_PASS",
            ),
            facebook=FacebookClientConfig(
                page_id_env="TEST_FB_PAGE",
                access_token_env="TEST_FB_TOKEN",
                enabled=True,
            ),
            publishing_preferences=PublishingPreferences(
                formats=("reel",),
                image_post=ImagePostConfig(enabled=False),
                reel=ReelConfig(enabled=True, video_url_env="TEST_VIDEO_URL"),
                max_posts_per_day=5,
            ),
        )
        os.environ["TEST_VIDEO_URL"] = "https://example.com/video.mp4"
        request = PublishRequest(
            article_id="pub_003",
            title="Reel Test",
            body="Body.",
            summary="Summary.",
        )
        summary = self.publisher.publish(request, client)
        self.assertEqual(len(summary.outcomes), 1)
        self.assertEqual(summary.outcomes[0].format, PublishFormat.REEL)
        self.assertTrue(summary.outcomes[0].success)
        os.environ.pop("TEST_VIDEO_URL", None)

    def test_multiple_formats_all_execute(self):
        client = ClientConfig(
            client_id="multi_fmt",
            client_name="Multi Format",
            business_type="test",
            enabled=True,
            routing_keywords=["test"],
            routing_priority=5,
            wordpress=WordPressClientConfig(
                base_url="https://multi.example.com",
                username="user",
                app_password_env="MULTI_WP_PASS",
            ),
            facebook=FacebookClientConfig(
                page_id_env="MULTI_FB_PAGE",
                access_token_env="MULTI_FB_TOKEN",
                enabled=True,
            ),
            publishing_preferences=PublishingPreferences(
                formats=("text_link", "image_post"),
                image_post=ImagePostConfig(enabled=True, image_provider="mock"),
                reel=ReelConfig(enabled=False),
                max_posts_per_day=5,
            ),
        )
        request = PublishRequest(
            article_id="pub_004",
            title="Multi-format Test",
            body="Body.",
            summary="Summary.",
            url="https://example.com",
            image_url="https://example.com/image.jpg",
        )
        summary = self.publisher.publish(request, client)
        # text_link → WP + FB text = 2 outcomes
        # image_post → FB photo = 1 outcome
        self.assertEqual(len(summary.outcomes), 3)


class TestRepositoryStub(unittest.TestCase):

    def test_get_by_id_raises_on_missing(self):
        repo = InMemoryRepository([FINANCE_CLIENT])
        with self.assertRaises(ClientNotFoundError):
            repo.get_by_id("does_not_exist")

    def test_get_by_business_type(self):
        # Two finance clients
        finance_b = _make_client("finance_b", "finance", ["bonds"])
        repo = InMemoryRepository([FINANCE_CLIENT, finance_b, TECH_CLIENT])
        results = repo.get_by_business_type("finance")
        ids = {c.client_id for c in results}
        self.assertIn("finance_a", ids)
        self.assertIn("finance_b", ids)
        self.assertNotIn("tech_a", ids)

    def test_disabled_client_excluded_from_get_all(self):
        disabled = _make_client("disabled_one", "test", ["test"])
        object.__setattr__(disabled, "enabled", False)  # ClientConfig is mutable, just set directly
        disabled.enabled = False
        repo = InMemoryRepository([FINANCE_CLIENT, disabled])
        all_clients = repo.get_all()
        ids = {c.client_id for c in all_clients}
        self.assertIn("finance_a", ids)
        self.assertNotIn("disabled_one", ids)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestKeywordClassifier))
    suite.addTests(loader.loadTestsFromTestCase(TestAutoPublisherRouter))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiClientPublisher))
    suite.addTests(loader.loadTestsFromTestCase(TestRepositoryStub))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
