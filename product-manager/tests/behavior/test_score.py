"""Unit tests for rating aggregation. These use synthetic human ratings, not model outputs."""

from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
from unittest.mock import patch
import tempfile
import unittest

from score import compare_runs, load_fixtures, main, score_run, skeleton


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

    def prepare_compare(self):
        baseline = deepcopy(self.ratings)
        baseline["run"]["skill_version"] = "1.1.0"
        candidate = deepcopy(self.ratings)
        baseline_path = self.base / "baseline" / "ratings.json"
        candidate_path = self.base / "candidate" / "ratings.json"
        for path, ratings in ((baseline_path, baseline), (candidate_path, candidate)):
            path.parent.mkdir(parents=True, exist_ok=True)
            for case_rating in ratings["cases"].values():
                response = path.parent / case_rating["response_file"]
                response.parent.mkdir(parents=True, exist_ok=True)
                response.write_text("Synthetic response for comparison test.", encoding="utf-8")
        return baseline_path, candidate_path, baseline, candidate

    def run_compare(self, baseline_path, candidate_path, baseline, candidate):
        baseline_path.write_text(json.dumps(baseline, ensure_ascii=False), encoding="utf-8")
        candidate_path.write_text(json.dumps(candidate, ensure_ascii=False), encoding="utf-8")
        output = io.StringIO()
        with redirect_stdout(output):
            result = compare_runs(baseline_path, candidate_path, self.cases, self.rubric)
        return result, output.getvalue()

    def test_all_full_marks_pass(self):
        self.assertEqual(self.run_score(), 0)

    def test_critical_partial_fails_even_with_high_average(self):
        self.ratings["cases"]["delivery_workbench"]["ratings"]["D1"]["score"] = 1
        self.assertEqual(self.run_score(), 1)

    def test_fixture_mismatch_rejected(self):
        self.ratings["run"]["fixture_sha256"] = "changed"
        with self.assertRaisesRegex(ValueError, "fixture hash mismatch"):
            self.run_score()

    def test_skeleton_uses_current_skill_version(self):
        self.assertEqual(self.ratings["run"]["skill_version"], "1.2.0")

    def test_compare_complete_matching_runs_pass(self):
        baseline_path, candidate_path, baseline, candidate = self.prepare_compare()
        result, output = self.run_compare(baseline_path, candidate_path, baseline, candidate)
        self.assertEqual(result, 0)
        self.assertIn("Weighted total:", output)
        self.assertIn("Per-case weighted scores:", output)
        self.assertIn("Criterion regressions:\n  none", output)
        self.assertIn("RESULT: PASS", output)

    def test_compare_cli_accepts_two_run_paths(self):
        baseline_path, candidate_path, baseline, candidate = self.prepare_compare()
        baseline_path.write_text(json.dumps(baseline), encoding="utf-8")
        candidate_path.write_text(json.dumps(candidate), encoding="utf-8")
        output = io.StringIO()
        with patch("sys.argv", ["score.py", "--compare", str(baseline_path), str(candidate_path)]):
            with redirect_stdout(output):
                result = main()
        self.assertEqual(result, 0)
        self.assertIn("RESULT: PASS", output.getvalue())

    def test_compare_requires_same_model(self):
        baseline_path, candidate_path, baseline, candidate = self.prepare_compare()
        candidate["run"]["model"] = "different-model"
        with self.assertRaisesRegex(ValueError, "model mismatch"):
            self.run_compare(baseline_path, candidate_path, baseline, candidate)

    def test_compare_requires_same_frozen_fixture(self):
        baseline_path, candidate_path, baseline, candidate = self.prepare_compare()
        candidate["run"]["fixture_sha256"] = "different-fixture"
        with self.assertRaisesRegex(ValueError, "fixture hash mismatch"):
            self.run_compare(baseline_path, candidate_path, baseline, candidate)

    def test_compare_requires_every_nonempty_response(self):
        baseline_path, candidate_path, baseline, candidate = self.prepare_compare()
        first_case = next(iter(candidate["cases"]))
        candidate["cases"][first_case]["response_file"] = "responses/does-not-exist.md"
        with self.assertRaisesRegex(ValueError, "missing/nonempty response file"):
            self.run_compare(baseline_path, candidate_path, baseline, candidate)

    def test_compare_requires_complete_ratings(self):
        baseline_path, candidate_path, baseline, candidate = self.prepare_compare()
        first_case = next(iter(candidate["cases"]))
        first_rating = next(iter(candidate["cases"][first_case]["ratings"]))
        del candidate["cases"][first_case]["ratings"][first_rating]
        with self.assertRaisesRegex(ValueError, "ratings mismatch"):
            self.run_compare(baseline_path, candidate_path, baseline, candidate)

    def test_compare_critical_drop_fails_candidate_gate(self):
        baseline_path, candidate_path, baseline, candidate = self.prepare_compare()
        candidate["cases"]["delivery_workbench"]["ratings"]["D1"]["score"] = 1
        result, output = self.run_compare(baseline_path, candidate_path, baseline, candidate)
        self.assertEqual(result, 1)
        self.assertIn("delivery_workbench/D1: 2 -> 1", output)
        self.assertIn("Candidate critical failures: delivery_workbench/D1", output)
        self.assertIn("RESULT: FAIL", output)

    def test_compare_reports_noncritical_drop_for_human_review(self):
        baseline_path, candidate_path, baseline, candidate = self.prepare_compare()
        case_id, item_id = next(
            (case_id, item["id"])
            for case_id, criteria in self.rubric["cases"].items()
            for item in criteria
            if not item["critical"]
        )
        candidate["cases"][case_id]["ratings"][item_id]["score"] = 1
        result, output = self.run_compare(baseline_path, candidate_path, baseline, candidate)
        self.assertEqual(result, 0)
        self.assertIn(f"{case_id}/{item_id}: 2 -> 1", output)
        self.assertIn("Noncritical regressions need human review", output)
        self.assertIn("REGRESSION_REVIEW: REQUIRED", output)
        self.assertIn("RELEASE_APPROVAL: REQUIRED", output)
        self.assertIn("RESULT: PASS", output)

    def test_compare_below_weighted_threshold_fails_without_critical_drop(self):
        baseline_path, candidate_path, baseline, candidate = self.prepare_compare()
        for case_id, criteria in self.rubric["cases"].items():
            for item in criteria:
                if not item["critical"]:
                    candidate["cases"][case_id]["ratings"][item["id"]]["score"] = 0
        result, output = self.run_compare(baseline_path, candidate_path, baseline, candidate)
        self.assertEqual(result, 1)
        self.assertIn("Candidate critical failures: none", output)
        self.assertIn("RESULT: FAIL", output)


if __name__ == "__main__":
    unittest.main()
