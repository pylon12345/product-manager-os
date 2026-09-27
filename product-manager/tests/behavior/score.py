#!/usr/bin/env python3
"""Aggregate human ratings for frozen PM Skill cases; this does not run or judge a model."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
CASES_PATH = BASE / "cases.json"
RUBRIC_PATH = BASE / "rubric.json"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def load_fixtures():
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    rubric = json.loads(RUBRIC_PATH.read_text(encoding="utf-8"))
    case_list = cases.get("cases")
    criteria_by_case = rubric.get("cases")
    if not isinstance(case_list, list) or not isinstance(criteria_by_case, dict):
        raise ValueError("fixtures need cases list and rubric cases object")
    ids = [case.get("id") for case in case_list]
    if len(ids) != len(set(ids)) or set(ids) != set(criteria_by_case):
        raise ValueError("case IDs must be unique and match rubric IDs")
    if not ids:
        raise ValueError("no cases")
    for case in case_list:
        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            raise ValueError(f"empty prompt: {case.get('id')}")
        criteria = criteria_by_case[case["id"]]
        if not isinstance(criteria, list) or not criteria:
            raise ValueError(f"empty rubric: {case['id']}")
        criterion_ids = [item.get("id") for item in criteria]
        if len(criterion_ids) != len(set(criterion_ids)):
            raise ValueError(f"duplicate criterion ID: {case['id']}")
        for item in criteria:
            if not item.get("observable") or type(item.get("weight")) is not int or item["weight"] < 1:
                raise ValueError(f"invalid observable or weight: {case['id']}/{item.get('id')}")
            if type(item.get("critical")) is not bool:
                raise ValueError(f"invalid critical flag: {case['id']}/{item.get('id')}")
    threshold = rubric.get("pass_fraction")
    if not isinstance(threshold, (int, float)) or not 0 < threshold <= 1:
        raise ValueError("pass_fraction must be in (0, 1]")
    return cases, rubric


def fixture_hash():
    payload = CASES_PATH.read_bytes() + b"\n" + RUBRIC_PATH.read_bytes()
    return hashlib.sha256(payload).hexdigest()


def skeleton(cases, rubric):
    return {
        "run": {
            "skill_version": "1.2.0",
            "model": "FILL_ME",
            "date": "YYYY-MM-DD",
            "evaluator": "FILL_ME",
            "fixture_sha256": fixture_hash(),
        },
        "cases": {
            case["id"]: {
                "response_file": "responses/" + case["id"] + ".md",
                "ratings": {
                    item["id"]: {"score": None, "evidence": ""}
                    for item in rubric["cases"][case["id"]]
                },
            }
            for case in cases["cases"]
        },
    }


def evaluate_run(ratings_path, cases, rubric):
    """Validate one complete human-rated run and return its deterministic totals."""
    run = json.loads(ratings_path.read_text(encoding="utf-8"))
    if not isinstance(run, dict):
        raise ValueError("ratings run must be an object")
    metadata = run.get("run", {})
    if not isinstance(metadata, dict):
        raise ValueError("run metadata must be an object")
    if metadata.get("fixture_sha256") != fixture_hash():
        raise ValueError("fixture hash mismatch: rerun against the exact frozen cases/rubric")
    for field in ("skill_version", "model", "date", "evaluator"):
        value = metadata.get(field)
        if not isinstance(value, str) or not value.strip() or value == "FILL_ME" or value == "YYYY-MM-DD":
            raise ValueError(f"missing run metadata: {field}")
    observed_cases = run.get("cases")
    expected_ids = {case["id"] for case in cases["cases"]}
    if not isinstance(observed_cases, dict) or set(observed_cases) != expected_ids:
        raise ValueError("ratings must cover every case exactly once")
    earned = possible = 0
    critical_failures = []
    case_results = {}
    for case in cases["cases"]:
        case_id = case["id"]
        entry = observed_cases[case_id]
        if not isinstance(entry, dict):
            raise ValueError(f"invalid case entry: {case_id}")
        response_file = entry.get("response_file")
        if not isinstance(response_file, str) or not response_file.strip():
            raise ValueError(f"missing response file: {case_id}")
        response_path = Path(response_file)
        if not response_path.is_absolute():
            response_path = ratings_path.parent / response_path
        if not response_path.is_file() or not response_path.read_text(encoding="utf-8").strip():
            raise ValueError(f"missing/nonempty response file: {case_id}")
        ratings = entry.get("ratings")
        criteria = rubric["cases"][case_id]
        if not isinstance(ratings, dict) or set(ratings) != {item["id"] for item in criteria}:
            raise ValueError(f"ratings mismatch: {case_id}")
        case_earned = case_possible = 0
        criterion_scores = {}
        for item in criteria:
            item_id = item["id"]
            mark = ratings[item_id]
            if not isinstance(mark, dict):
                raise ValueError(f"invalid rating: {case_id}/{item_id}")
            value = mark.get("score")
            if type(value) is not int or value not in (0, 1, 2):
                raise ValueError(f"score must be 0, 1, or 2: {case_id}/{item_id}")
            if not isinstance(mark.get("evidence"), str) or not mark["evidence"].strip():
                raise ValueError(f"human evidence note required: {case_id}/{item_id}")
            case_earned += value * item["weight"]
            case_possible += 2 * item["weight"]
            criterion_scores[item_id] = value
            if item["critical"] and value != 2:
                critical_failures.append(f"{case_id}/{item_id}")
        earned += case_earned
        possible += case_possible
        case_results[case_id] = {
            "earned": case_earned,
            "possible": case_possible,
            "criteria": criterion_scores,
        }
    fraction = earned / possible
    passed = fraction >= rubric["pass_fraction"] and not critical_failures
    return {
        "metadata": metadata,
        "earned": earned,
        "possible": possible,
        "fraction": fraction,
        "critical_failures": critical_failures,
        "passed": passed,
        "cases": case_results,
    }


def score_run(ratings_path, cases, rubric):
    result = evaluate_run(ratings_path, cases, rubric)
    metadata = result["metadata"]
    print(f"Run: {metadata['skill_version']} | {metadata['model']} | {metadata['date']}")
    print(f"Fixture SHA-256: {fixture_hash()}")
    print("\n".join(
        f"{case_id}: {case_result['earned']}/{case_result['possible']}"
        for case_id, case_result in result["cases"].items()
    ))
    print(
        f"Weighted total: {result['earned']}/{result['possible']} = "
        f"{result['fraction']:.1%}; gate: {rubric['pass_fraction']:.0%}"
    )
    print("Critical failures: " + (
        ", ".join(result["critical_failures"]) if result["critical_failures"] else "none"
    ))
    print("RESULT: " + ("PASS" if result["passed"] else "FAIL"))
    print("Human ratings are evidence-based judgments; this script does not execute or evaluate the model.")
    return 0 if result["passed"] else 1


def compare_runs(baseline_path, candidate_path, cases, rubric):
    """Compare two complete human-rated runs of the same model and frozen fixture."""
    baseline = evaluate_run(baseline_path, cases, rubric)
    candidate = evaluate_run(candidate_path, cases, rubric)
    baseline_meta = baseline["metadata"]
    candidate_meta = candidate["metadata"]
    if baseline_meta["fixture_sha256"] != candidate_meta["fixture_sha256"]:
        raise ValueError("fixture hash mismatch between runs")
    if baseline_meta["model"] != candidate_meta["model"]:
        raise ValueError("model mismatch between runs: use the same model for comparison")

    print(
        f"Baseline: {baseline_meta['skill_version']} | {baseline_meta['model']} | "
        f"{baseline_meta['date']}"
    )
    print(
        f"Candidate: {candidate_meta['skill_version']} | {candidate_meta['model']} | "
        f"{candidate_meta['date']}"
    )
    print(f"Fixture SHA-256: {baseline_meta['fixture_sha256']}")
    print(
        f"Weighted total: {baseline['earned']}/{baseline['possible']} "
        f"({baseline['fraction']:.1%}) -> {candidate['earned']}/{candidate['possible']} "
        f"({candidate['fraction']:.1%}); delta {candidate['earned'] - baseline['earned']:+d}; "
        f"gate: {rubric['pass_fraction']:.0%}"
    )
    print("Per-case weighted scores:")
    regressions = []
    noncritical_regressions = False
    for case in cases["cases"]:
        case_id = case["id"]
        old = baseline["cases"][case_id]
        new = candidate["cases"][case_id]
        print(
            f"  {case_id}: {old['earned']}/{old['possible']} -> "
            f"{new['earned']}/{new['possible']} ({new['earned'] - old['earned']:+d})"
        )
        for criterion in rubric["cases"][case_id]:
            item_id = criterion["id"]
            old_score = old["criteria"][item_id]
            new_score = new["criteria"][item_id]
            if new_score < old_score:
                noncritical_regressions |= not criterion["critical"]
                regressions.append(
                    f"  {case_id}/{item_id}: {old_score} -> {new_score} "
                    f"(weighted {(new_score - old_score) * criterion['weight']:+d}; "
                    f"{'critical' if criterion['critical'] else 'noncritical'})"
                )
    print("Criterion regressions:")
    print("\n".join(regressions) if regressions else "  none")
    print("Candidate critical failures: " + (
        ", ".join(candidate["critical_failures"]) if candidate["critical_failures"] else "none"
    ))
    print("REGRESSION_REVIEW: " + ("REQUIRED" if regressions else "NONE"))
    if noncritical_regressions:
        print("Noncritical regressions need human review; this comparison does not approve release.")
    print("SCORING_GATE: " + ("PASS" if candidate["passed"] else "FAIL"))
    print("RELEASE_APPROVAL: REQUIRED; scoring success is not publication approval.")
    print("RESULT: " + ("PASS" if candidate["passed"] else "FAIL") + " (scoring gate only)")
    print("Human ratings are evidence-based judgments; this script does not execute or evaluate the model.")
    return 0 if candidate["passed"] else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="validate frozen fixtures only")
    group.add_argument("--prompt", metavar="CASE_ID", help="print one blind-run prompt")
    group.add_argument("--skeleton", action="store_true", help="print a blank human-rating form")
    group.add_argument("--score", type=Path, metavar="RATINGS_JSON", help="aggregate a complete human-rated run")
    group.add_argument(
        "--compare", nargs=2, type=Path, metavar=("BASELINE", "CANDIDATE"),
        help="compare complete human-rated runs using the same model and fixture",
    )
    args = parser.parse_args()
    try:
        cases, rubric = load_fixtures()
        if args.check:
            print(f"OK: {len(cases['cases'])} cases, fixture SHA-256 {fixture_hash()}")
            print("Fixture validation only; no model was run or graded.")
        elif args.prompt:
            case = next((item for item in cases["cases"] if item["id"] == args.prompt), None)
            if case is None:
                raise ValueError(f"unknown case: {args.prompt}")
            print(case["prompt"])
        elif args.skeleton:
            print(json.dumps(skeleton(cases, rubric), ensure_ascii=False, indent=2))
        elif args.compare:
            return compare_runs(*(path.resolve() for path in args.compare), cases, rubric)
        else:
            return score_run(args.score.resolve(), cases, rubric)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
