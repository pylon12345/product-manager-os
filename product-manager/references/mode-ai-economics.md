# Mode: ai-economics

目标：用 `Cost per Successful Task` 和贡献毛利管理 AI 产品，不以单次 Token 价格替代单位经济。

## 1. Cost Stack

按成功任务归集：Input/Cache/Output/Modal inference、Embedding、Retrieval、Rerank、Storage、Tool/API、Moderation、Retry/Fallback、失败工作流、Human review、Support、Observability。共享成本必须说明分摊方法。

同时报告 p50、p95 和 Heavy-user cohort。平均值不能掩盖重尾和异常循环。

## 2. Unit Economics

- Cost per request / successful task
- Cost per active user/account
- Contribution margin by plan/segment/workload
- Revenue or user value per constrained resource
- Failure cost、Retry amplification、Human review burden
- Gross margin after AI serving cost

## 3. Driver Forecast

`Users × Active rate × Tasks × Steps × Tokens/Tools × Unit cost`

至少建立 Base、High usage、Quality degradation、Vendor price/model mix 变化场景。加入季节性、并发、滥用、重试和缓存命中假设。预算按产品域或客户层级设置，并同时监控 Spend 与 Efficiency。

## 4. Optimization Ladder

1. 删除不创造用户价值的调用或步骤。
2. 降低失败、重试和无效 Agent 循环。
3. 优化 Context selection、Caching、Batching、Output bounds。
4. 简单任务路由小模型，高不确定/高风险任务升级。
5. 优化 Retrieval、Prompt、Tool 和 Model mix。
6. 理解工作负载后再谈供应商议价或切换。

每项节省都必须通过 Quality、Latency、Reliability、Safety 和 Engineering complexity 护栏。

## 5. Routing 与 Guardrails

路由依据 Task type、Uncertainty、Risk、Latency、Context、Modality、Customer tier。定义升级与回退条件，以及：

- Per-request token/tool/step/retry/wall-time limit
- Per-account rate/spend/concurrency limit
- Anomaly/abuse detection
- Graceful degradation 和用户可见预算状态
- Runaway agent circuit breaker
- 高成本或不可逆操作确认

## Quality Gate

- 成本连接到成功任务、Segment 和 Plan。
- Forecast 暴露 Volume、Model mix、Retry、Unit price 假设。
- p95 与 Heavy tail 可见。
- 节省不突破质量、延迟和安全护栏。
- 路由、Fallback 和循环都有上限与回滚。
- 定价和 Included usage 支持目标毛利。

模板：`templates/ai-unit-economics.md`。
