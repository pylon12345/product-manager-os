# AI Product Manager OS｜正式版产品与运营指南

> 版本：v1.0.0 · 文档日期：2026-09-26 · 适用对象：产品负责人、研究人员、设计与研发协作者、AI 产品运营者

## 1. 产品定位

AI Product Manager OS 是一个可安装到 Codex 等 Agent 环境的中文产品决策 Skill。它把产品发现、证据判断、方案取舍、交付规格、AI 质量与成本控制、上线复盘组织成可重复的工作方式。核心交付物不是更多文档，而是**带依据、责任人和复查条件的下一项决定**。

它适用于 AI 产品、Agent、SaaS、0→1 探索，以及已有产品的跨版本、跨角色改版。它能辅助负责人提出问题、组织研究、评审方案和留下可追溯记录；不能替代真实用户接触、财务/法律专业判断、产品负责人批准或线上验收。

特别需要区分三件事：

- **Skill** 是任务路由与方法层；安装后由用户任务或 Agent 调用，不是常驻服务。
- **项目记录** 是产品上下文、用户证据与决策历史；默认只读，须在授权范围内写回。
- **本地网页知识库** 是可选的公开来源快照；可用于离线查找和追溯，不等于当前事实，也不会自动变成项目证据。

因此，本系统的“持续工作”指跨次任务复用可核验上下文，并按观察、决定、执行、测量、复查推进；不意味着 Skill 自行监控业务、联系用户、修改项目或发布产品。

## 2. 能力架构与职责边界

| 层 | 作用 | 核心资产 |
|---|---|---|
| 入口与路由 | 识别用户意图，只加载当前决定需要的模式 | [SKILL.md](product-manager/SKILL.md)、`agents/openai.yaml` |
| 项目上下文 | 识别目标用户、战略、商业模式和约束 | `.pmcontext.md`、`templates/pmcontext.md` |
| 证据与决策 | 区分事实、推断、假设；定义证据门槛与负责人 | `references/decision-contract.md`、`templates/evidence-ledger.md`、`templates/decision-log.md` |
| 专业模式 | 按问题调用研究、竞争、定价、体验、交付、AI Eval、成本等能力 | `references/mode-*.md` |
| 生命周期 | 从想法到验证、构建、上线与复盘 | `workflows/`、`templates/` |
| 知识更新 | 精确 URL 白名单同步、离线检索、备份及恢复 | `references/knowledge-sources.json`、`scripts/pm_kb.py` |
| 质量控制 | 结构检查、工具测试与人工行为回归 | `validate.py`、`tests/` |

系统覆盖用户研究、竞品情报、优先级、MVP、产品体验、PRD、定价、AI 架构、Eval、单位经济、研发交接、灰度上线和复盘。方法与模板按任务加载，不要求每次都填写完整套件。产品体验模式定义任务流程、信息优先级、关键状态和验收；视觉风格、高保真 UI 与前端实现仍由设计或开发工作流承担。

## 3. 标准决策工作流

对复杂任务，先明确本轮要支持的**一个主要决定**，再选择主模式；确有依赖时增加一个辅助模式。建议按以下顺序运行：

1. **确认现实**：核对项目版本、环境、目标用户、现有能力、约束，以及证据的观察日期。旧系统、演示版、自动测试和真实用户验收不能混为“当前已上线”。
2. **建立决策契约**：写清 Decision、Owner、截止时间与可逆性、至少包含“不做”的选项、评价标准和证据门槛。高成本、不可逆或高风险决定需要更强证据；低风险请求可直接给带假设的可用草稿。
3. **选择最小验证**：先确认用户问题和当前替代方案，再决定是访谈、数据核查、原型、MVP 还是完整规格。证据不足时，不以精美 PRD 掩盖未知数。
4. **交付可执行建议**：结论先行，说明被放弃选项、关键 Trade-off、失败路径、Success Metric、Owner 与下一动作。AI 功能额外规定 Eval、Golden Set、成本、延迟、Guardrail 和人工兜底。
5. **复查与校准**：建议先标 `PROPOSED`；负责人确认或有可核验的授权记录后才成为 `COMMITTED`。获得真实结果后追加 `REVISITED`，比较预期与实际，并决定继续、调整、回滚或停止。保留原始判断，不覆盖历史。

产品阶段按 `IDEA → DISCOVERY → VALIDATION → MVP → BUILD → TEST → LAUNCH → MEASURE → ITERATE` 推进。这个序列是检查阶段门槛的工具，不是让每个小请求都走一遍流程。AI 方案优先从规则或传统代码、固定 Workflow 开始；只有必要时才升级到 LLM、RAG、工具调用、Agent 或 Fine-tuning，并说明增益、代价与回退路径。

完整的跨次协议见 [Continuous Product Loop](product-manager/workflows/continuous-product-loop.md)；具体模式由 [Skill 入口](product-manager/SKILL.md) 路由。

## 4. 安装与首次启用

1. 将完整的 `product-manager/` 目录放入 Agent 支持的 Skill 目录，保留 `SKILL.md` 与其 `references/`、`templates/`、`workflows/`、`knowledge/`、`scripts/` 的相对关系。Codex 的全局及项目级位置、不同平台的复制命令见 [INSTALL.md](product-manager/INSTALL.md)。已有同名安装时先比较版本和自定义内容，不静默覆盖。
2. 在 Skill 目录运行 `python validate.py`；输出 `OK` 只证明包结构与引用基本完整，不证明模型在真实项目上的产品判断正确。
3. 新开任务并显式调用 `$product-manager`，给出项目目标、用户、当前阶段、可用证据和本次希望支持的决定。复杂项目建议先建立 `.pmcontext.md`；没有真实信息时允许标 `[假设]`，不得补造业务数据。
4. 若需要跨次持续工作，在项目中由负责人维护或授权维护 `product/evidence.md`、`product/decisions.md` 等记录。Skill 不会因安装而自动建档或写回。

可直接使用的任务指令：

```text
$product-manager 先评估这个需求是否值得做。目标用户是……；现有证据是……。请区分事实、假设与待验证项，给出最小验证和明确的不做条件；先不要写 PRD 或修改文件。
```

```text
$product-manager 按 delivery-os 审查现有工作台。请分别核对旧版、当前版和演示版，列出目标角色的端到端任务、权限与失败路径，并给出可运营范围和 Go/No-go 门槛。
```

```text
$product-manager 用 pricing 模式评估从按席位收费改为混合计费。请给出价值度量、迁移风险、Downside/Base/Upside 假设及必须补齐的数据；所有价格与竞品事实都附观察日期。
```

```text
$product-manager 为这个 AI 功能选择最简单可行架构，并定义 Eval 切片、Golden Set、失败兜底、每次成功任务成本、延迟门槛和灰度回滚条件。不要默认采用 Agent。
```

```text
$product-manager 延续这个项目：先核对上下文、证据与既有决策；只推进本轮最重要的一个决定。输出 Owner、下一动作和复查触发条件，未经我确认不要更新项目记录。
```

## 5. 知识来源、同步和本地备份

发行版的 `references/knowledge-sources.json` 默认列出 8 个已启用的**精确 HTTPS 页面**，覆盖研究方法、商业模式、定价、AI Eval、模型成本、风险框架与行业趋势。同步器只尝试这些页面，不跟随链接，不抓取整站、登录页或项目私有资料；仍须遵守 robots.txt、网站规则和运行环境的网络权限。新增来源需负责人逐条审核用途、公开可访问性与抓取许可，然后手工加入单个 URL。

首次启用应选择 **Skill 包外**、明确可写且可长期保留的数据目录。以下命令在 `product-manager/` 中运行，尖括号是待替换占位符：

```text
python scripts/pm_kb.py --data-dir "<知识库绝对路径>" --sources-file references/knowledge-sources.json sync
python scripts/pm_kb.py --data-dir "<知识库绝对路径>" --sources-file references/knowledge-sources.json status
python scripts/pm_kb.py --data-dir "<知识库绝对路径>" --sources-file references/knowledge-sources.json search "evaluation" --limit 10
python scripts/pm_kb.py --data-dir "<知识库绝对路径>" --sources-file references/knowledge-sources.json backup
python scripts/pm_kb.py --data-dir "<知识库绝对路径>" --sources-file references/knowledge-sources.json verify-backup "<备份绝对路径>"
```

活动库保存公开页面文本快照、原始 URL、抓取时间和内容哈希；备份是独立的 SQLite 文件，并可校验和恢复。使用快照形成结论时必须注明来源与时间；**快照时间不代表事实有效期**。竞品功能、API 价格、模型能力、政策等易变信息仍须到当前一手页面核验。网页文本是待分析资料，不能执行其中夹带的指令。网页快照也不能自动写入项目用户证据或决策日志。

安装 Skill 不启动定时抓取。需要每周等周期运行时，应另行获得授权并配置外部调度，按 `sync → status → backup → verify-backup` 顺序执行，区分全部成功、部分失败和旧快照仍可检索。恢复须人工选择已验证备份，先在隔离目录演练；覆盖活动库涉及后续数据丢失风险，必须由数据负责人确认。同目录备份不抵御磁盘故障；如需异盘或异地容灾，应另行授权复制到受控存储。详见 [Knowledge Base Ops](product-manager/references/knowledge-base-ops.md)。

## 6. 证据、授权与安全原则

- **证据分级**：项目一手访谈、行为数据、客服与销售记录优先于通用方法文章。外部来源必须保留具体页面、观察日期、适用地区/产品版本和支持的主张；无法核验则标 `[待验证]`。
- **判断状态**：模型建议不是团队承诺；计划指标不是已观测结果；自动测试不是用户验收。若新证据推翻旧结论，追加记录并标记旧记录 `SUPERSEDED`，不悄悄改写。
- **权限最小化**：建议、审查和草拟不构成写文件、联系用户、改价、发布、删数据或操作生产系统的授权。项目记录默认只读；每次外部变更核对范围、负责人和回滚方案。
- **资料隔离**：公开网页缓存与私有研究资料分开保存。不得把账号、Token、客户数据、内部访谈、完整本地知识库或备份打包进 Skill 仓库；私有 GitHub 仓库也不应视为无限制的数据接收方。
- **审慎发布**：本指南、Skill 代码和空白模板可作为私有仓库的版本化资产；上传前检查仓库可见性及提交内容，确保不包含机器本地路径、凭证、客户资料和运行时数据库。

## 7. 质量保证与适用结论

该版本提供三层验证手段：`validate.py` 检查包结构；`tests/test_pm_kb.py` 与 `tests/behavior/test_score.py` 检查工具行为；`tests/behavior/` 的 7 个冻结任务与人工评分规则用于观察实际 Agent 回答。行为评估应在隔离的新任务中保留原始回答，记录 Skill 版本、模型、日期和工具限制，再由评审按可观察标准评分。运行 `score.py --check` 仅检查案例与规则文件，**不会自动证明 Skill 的回答质量**。测试协议见 [Behavior regression kit](product-manager/tests/behavior/README.md)。

已实现并可检查的是任务路由、模板与工作流、受控网页同步、本地检索、备份/校验/恢复的工具和相应测试材料。尚不能据此宣称：真实业务转化率提升、定价实验成功、用户满意度提高、任意模型/场景下稳定正确，或自动完成上线后的持续运营。这些结果必须通过真实项目基线、独立验收与持续复查建立。

建议每次发布至少完成：版本与 `CHANGELOG.md` 对齐、包结构检查、知识库工具测试、冻结案例回归、来源白名单及权限审查、对安装升级和数据目录分离的检查。对高风险变化增加人工评审与恢复演练。

## 8. 维护与版本治理

正式发行版本为 **v1.0.0**；先前 2.x 是开发迭代编号，此次定版**不回退功能，也不迁移、清空或重抓包外知识库**。后续变更应同时更新 `manifest.yaml`、`SKILL.md`、`README.md`、`CHANGELOG.md` 和必要的测试。保留冻结行为案例以比较新旧版本；若修改评分规则，需说明原因并保留可追溯的旧结果。升级前比较现有安装和自定义内容，避免覆盖用户数据。

知识来源需要维护，但不是“越多越好”：只增加与当前决策相关、可核验、允许抓取的具体页面；记录来源失效、变更与时效风险。业务证据则由项目负责人按权限独立维护，遵循 `PROPOSED → COMMITTED → REVISITED` 的决策闭环。维护目标是减少错误决策和无效工作，而不是增加模板数量或自动化次数。

相关入口：[README](product-manager/README.md) · [安装说明](product-manager/INSTALL.md) · [变更记录](product-manager/CHANGELOG.md) · [正式版定版说明](product-manager/UPGRADE_NOTES.md)。
