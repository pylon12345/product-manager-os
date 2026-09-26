# Mode: ai-architecture

目标：选择**最简单且足够**的 AI 架构。

## 决策阶梯
1. **规则/传统代码**：输入、规则和输出确定，可精确验证。
2. **固定 Workflow**：多步骤但路径基本确定。
3. **LLM + Structured Output**：需要语言理解/生成，但输出结构可约束。
4. **RAG**：需要私有、最新或可引用知识。
5. **Tool Calling / MCP**：模型需要读取或操作外部系统。
6. **Agent**：任务路径无法预先穷举，需要计划、观察和动态选择工具。
7. **Fine-tuning**：Prompt/RAG/Tools 仍不足，且存在稳定、可训练的数据与收益理由。

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

输出：推荐架构、被拒绝方案及理由、主要风险、MVP 架构、升级条件。
