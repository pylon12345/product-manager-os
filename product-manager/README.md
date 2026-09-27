# AI Product Manager OS v1.1.0

一个面向 **AI 产品经理、AI Agent、SaaS 和 0→1 开发** 的中文产品经理 Skill。

v1.1.0 在首个正式版基础上加入已有项目反推拆解：从代码/产品仓库重建现状，再把产品意图、用户价值与待验证假设分开。它可在 Codex、Claude Code、Cursor、Windsurf 或其他 Agent 工作流中复用；升级不会迁移或重抓包外知识库，也不会改变已配置的每周自动化。

## 正式版核心能力

- **Router**：先识别任务，再按需加载知识。
- `.pmcontext.md`：同一项目只需建立一次产品上下文。
- **Evidence Gate**：弱证据不能直接升级成高成本开发。
- **Critical Review / PM Slop Test**：AI 不再只会顺着需求写文档。
- **Decision Log**：记录为什么做、接受了什么代价、什么时候重新评估。
- 完整生命周期：`IDEA → DISCOVERY → VALIDATION → MVP → BUILD → TEST → LAUNCH → MEASURE → ITERATE`。
- AI 架构采用阶梯式判断：规则 → Workflow → LLM → RAG → Tools/MCP → Agent → Fine-tune。
- AI PRD 单独建模：Eval、Golden Set、Guardrails、Failure Modes、HITL、成本、延迟、上线门槛。
- 100 个术语移到按需加载知识层，不再浪费每次调用的上下文。
- Decision Contract 把每个复杂任务绑定到决定、Owner、证据门槛与 Revisit/Kill 条件。
- 竞品情报、研究运营、定价商业化、AI 单位经济与产品体验专业模式。
- 价格调整与 AI 质量-成本闭环工作流，以及对应决策模板。
- Codex 原生 `agents/openai.yaml`，支持自动发现和清晰的默认调用。
- 已有产品的现实快照与跨端交付判断，避免把“完整”误解为补齐所有页面。
- 从已有仓库反推用户任务、能力、模块依赖与下一步；关键结论附来源，不把代码存在等同已上线或被用户需要。
- 将项目证据、决策承诺、执行结果与复查连接成轻量持续工作闭环，并加入可复现的行为回归材料。
- 受控公开来源增量同步、本地检索、可校验备份和安全恢复；知识库数据与 Skill 包分离。

## 目录

```text
product-manager/
├─ SKILL.md
├─ agents/openai.yaml
├─ README.md
├─ INSTALL.md
├─ LICENSE
├─ manifest.yaml
├─ CHANGELOG.md
├─ UPGRADE_NOTES.md
├─ SOURCES.md
├─ validate.py
├─ knowledge/
│  ├─ glossary.md
│  ├─ glossary.json
│  ├─ frameworks.md
│  └─ ai-product-craft.md
├─ references/
│  ├─ foundations.md
│  ├─ decision-contract.md
│  ├─ operating-loop.md
│  ├─ project-reality.md
│  ├─ living-sources.md
│  ├─ knowledge-sources.json
│  ├─ knowledge-base-ops.md
│  ├─ mode-teach.md
│  ├─ mode-assess.md
│  ├─ mode-discover.md
│  ├─ mode-research-ops.md
│  ├─ mode-competitive-intelligence.md
│  ├─ mode-prioritize.md
│  ├─ mode-mvp.md
│  ├─ mode-reverse-decompose.md
│  ├─ mode-delivery-os.md
│  ├─ mode-experience.md
│  ├─ mode-prd.md
│  ├─ mode-review.md
│  ├─ mode-metrics.md
│  ├─ mode-pricing.md
│  ├─ mode-roadmap.md
│  ├─ mode-handoff.md
│  ├─ mode-ai-architecture.md
│  ├─ mode-ai-prd.md
│  ├─ mode-eval.md
│  ├─ mode-ai-economics.md
│  ├─ mode-launch.md
│  ├─ mode-retro.md
│  └─ mode-interview.md
├─ templates/
│  ├─ pmcontext.md
│  ├─ evidence-ledger.md
│  ├─ problem-brief.md
│  ├─ discovery-plan.md
│  ├─ mvp.md
│  ├─ prd.md
│  ├─ ai-prd.md
│  ├─ metrics.md
│  ├─ roadmap.md
│  ├─ tech-handoff.md
│  ├─ eval-spec.md
│  ├─ launch-checklist.md
│  ├─ decision-log.md
│  ├─ retro.md
│  ├─ competitive-intelligence.md
│  ├─ research-plan.md
│  ├─ pricing-decision.md
│  ├─ ai-unit-economics.md
│  ├─ experience-brief.md
│  ├─ project-reverse-map.md
│  ├─ system-reality-map.md
│  ├─ role-task-permission-map.md
│  └─ cross-surface-acceptance.md
├─ workflows/
│  ├─ lifecycle.md
│  ├─ continuous-product-loop.md
│  ├─ idea-to-mvp.md
│  ├─ feature-development.md
│  ├─ ai-product-0-to-1.md
│  ├─ agent-development.md
│  ├─ product-review.md
│  ├─ pricing-change.md
│  └─ ai-quality-cost-loop.md
├─ scripts/
│  └─ pm_kb.py
├─ tests/
│  ├─ test_pm_kb.py
│  └─ behavior/
│     ├─ cases.json
│     ├─ rubric.json
│     ├─ score.py
│     ├─ test_score.py
│     └─ README.md
└─ examples/
   ├─ call-examples.md
   ├─ scenario-audit-v2.2.md
   └─ workbench-delivery-trial.md
```

## 正式版运行资产

- 29 个按需 references，覆盖从项目反推、发现、研究、竞争、定价到 AI 质量、成本、跨端交付、持续运营和知识库运维。
- 23 个可直接填充的产品模板。
- 9 个端到端 workflows。
- Codex 原生 `agents/openai.yaml`，默认允许自动发现，也可用 `$product-manager` 显式调用。
- `validate.py` 提供无网络、只读的包完整性检查；行为回归材料用于检查实际任务表现，不能以结构校验代替。
- `scripts/pm_kb.py` 使用 Python 标准库，在明确指定的数据目录中保存公开网页快照并管理本地备份；安装后不会自行运行。

## 行为质量怎样验收

`tests/behavior/` 包含 8 个冻结任务和人工评分规则，覆盖项目反推、多版本交付、定价、AI Eval、单位经济、过期来源、越权与上线后复查。先在全新任务中只提供 Skill 和单个案例输入，保存未经修改的回答；再由评审按可观察标准打分。运行 `python tests/behavior/score.py --check` 只验证案例与规则文件，**不会调用或评判模型**。完整操作见 `tests/behavior/README.md`。

## 持续工作怎样运行

对同一项目的连续任务，先读取已有 `.pmcontext.md`、相关证据和决策记录，核对适用版本与时间，再只推进本轮最重要的一个决定。建议与已确认决策分开；实施结果要对照原预测复查。最小闭环是：**证据 → 决定 → Owner 与下一动作 → 可观察结果 → 复查触发条件**。详见 `workflows/continuous-product-loop.md`。

这个项目决策闭环不会自行修改项目或自动发布。网页知识库同步是独立的可选工具；只有明确调用或另行配置周期自动化时才运行，也不会自动写入项目证据与决策日志。没有写入授权时，Skill 只在答复中给出待确认的记录建议。

```text
调用 product-manager，延续这个项目。先核对已有上下文、证据和历史决策；告诉我本轮应做的一个决定、依据、下一动作和复查条件。先不要修改项目文件。
```
## 产品设计与 UI 的分工

`experience` 负责用户任务闭环、信息结构、关键状态、反馈与恢复、可用性验证及产品验收。需要视觉风格、高保真页面、原型或前端实现时，继续使用相应的产品设计或开发工作流。已有界面的视觉问题必须基于截图或实际界面证据审查。

静态场景审计见 `examples/scenario-audit-v2.2.md`；匿名化交付判断示例见 `examples/workbench-delivery-trial.md`。两者用于检查规则与路由，不等于真实身份或真机业务验收。

## 已有产品怎样使用

接手一个已有代码/产品仓库、想弄清“现有项目究竟实现了什么、可能服务什么任务、下一步从何拆起”时，先用 `reverse-decompose`。它从可追溯证据重建 **as-is** 能力与依赖，把推断的用户和价值留作假设；按需填写 `templates/project-reverse-map.md`。没有真实运行或用户证据时，不宣称已上线、有效果或已验证需求。

```text
调用 product-manager，用 reverse-decompose 分析这个代码仓库。请先说明检查范围和提交版本，沿入口→用户任务→能力→模块/数据依赖反推现状；每个关键结论标明来源，区分观察、推断与待验证，并给出最值得先核验的一条任务链。先不要改项目文件或写完整 PRD。
```

遇到“把旧工作台做完整”“多端系统能否上线”时，先用 `delivery-os`。它先核实当前入口、版本、数据源及证据等级，再定义目标角色的任务闭环，最后给出 Now/Next/Later 和跨端验收门槛。按需使用三份模板，不要求每个任务都填满三张表。

示例：

```text
调用 product-manager，按 delivery-os 审查现有教师工作台。区分旧系统、当前系统与演示版；给我可运营范围、跨角色任务闭环和 Go/No-go 验收，不要修改生产数据。
```

## 可更新知识来源

`references/living-sources.md` 收录经核对的官方或一手入口，按用户研究、商业模式、定价、AI Eval、模型成本、风险和行业趋势分类。`references/knowledge-sources.json` 是机器白名单：同步器只尝试其中启用的完整 HTTPS URL，不跟随页面链接；抓取仍受 robots.txt 和站点规则约束。项目访谈、实际使用数据及业务约束始终优先于通用文章。本地快照用于离线查找和追溯，定价、政策、模型能力等易变事实仍要打开当前一手页面核验。

## 本地知识库：同步、检索和备份

从 Skill 根目录运行以下命令，把示例绝对路径换成你自己的**包外数据目录**。工具不会把数据库写进 Skill 安装包，也不需要第三方依赖。

```powershell
python scripts/pm_kb.py --data-dir "C:\path\to\product\knowledge-base" --sources-file references/knowledge-sources.json sync
python scripts/pm_kb.py --data-dir "C:\path\to\product\knowledge-base" --sources-file references/knowledge-sources.json search "evaluation" --limit 10
python scripts/pm_kb.py --data-dir "C:\path\to\product\knowledge-base" --sources-file references/knowledge-sources.json status
python scripts/pm_kb.py --data-dir "C:\path\to\product\knowledge-base" --sources-file references/knowledge-sources.json backup
```

备份命令会返回文件路径；再用 `verify-backup <备份绝对路径>` 校验。恢复需要显式 `restore <备份绝对路径>`，已有活动库时还要 `--force`：工具先原样隔离旧库供排查；若旧库完整，另生成可验证的 `pre-restore` 安全备份。原样隔离副本未经验证，不等于可恢复备份。完整的故障处理、来源增减、时效标注、恢复演练和每周自动化顺序见 `references/knowledge-base-ops.md`。Skill 不常驻；每周运行必须另行配置调度。

## 最常用的调用方式

```text
调用 product-manager，先评估这个想法，不要急着写 PRD：……
```

```text
调用 product-manager，执行 teach，帮这个项目建立 .pmcontext.md。
```

```text
调用 product-manager，把这个需求推进到 MVP，但先检查证据和关键假设。
```

```text
调用 product-manager，评审这个 PRD。重点找：用户问题、指标、Non-goals、边界、失败路径和不可验收项。
```

```text
调用 product-manager，判断这个 AI 功能应该用 Workflow、RAG、Tool Calling 还是 Agent，不要默认上 Agent。
```

```text
调用 product-manager，为这个 AI 功能生成 AI PRD + Eval Spec + 上线门槛。
```

```text
调用 product-manager，用 competitive-intelligence 判断我们该差异化、监控还是忽略，不要只做功能矩阵。
```

```text
调用 product-manager，用 pricing 模式设计价值度量、套餐和调价迁移，并建 Downside/Base/Upside 模型。
```

```text
调用 product-manager，用 ai-economics 计算 Cost per Successful Task，给模型路由、预算和熔断建议。
```

## 推荐安装思路

把整个目录作为一个 Skill 目录安装，入口保持为 `SKILL.md`。不同 Agent 的发现目录不同，因此本包不把运行时路径写死；核心原则是：**入口文件可见，且 `references/`、`templates/`、`knowledge/` 保持相对路径不变。**

## 使用原则

- 想法阶段先 `assess` / `discover`，不要直接 `prd`。
- 重大开发前先建立 `.pmcontext.md`。
- AI 功能必须跑 `ai-architecture` 和 `eval`。
- 对复杂产品体验先明确任务、信息优先级和恢复路径；需要视觉方案时接续设计工作流。
- 重大交付前用 `review` 检查问题、范围、体验和风险。
- 上线后用 `retro` 回看原始预测与真实结果。

## 安装

`INSTALL.md` 给出 Windows PowerShell 与 macOS/Linux 的复制命令；包内没有独立安装脚本。

## 版本与定版说明

详见 `UPGRADE_NOTES.md`。

## 开源许可

本 Skill 以 [Apache License 2.0](LICENSE) 开源。公开仓库仅提供代码、模板和方法资料；运行时抓取的网页全文及本地知识库备份不属于发行包。
