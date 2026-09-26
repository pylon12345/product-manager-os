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
            "skill_version": "1.0.0",
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


def score_run(ratings_path, cases, rubric):
    run = json.loads(ratings_path.read_text(encoding="utf-8"))
    metadata = run.get("run", {})
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
    case_lines = []
    for case in cases["cases"]:
        case_id = case["id"]
        entry = observed_cases[case_id]
        response_path = Path(entry.get("response_file", ""))
        if not response_path.is_absolute():
            response_path = ratings_path.parent / response_path
        if not response_path.is_file() or not response_path.read_text(encoding="utf-8").strip():
            raise ValueError(f"missing/nonempty response file: {case_id}")
        ratings = entry.get("ratings")
        criteria = rubric["cases"][case_id]
        if not isinstance(ratings, dict) or set(ratings) != {item["id"] for item in criteria}:
            raise ValueError(f"ratings mismatch: {case_id}")
        case_earned = case_possible = 0
        for item in criteria:
            item_id = item["id"]
            mark = ratings[item_id]
            value = mark.get("score")
            if type(value) is not int or value not in (0, 1, 2):
                raise ValueError(f"score must be 0, 1, or 2: {case_id}/{item_id}")
            if not isinstance(mark.get("evidence"), str) or not mark["evidence"].strip():
                raise ValueError(f"human evidence note required: {case_id}/{item_id}")
            case_earned += value * item["weight"]
            case_possible += 2 * item["weight"]
            if item["critical"] and value != 2:
                critical_failures.append(f"{case_id}/{item_id}")
        earned += case_earned
        possible += case_possible
        case_lines.append(f"{case_id}: {case_earned}/{case_possible}")
    fraction = earned / possible
    passed = fraction >= rubric["pass_fraction"] and not critical_failures
    print(f"Run: {metadata['skill_version']} | {metadata['model']} | {metadata['date']}")
    print(f"Fixture SHA-256: {fixture_hash()}")
    print("\n".join(case_lines))
    print(f"Weighted total: {earned}/{possible} = {fraction:.1%}; gate: {rubric['pass_fraction']:.0%}")
    print("Critical failures: " + (", ".join(critical_failures) if critical_failures else "none"))
    print("RESULT: " + ("PASS" if passed else "FAIL"))
    print("Human ratings are evidence-based judgments; this script does not execute or evaluate the model.")
    return 0 if passed else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="validate frozen fixtures only")
    group.add_argument("--prompt", metavar="CASE_ID", help="print one blind-run prompt")
    group.add_argument("--skeleton", action="store_true", help="print a blank human-rating form")
    group.add_argument("--score", type=Path, metavar="RATINGS_JSON", help="aggregate a complete human-rated run")
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
        else:
            return score_run(args.score.resolve(), cases, rubric)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
