"""Offline regression tests for the opt-in public-source knowledge base."""

from __future__ import annotations

from contextlib import closing, redirect_stdout
import io
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import pm_kb  # noqa: E402


HTML_A = b"<html><head><title>PM Example</title></head><body><nav>Ignore navigation</nav><main><h1>Product research</h1><p>" + b"Alpha feature has evidence and a useful decision record. " * 6 + b"</p></main></body></html>"
HTML_B = b"<html><head><title>PM Example Update</title></head><body><main><h1>Product research</h1><p>" + b"Beta feature has new evidence and an updated decision record. " * 6 + b"</p></main></body></html>"


class FakeFetcher:
    def __init__(self, body=HTML_A, *, allowed=True, status=200):
        self.body = body
        self.is_allowed = allowed
        self.status = status
        self.calls = []

    def allowed(self, url):
        self.calls.append(("robots", url))
        return self.is_allowed, 1.0

    def page(self, url, *, etag, modified, interval):
        self.calls.append(("page", url, etag, modified, interval))
        return self.status, self.body, {
            "Content-Type": "text/html; charset=utf-8",
            "ETag": '"abc"',
            "Last-Modified": "Mon, 01 Sep 2025 00:00:00 GMT",
        }


class FakeResponse:
    def __init__(self, status, body, headers=None):
        self.status = status
        self.body = body
        self.headers = headers or {}
        self.cursor = 0

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def getcode(self):
        return self.status

    def read(self, size):
        result = self.body[self.cursor:self.cursor + size]
        self.cursor += len(result)
        return result

    read1 = read


class FakeOpener:
    def __init__(self, *, robots=b"User-agent: *\nDisallow: /private\nCrawl-delay: 2\n", fail=False):
        self.robots = robots
        self.fail = fail
        self.requests = []

    def open(self, req, timeout):
        self.requests.append((req, timeout))
        if self.fail:
            raise URLError("offline test")
        if req.full_url.endswith("/robots.txt"):
            return FakeResponse(200, self.robots)
        return FakeResponse(200, HTML_A, {"Content-Type": "text/html"})


class KnowledgeBaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.data_dir = self.root / "kb"
        self.config = self.root / "sources.json"
        self.write_config("https://example.com/public")

    def write_config(self, url, *, enabled=True):
        self.config.write_text(json.dumps({
            "version": 1,
            "sources": [{
                "id": "example", "title": "Example docs", "url": url,
                "topic": "research", "enabled": enabled,
            }],
        }), encoding="utf-8")

    def test_allowlist_rejects_unsafe_urls(self):
        for url in (
            "http://example.com/page",
            "https://example.com/page?token=secret",
            "https://user:pass@example.com/page",
            "https://127.0.0.1/page",
            "https://localhost/page",
            "https://example.com:8443/page",
        ):
            with self.subTest(url=url):
                self.write_config(url)
                with self.assertRaises(pm_kb.KBError):
                    pm_kb.load_sources(self.config)
        self.write_config("https://example.com/public")
        self.assertEqual(len(pm_kb.load_sources(self.config)), 1)

    def test_existing_unrelated_database_is_not_modified(self):
        self.data_dir.mkdir()
        db_path = self.data_dir / pm_kb.DB_NAME
        with closing(sqlite3.connect(db_path)) as conn:
            conn.execute("CREATE TABLE unrelated(value TEXT)")
            conn.commit()
        with self.assertRaises(pm_kb.KBError):
            pm_kb.sync_sources(self.data_dir, self.config, fetcher=FakeFetcher())
        with closing(sqlite3.connect(db_path)) as conn:
            tables = {row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertEqual(tables, {"unrelated"})

    def test_robots_disallow_and_network_failure_fail_closed(self):
        opener = FakeOpener()
        fetcher = pm_kb.Fetcher(opener=opener, clock=lambda: 100.0, sleeper=lambda _: None,
                                resolver=lambda _: ["8.8.8.8"])
        self.assertEqual(fetcher.allowed("https://example.com/private"), (False, 2.0))
        self.assertEqual(fetcher.allowed("https://example.com/public"), (True, 2.0))
        self.assertEqual(len(opener.requests), 1, "robots.txt should be cached per origin")
        failing = pm_kb.Fetcher(opener=FakeOpener(fail=True), clock=lambda: 100.0,
                                sleeper=lambda _: None, resolver=lambda _: ["8.8.8.8"])
        with self.assertRaises(pm_kb.KBError):
            failing.allowed("https://example.com/public")
        private_opener = FakeOpener()
        private = pm_kb.Fetcher(opener=private_opener, resolver=lambda _: ["10.0.0.8"])
        with self.assertRaises(pm_kb.KBError):
            private.allowed("https://example.com/public")
        self.assertEqual(private_opener.requests, [], "private DNS must be blocked before network I/O")
        mixed = pm_kb.Fetcher(opener=private_opener,
                              resolver=lambda _: ["8.8.8.8", "127.0.0.1"])
        with self.assertRaises(pm_kb.KBError):
            mixed.allowed("https://example.com/public")
        dns_fail = pm_kb.Fetcher(opener=private_opener,
                                 resolver=lambda _: (_ for _ in ()).throw(OSError()))
        with self.assertRaises(pm_kb.KBError):
            dns_fail.allowed("https://example.com/public")

    def test_fetcher_sends_conditional_headers_and_limits_bytes(self):
        opener = FakeOpener()
        fetcher = pm_kb.Fetcher(opener=opener, clock=lambda: 100.0, sleeper=lambda _: None,
                                resolver=lambda _: ["8.8.8.8"])
        allowed, interval = fetcher.allowed("https://example.com/public")
        self.assertTrue(allowed)
        fetcher.page("https://example.com/public", etag='"abc"',
                     modified="Mon, 01 Sep 2025 00:00:00 GMT", interval=interval)
        request_headers = dict(opener.requests[-1][0].header_items())
        self.assertEqual(request_headers["If-none-match"], '"abc"')
        self.assertIn("If-modified-since", request_headers)
        large_opener = FakeOpener(robots=b"a" * (pm_kb.MAX_ROBOTS_BYTES + 1))
        large = pm_kb.Fetcher(opener=large_opener, clock=lambda: 100.0,
                              sleeper=lambda _: None, resolver=lambda _: ["8.8.8.8"])
        with self.assertRaises(pm_kb.KBError):
            large.allowed("https://example.com/public")
        with self.assertRaises(pm_kb.KBError):
            pm_kb.NoRedirectHandler().redirect_request(None, None, 301, "Moved", {},
                                                        "https://other.example/page")

    def test_versioned_sync_search_status_and_conditional_get(self):
        first = FakeFetcher()
        report = pm_kb.sync_sources(self.data_dir, self.config, fetcher=first)
        self.assertEqual(report["results"][0]["status"], "new")
        self.assertEqual(pm_kb.status_report(self.data_dir)["snapshots"], 1)
        self.assertEqual(pm_kb.search_db(self.data_dir, "Alpha feature", limit=5)["count"], 1)
        self.assertEqual(pm_kb.search_db(self.data_dir, "Ignore navigation", limit=5)["count"], 0)

        unchanged = FakeFetcher()
        report = pm_kb.sync_sources(self.data_dir, self.config, fetcher=unchanged)
        self.assertEqual(report["results"][0]["status"], "unchanged")
        self.assertEqual(unchanged.calls[-1][2], '"abc"')
        self.assertEqual(pm_kb.status_report(self.data_dir)["snapshots"], 1)

        changed = FakeFetcher(HTML_B)
        report = pm_kb.sync_sources(self.data_dir, self.config, fetcher=changed)
        self.assertEqual(report["results"][0]["status"], "new")
        self.assertEqual(pm_kb.status_report(self.data_dir)["snapshots"], 2)
        self.assertEqual(pm_kb.search_db(self.data_dir, "Beta feature", limit=5)["count"], 1)

        not_modified = FakeFetcher(status=304)
        report = pm_kb.sync_sources(self.data_dir, self.config, fetcher=not_modified)
        self.assertEqual(report["results"][0]["status"], "not_modified")
        self.assertEqual(pm_kb.status_report(self.data_dir)["snapshots"], 2)

    def test_failure_keeps_last_good_snapshot_and_has_nonzero_exit(self):
        pm_kb.sync_sources(self.data_dir, self.config, fetcher=FakeFetcher())
        report = pm_kb.sync_sources(self.data_dir, self.config,
                                    fetcher=FakeFetcher(allowed=False))
        self.assertEqual(report["status"], "partial_failure")
        self.assertEqual(report["failed"], 1)
        status = pm_kb.status_report(self.data_dir)
        self.assertEqual(status["snapshots"], 1)
        self.assertEqual(status["sources"][0]["last_status"], "error")
        with redirect_stdout(io.StringIO()) as output:
            code = pm_kb.main(["--data-dir", str(self.data_dir), "--sources-file",
                               str(self.config), "sync", "--source", "missing"])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue())["status"], "error")

    def test_cli_mutating_command_refuses_concurrent_writer(self):
        pm_kb.sync_sources(self.data_dir, self.config, fetcher=FakeFetcher())
        with pm_kb.mutation_lock(self.data_dir):
            with redirect_stdout(io.StringIO()) as output:
                code = pm_kb.main(["--data-dir", str(self.data_dir), "backup"])
            self.assertEqual(code, 2)
            self.assertIn("busy", json.loads(output.getvalue())["error"])
            with redirect_stdout(io.StringIO()) as output:
                status_code = pm_kb.main(["--data-dir", str(self.data_dir), "status"])
            self.assertEqual(status_code, 0)

    def test_backup_verify_restore_and_pre_restore_safety_backup(self):
        pm_kb.sync_sources(self.data_dir, self.config, fetcher=FakeFetcher())
        original = pm_kb.create_backup(self.data_dir)
        self.assertTrue(original.exists())
        self.assertEqual(pm_kb.verify_backup(original)["snapshots"], 1)
        storage = pm_kb.status_report(self.data_dir)["storage"]
        self.assertEqual(storage["backup_count"], 1)
        self.assertGreater(storage["backup_bytes"], 0)
        with patch.object(pm_kb, "BACKUP_WARNING_BYTES", 1):
            self.assertTrue(pm_kb.status_report(self.data_dir)["storage"]["backup_size_warning"])
        pm_kb.sync_sources(self.data_dir, self.config, fetcher=FakeFetcher(HTML_B))
        with self.assertRaises(pm_kb.KBError):
            pm_kb.restore_backup(self.data_dir, original, force=False)
        with closing(sqlite3.connect(self.data_dir / pm_kb.DB_NAME)) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
        restored = pm_kb.restore_backup(self.data_dir, original, force=True)
        self.assertEqual(pm_kb.status_report(self.data_dir)["snapshots"], 1)
        safety = Path(restored["pre_restore_backup"])
        self.assertTrue(safety.exists())
        self.assertEqual(pm_kb.verify_backup(safety)["snapshots"], 2)
        sidecar = Path(f"{original}.sha256")
        saved_sidecar = sidecar.read_text(encoding="ascii")
        sidecar.unlink()
        with self.assertRaises(pm_kb.KBError):
            pm_kb.verify_backup(original)
        sidecar.write_text("0" * 64 + "  backup.sqlite3\n", encoding="ascii")
        with self.assertRaises(pm_kb.KBError):
            pm_kb.verify_backup(original)
        sidecar.write_text(saved_sidecar, encoding="ascii")
        with original.open("ab") as stream:
            stream.write(b"tampered")
        with self.assertRaises(pm_kb.KBError):
            pm_kb.verify_backup(original)

    def test_corrupt_live_database_restores_with_raw_quarantine(self):
        pm_kb.sync_sources(self.data_dir, self.config, fetcher=FakeFetcher())
        valid_backup = pm_kb.create_backup(self.data_dir)
        live = self.data_dir / pm_kb.DB_NAME
        live.write_bytes(b"damaged active database")
        wal = self.data_dir / f"{pm_kb.DB_NAME}-wal"
        shm = self.data_dir / f"{pm_kb.DB_NAME}-shm"
        wal.write_bytes(b"old wal companion")
        shm.write_bytes(b"old shm companion")
        restored = pm_kb.restore_backup(self.data_dir, valid_backup, force=True)
        self.assertIsNone(restored["pre_restore_backup"])
        self.assertFalse(restored["raw_original_verified"])
        quarantine = Path(restored["raw_original_quarantine"])
        self.assertEqual((quarantine / pm_kb.DB_NAME).read_bytes(), b"damaged active database")
        self.assertEqual((quarantine / wal.name).read_bytes(), b"old wal companion")
        self.assertEqual((quarantine / shm.name).read_bytes(), b"old shm companion")
        self.assertEqual(pm_kb.verify_database(live)["snapshots"], 1)
        storage = pm_kb.status_report(self.data_dir)["storage"]
        self.assertEqual(storage["quarantine_count"], 1)
        self.assertGreater(storage["quarantine_bytes"], 0)

    def test_url_change_keeps_history_and_resets_conditional_headers(self):
        pm_kb.sync_sources(self.data_dir, self.config, fetcher=FakeFetcher())
        self.write_config("https://example.com/other")
        blocked = pm_kb.sync_sources(self.data_dir, self.config,
                                     fetcher=FakeFetcher(allowed=False))
        self.assertEqual(blocked["failed"], 1)
        old_result = pm_kb.search_db(self.data_dir, "Alpha feature", limit=5)
        self.assertEqual(old_result["results"][0]["url"], "https://example.com/public")
        self.assertEqual(pm_kb.status_report(self.data_dir)["sources"][0]["snapshot_url"],
                         "https://example.com/public")
        invalid_304 = pm_kb.sync_sources(self.data_dir, self.config,
                                         fetcher=FakeFetcher(status=304))
        self.assertEqual(invalid_304["failed"], 1)
        changed = FakeFetcher()
        report = pm_kb.sync_sources(self.data_dir, self.config, fetcher=changed)
        self.assertEqual(report["results"][0]["status"], "new")
        self.assertIsNone(changed.calls[-1][2])
        self.assertEqual(pm_kb.status_report(self.data_dir)["snapshots"], 2)

    def test_full_sync_retires_removed_source_without_deleting_history(self):
        pm_kb.sync_sources(self.data_dir, self.config, fetcher=FakeFetcher())
        self.config.write_text(json.dumps({
            "version": 1,
            "sources": [{"id": "replacement", "title": "Replacement", "topic": "research",
                         "url": "https://example.com/replacement", "enabled": True}],
        }), encoding="utf-8")
        pm_kb.sync_sources(self.data_dir, self.config, fetcher=FakeFetcher())
        report = pm_kb.status_report(self.data_dir)
        old = next(source for source in report["sources"] if source["id"] == "example")
        self.assertEqual(old["enabled"], 0)
        self.assertEqual(old["last_status"], "retired")
        self.assertEqual(old["versions"], 1)


if __name__ == "__main__":
    unittest.main()
