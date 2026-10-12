"""Offline tests for evidence diffs, source identity, and read-only operation."""

from contextlib import closing, redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import pm_kb


class SnapshotChangesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.data_dir = Path(self.temp.name) / "kb"

    def snapshot(self, text, *, source="example", url="https://example.com/docs"):
        with closing(pm_kb.connect_db(self.data_dir / pm_kb.DB_NAME, create=True)) as conn:
            with conn:
                conn.execute(
                    "INSERT OR IGNORE INTO sources(id,title,url,topic,enabled) VALUES (?,?,?,?,1)",
                    (source, "Example", url, "research"),
                )
                cursor = conn.execute(
                    "INSERT INTO snapshots(source_id,fetched_at,url,title,content_text,"
                    "content_sha256,http_status,bytes_read) VALUES (?,?,?,?,?,?,200,?)",
                    (source, pm_kb.utc_now(), url, "Example", text,
                     hashlib.sha256(text.encode()).hexdigest(), len(text.encode())),
                )
                sid = cursor.lastrowid
                conn.execute("UPDATE sources SET latest_snapshot_id=?,url=? WHERE id=?",
                             (sid, url, source))
        return sid

    def test_missing_database_is_not_created(self):
        with self.assertRaises(pm_kb.KBError):
            pm_kb.snapshot_changes(self.data_dir, "example")
        self.assertFalse(self.data_dir.exists())

    def test_first_snapshot_and_cli_are_read_only(self):
        sid = self.snapshot("Initial content")
        path = self.data_dir / pm_kb.DB_NAME
        before = path.read_bytes()
        files = sorted(p.name for p in self.data_dir.iterdir())
        with redirect_stdout(io.StringIO()) as output:
            code = pm_kb.main(["--data-dir", str(self.data_dir), "changes", "--source", "example"])
        report = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(report["change_type"], "initial_snapshot")
        self.assertIsNone(report["baseline"])
        self.assertEqual(report["current"]["id"], sid)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(sorted(p.name for p in self.data_dir.iterdir()), files)

    def test_reordered_prices_still_require_context_review(self):
        self.snapshot("Model A\n$2\nModel B\n$5")
        self.snapshot("Model A\n$5\nModel B\n$2")
        report = pm_kb.snapshot_changes(self.data_dir, "example")
        self.assertEqual(report["change_type"], "line_order_changed")
        self.assertEqual(report["impact"], "not_assessed")
        self.assertTrue(report["diff"], "reordered lines can change table relationships")

    def test_explicit_history_and_numeric_change(self):
        first = self.snapshot("Model A\nPrice $2")
        second = self.snapshot("Model A\nPrice $3")
        self.snapshot("Model A\nPrice $4")
        report = pm_kb.snapshot_changes(self.data_dir, "example", from_snapshot=first,
                                        to_snapshot=second)
        self.assertEqual(report["change_type"], "content_changed")
        self.assertEqual(report["current"]["id"], second)
        self.assertIn("-Price $2", report["diff"])
        self.assertIn("+Price $3", report["diff"])

    def test_same_text_at_changed_url_is_flagged(self):
        self.snapshot("Same body")
        self.snapshot("Same body", url="https://example.com/replacement")
        report = pm_kb.snapshot_changes(self.data_dir, "example")
        self.assertEqual(report["change_type"], "identical")
        self.assertTrue(report["source_url_changed"])
        self.assertNotEqual(report["baseline"]["url"], report["current"]["url"])

    def test_invalid_ids_wrong_source_and_limits(self):
        first = self.snapshot("Initial")
        other = self.snapshot("Other", source="other")
        for args in ({"from_snapshot": first}, {"to_snapshot": other},
                     {"from_snapshot": other}, {"to_snapshot": -1},
                     {"to_snapshot": 999}, {"max_lines": 0}, {"max_lines": 1001}):
            with self.subTest(args=args), self.assertRaises(pm_kb.KBError):
                pm_kb.snapshot_changes(self.data_dir, "example", **args)
        with self.assertRaises(pm_kb.KBError):
            pm_kb.snapshot_changes(self.data_dir, "missing")

    def test_diff_is_bounded_and_truncation_is_explicit(self):
        self.snapshot("\n".join("old " + str(i) for i in range(50)))
        self.snapshot("\n".join("new " + str(i) for i in range(50)))
        report = pm_kb.snapshot_changes(self.data_dir, "example", max_lines=5)
        self.assertEqual(len(report["diff"]), 5)
        self.assertTrue(report["diff_truncated"])
        self.snapshot("x" * 1000)
        report = pm_kb.snapshot_changes(self.data_dir, "example", max_lines=1000)
        self.assertTrue(report["line_text_truncated"])
        self.assertTrue(all(len(line) <= 512 for line in report["diff"]))

    def test_corrupt_snapshot_is_rejected(self):
        self.snapshot("Original")
        with closing(pm_kb.connect_db(self.data_dir / pm_kb.DB_NAME, create=True)) as conn:
            with conn:
                conn.execute("UPDATE snapshots SET content_text='tampered'")
        with self.assertRaisesRegex(pm_kb.KBError, "hash mismatch"):
            pm_kb.snapshot_changes(self.data_dir, "example")


if __name__ == "__main__":
    unittest.main()
