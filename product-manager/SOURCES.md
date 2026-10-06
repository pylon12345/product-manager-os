# 设计来源与吸收原则

正式版 v1.0.0 在开发过程中参考了公开 GitHub PM Skill 的**架构思想与工作方法**，没有直接复制其大段正文。

重点吸收：
- Router + 按需知识加载：避免单一 SKILL.md 过长。
- Context Gate / 项目上下文：先建立 ICP、战略重点、约束和证据。
- Adversarial Review / PM Slop Test：主动找漏洞，不做 yes-machine。
- Progressive Disclosure：主 Skill 保持短，深度知识放 references。
- AI PRD：将模型、Eval、Guardrail、Failure Mode、HITL、成本和上线门槛纳入产品规格。
- AI vs 非 AI 判断：先证明 AI 的必要性。

公开参考仓库：
- Digidai/product-manager-skills
- rajann44/pm-skills
- jameshemson/pm-skills
- assimovt/productskills
- github/awesome-copilot (`skills/prd`)
- borghei/Claude-Skills (`ai-feature-prd`)
- xihuishawpy/ai_product_skills

框架名称沿用其公开行业名称，如 Mom Test、JTBD、RICE、Shape Up、Opportunity Solution Tree、Now/Next/Later。使用这些名称不代表复制具体实现文本。

可随时间更新的外部资料入口与使用边界见 `references/living-sources.md`。这些是需要时直接打开核对的入口，不随 Skill 包缓存网页内容。
