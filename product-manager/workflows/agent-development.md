# Workflow: Agent Development

1. 证明固定 Workflow 不足。
2. 定义 Goal / Done Definition。
3. 明确 Planner 与可预定义步骤的边界。
4. Tools 最小权限；危险操作加确认。
5. Memory / State / Idempotency。
6. Max Steps / Timeout / Token/Cost Budget。
7. HITL / Fallback / Stop Condition。
8. Trace 每一步 reasoning outcome、tool call、error（不要存不必要的敏感信息）。
9. Eval：Task Success、Tool Success、Loop/Timeout、错误动作、安全、Cost per Successful Task。
10. 从单任务、少工具、低权限开始灰度。
