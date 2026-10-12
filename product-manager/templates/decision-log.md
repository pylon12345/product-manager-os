# Product Decision Log

每项重要决策保留稳定 ID 和状态历史。`PROPOSED` 是建议，不代表批准；`COMMITTED` 需负责人确认或可核验的授权记录；`REVISITED` 表示按触发条件复查并记录实际观察；`REJECTED`（负责人否决）、`STOPPED`（触发 kill 条件或决定停止）、`SUPERSEDED`（被新决策取代）为终止状态。未获写入授权时，把下列条目作为回复草稿，不修改项目文件。

## DEC-YYYYMMDD-01 — 决策主题

- Decision / scope: 要决定什么；适用产品版本、环境、用户群
- Owner: 最终决策人；未知则 `[待确认]`
- Status: PROPOSED / COMMITTED / REVISITED / REJECTED / STOPPED / SUPERSEDED
- Proposed at / by: YYYY-MM-DD / 提出者
- Options: 推荐方案；现状/不做；其他可行方案及放弃原因
- Evidence: 证据 ID、来源日期；关键假设与冲突
- Criteria / trade-off: 用户价值、成本、风险、可逆性；接受的损失
- Expected outcome: 指标或可观察变化、基线、观察窗口；缺失项标 `[待验证]`
- Guardrail / rollback / kill: 护栏、回退方式、停止条件
- Review trigger: 日期或具体事件；不写“定期看看”
- Next action: owner / action / deadline or trigger

### State history（仅追加，不覆盖既有事件）

| At | Transition | Authorized by / source | Observation or reason | Next action |
|---|---|---|---|---|
| YYYY-MM-DD | → PROPOSED | 需求/分析来源 | 提议依据与未决事项 | 待负责人确认 |

实际使用时仅填写已发生的状态事件。负责人确认后追加 `PROPOSED → COMMITTED`，否决则追加 `PROPOSED → REJECTED`；复查后追加 `→ REVISITED` 和实际结果；触发停止条件追加 `→ STOPPED`。若复查产生不同决定，新建 ID，旧条目追加 `→ SUPERSEDED` 并相互引用，不静默修改旧决策。
