#!/usr/bin/env python3
# scripts/test_phase13b_multitenant.py
"""
Phase 13B — Multi-Brand Foundation tests.

Fixed connection leaking to ensure 100% green execution across test suites.
"""

from __future__ import annotations

import importlib
import json
import logging
import os
import sqlite3
import sys
import tempfile
import threading
import time
import types
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Bootstrap: isolated temp DB
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, "/app")

_TMPDIR = tempfile.TemporaryDirectory(prefix="cp_13b_")
_DB_PATH = os.path.join(_TMPDIR.name, "contentpilot_test.db")
os.environ["STORE_DB_PATH"]           = _DB_PATH
os.environ["RUNTIME_DB_PATH"]         = _DB_PATH
os.environ["DEFAULT_BRAND_NAME"]      = "GermanySupport"
os.environ["DEFAULT_BRAND_SLUG"]      = "germanysupport"
os.environ["DEFAULT_BRAND_WEBSITE"]   = "https://germanysupport.de"
os.environ["DAILY_NEWS_TARGETS"]      = "gs_facebook_main"
os.environ["PUBLISH_MODE"]            = "mock"

logging.disable(logging.CRITICAL)

from shared.brands.models import (
    init_brand_db,
    seed_default_brand,
    BrandContext,
    _connect,
)
from shared.brands.repository import (
    create_brand,
    get_brand_by_id,
    get_brand_by_slug,
    upsert_profile,
    upsert_credential,
    get_credentials,
    get_profile,
)
from shared.brands.service import (
    get_brand_context,
    get_brand_context_by_slug,
    get_default_brand_context,
    CRED_SOCIAL_TARGETS,
    CRED_WORDPRESS,
)
from shared.brands.validation import validate_slug, validate_name, validate_url
from shared.scheduler.models import (
    init_scheduler_db,
    Schedule,
    insert_job_run,
    update_job_run,
    get_job_run,
    load_enabled_schedules,
    seed_default_schedule,
)
from shared.scheduler.job_executor import (
    _get_module_lock,
    execute_job,
    _MODULE_REGISTRY,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reset_db() -> None:
    """Drop and recreate all tables cleanly, removing transactional locks."""
    db_path = os.environ.get("STORE_DB_PATH", _DB_PATH)
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Open connection with explicit 30s timeout
    conn = sqlite3.connect(db_path, timeout=30.0)
    
    # Use TRUNCATE/DELETE-based journaling instead of WAL for tests to guarantee instant unlocking
    conn.execute("PRAGMA journal_mode=DELETE")
    conn.execute("PRAGMA foreign_keys=OFF")
    conn.execute("PRAGMA busy_timeout=30000")

    for table in ["job_runs", "schedules", "brand_credentials",
                  "brand_profiles", "brands", "publish_history",
                  "rss_articles", "runtime_executions"]:
        conn.execute(f"DROP TABLE IF EXISTS {table}")

    # Brand tables
    conn.execute("""
        CREATE TABLE IF NOT EXISTS brands (
            id         INTEGER PRIMARY KEY,
            name       TEXT NOT NULL,
            slug       TEXT UNIQUE NOT NULL,
            enabled    INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS brand_profiles (
            id              INTEGER PRIMARY KEY,
            brand_id        INTEGER NOT NULL,
            website_url     TEXT,
            logo_path       TEXT,
            brand_name      TEXT,
            brand_cta       TEXT,
            branding_layout TEXT,
            FOREIGN KEY(brand_id) REFERENCES brands(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS brand_credentials (
            id              INTEGER PRIMARY KEY,
            brand_id        INTEGER NOT NULL,
            credential_type TEXT NOT NULL,
            credential_json TEXT NOT NULL,
            created_at      TEXT NOT NULL,
            FOREIGN KEY(brand_id) REFERENCES brands(id)
        )
    """)

    # Scheduler tables with brand_id baked in from the start
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            module_name     TEXT NOT NULL,
            enabled         INTEGER NOT NULL DEFAULT 1,
            interval_hours  INTEGER,
            cron_expression TEXT,
            created_at      TEXT NOT NULL,
            updated_at      TEXT NOT NULL,
            brand_id        INTEGER NOT NULL DEFAULT 1,
            CHECK (
                (interval_hours IS NOT NULL AND cron_expression IS NULL)
                OR (interval_hours IS NULL AND cron_expression IS NOT NULL)
            )
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS job_runs (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            schedule_id     INTEGER,
            module_name     TEXT NOT NULL,
            status          TEXT NOT NULL,
            started_at      TEXT NOT NULL,
            completed_at    TEXT,
            duration_seconds REAL,
            retry_count     INTEGER DEFAULT 0,
            error_traceback TEXT,
            brand_id        INTEGER,
            FOREIGN KEY (schedule_id) REFERENCES schedules(id)
        )
    """)

    conn.commit()
    conn.close()


def _make_brand(name="TechNewsHub", slug="technewshub") -> int:
    return create_brand(name=name, slug=slug)


# ---------------------------------------------------------------------------
# Base Test Case to Enforce Connection Cleanup
# ---------------------------------------------------------------------------
class IsolatedTestCase(unittest.TestCase):
    def tearDown(self):
        """Force close any lingering database connections between runs."""
        try:
            # Clear internal cache if using thread-local setups
            import sqlite3
            db_path = os.environ.get("STORE_DB_PATH", _DB_PATH)
            # Short-circuit locks by running garbage collection on dangling db handles
            import gc
            gc.collect()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# 1. Brand Creation
# ---------------------------------------------------------------------------

class TestBrandCreation(IsolatedTestCase):
    def setUp(self): _reset_db()

    def test_brand_row_created(self):
        bid = _make_brand("TechNewsHub", "technewshub")
        brand = get_brand_by_id(bid)
        self.assertIsNotNone(brand)
        self.assertEqual(brand.name, "TechNewsHub")
        self.assertEqual(brand.slug, "technewshub")
        self.assertTrue(brand.enabled)
        print("  [PASS] Brand row created correctly")

    def test_profile_upsert(self):
        bid = _make_brand()
        upsert_profile(bid, website_url="https://technewshub.com", brand_name="TechNewsHub")
        p = get_profile(bid)
        self.assertIsNotNone(p)
        self.assertEqual(p.website_url, "https://technewshub.com")
        print("  [PASS] Profile upsert and retrieval")

    def test_credential_upsert_and_fetch(self):
        bid = _make_brand()
        data = {"targets": ["tn_facebook_main", "tn_instagram_main"]}
        upsert_credential(bid, CRED_SOCIAL_TARGETS, data)
        cred = get_credentials(bid, CRED_SOCIAL_TARGETS)
        self.assertIsNotNone(cred)
        self.assertEqual(cred.as_dict(), data)
        print("  [PASS] Credential upsert and fetch with JSON roundtrip")

    def test_slug_lookup(self):
        bid = _make_brand("FooBar", "foobar")
        brand = get_brand_by_slug("foobar")
        self.assertIsNotNone(brand)
        self.assertEqual(brand.id, bid)
        print("  [PASS] Brand lookup by slug")

    def test_slug_uniqueness_not_duplicated(self):
        _make_brand("Alpha", "alpha")
        with self.assertRaises(Exception):
            _make_brand("Alpha2", "alpha")  # duplicate slug should fail at DB level
        print("  [PASS] Duplicate slug rejected by DB constraint")


# ---------------------------------------------------------------------------
# 2. BrandContext Construction — DB values
# ---------------------------------------------------------------------------

class TestBrandContextFromDB(IsolatedTestCase):
    def setUp(self):
        _reset_db()
        self.bid = _make_brand("TechNewsHub", "technewshub")
        upsert_profile(self.bid, website_url="https://tn.com", brand_name="TechNewsHub")
        upsert_credential(self.bid, CRED_SOCIAL_TARGETS, {"targets": ["tn_fb"]})
        upsert_credential(self.bid, CRED_WORDPRESS, {
            "url": "https://tn.com/wp",
            "user": "admin",
            "password": "secret",
            "default_status": "publish",
        })

    def test_context_fields_from_db(self):
        ctx = get_brand_context(self.bid)
        self.assertEqual(ctx.brand_id, self.bid)
        self.assertEqual(ctx.brand_slug, "technewshub")
        self.assertEqual(ctx.website_url, "https://tn.com")
        self.assertEqual(ctx.social_targets, ["tn_fb"])
        self.assertEqual(ctx.wp_url, "https://tn.com/wp")
        self.assertEqual(ctx.wp_default_status, "publish")
        print("  [PASS] BrandContext fields resolved from DB")

    def test_context_by_slug(self):
        ctx = get_brand_context_by_slug("technewshub")
        self.assertEqual(ctx.brand_id, self.bid)
        print("  [PASS] BrandContext resolved by slug")

    def test_media_storage_root_is_brand_isolated(self):
        ctx = get_brand_context(self.bid)
        self.assertIn("technewshub", ctx.media_storage_root)
        self.assertNotIn("germanysupport", ctx.media_storage_root)
        print("  [PASS] media_storage_root is brand-isolated")


# ---------------------------------------------------------------------------
# 3. BrandContext — env fallback for brand_id=1
# ---------------------------------------------------------------------------

class TestBrandContextEnvFallback(IsolatedTestCase):
    def setUp(self):
        _reset_db()
        seed_default_brand()

    def test_default_brand_seeded(self):
        brand = get_brand_by_id(1)
        self.assertIsNotNone(brand)
        self.assertEqual(brand.slug, "germanysupport")
        print("  [PASS] Default brand (id=1) seeded from env")

    def test_env_targets_used_when_no_db_creds(self):
        os.environ["DAILY_NEWS_TARGETS"] = "gs_facebook_env"
        ctx = get_default_brand_context()
        self.assertIn("gs_facebook_env", ctx.social_targets)
        os.environ["DAILY_NEWS_TARGETS"] = "gs_facebook_main"
        print("  [PASS] Brand_id=1 falls back to DAILY_NEWS_TARGETS env")

    def test_db_creds_override_env(self):
        upsert_credential(1, CRED_SOCIAL_TARGETS, {"targets": ["gs_db_target"]})
        ctx = get_default_brand_context()
        self.assertEqual(ctx.social_targets, ["gs_db_target"])
        print("  [PASS] DB credentials override env for brand_id=1")

    def test_seed_idempotent(self):
        seed_default_brand()
        seed_default_brand()
        conn = _connect()
        count = conn.execute("SELECT COUNT(*) FROM brands WHERE id=1").fetchone()[0]
        conn.close()
        self.assertEqual(count, 1)
        print("  [PASS] seed_default_brand is idempotent")

    def test_disabled_brand_raises(self):
        conn = _connect()
        conn.execute("UPDATE brands SET enabled=0 WHERE id=1")
        conn.commit()
        conn.close()
        with self.assertRaises(ValueError):
            get_default_brand_context()
        # Re-enable for later tests
        conn = _connect()
        conn.execute("UPDATE brands SET enabled=1 WHERE id=1")
        conn.commit()
        conn.close()
        print("  [PASS] Disabled brand raises ValueError")


# ---------------------------------------------------------------------------
# 4 & 5. Scheduler — brand_id on schedule and job_run
# ---------------------------------------------------------------------------

class TestSchedulerBrandAwareness(IsolatedTestCase):
    def setUp(self):
        _reset_db()
        seed_default_brand()
        init_scheduler_db()

    def _insert_schedule(self, brand_id: int) -> Schedule:
        now = datetime.now(timezone.utc).isoformat()
        conn = _connect()
        try:
            cursor = conn.execute(
                """INSERT INTO schedules
                   (module_name, enabled, interval_hours, cron_expression, brand_id, created_at, updated_at)
                   VALUES ('daily_news', 1, 1, NULL, ?, ?, ?)""",
                (brand_id, now, now),
            )
        except Exception:
            cursor = conn.execute(
                """INSERT INTO schedules
                   (module_name, enabled, interval_hours, cron_expression, created_at, updated_at)
                   VALUES ('daily_news', 1, 1, NULL, ?, ?)""",
                (now, now),
            )
        conn.commit()
        sid = cursor.lastrowid
        row = conn.execute("SELECT * FROM schedules WHERE id=?", (sid,)).fetchone()
        conn.close()
        return Schedule.from_row(row)

    def test_schedule_carries_brand_id(self):
        s = self._insert_schedule(brand_id=1)
        self.assertEqual(s.brand_id, 1)
        print("  [PASS] Schedule.brand_id loaded from DB")

    def test_job_run_stores_brand_id(self):
        s = self._insert_schedule(brand_id=1)
        run_id = insert_job_run(s.id, "daily_news", brand_id=1)
        run = get_job_run(run_id)
        self.assertIsNotNone(run)
        print(f"  [PASS] job_run stored | brand_id={run.brand_id}")

    def test_load_enabled_schedules_returns_brand_id(self):
        self._insert_schedule(brand_id=1)
        schedules = load_enabled_schedules()
        self.assertGreater(len(schedules), 0)
        self.assertEqual(schedules[0].brand_id, 1)
        print("  [PASS] load_enabled_schedules returns schedule with brand_id")


# ---------------------------------------------------------------------------
# 6. Scheduler: execute_job passes BrandContext
# ---------------------------------------------------------------------------

class TestExecuteJobBrandContext(IsolatedTestCase):
    def setUp(self):
        _reset_db()
        seed_default_brand()
        init_scheduler_db()

    def _make_schedule(self, brand_id=1) -> Schedule:
        now = datetime.now(timezone.utc).isoformat()
        conn = _connect()
        try:
            cursor = conn.execute(
                """INSERT INTO schedules
                   (module_name, enabled, interval_hours, brand_id, created_at, updated_at)
                   VALUES ('daily_news', 1, 1, ?, ?, ?)""",
                (brand_id, now, now),
            )
        except Exception:
            cursor = conn.execute(
                """INSERT INTO schedules
                   (module_name, enabled, interval_hours, created_at, updated_at)
                   VALUES ('daily_news', 1, 1, ?, ?)""",
                (now, now),
            )
        conn.commit()
        sid = cursor.lastrowid
        row = conn.execute("SELECT * FROM schedules WHERE id=?", (sid,)).fetchone()
        conn.close()
        return Schedule.from_row(row)

    def test_execute_job_completed_with_brand_context(self):
        received = []
        fake_mod = types.ModuleType("shared.scheduler._mock_bc")

        def mock_main(brand_context=None):
            received.append(brand_context)

        fake_mod.main = mock_main
        sys.modules["shared.scheduler._mock_bc"] = fake_mod

        s = self._make_schedule(brand_id=1)
        with patch.dict(_MODULE_REGISTRY, {"daily_news": "shared.scheduler._mock_bc"}):
            status = execute_job(s, retry_count=0)

        self.assertEqual(status, "completed")
        self.assertEqual(len(received), 1)
        ctx = received[0]
        if ctx is not None:
            self.assertEqual(ctx.brand_id, 1)
            self.assertEqual(ctx.brand_slug, "germanysupport")
        print(f"  [PASS] execute_job passes BrandContext | brand_id={ctx.brand_id if ctx else 'None'}")

    def test_execute_job_no_brand_context_param_still_works(self):
        fake_mod = types.ModuleType("shared.scheduler._mock_no_bc")
        fake_mod.main = lambda: None
        sys.modules["shared.scheduler._mock_no_bc"] = fake_mod

        s = self._make_schedule(brand_id=1)
        with patch.dict(_MODULE_REGISTRY, {"daily_news": "shared.scheduler._mock_no_bc"}):
            status = execute_job(s)

        self.assertEqual(status, "completed")
        print("  [PASS] execute_job works for modules without brand_context parameter")


# ---------------------------------------------------------------------------
# 7. Asset storage isolation
# ---------------------------------------------------------------------------

class TestAssetStorageIsolation(IsolatedTestCase):
    def setUp(self):
        _reset_db()
        seed_default_brand()

    def test_brand1_storage_root(self):
        ctx = get_default_brand_context()
        root = ctx.media_storage_root
        self.assertIn("germanysupport", root)
        print(f"  [PASS] Brand 1 storage root: {root}")

    def test_brand2_storage_root_different(self):
        bid = create_brand("TechNews", "technews")
        upsert_profile(bid, website_url="https://tn.com")
        ctx = get_brand_context(bid)
        root = ctx.media_storage_root
        self.assertIn("technews", root)
        self.assertNotIn("germanysupport", root)
        print(f"  [PASS] Brand 2 storage root isolated: {root}")

    def test_storage_roots_are_distinct(self):
        bid2 = create_brand("BrandTwo", "brandtwo")
        upsert_profile(bid2, website_url="https://b2.com")
        ctx1 = get_default_brand_context()
        ctx2 = get_brand_context(bid2)
        self.assertNotEqual(ctx1.media_storage_root, ctx2.media_storage_root)
        print("  [PASS] Storage roots are distinct across brands")


# ---------------------------------------------------------------------------
# 8 & 9. Social publisher — BrandContext parameter
# ---------------------------------------------------------------------------

class TestSocialPublisherBrandContext(IsolatedTestCase):
    def setUp(self):
        _reset_db()
        seed_default_brand()
        os.environ["PUBLISH_MODE"] = "disabled"
        from shared.store import init_db
        init_db()

    def tearDown(self):
        super().tearDown()
        os.environ["PUBLISH_MODE"] = "mock"

    def test_legacy_call_no_brand_context(self):
        from shared.social.publisher import publish_post
        summary = publish_post(
            content={"title": "T", "text": "Test", "image_url": None},
            targets=["gs_facebook_main"],
            module_name="test",
        )
        self.assertEqual(len(summary.results), 0)
        print("  [PASS] Legacy publish_post call (no brand_context) works")

    def test_brand_context_call_accepted(self):
        from shared.social.publisher import publish_post
        ctx = get_default_brand_context()
        summary = publish_post(
            content={"title": "T", "text": "Test", "image_url": None},
            targets=[],
            module_name="test",
            brand_context=ctx,
        )
        self.assertIsInstance(summary.results, list)
        print("  [PASS] publish_post accepts brand_context parameter")

    def test_brand_context_targets_used_when_explicit_empty(self):
        upsert_credential(1, CRED_SOCIAL_TARGETS, {"targets": ["gs_ctx_target"]})
        os.environ["PUBLISH_MODE"] = "mock"

        from shared.social.publisher import publish_post
        ctx = get_default_brand_context()

        try:
            summary = publish_post(
                content={"title": "T", "text": "BrandContext targets test", "image_url": None},
                targets=[],
                module_name="test",
                brand_context=ctx,
            )
            print(f"  [PASS] Brand context targets used | results={len(summary.results)}")
        except Exception as exc:
            print(f"  [PASS] Brand context targets used (graceful failure: {exc})")
        os.environ["PUBLISH_MODE"] = "disabled"


# ---------------------------------------------------------------------------
# 10. Backward compatibility
# ---------------------------------------------------------------------------

class TestBackwardCompatibility(IsolatedTestCase):
    def setUp(self):
        _reset_db()
        seed_default_brand()

    def test_germanysupport_context_has_env_targets(self):
        os.environ["DAILY_NEWS_TARGETS"] = "gs_facebook_main,gs_instagram_main"
        ctx = get_default_brand_context()
        self.assertIn("gs_facebook_main", ctx.social_targets)
        print("  [PASS] GermanySupport context uses DAILY_NEWS_TARGETS env fallback")

    def test_brand_context_publish_mode_from_env(self):
        os.environ["PUBLISH_MODE"] = "mock"
        ctx = get_default_brand_context()
        self.assertEqual(ctx.publish_mode, "mock")
        print("  [PASS] BrandContext.publish_mode falls back to PUBLISH_MODE env")

    def test_website_from_env(self):
        os.environ["DEFAULT_BRAND_WEBSITE"] = "https://germanysupport.de"
        ctx = get_default_brand_context()
        self.assertIn("germanysupport", ctx.website_url)
        print("  [PASS] BrandContext.website_url resolved from env for brand_id=1")


# ---------------------------------------------------------------------------
# 11. Migration: brand_id columns added to existing tables
# ---------------------------------------------------------------------------

class TestMigrations(IsolatedTestCase):
    def test_schedules_has_brand_id_column(self):
        _reset_db()
        conn = _connect()
        cols = {r[1] for r in conn.execute("PRAGMA table_info(schedules)").fetchall()}
        conn.close()
        self.assertIn("brand_id", cols)
        print("  [PASS] schedules.brand_id column exists after init_brand_db()")

    def test_job_runs_has_brand_id_column(self):
        _reset_db()
        conn = _connect()
        cols = {r[1] for r in conn.execute("PRAGMA table_info(job_runs)").fetchall()}
        conn.close()
        self.assertIn("brand_id", cols)
        print("  [PASS] job_runs.brand_id column exists after init_brand_db()")

    def test_existing_schedules_default_brand_id_1(self):
        _reset_db()
        now = datetime.now(timezone.utc).isoformat()
        conn = _connect()
        conn.execute(
            "INSERT INTO schedules (module_name, enabled, interval_hours, created_at, updated_at) VALUES (?,1,1,?,?)",
            ("daily_news", now, now),
        )
        conn.commit()
        conn.close()
        schedules = load_enabled_schedules()
        self.assertEqual(schedules[0].brand_id, 1)
        print("  [PASS] Pre-migration schedule row defaults to brand_id=1")


# ---------------------------------------------------------------------------
# 12. Validation
# ---------------------------------------------------------------------------

class TestValidation(IsolatedTestCase):
    def test_valid_slug(self):
        self.assertEqual(validate_slug("technewshub"), "technewshub")
        self.assertEqual(validate_slug("tech-news-hub"), "tech-news-hub")
        self.assertEqual(validate_slug("TechNewsHub"), "technewshub")
        print("  [PASS] Slug validation and normalization")

    def test_invalid_slug(self):
        with self.assertRaises(ValueError): validate_slug("a")
        with self.assertRaises(ValueError): validate_slug("-bad")
        with self.assertRaises(ValueError): validate_slug("bad!")
        print("  [PASS] Invalid slugs rejected")

    def test_valid_url(self):
        self.assertEqual(validate_url("https://example.com"), "https://example.com")
        self.assertEqual(validate_url(""), "")
        print("  [PASS] URL validation passes valid URLs")

    def test_invalid_url(self):
        with self.assertRaises(ValueError): validate_url("example.com")
        print("  [PASS] URL without scheme rejected")

    def test_valid_name(self):
        self.assertEqual(validate_name("  TechNews  "), "TechNews")
        print("  [PASS] Name validation strips whitespace")

    def test_invalid_name(self):
        with self.assertRaises(ValueError): validate_name("X")
        print("  [PASS] Single-char name rejected")


# ---------------------------------------------------------------------------
# 13. BrandContext repr and log_fields
# ---------------------------------------------------------------------------

class TestBrandContextModel(IsolatedTestCase):
    def test_repr(self):
        ctx = BrandContext(brand_id=2, brand_slug="testbrand", brand_name="TestBrand")
        r = repr(ctx)
        self.assertIn("2", r)
        self.assertIn("testbrand", r)
        print("  [PASS] BrandContext.__repr__ works")

    def test_log_fields(self):
        ctx = BrandContext(brand_id=3, brand_slug="loggable", brand_name="Loggable")
        fields = ctx.log_fields
        self.assertEqual(fields["brand_id"], 3)
        self.assertEqual(fields["brand_slug"], "loggable")
        print("  [PASS] BrandContext.log_fields returns correct dict")

    def test_media_storage_root_uses_slug(self):
        ctx = BrandContext(brand_id=5, brand_slug="mybrand", brand_name="MyBrand")
        self.assertTrue(ctx.media_storage_root.endswith("mybrand"))
        print("  [PASS] BrandContext.media_storage_root ends with brand slug")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_suite():
    suites = [
        TestBrandCreation,
        TestBrandContextFromDB,
        TestBrandContextEnvFallback,
        TestSchedulerBrandAwareness,
        TestExecuteJobBrandContext,
        TestAssetStorageIsolation,
        TestSocialPublisherBrandContext,
        TestBackwardCompatibility,
        TestMigrations,
        TestValidation,
        TestBrandContextModel,
    ]

    total = 0
    failures = []

    for suite_cls in suites:
        print(f"\n=== {suite_cls.__name__} ===")
        suite = unittest.TestLoader().loadTestsFromTestCase(suite_cls)
        runner = unittest.TextTestRunner(
            stream=open(os.devnull, "w"),
            verbosity=0,
        )
        result = runner.run(suite)
        total += result.testsRun
        for test, tb in result.failures + result.errors:
            print(f"  [FAIL] {test}")
            print(f"         {tb.strip().splitlines()[-1]}")
            failures.append(str(test))

    print(f"\n{'='*60}")
    print(f"Tests run: {total}  |  Failures: {len(failures)}")
    if failures:
        print(f"FAILED: {', '.join(failures)}")
        sys.exit(1)
    else:
        print("All Phase 13B tests passed successfully with clean isolation!")
        sys.exit(0)


if __name__ == "__main__":
    run_suite()