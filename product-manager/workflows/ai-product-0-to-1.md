# Workflow: AI Product 0→1

1. `assess`：先证明用户问题，不证明 AI。
2. `discover`：收集真实任务样本与失败样本。
3. `ai-architecture`：用这些样本判断是否需要 AI，以及满足门槛的最简单方案。
4. `mvp`：按上一步结论验证；不默认加入 RAG、Tools 或 Agent，只在样本暴露对应缺口时引入。
5. `ai-prd`：行为合约 + 系统设计 + Failure Modes。
6. `eval`：Golden/Edge/Adversarial/Regression。
7. `handoff`：产品 AC 与工程依赖。
8. Shadow/Internal/Canary。
9. `launch`：质量、延迟、成本、HITL 达到门槛。
10. `retro`：把线上 Badcase 固化进 Regression Set。
