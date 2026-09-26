# AI Eval Spec

> 先定义用户任务与上线决定，再选择指标。空白字段表示待确定，不是已通过的门槛。

## Decision and task

- Product / feature / owner:
- Decision this Eval supports (ship, hold, route, rollback, or investigate):
- Target users and task context:
- Task success (observable outcome, not merely model accuracy):
- Critical failures and affected users:
- Baseline and current evidence (source, date, version):

## Dataset and provenance

| Slice | Purpose and inclusion rule | Source / consent / privacy treatment | Size / coverage | Refresh or retirement trigger |
|---|---|---|---:|---|
| Golden | Representative core tasks | | | |
| Edge | Rare but consequential cases | | | |
| Adversarial | Abuse, prompt injection, unsafe or unauthorized actions | | | |
| Regression | Previously observed failures | | | |

- Split / leakage control (including train–test overlap):
- Known coverage gaps and sampling bias:
- Who may inspect raw examples and how long they are retained:

## Eval tree and release gates

| Level | Metric and calculation | Slice | Baseline | Target / minimum gate | Frequency | Action if failed |
|---|---|---|---:|---:|---|---|
| Output / component | | | | | | |
| User task | | | | | | |
| Product | | | | | | |
| Business / cost | | | | | | |

Do not average away critical-slice failures. State which gates are hard blockers and which require investigation.

## Scoring and calibration

| Dimension | Deterministic, reference, human, or LLM judge | Rubric anchors / examples | Human calibration or agreement | Limitations |
|---|---|---|---|---|
| | | | | |

- Human review sample and adjudication owner:
- If using an LLM judge: calibration against human labels, disagreement review, and prompt/model version:
- How false positives and false negatives will be inspected:

## Versioned run and monitoring

- Dataset version / evaluation date / evaluator:
- Model, prompt, retrieval, tools, and policy versions:
- Offline result and confidence/uncertainty:
- Online monitoring: task success, critical failures, latency, cost per successful task, drift:
- Rollback / human fallback trigger and owner:
- Next review date or evidence trigger:
