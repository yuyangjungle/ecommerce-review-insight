# MVP PRD

## 1. Project overview

### Working title

Review Insight Copilot

### One-line summary

帮助电商运营或商品经理快速从评论、问答和竞品信息中提取用户痛点、卖点机会和可直接使用的文案建议。

## 2. Problem statement

在商品运营场景中，用户反馈高度非结构化，评论数量大、噪音高、表达分散。运营人员通常要手动阅读大量评论，才能总结出：

- 用户最在意什么
- 商品最大的负面痛点是什么
- 哪些卖点应该强调
- FAQ 该怎么写
- 商品文案该如何优化

这个过程费时、主观、难复用，也不容易形成标准化的分析流程。

## 3. Target users

### Primary users

- 电商运营
- 商品经理
- 内容运营

### Secondary users

- AI 产品经理
- 算法策略同学
- 商家增长团队

## 4. User goals

1. 在短时间内看懂一批评论反映了什么问题。
2. 快速得到可执行的卖点和优化方向。
3. 降低“AI 总结不可信”的担忧，看到结果来源。
4. 对不同 Prompt 或 workflow 的效果进行基本对比。

## 5. Core scenarios

### Scenario A: 评论洞察

用户上传评论数据后，系统输出：

- 正向反馈主题
- 负向反馈主题
- 高频问题列表
- 典型代表评论

### Scenario B: 商品文案优化

基于评论洞察，系统生成：

- 商品卖点建议
- 商品标题改写建议
- 详情页卖点描述建议

### Scenario C: FAQ 草案生成

系统根据评论和问答自动生成常见问题及建议回答。

### Scenario D: Prompt 评估

用户对比两版 Prompt 的输出效果，查看：

- 结构完整度
- 引用覆盖情况
- 人工主观偏好

## 6. MVP feature list

### Feature 1: Data input

支持导入 JSON 格式的评论和问答数据。

输入字段：

- product_id
- review_id
- rating
- content
- created_at

### Feature 2: Theme extraction

基于规则 + LLM 的方式提取：

- 正向主题
- 负向主题
- 主题频次
- 主题示例

### Feature 3: Opportunity summary

输出三类产品化结果：

- 用户最关注问题
- 推荐强化卖点
- 建议优化点

### Feature 4: Content generation

生成：

- 商品卖点文案
- FAQ 草案
- 标题或短描述改写建议

### Feature 5: Citation grounding

每条结论附带引用评论 ID 或原始文本片段。

### Feature 6: Evaluation

支持对不同 Prompt 版本做基础评估，至少包括：

- 引用率
- 结构完整度
- 人工可用性评分

## 7. Out of scope

第一版不做：

- 多商品横向分析
- 真实商家账号体系
- 实时在线训练
- 复杂多 Agent 系统
- 真正的生产级向量数据库

## 8. User flow

1. 选择示例商品数据。
2. 点击生成分析。
3. 查看评论主题和用户痛点。
4. 查看卖点建议、FAQ 与文案改写结果。
5. 打开引用来源验证结果。
6. 切换 Prompt 版本，查看评估对比。

## 9. Success metrics

### Product metrics

- 单次分析完成时间
- 用户点击引用来源比例
- 生成结果被保留/采纳比例

### Model metrics

- citation coverage
- hallucination rate
- structure completeness
- human preference score

## 10. 项目价值

这个项目聚焦以下几个产品价值点：

- 将非结构化评论转成可消费的结构化结论
- 将主题抽取、内容生成与引用回看串成完整 workflow
- 为评论洞察结果提供基础评估维度
- 为后续接入真实 LLM 与线上部署预留清晰扩展路径
