# Mode: ai-prd

AI 功能输出具有概率性，因此“规格”必须同时包含**产品行为 + Eval 合约**。

## 必需章节
1. Executive Summary
2. User / Problem / Evidence
3. Goals / Non-goals / Success Metrics
4. Experience / User Flow / Human Override：进度、不确定性、纠错、恢复与人工接管；复杂流程读取 `references/mode-experience.md`
5. AI Task Contract：输入、输出、允许行为、禁止行为、不确定性表达
6. Architecture：模型、Prompt、RAG、Tools、Memory、Fallback、被拒绝方案
7. Data：来源、权限、保留、敏感数据、引用/溯源
8. Eval & Safety：Golden Set、质量、幻觉、拒答、工具成功、安全、红队
9. Failure Modes：错误答案、工具失败、循环、超时、越权、数据泄露、不可恢复操作
10. Performance & Cost：P50/P95 延迟、单次成功任务成本、预算上限
11. Observability：Trace、模型/Prompt 版本、Badcase、Drift
12. Rollout：Shadow/Internal/Canary/Percentage/GA 与每阶段门槛

模板：`templates/ai-prd.md`。配套生成 `templates/eval-spec.md`。
