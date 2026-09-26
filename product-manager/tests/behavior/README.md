# Behavior regression kit

This is a **reproducible evaluation protocol**, not a claim that the Skill has passed a model test. `validate.py` and `score.py --check` check files and fixture integrity only. `score.py --score` aggregates **human** ratings; it cannot decide whether a response is good.

## Run a blind forward test

1. Pin the Skill version, model, date, and fixture hash. Start a fresh, isolated task for each case. Give the evaluator only the Skill and the output of `python tests/behavior/score.py --prompt CASE_ID`; do **not** reveal `rubric.json`, suspected failures, or earlier answers. No production writes, customer contact, pricing changes, or live data exports.
2. Save each raw response under a temporary `responses/CASE_ID.md` directory outside the Skill package. Keep the response unedited. Record unavailable tools or blocked browsing rather than filling gaps.
3. Inspect `rubric.json`. For every observable criterion, assign 0 (wrong/absent), 1 (partial), or 2 (clearly met) and a short evidence note pointing to the response. For consequential cases, use a second reviewer and adjudicate disagreements.
4. Run `python tests/behavior/score.py --skeleton` to obtain the ratings form. Place a filled copy beside `responses/`, then run `python tests/behavior/score.py --score PATH_TO_RATINGS.json`. The tool reads responses and ratings but writes nothing. It fails if a critical criterion is not 2 or the weighted score is below 80%.

`python tests/behavior/score.py --check` validates seven frozen prompts and their rubric. The printed SHA-256 changes when either file changes; preserve old fixtures when comparing versions instead of quietly editing the test. The initial suite covers cross-version delivery, pricing, AI Eval, AI economics, stale sources and prompt injection, authorization boundaries, and post-launch decision continuity.

A passing score is only evidence for these cases on this model/run, not general reliability. Add real bad cases after a user-visible failure, review whether the rubric still measures the intended decision, and compare the same frozen inputs before and after Skill changes. Avoid scoring by keyword presence or document headings; inspect the actual recommendation, evidence handling, and authorized actions.
