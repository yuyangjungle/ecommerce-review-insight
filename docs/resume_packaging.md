# Resume and GitHub Packaging

## 1. Recommended project name on resume

建议中文名：

电商评论洞察与商品优化 AI 助手

建议英文名：

Review Insight Copilot for E-commerce

## 2. Resume bullet draft

如果你在当前阶段就要写进简历，可以先用这一版：

1. 围绕电商商品优化场景，设计并开发 AI 评论洞察助手，基于商品评论自动抽取正负反馈主题、用户关注问题、卖点建议与 FAQ 草案，降低运营人员处理非结构化反馈的理解成本。
2. 拆解“评论输入-主题抽取-洞察生成-引用校验-结果评估”的 workflow，设计 Prompt 模板、结果结构与 API 草案，形成可演示的 AI 产品方案。
3. 搭建轻量评估框架，使用 citation coverage、structure completeness 等指标验证输出可信度与结构质量，并通过前端原型展示结果卡片与引用依据。

## 3. Stronger version after next iteration

等你后面补完真实模型调用、Prompt 对比和在线 demo 后，可以升级成更强的一版：

1. 面向电商商品运营场景开发 AI 评论洞察与商品优化助手，整合评论分析、FAQ 生成、卖点提炼与优化建议输出，提升商品反馈分析效率与内容生产效率。
2. 设计并实现“主题抽取 + grounding + 生成”的 AI workflow，结合 Prompt 编排与引用回溯机制降低幻觉风险，提升结果可解释性。
3. 建立 Prompt A/B 对比与人工评测机制，围绕 citation coverage、可用性评分与结构完整度进行效果评估，为后续产品迭代提供依据。

## 4. GitHub repo checklist

后面准备放 GitHub 时，建议仓库至少具备：

1. 一个非常清楚的 README 首页图。
2. 项目背景、用户问题、核心功能、workflow 图。
3. 技术结构图和目录说明。
4. 运行方式。
5. 示例输入与输出截图。
6. 评估方法和关键指标说明。
7. 未来 roadmap。

## 5. Demo checklist

在线 demo 最好至少有这几个页面：

1. 首页：一句话说明项目价值。
2. 数据选择页：切换样例商品。
3. 结果页：主题、卖点、FAQ、优化建议、引用来源。
4. 对比页：Prompt v1 和 v2。

## 6. Interview talking points

面试里你可以重点讲这四件事：

1. 为什么这个场景值得做，而不是泛泛做个聊天机器人。
2. 为什么要把 workflow 拆成抽取、总结、生成和引用校验。
3. 为什么评估不能只看“输出像不像人写的”，还要看 grounding 和可用性。
4. 当前方案有哪些局限，以及后续如何从规则版升级到 LLM/RAG 版。
