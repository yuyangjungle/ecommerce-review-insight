# 电商评论洞察助手

一个面向电商运营场景的评论分析演示项目。系统从商品评论中抽取正负向主题、用户关注问题、卖点建议、FAQ 草案与优化方向，并支持引用回看与不同工作流结果对比。当前仓库同时提供公开可访问的静态展示页，以及可接入真实模型的完整版本。

## 在线体验

- 在线演示：[https://yuyangjungle.github.io/ecommerce-review-insight/](https://yuyangjungle.github.io/ecommerce-review-insight/)
- 项目说明：[docs/case_study.md](./docs/case_study.md)
- 技术架构：[docs/architecture.md](./docs/architecture.md)

公开页说明：

- 当前公开版本部署在 GitHub Pages
- 页面使用 `site/` 目录中的静态站点
- 评论分析逻辑在浏览器本地执行，适合直接预览和快速体验

## 项目概览

- 导入内置样例或上传 JSON 评论数据
- 抽取正向/负向主题并统计提及
- 提炼用户核心问题
- 生成卖点建议、FAQ 草案和优化方向
- 为结论保留引用并支持原文回看
- 对比 `v1` 与 `v2` 两套分析工作流
- 提供本地完整演示版与 GitHub Pages 静态展示版

## 背景

在电商运营场景中，评论数据通常非结构化、信息量大，人工通读成本高；直接生成式总结又容易缺少依据。这个项目聚焦一条更可控的分析链路：先抽取主题，再组织问题与内容，并为结果保留引用，以提升输出的可解释性和可回溯性。

## 当前范围

当前仓库目前包含两种运行形态：

- `site/`：纯静态展示版，已部署到 GitHub Pages
- `apps/`：本地完整版本，包含 Python 后端与前端页面
- `api/` 与根目录 `index.html`：为 Vercel 部署准备的完整版本入口
- 默认使用轻量规则与模拟工作流，可切换到真实 LLM 混合模式
- 已支持通过 DeepSeek 或其他 OpenAI 兼容接口进行内容层生成与润色

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
powershell -ExecutionPolicy Bypass -File .\scripts\run_analysis.ps1
```

启动交互式演示页：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_demo.ps1
```

默认访问地址：

- `http://127.0.0.1:8765`

## 真实模型接入

项目默认以 `mock` 模式运行；如果希望启用真实模型混合模式，优先推荐使用 DeepSeek-V4-Pro：

```powershell
$env:REVIEW_INSIGHT_USE_LLM="auto"
$env:DEEPSEEK_API_KEY="你的 API Key"
$env:DEEPSEEK_BASE_URL="https://api.deepseek.com"
$env:DEEPSEEK_MODEL="deepseek-v4-pro"
```

说明：

- 当 `DEEPSEEK_API_KEY` 未提供时，系统自动使用本地 `mock` 模式
- 当模型调用失败时，系统会自动回退到 `mock` 输出，并在页面上提示
- 也支持其他 OpenAI 兼容接口，示例环境变量可参考：[.env.example](./.env.example)

静态展示版本地预览：

```powershell
python -m http.server 8766 --directory site
```

- `http://127.0.0.1:8766`

## GitHub Pages

当前公开页已部署到 GitHub Pages：

- 公开地址：`https://yuyangjungle.github.io/ecommerce-review-insight/`
- 工作流文件：`.github/workflows/deploy-pages.yml`
- 静态站点目录：`site/`
- 发布方式：`GitHub Actions`

## Vercel 部署

仓库已补齐 Vercel 所需结构：

- 根目录 `index.html` 作为完整版本入口
- 根目录 `api/` 提供 Vercel Python Functions
- `vercel.json` 用于配置函数运行时

如果在 Vercel 项目中配置好 `DEEPSEEK_API_KEY`、`DEEPSEEK_BASE_URL` 和 `DEEPSEEK_MODEL`，即可将完整版本部署为公网可调用模型的演示页。

## 目录说明

```text
apps/api/             轻量后端与模拟分析流程
apps/web/             交互式前端演示页
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
