# Mode: prd

## 写 PRD 前的门禁
至少具备：明确用户、问题、目标、Scope、成功指标。若缺少，允许先出 `[DRAFT / 未验证]`，但不能伪装成最终规格。

## PRD 规则
- Problem Statement 不包含具体方案。
- Success Metrics 必须可观测；未知基准写 `TBD`。
- 至少写 In Scope / Out of Scope。
- 需求用用户行为 + 业务规则 + Acceptance Criteria 表达。
- 覆盖 Empty / Loading / Error / Timeout / Retry / Duplicate / Permission / Offline（适用时）。
- 当用户流程、信息优先级或恢复路径尚不清楚时，先用 `references/mode-experience.md` 建立体验约束；PRD 保留可验收的行为，不代替视觉稿。
- 技术实现细节只写产品必须约束的部分，不代替工程 RFC。
- AI 功能不要用普通 PRD，转 `mode-ai-prd.md`。

模板：`templates/prd.md`
