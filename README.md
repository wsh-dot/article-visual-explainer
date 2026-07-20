# Article Visual Explainer Skill

中文说明见下方 [中文说明](#中文说明)。

## English

`article-visual-explainer` is an AI-agent skill for turning one complete article or chapter into a source-faithful, mobile-readable, single-file HTML visual explainer.

It is designed for long-form reading and editorial explanation—not for producing a short generic summary. The skill preserves the source's argument, evidence, uncertainty, numbers, terminology, limitations, and consequences while selecting a concise reading path and meaningful visuals.

### What it does

- Acquires and checks a complete source before deep interpretation.
- Supports URL, WeChat article, Markdown, pasted text, HTML, PDF, OCR text, and scanned PDF workflows.
- Builds an evidence ledger for claims, evidence, boundaries, uncertainty, and missing information.
- Distinguishes `FACT`, `AUTHOR_VIEW`, `INFERENCE`, `UNCERTAINTY`, and `MISSING`.
- Organizes the explanation around reasoning: background → problem → mechanism → evidence → limits → implications.
- Selects HTML, SVG, tables, or embedded source images according to the relationships in the article.
- Produces a self-contained HTML file with responsive mobile reading, accessibility requirements, and no remote assets.
- Runs structural and rendered layout validation at desktop, tablet, and mobile viewport sizes.

### When to use it

Use this skill when you need:

- A shareable HTML long page for an article, report, paper, or chapter.
- A faithful visual reading aid with explicit evidence and caveats.
- An information-visualization explainer rather than a dashboard or landing page.
- A single-file artifact that can be opened locally or published as a static page.

For a short summary, bullet list, translation, or ordinary Markdown notes, this skill is usually heavier than necessary.

### Recommended installation

If your AI coding tool supports installing a skill from GitHub, use the repository URL:

```text
https://github.com/wsh-dot/article-visual-explainer
```

The repository root is the skill root and directly contains `SKILL.md`, `references/`, `assets/`, and `scripts/`.

You can also give your AI IDE this instruction:

```text
Please install the article-visual-explainer skill from:
https://github.com/wsh-dot/article-visual-explainer

The installed skill root must directly contain SKILL.md, references/, assets/, and scripts/.
```

### Manual installation

Clone the repository:

```bash
git clone https://github.com/wsh-dot/article-visual-explainer.git
```

Install for Codex on Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item -Recurse ".\article-visual-explainer" "$env:USERPROFILE\.codex\skills\article-visual-explainer"
```

For another AI IDE, copy the complete repository directory into that IDE's skills directory.

### Typical request

```text
Use the article-visual-explainer skill to turn this complete article into a
source-faithful, mobile-readable, single-file HTML visual explainer:
<article URL or pasted source>
```

The default output is `article_explainer.html`, unless another filename is requested.

### Repository layout

```text
article-visual-explainer/
├── SKILL.md
├── assets/
│   └── explainer-shell.html
├── references/
│   ├── analysis-contract.md
│   ├── html-contract.md
│   ├── layout-safety.md
│   ├── ledger-to-html-example.md
│   ├── source-routing.md
│   └── visual-system.md
└── scripts/
    ├── check_layout.py
    └── validate_explainer.py
```

### Validation

For a generated HTML file, run both validators from the repository root:

```bash
python scripts/validate_explainer.py path/to/article_explainer.html
python scripts/check_layout.py path/to/article_explainer.html
```

The full acceptance workflow also checks the rendered page at `1440x900`, `768x1024`, and `375x812` using Chrome, Edge, or Chromium. A generated page is not considered fully validated if the rendered browser check cannot run.

### Design principles

- Source completeness before interpretation.
- One primary visible home for each important claim.
- Evidence and uncertainty remain visible.
- Visuals answer explicit reader questions; decoration does not count as visualization.
- Short sources stay compact instead of being padded with repeated modules.
- Canonical product, model, paper, company, policy, and technical names are not shortened for layout.

## 中文说明

`article-visual-explainer` 是一个面向 AI 编程 Agent 的文章可视化解读 skill：它把一篇完整的文章或章节，转换成忠实于原文、适合手机阅读、可独立打开的单文件 HTML 图文解读页面。

它面向长文阅读和编辑式解读，不是普通的“总结一下”。skill 会保留原文的论证、证据、不确定性、数字、术语、限制条件和影响，同时压缩阅读路径，选择真正有信息价值的图表或 SVG。

### 主要能力

- 在深度解读之前先获取并检查完整来源。
- 支持网页、微信公众号文章、Markdown、粘贴文本、HTML、PDF、OCR 文本和扫描版 PDF。
- 建立证据台账，记录主张、证据、边界、不确定性和缺失信息。
- 区分 `FACT`（事实）、`AUTHOR_VIEW`（作者观点）、`INFERENCE`（解读/推断）、`UNCERTAINTY`（不确定性）和 `MISSING`（缺失）。
- 按“背景 → 问题 → 机制 → 证据/案例 → 限制 → 结论/影响”组织内容。
- 根据文章中的关系选择 HTML、SVG、表格或内嵌原图作为视觉表达。
- 生成不依赖远程资源的单文件 HTML，包含响应式移动端布局和可访问性要求。
- 在桌面、平板和手机尺寸下执行结构与布局检查。

### 适用场景

适合以下任务：

- 把文章、报告、论文或书籍章节做成可分享的 HTML 长页。
- 制作带证据、限制条件和来源边界的深度图文解读。
- 把文章中的机制、流程、拓扑或因果关系做成信息图。
- 生成可以本地打开、部署到静态网站或 GitHub Pages 的单文件产物。

如果只是要摘要、要点列表、翻译或普通 Markdown 笔记，这个 skill 通常会显得过重。

### 推荐安装方式

支持从 GitHub 安装 skill 的 AI 编程工具，可以直接使用：

```text
https://github.com/wsh-dot/article-visual-explainer
```

本仓库根目录就是 skill 根目录，直接包含 `SKILL.md`、`references/`、`assets/` 和 `scripts/`。

也可以把下面这段话发送给 AI IDE：

```text
请从这个 GitHub 仓库安装 article-visual-explainer skill：
https://github.com/wsh-dot/article-visual-explainer

安装后的 skill 根目录必须直接包含 SKILL.md、references/、assets/ 和 scripts/。
```

### 手动安装

先 clone 仓库：

```bash
git clone https://github.com/wsh-dot/article-visual-explainer.git
```

安装到 Codex Skills（Windows PowerShell）：

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item -Recurse ".\article-visual-explainer" "$env:USERPROFILE\.codex\skills\article-visual-explainer"
```

其他 AI IDE 也类似：将完整的 `article-visual-explainer/` 目录复制到对应的 skills 目录中。

### 典型用法

```text
请使用 article-visual-explainer skill，把下面这篇完整文章制作成忠实原文、适合手机阅读的单文件 HTML 图文解读：
<文章链接或完整正文>
```

默认输出文件名为 `article_explainer.html`，也可以在请求中指定其他文件名。

### 验证生成结果

在仓库根目录运行：

```bash
python scripts/validate_explainer.py path/to/article_explainer.html
python scripts/check_layout.py path/to/article_explainer.html
```

完整验收还需要使用 Chrome、Edge 或 Chromium，在 `1440x900`、`768x1024` 和 `375x812` 三种尺寸下检查实际渲染效果。如果无法运行浏览器渲染检查，不能宣称页面已完整通过验收。

### 核心原则

- 先确认来源完整，再进行深度解读。
- 每个重要主张只设置一个主要呈现位置。
- 证据、不确定性和限制条件必须保留。
- 视觉必须回答明确的读者问题，装饰性模块不算信息图。
- 短文章保持紧凑，不通过重复模块凑长度。
- 产品、模型、论文、公司、政策和技术术语不得为了排版而随意缩写。

### 目录结构

```text
article-visual-explainer/
├── SKILL.md                  # skill 主说明
├── assets/explainer-shell.html # HTML 起始模板
├── references/               # 分析、视觉、HTML 和布局规范
└── scripts/                  # HTML 与布局校验脚本
```

## License

Unless otherwise noted, this repository is provided for personal and agent-assisted content-production workflows. Check the source article's copyright and usage terms before redistributing generated explainers or embedded source images.
