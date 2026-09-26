# Mode: eval

## 先定义任务成功
不要先选 Accuracy。先说明“一个任务什么时候算成功”。

## Eval 四层
1. **Model/Output**：正确性、完整性、引用质量、格式、幻觉/拒答。
2. **Task**：Task Success、Tool Success、完成时间、重试、人工接管。
3. **Product**：Activation、Retention、Feature Adoption、CSAT。
4. **Business**：Conversion、ARPU/LTV、Cost per Successful Task、Gross Margin。

## 数据集
- Golden Set：代表真实核心任务。
- Edge Cases：边界和低频高风险。
- Adversarial Set：越权、提示注入、敏感信息、恶意工具调用等。
- Regression Set：历史 Badcase 固化为回归样本。

每个指标写：计算口径、目标/最低阈值、样本来源、评测频率、失败后的动作。
不要把 LLM-as-a-Judge 当唯一标准；高风险任务应加入人工抽检或确定性验证。

模板：`templates/eval-spec.md`。
