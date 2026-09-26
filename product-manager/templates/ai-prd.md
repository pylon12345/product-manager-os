# AI Feature PRD

## 1. Executive Summary
- Problem:
- User:
- Proposed behavior:
- Why AI:

## 2. Evidence / Assumptions
### [事实]
-
### [假设]
-
### [待验证]
-

## 3. Goals / Non-goals / Metrics
- Goal:
- Non-goals:
- Product metrics:
- AI quality metrics:
- Guardrails:

## 4. UX / User Flow / Human Override
- 用户如何知道 AI 当前状态、来源与不确定性：
- 如何纠错、撤销、重试、恢复或转人工：
- 自动执行外部动作前如何确认：
-

## 5. AI Task Contract
- Input:
- Expected output:
- Allowed behavior:
- Prohibited behavior:
- Uncertainty / refusal behavior:
- Done definition:

## 6. Architecture Decision
- Rules / Workflow:
- LLM:
- Structured output:
- RAG:
- Tools / MCP:
- Agent:
- Memory / State:
- Primary model / fallback strategy:
- Rejected alternatives and why:

## 7. Data / Privacy / Provenance
- Knowledge sources:
- Permissions:
- Retention:
- Sensitive data:
- Citation / traceability:

## 8. Eval & Safety
- Golden set:
- Edge cases:
- Adversarial set:
- Acceptance threshold:
- Hallucination / refusal:
- Guardrails:
- HITL:

## 9. Failure Modes
| Failure | Severity | Detection | Fallback | Owner |
|---|---|---|---|---|

## 10. Performance & Cost
- P50/P95 latency:
- Cost per successful task:
- Max budget / task:
- Max agent steps / timeout:

## 11. Observability
- Trace:
- Model version:
- Prompt version:
- Retrieval/tool logs:
- Badcase collection:
- Drift / regression:

## 12. Rollout
- Shadow:
- Internal:
- Canary:
- Percentage rollout:
- GA gate:
- Kill switch / rollback:
