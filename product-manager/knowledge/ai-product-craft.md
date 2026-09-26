# AI Product Craft

## 1. 产品经理需要定义的不是“模型”，而是任务合约
- 输入是什么
- 用户期望的输出是什么
- 允许的不确定性
- 哪些动作必须可逆
- 哪些错误绝对不能发生
- 什么时候必须人工接管

## 2. 非确定性产品的核心设计
传统软件强调规则正确，AI 产品强调统计质量和失败管理。因此必须设计：
- Golden Set
- Failure Taxonomy
- Fallback
- Human-in-the-loop
- Trace / Observability
- Regression Eval

## 3. 成本指标
优先看 `Cost per Successful Task`，而不是只看单次模型调用价格。Agent 任务可能多次调用模型与工具，失败重试会显著抬高真实成本。

至少分解 Inference、Retrieval、Tool/API、Retry/Fallback、Human review、Support，并报告 p50、p95 与重度用户。成本优化必须同时守住质量、延迟、安全和贡献毛利。

## 4. 模型可替换性
将模型供应商、Prompt、RAG、Tools、Eval 解耦。产品规格应定义行为和门槛，而不是把某一个模型名称写成永久需求。

## 5. 高风险动作
支付、删除、公开发布、发送外部消息、修改权限、医疗/金融/法律高风险结论等动作应优先设计确认、权限、审计、限额和人工兜底。
