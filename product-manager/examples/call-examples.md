# 调用示例

## 1. 新产品想法
> 调用 product-manager，用 assess 模式评估：我想做一个能自动回复微信客户的 AI Agent。先不要写 PRD。

## 2. 建项目上下文
> 调用 product-manager，执行 teach。我把项目介绍给你，输出一份 `.pmcontext.md`。

## 3. 从 Idea 到 MVP
> 调用 product-manager，按 idea-to-mvp workflow 推进。所有假设都标出来，优先找最便宜的验证方式。

## 4. 写 PRD
> 调用 product-manager，基于 `.pmcontext.md` 和已验证需求写 PRD。必须包含 Non-goals、Edge Cases、埋点、验收和回滚。

## 5. AI 架构
> 调用 product-manager，判断这个任务应该用固定 Workflow、RAG、Tool Calling、MCP 还是 Agent。请给被拒绝方案和升级条件。

## 6. AI PRD + Eval
> 调用 product-manager，生成 AI PRD 和 Eval Spec。重点写 Golden Set、失败模式、HITL、P95 延迟、Cost per Successful Task、灰度门槛。

## 7. 对抗性评审
> 调用 product-manager，review 这份 PRD。不要帮我润色，先按 PM Slop Test 找根本问题，然后给 Top 3 修复项。

## 8. 需求优先级
> 调用 product-manager，对下面 12 个需求做优先级。不要只给 RICE 分数，说明每个分数的证据与 Trade-off，并至少砍掉 3 项。

## 9. 上线后复盘
> 调用 product-manager，对照 product/decisions.md 做 retro，区分决策质量和执行结果。

## 10. 面试训练
> 调用 product-manager，interview 模式，把这个项目整理成高级 AI 产品经理面试案例。不能虚构数据，缺数据就标出来。

## 11. 专业竞品情报
> 调用 product-manager，competitive-intelligence 模式。比较同一 Segment/JTBD，区分 Claimed/Observed/Inferred，最后给战略回应而不是功能表。

## 12. 用户研究运营
> 调用 product-manager，research-ops 模式。为这个决策设计方法、样本、同意与隐私、证据表、反例和停止条件。

## 13. 定价商业化
> 调用 product-manager，pricing 模式。比较 Value Metric，设计 Packaging，建立三种财务情景和迁移/回滚方案。

## 14. AI 单位经济
> 调用 product-manager，ai-economics 模式。按成功任务分解 p50/p95 成本、重试和人工接管，给出不伤质量的优化顺序。

## 15. 根据已有项目反推拆解
> 调用 product-manager，用 reverse-decompose 分析这个代码仓库。先锁定提交版本与检查范围，再把入口、用户任务、能力、模块和数据依赖串起来；标出证据、推断、未知与最小验证。不要仅凭代码推断已上线或已有真实用户，也不要修改项目文件。
