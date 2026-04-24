# 电商评论洞察助手 | Review Insight Copilot

一个面向电商运营场景的 AI 产品作品。

系统从商品评论中抽取正负向主题、用户核心问题、卖点建议、FAQ 草案与优化方向，并支持不同提示词工作流的效果对比与引用回看。

## 项目定位

当前版本定位为：

`可交互本地 Demo / MVP 验证版`

这意味着：

- 它不是单纯的高保真原型图，而是有真实前后端交互的可运行作品。
- 它还不是正式上线产品，因为当前 AI 能力层仍以规则与 mock workflow 为主，尚未接入真实 LLM 服务。

## 这个项目解决什么问题

在电商运营场景中，用户反馈高度非结构化。运营或商品经理通常需要手动阅读大量评论，才能回答这些问题：

- 用户最在意什么？
- 商品最大的负面痛点是什么？
- 哪些卖点值得强调？
- FAQ 应该怎么写？
- 商品文案应该如何优化？

这个项目希望把“评论阅读与总结”变成一条可复用、可解释、可评估的 AI workflow。

## 我希望证明的能力

这个项目不是为了堆技术名词，而是为了集中展示以下能力证据：

- 业务理解：围绕电商商品优化场景识别真实问题。
- AI 产品设计：把能力拆成输入、抽取、总结、生成、引用、评估几个环节。
- 工程落地意识：前后端协同、接口设计、上传数据、结果结构化展示。
- 数据闭环：通过引用覆盖率、结构完整度等指标做基础评估。

## 当前版本包含什么

- 内置商品评论样例数据
- 上传自定义评论 JSON
- 正向/负向主题抽取
- 核心问题提炼
- 卖点建议与 FAQ 草案
- 优化方向输出
- `v1` 与 `v2` 提示词工作流对比
- citation drawer：点击引用可查看原始评论
- 核心摘要：将原始评论压缩为可讲述的业务判断
- `site/` 下的纯静态展示版，可部署到 GitHub Pages

## 当前版本的真实状态

已完成：

- 本地交互式前端页面
- Python 标准库后端接口
- 评论数据上传与解析
- 样例数据分析与可视化
- 引用回看交互
- 工作流对比页
- PRD、架构、API 与简历包装文档

未完成：

- 真实 LLM provider 接入
- 公网部署
- 用户账号体系
- 数据库存储与历史分析记录
- 更真实的人工评测闭环

## 适合作为怎样的作品

当前最适合作为：

- AI 产品岗作品集中的主项目雏形
- GitHub 展示项目
- 面试时讲解“如何设计 AI workflow 与评估闭环”的案例

如果要作为最终版主讲项目，建议再完成两步：

1. 接入真实 LLM
2. 部署为公网可访问 demo

## 核心工作流

当前版本的分析链路：

1. 输入评论数据
2. 抽取正负向主题
3. 提炼用户关注问题
4. 生成卖点、FAQ 与优化方向
5. 给每条结论附引用
6. 对比不同提示词工作流输出

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

## 公网部署

仓库内已经包含 GitHub Pages 工作流：

- 工作流文件：`.github/workflows/deploy-pages.yml`
- 静态站点目录：`site/`
- 预期公开地址：`https://yuyangjungle.github.io/ecommerce-review-insight/`

说明：

- `apps/` 下是本地完整 demo，依赖 Python 服务。
- `site/` 下是纯静态展示版，不依赖后端，适合公网作品集展示。

## 目录说明

```text
apps/api/             轻量后端与 mock pipeline
apps/web/             交互式前端 demo
data/sample/          演示用样例数据
docs/                 PRD、架构、API、作品包装材料
prompts/              提示词模板
scripts/              本地运行脚本
site/                 GitHub Pages 静态展示版
```

## 文档入口

- 产品需求：[docs/prd.md](./docs/prd.md)
- 技术架构：[docs/architecture.md](./docs/architecture.md)
- API 草案：[docs/api.md](./docs/api.md)
- 简历包装：[docs/resume_packaging.md](./docs/resume_packaging.md)
- 作品集 case study：[docs/case_study.md](./docs/case_study.md)
- 作品集呈现建议：[docs/portfolio_guide.md](./docs/portfolio_guide.md)

## 面试时可以怎么讲

一个简洁的讲法是：

“我做了一个面向电商运营场景的 AI 产品作品。它把评论分析拆成主题抽取、问题提炼、内容生成、引用回看和工作流评估几个环节。当前版本已经做成可交互 demo，用来验证 AI workflow 的设计与结果可解释性；下一步会接入真实 LLM 并完成公网部署。”

## 下一步路线图

短期优先级：

1. 接入真实 LLM provider，替换当前 mock generation
2. 增加更真实的 Prompt A/B 评估记录
3. 部署公网 demo
4. 补截图、录屏与 GitHub 首页视觉材料

## 说明

如果你是在招聘场景里看到这个仓库，当前最推荐的阅读顺序是：

1. 先看本 README
2. 再看 [docs/case_study.md](./docs/case_study.md)
3. 最后再看代码与产品文档
