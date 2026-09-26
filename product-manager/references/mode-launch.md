# Mode: launch

上线不是“代码部署完成”。产品侧至少检查：
- Acceptance Criteria 全部通过
- 埋点与 Dashboard 可用
- Feature Flag / Kill Switch
- Rollback / Fallback
- 权限与数据策略
- Support / FAQ / Owner
- 关键依赖和配额
- 监控与告警
- AI：Eval Gate、Prompt/Model 版本、成本预算、HITL、Badcase 回收

优先渐进放量：内部 → 小流量 → 扩大 → GA。每一步写进入/退出门槛。
模板：`templates/launch-checklist.md`。
