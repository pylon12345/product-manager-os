# AI Product Manager OS v1.2.1

中文产品经理 Skill，面向 AI、Agent、SaaS、0→1 项目与已有产品改版。通过按需路由，将用户问题、证据判断、方案取舍、交付规格、AI 质量与成本、上线复盘组织成可重复的工作方式。

**先确认本轮要支持什么决定，再选择方法与产物。** 重要结果应带依据、假设、责任人、下一动作与复查条件，不以模板数量代替产品进展。

## 文档导航

- [安装与升级](INSTALL.md)：Codex、Claude Code、Claude 网页／桌面端与 WorkBuddy 的安装、调用确认、升级和排错。
- [详细使用说明](USER_GUIDE.md)：输入准备、26 个模式、常用指令与连续项目。
- [电商 AI 客服演练](examples/ecommerce-customer-service.md)：从问题验证到 PRD、Eval 与上线决定。
- [主入口](SKILL.md)：Agent 执行规则、路由和按需资源。
- [版本记录](CHANGELOG.md) · [升级说明](UPGRADE_NOTES.md) · [方法来源](SOURCES.md)。

## 核心能力

| 范围 | 能力 |
|---|---|
| 需求与研究 | 项目上下文、想法评估、用户发现、研究运营、竞品情报 |
| 决策与交付 | 优先级、MVP、PRD、评审、指标、定价、Roadmap、交接 |
| 已有产品 | 仓库反推、现实快照、跨角色交付、体验与验收 |
| AI 产品 | 任务驱动架构、AI PRD、Eval、失败兜底、延迟与单位经济 |
| 持续改进 | 上线门槛、监测、复盘、证据与历史决策复查 |
| Skill 维护 | 坏例归因、候选改动、同夹具人工评分比较与维护者审批 |
| 可选知识库 | 白名单同步、本地检索、快照差异、备份校验与恢复 |

包内包含 26 个模式、25 个模板、9 个工作流与 100 个术语。只加载当前任务需要的文件，不把整个知识目录注入每轮上下文。

## 第一次调用

下例使用 Codex 语法；Claude Code 改为 `/product-manager`，Claude／WorkBuddy 使用自然语言指定已安装技能。

```text
$product-manager
项目：……
目标用户与当前问题：……
已有证据：……；未知的信息：……
本轮要支持的决定：……
约束与授权范围：……
请先给结论，区分事实与假设，再给最小验证、下一动作和复查条件。
```

输入不全时可要求带假设的草稿；高成本、不可逆或高风险决定仍需补齐证据。

## 运行机制与边界

- 一般中文产品任务由本 Skill 处理；`product-manager-skills` 可用于 PLG、定位、财务与职业辅导的专项深挖，**不是安装依赖**。
- 产品体验模式负责任务、流程、信息优先级和验收；实际 UI 产物接入设计或开发工作流。
- 项目上下文、证据与决策记录用于跨次衔接；没有写回授权时只给记录建议。
- 易变的外部事实直接核对一手来源并注明观察日期，不当作项目内部证据。
- 安装不启动服务或调度，也不自动执行发布、调价或生产修改。

## 质量检查

从本目录运行：

```bash
python validate.py
python -m unittest discover -s tests -p "test_*.py"
python -m unittest discover -s tests/behavior -p "test_*.py"
python tests/behavior/score.py --check
```

这些检查验证包结构、工具行为和测试材料。实际模型表现需按 [Behavior regression kit](tests/behavior/README.md)独立评估，不把工具测试当作业务验收。

## v1.2.1

整合主分支正向／反向标准流程、阶段定义和统一词表；保留可选知识库，新增快照差异查看与成本费率追溯，并加入受控的 Skill 自身迭代。升级不迁移、重抓或清空包外知识库，也不变更已有周期任务。许可见 [LICENSE](LICENSE)。

## 可选知识库与自身迭代

知识库仅在用户要求时使用，Python 标准库即可运行；指定包外绝对数据目录，按[Knowledge Base Ops](references/knowledge-base-ops.md)执行 `sync`、`status`、`search`、`changes`、`backup`、`verify-backup` 或显式恢复。只抓取白名单精确 URL，不跟随页面链接，不绕过站点限制；抓取成功不代表文章正文可用，缓存不代替实时一手核验。快照、备份、私有研究和项目记录不公开。

改进 Skill 用 `improve-os` 和[改进工作流](workflows/skill-improvement-loop.md)：区分真实坏例与上下文或工具问题，提出最小修改，在同一冻结夹具上比较新旧原始回答及人工评分，再由维护者批准发布。9 个冻结案例只提供评测材料；本版完整新旧人工行为评测仍待完成。
