# Architecture and Workflow

## 1. System overview

系统分为四层：

1. Data layer
2. Workflow layer
3. Service/API layer
4. Presentation layer

## 2. Workflow design

### Step 1: Input normalization

目标：将评论、问答、竞品信息统一为标准结构。

输出字段：

- source_type
- text
- rating
- metadata

### Step 2: Theme extraction

目标：抽取评论中的高频主题与情绪倾向。

首版策略：

- 规则切分文本
- 按关键词或简单分类聚合
- 再调用 LLM 做主题命名与总结

### Step 3: Insight generation

基于主题与原始文本生成：

- 用户最关注问题
- 正向卖点
- 负向改进点
- FAQ 建议

### Step 4: Citation linking

将每条洞察关联到 1 到 3 条代表性评论，降低“黑盒总结”风险。

### Step 5: Prompt evaluation

同一份输入跑两套 Prompt：

- v1: 直接总结
- v2: 先抽主题再总结

对比输出结构与可用性。

## 3. Recommended architecture

### Frontend

- Dashboard 页面
- Dataset selector
- Result cards
- Citation drawer
- Prompt comparison view

### Backend

- `/health`
- `/datasets`
- `/analyze`
- `/evaluate`

### Storage

首版使用本地 JSON + SQLite。

## 4. Data model

### Review

```json
{
  "product_id": "p001",
  "review_id": "r001",
  "rating": 5,
  "content": "续航很强，通勤一天完全够用。",
  "created_at": "2026-03-08"
}
```

### Insight

```json
{
  "title": "用户认可续航表现",
  "type": "positive_theme",
  "summary": "多条评论提到日常通勤续航充足。",
  "citations": ["r001", "r008"]
}
```

### Generated asset

```json
{
  "asset_type": "faq",
  "title": "一天一充够吗？",
  "content": "根据多数评论，正常通勤场景基本可以满足一天使用。",
  "citations": ["r001", "r003"]
}
```

## 5. Evaluation plan

### Offline evaluation

- 结构完整度：是否包含主题、洞察、卖点、FAQ、引用
- 引用覆盖率：洞察是否附带引用
- 人工可用性：1 到 5 分
- 人工可信度：1 到 5 分

### Demo evaluation

支持展示 Prompt v1 与 Prompt v2 输出差异。

## 6. Portfolio talking points

面试讲解时可以重点强调：

- 为什么选择“先抽主题再生成”的 workflow
- 为什么要做 citation grounding
- 为什么产品评估不能只看模型输出流畅度
- 为什么首版要控制在规则 + LLM 的可解释方案
