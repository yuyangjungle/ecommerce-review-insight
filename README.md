# 电商评论洞察助手 | Review Insight Copilot

一个面向电商运营场景的评论分析 demo。系统从商品评论中抽取正负向主题、用户关注问题、卖点建议、FAQ 草案与优化方向，并支持引用回看与不同工作流结果对比。

## 项目概览

- 导入内置样例或上传 JSON 评论数据
- 抽取正向/负向主题并统计提及
- 提炼用户核心问题
- 生成卖点建议、FAQ 草案和优化方向
- 为结论保留引用并支持原文回看
- 对比 `v1` 与 `v2` 两套分析工作流
- 提供本地完整 demo 与 GitHub Pages 静态展示版

## 背景

在电商运营场景中，评论数据通常非结构化、信息量大，人工通读成本高；直接生成式总结又容易缺少依据。这个项目聚焦一条更可控的分析链路：先抽取主题，再组织问题与内容，并为结果保留引用，以提升输出的可解释性和可回溯性。

## 当前范围

当前仓库主要用于展示评论洞察 workflow 与交互形态：

- `apps/` 提供本地完整 demo，包含 Python 后端与前端页面
- `site/` 提供纯静态展示版，可部署到 GitHub Pages
- 当前分析引擎使用轻量规则与 mock workflow，用于验证产品流程、结果结构与评估方式
- 真实 LLM provider、持久化存储和线上用户系统尚未接入

## 核心流程

1. 输入评论数据
2. 抽取正负向主题
3. 提炼用户关注问题
4. 生成卖点、FAQ 与优化方向
5. 为结论附上引用
6. 对比不同工作流输出

## 当前功能

- 内置商品评论样例数据
- 上传自定义评论 JSON
- 正向/负向主题抽取
- 核心问题提炼
- 卖点建议与 FAQ 草案
- 优化方向输出
- 引用回看抽屉
- `v1` / `v2` 工作流对比
- 核心摘要与基础评估指标展示

## 本地运行

生成分析结果：

```powershell
pwsh -File .\scripts\run_analysis.ps1
```

启动交互式 demo：

```powershell
pwsh -File .\scripts\run_demo.ps1
```

默认访问地址：

- `http://127.0.0.1:8765`

静态展示版本地预览：

```powershell
python -m http.server 8766 --directory site
```

- `http://127.0.0.1:8766`

## GitHub Pages

仓库已包含 GitHub Pages 工作流与静态站点目录：

- 工作流文件：`.github/workflows/deploy-pages.yml`
- 静态站点目录：`site/`
- 预期公开地址：`https://yuyangjungle.github.io/ecommerce-review-insight/`

如果需要启用 Pages 发布，请在仓库 `Settings -> Pages` 中将 `Source` 设为 `GitHub Actions`。

## 目录说明

```text
apps/api/             轻量后端与 mock pipeline
apps/web/             交互式前端 demo
data/sample/          演示用样例数据
docs/                 PRD、架构、API 与项目说明文档
prompts/              提示词模板
scripts/              本地运行脚本
site/                 GitHub Pages 静态展示版
```

## 文档

- 产品需求：[docs/prd.md](./docs/prd.md)
- 技术架构：[docs/architecture.md](./docs/architecture.md)
- API 草案：[docs/api.md](./docs/api.md)
- 项目说明：[docs/case_study.md](./docs/case_study.md)
