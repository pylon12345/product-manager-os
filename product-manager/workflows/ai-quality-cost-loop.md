# Workflow: AI Quality And Cost Loop

1. 从用户任务定义成功，不先从模型指标开始。
2. 建立 Eval tree 和 Golden / Edge / Adversarial / Regression sets。
3. 分解 Trace，把失败归因到 Retrieval、Reasoning、Tool、Policy 或 UX。
4. 计算 p50/p95 Cost per Successful Task 与 Heavy-user cohort。
5. 按“无价值工作 → 失败/重试 → Context/Cache → Routing → Model mix”顺序优化。
6. 每次变化同时比较 Quality、Critical slices、Latency、Safety、Cost。
7. Shadow / Replay 后小流量灰度，定义回滚阈值。
8. 线上 Badcase 经隐私审查后进入 Regression Set。
9. 定期复查价格/套餐是否仍覆盖目标毛利。
