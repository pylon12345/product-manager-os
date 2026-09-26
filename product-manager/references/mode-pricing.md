# Mode: pricing

目标：连接客户价值、价值度量、Packaging、购买行为、迁移风险和单位经济，而不是给套餐“拍三个档”。

## 1. Monetization Thesis

先明确 Segment、Buyer、User、核心价值、替代方案、Cost-to-serve、Sales motion，以及本次优先优化 Adoption、Expansion、Margin、Predictability 或 Position。不能假设一套方案同时最大化所有目标。

## 2. Value Metric

候选计费度量按以下维度评估：

- 与客户获得价值同步
- 可测量、难作弊
- 可预算、账单可解释
- 随使用或价值自然扩张
- 不惩罚核心价值行为
- 与可变成本保持合理关系
- 对不同规模客户公平

Seats、Usage、Outcome、Workflow、Asset、Hybrid 都是候选，不默认其中一个。

## 3. Packaging

套餐围绕不同 Segment / Job / Buying motion 设计。每档写 Target、Outcome、Entitlements、Metering、Limits、Support、Proof、Upgrade trigger、Downgrade path。区分：

- Entitlement：可以做什么。
- Metering：测量什么。
- Billing：如何收费。

## 4. 证据

组合使用：Win/Loss、销售录音、历史折扣与转化、使用/留存分布、Conjoint/Discrete Choice、Van Westendorp、Gabor-Granger、真实 Offer/Fake Door。明确哪些是 `Stated preference`，哪些是 `Revealed behavior`。

## 5. 财务模型

至少建立 Downside / Base / Upside：Eligible accounts、Conversion、Churn、Downgrade、Expansion、ARPA/Usage distribution、Discount leakage、Gross margin、Support cost、Implementation、Sales compensation、Revenue timing。对最敏感假设做敏感性分析。

## 6. Price Change

选择 Grandfather、Delayed migration、Opt-in、Partial protection 或 Full migration。按 Tenure、Contract、Usage、Profitability、Value realization 分群。定义沟通、例外授权、Holdout、观察窗口、回滚阈值。

## 7. AI Pricing

计入 Inference、Retrieval、Tools、Retries、Human review 与 Support。重尾使用下避免无护栏 Unlimited。Credits 应对应客户能理解的价值单位；除基础设施买家外，不直接暴露 Token 作为产品价值。

## Quality Gate

- Value metric 同时考虑客户价值、可预测性和成本行为。
- 套餐有明确 Segment、Job 和升级逻辑。
- 证据区分陈述偏好与真实行为。
- 模型包含 Churn、Downgrade、Discount 与 Margin。
- 调价包含迁移、例外、监控与回滚。
- 明确 Growth、Revenue 与 Margin 的取舍。

模板：`templates/pricing-decision.md`。
