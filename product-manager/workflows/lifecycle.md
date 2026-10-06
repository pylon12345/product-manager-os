# Product Lifecycle

每节 `A → B`：**进入条件**满足时可以开始为这次转换做准备；**退出条件**满足才算离开 A、进入 B。判断当前阶段时看最近一个已满足的退出条件。

VALIDATION 与 MVP 的区别：VALIDATION 阶段用 `assess`/`discover`/`mvp` 模式明确最危险假设并**设计**最低成本验证；MVP 阶段**执行**这次验证并收集信号。`mvp` 模式在两个阶段都会用到，不能据此判断阶段。

## IDEA → DISCOVERY
进入条件：有明确想解决的问题或机会。
退出条件：能描述具体用户、场景、当前替代方案和最大未知数。

## DISCOVERY → VALIDATION
进入条件：问题和用户范围已收敛。
退出条件：已有足够证据支持一次低成本验证。

## VALIDATION → MVP
进入条件：最危险假设已明确。
退出条件：有最小闭环、成功/停止门槛和资源范围。

## MVP → BUILD
进入条件：验证信号足够，且完整开发相对合理。
退出条件：PRD/AI PRD、指标、验收、依赖和风险达到评审标准。

## BUILD → TEST
退出条件：核心功能可测，埋点与 Eval 可运行。

## TEST → LAUNCH
退出条件：Acceptance + Guardrail + Rollback Gate 通过。

## LAUNCH → MEASURE
退出条件：真实用户数据可观测。

## MEASURE → ITERATE
退出条件：基于实际结果形成新的决策，不按原 Roadmap 惯性推进。
