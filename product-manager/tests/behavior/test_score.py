"""Unit tests for rating aggregation. These use synthetic human ratings, not model outputs."""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

from score import load_fixtures, score_run, skeleton


class ScoreRunTests(unittest.TestCase):
    def setUp(self):
        self.cases, self.rubric = load_fixtures()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.ratings = skeleton(self.cases, self.rubric)
        self.ratings["run"].update(
            {"model": "synthetic-test", "date": "2026-09-26", "evaluator": "unit-test"}
        )
        for case_id, case_rating in self.ratings["cases"].items():
            response = self.base / case_rating["response_file"]
            response.parent.mkdir(parents=True, exist_ok=True)
            response.write_text("Synthetic response for aggregation test.", encoding="utf-8")
            for mark in case_rating["ratings"].values():
                mark.update({"score": 2, "evidence": "Synthetic human note."})
        self.ratings_path = self.base / "ratings.json"

    def run_score(self):
        self.ratings_path.write_text(
            json.dumps(self.ratings, ensure_ascii=False), encoding="utf-8"
        )
        with redirect_stdout(io.StringIO()):
            return score_run(self.ratings_path, self.cases, self.rubric)

    def test_all_full_marks_pass(self):
        self.assertEqual(self.run_score(), 0)

    def test_critical_partial_fails_even_with_high_average(self):
        self.ratings["cases"]["delivery_workbench"]["ratings"]["D1"]["score"] = 1
        self.assertEqual(self.run_score(), 1)

    def test_fixture_mismatch_rejected(self):
        self.ratings["run"]["fixture_sha256"] = "changed"
        with self.assertRaisesRegex(ValueError, "fixture hash mismatch"):
            self.run_score()


if __name__ == "__main__":
    unittest.main()
