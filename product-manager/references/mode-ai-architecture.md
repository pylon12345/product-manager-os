# Mode: ai-architecture

目标：选择**最简单且足够**的 AI 架构。

## 按任务缺口选择

先评估最简单且满足质量、成本、延迟和权限要求的基线，再选择必要能力。下列条目不是升级顺序；RAG、Tools 和 Fine-tuning 可组合，也不要求先采用 Agent。

1. **规则/传统代码**：输入、规则和输出确定，可精确验证。
2. **固定 Workflow**：多步骤但路径基本确定。
3. **LLM + Structured Output**：需要语言理解/生成，但输出结构可约束。
4. **RAG**：需要私有、最新或可引用知识。
5. **Tool Calling / MCP**：模型需要读取或操作外部系统。
6. **Agent**：任务路径无法预先穷举，需要计划、观察和动态选择工具。
7. **Fine-tuning**：任务需要稳定的行为、格式或领域适配，已有适用训练数据；与 Prompt 等合理基线比较，能用 Eval 证明收益足以覆盖训练、维护和回归成本。需要新知识时仍评估检索，不把微调当作持续更新知识库的替代。

例如，查询订单可用 LLM + Tools，无须先做 RAG；文档问答可用 LLM + RAG，无须先做 Agent；RAG 可搭配经过微调的生成模型。对每个候选说明其解决的缺口和组合关系，再用代表性任务比较效果，不以技术名称决定复杂度。

## AI vs 非 AI 检查
- 模糊性：规则是否难以穷举？
- 规模性：重复认知劳动是否足够大？
- 容错性：错误是否可检测、可回退？
- 替代性：普通软件是否已经低成本解决？
- 差异化：AI 的质量/速度/成本是否真正改善用户价值？

## Agent 必须额外回答
- Goal / Done Definition
- Tools + 权限最小化
- Memory / State
- Max steps / Timeout / Budget
- Human-in-the-loop
- Retry / Idempotency
- Observability / Trace
- Stop condition

输出：推荐架构及必要组合、被拒绝方案及理由、主要风险、MVP 架构、引入或移除能力的触发条件。
