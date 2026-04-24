# API Draft

## GET /health

返回服务状态。

### Response

```json
{
  "status": "ok"
}
```

## GET /datasets

返回可用的演示数据集列表。

### Response

```json
{
  "datasets": [
    {
      "id": "wireless-earbuds-demo",
      "name": "Wireless Earbuds Demo"
    }
  ]
}
```

## POST /analyze

对指定数据集执行评论洞察和生成流程。

### Request

```json
{
  "dataset_id": "wireless-earbuds-demo",
  "prompt_version": "v1"
}
```

### Response

```json
{
  "dataset_id": "wireless-earbuds-demo",
  "summary": {
    "top_positive_themes": [],
    "top_negative_themes": [],
    "key_questions": []
  },
  "assets": {
    "selling_points": [],
    "faqs": [],
    "copy_suggestions": []
  }
}
```

## POST /evaluate

比较两个 Prompt 版本的输出表现。

### Request

```json
{
  "dataset_id": "wireless-earbuds-demo",
  "left_prompt_version": "v1",
  "right_prompt_version": "v2"
}
```

### Response

```json
{
  "winner": "v2",
  "scores": {
    "v1": {
      "citation_coverage": 0.67,
      "structure_completeness": 0.8,
      "human_usable_score": 3.8
    },
    "v2": {
      "citation_coverage": 0.92,
      "structure_completeness": 1.0,
      "human_usable_score": 4.4
    }
  }
}
```
