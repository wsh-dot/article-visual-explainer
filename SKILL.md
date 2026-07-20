---
name: article-visual-explainer
description: >-
  Use when asked to turn one source article or chapter from a URL, WeChat page,
  Markdown, pasted text, HTML, PDF, OCR text, or scanned PDF into a
  source-faithful, mobile-readable, single-file HTML visual explainer. The skill
  builds a complete evidence ledger, selects only page-worthy claims, controls
  repetition and density, and chooses HTML, SVG, tables, or source images from
  the relationships in the article. Keywords include 文章深度解读, 图文总结,
  信息可视化长页, article_explainer.html, OCR, scanned PDF,
  validate_explainer.py, and check_layout.py.
---

# Article Visual Explainer

Turn one complete source article into a faithful visual reading aid. Preserve the article's argument, evidence, uncertainty, and consequences while giving the reader a clear sequence of ideas. Do not turn source coverage into visible repetition.

## Load resources deliberately

- Read `references/source-routing.md` before acquiring URL, WeChat, PDF, scanned, OCR, or partially accessible content. Skip it for fully pasted Markdown or plain text.
- Read `references/analysis-contract.md` before extracting claims. It owns the ledger, claim typing, page selection, and evidence mapping rules.
- Read `references/ledger-to-html-example.md` only when chapter placement or a visual encoding remains unclear after the ledger is complete.
- Read `references/visual-system.md` before selecting visual forms or changing the hero and layout direction. It owns relationship recognition, renderer selection, visual grammar, and SVG requirements.
- Read `references/html-contract.md` immediately before composing or revising HTML. It owns module interfaces, density limits, data attributes, accessibility, and single-file packaging.
- Read `references/layout-safety.md` before writing or changing CSS. Its numeric thresholds override aesthetic preferences.
- For a new page without a user-supplied layout, copy `assets/explainer-shell.html`, replace every `{{PLACEHOLDER}}`, retain its editorial composition hooks, and preserve everything from `LAYOUT_GUARD_V2` through `END_LAYOUT_GUARD_V2` unchanged. With a concrete visual reference, match the reference outside that protected block and the required module markers.
- Run `scripts/validate_explainer.py` and `scripts/check_layout.py` on every generated HTML. Read the scripts only when they fail or need modification.

## Workflow

### 1. Acquire the complete source

Identify the source type and follow `references/source-routing.md`. Capture the title, author, publisher, publication time, canonical URL, article body, captions, tables, and meaningful image context when present.

Default unit of work: one primary article or one chapter-level source.

Boundary rules:

- For a multi-article bundle or several independent links, ask the user to choose one canonical source unless the task is explicitly a synthesis.
- Treat comments, repost commentary, and platform discussion as outside the source body unless the user requests them as context.
- Do not treat snippets, previews, a few screenshots, or opening paragraphs as a complete article.

Set one completeness state before analysis:

- `COMPLETE`: the full body and ending were acquired.
- `PARTIAL`: name the missing region, disclose it in-page, and do not infer it.
- `BLOCKED`: stop before deep interpretation and request an accessible source or pasted text.

### 2. Build a complete evidence ledger

Follow `references/analysis-contract.md`. Record every must-keep claim, evidence item, boundary, uncertainty, and expected-but-missing field before deciding what appears on the page.

Maintain the terminology registry beside it:

- Copy product, model, paper, company, policy, architecture, and technical names exactly.
- Put each complete registered term in `data-canonical-term`; use `data-approved-abbreviation` only when the source explicitly defines it.
- Use only `FACT`, `AUTHOR_VIEW`, `INFERENCE`, `UNCERTAINTY`, and `MISSING`.
- Preserve exact numbers, units, dates, versions, baselines, cases, and limitations.

The ledger is complete; the page is selective. Every must-keep row must map to one visible primary home, but supporting rows may be merged or omitted when they do not change the mechanism, evidence, boundary, or application.

### 3. Reconstruct the logic and assign one visible home per claim

Organize by reasoning rather than paragraph boundaries:

`background -> core problem -> mechanism/argument -> evidence/cases -> limits -> conclusion -> implications`

For every page-worthy claim, choose one primary explanation location. A later module may mention it only to add a new mechanism, evidence item, boundary, or application. Delete exact restatements and containment-style paraphrases.

### 4. Set the reading path and density

Use this default rhythm, but let the source determine optional sections and placement:

`导读 -> 2–3 条速读 -> 3–5 步文章主线 -> 1–3 个重点深读 -> 可选概念/综合图 -> 2–3 条结论`

Choose the smallest composition that can carry the source before adding units. Treat the ranges above as ceilings to earn, not slots to fill.

- For a short, single-thesis source, start with the compact composition: `2 quick -> 3 core -> 1 deep -> 0 concepts -> 0 synthesis -> 2 takeaways`, with two major visuals total. Add a third quick item, core step, deep chapter, takeaway, or visual only when it introduces a distinct claim, mechanism, evidence item, boundary, or application.
- Before admitting deep chapter 2 or 3, finish this sentence: `Compared with every earlier module, this chapter newly explains ____.` If the blank is only a paraphrase, example-free restatement, or longer version of an upstream claim, delete the chapter.
- A short article may stay far below 1500 units. Never compensate for a small ledger by expanding the same thesis across more modules.

- Put concepts required to understand later reasoning before deep-dive. Put definitions, disambiguations, or explanatory concepts with genuine supplementary value after deep-dive. Omit the module only when it adds no necessary definition, disambiguation, or supplementary value.
- Use at most three concepts and at most one synthesis visual.
- Use `standard` density by default: aim for 1500–2200 editorial units. Do not pad a short source to reach 1500.
- Use `expanded` only when source-essential content cannot fit at 2200; never exceed 2600 and treat the validator's warning as a manual confirmation gate.
- Keep deep-dive to 1–3 chapters. Each chapter contains one core judgment, necessary explanation, and only source-useful evidence or limits.
- Treat any new layer count, renamed framework, or regrouping invented by the explainer as `INFERENCE`. Label it `解读`, and never present it as the source's official or minimum structure unless the source says so.
- Make takeaways pass a reuse test: each one should add a durable principle, tradeoff, or decision rule that still helps outside the article. Do not replay the quick-read wording or restate the core-thread steps.
- After drafting, run a cross-module novelty pass. For every paragraph, caption, and takeaway, name its ledger row and role: `claim`, `mechanism`, `evidence`, `boundary`, or `application`. When two locations serve the same row in the same role, keep the primary home and delete the other. Synonyms do not make repeated content new.

### 5. Select visuals from article relationships

Follow `references/visual-system.md`: identify the reader question and relationship first, then select renderer and form.

Required invariants:

- Use 2–5 meaningful major visual units across the whole page. The core thread counts when it is a marked visual; synthesis is optional and limited to one.
- Use one dominant visual grammar for the article and at most one supporting grammar.
- Prefer source images when the source already contains a decisive figure and attribution is possible. Preserve the single-file artifact by embedding the asset as a data URI or equivalent inline resource; never remote-hotlink it.
- Use `data-viz-renderer="html|svg|table|source-image"` and an allowed `data-viz-kind` on every counted visual root.
- A visual must answer one explicit reader question. Do not manufacture a chart for a definition, a weak relationship, or data without a common basis.
- A single concept without a meaningful relationship stays a concise definition or annotation; it does not need a diagram.
- When a system has a shared bus, cross-layer fan-out/fan-in, feedback paths, or connections on more than one axis, the topology—not the word “architecture”—decides the renderer: use one responsive inline SVG as the dominant visual. Reserve HTML architecture diagrams for simple one-axis layers or trees that can reflow without losing connections.
- For a short, single-thesis source, two visuals are the default ceiling as well as the minimum. A third visual must reveal an independent relationship; a second drawing of the core-thread sequence is duplication.
- Inline SVG is for information structure only, never decorative illustration. Keep long prose outside it, and mark every information-bearing SVG `<text>` with `data-viz-label`; remove decorative text or mark it `aria-hidden="true"`.
- Do not add a visible text alternative that repeats the figure. Use a caption or heading, a reading guide, semantic nodes, and accessible naming.

### 6. Compose the single-file HTML

Follow `references/html-contract.md`. Default output name: `article_explainer.html`, unless the user specifies another path.

Required modules are `hero`, `quick-read`, `core-thread`, `deep-dive`, and `takeaways`. `concepts` and `visualizations` are optional. `key-table` and `coverage` are forbidden. A real source comparison or data table may still appear inside the chapter where it provides evidence.

Default to an editorial reading composition rather than a dashboard or landing page. Preserve distinct rhythms for the quick-read rail, ordered core thread, selective deep chapters, optional concept rows, and concise conclusion. Do not turn every unit into the same rounded card or reinstate a fixed explanation/evidence/impact band.

Keep primary visual labels on one line and supporting detail outside or below them. When a canonical term does not fit, repair in this order: `reduce columns -> use full-width -> switch to vertical flow`. Never abbreviate the term, insert `<br>` in `data-viz-label`, or lower the floors in `references/layout-safety.md`.

### 7. Validate and decide

Run both validators on the final HTML at exactly `1440x900`, `768x1024`, and `375x812`. Then perform one rendered quality pass:

- The first screen reads as title -> thesis -> reading path -> source.
- Section order feels progressive; no module restates the previous module at greater length.
- In short single-thesis pages, the compact composition is used unless every additional unit passes the novelty sentence above.
- Takeaways add implications rather than repeating the quick-read claims or migration sequence.
- Visual form matches the source relationship, labels remain legible, and the page uses at most one supporting visual grammar.
- Mobile navigation is scrollable, keyboard focus is visible, SVG labels remain readable, and deep content reads top to bottom.
- No generic AI-template treatment remains: gratuitous gradients, routine shadow cards, decorative emoji, or a new color/style in every section.

Acceptance gates:

1. `Source gate`: acquisition is `COMPLETE`, or every missing region is disclosed in-page.
2. `Evidence gate`: every must-keep ledger row maps to visible content with the correct claim type, terminology, number basis, and caveat.
3. `Artifact gate`: both validators return zero errors; density, section counts, visual counts, renderer rules, duplication checks, responsive layout, focus visibility, and mobile reading order pass. An `expanded` warning requires manual confirmation before delivery. If no Chrome, Edge, or Chromium is available, this gate fails.

Fix every `ERROR`; review every `WARN` against the source. A manual preview may add evidence but cannot waive a failed or unavailable rendered check.

## Non-negotiable rules

- Never deeply interpret before establishing source completeness. Missing endings often contain the conclusion, limits, or reversal.
- Never convert an author's opinion, prediction, or causal interpretation into fact. Never cite a number without its unit and comparison basis, and never invent data.
- Keep one primary visible explanation per claim. Later reuse must add mechanism, evidence, boundary, or application.
- Choose a visual only after naming the relationship. Do not force a visual for a standalone concept or count decoration, colored prose boxes, or duplicated figures as information graphics.
- Do not generate visible `key-table`, `coverage`, or `data-text-alternative` blocks. Put real evidence where the claim is explained.
- Never shorten a canonical term to make it fit. Never remove `LAYOUT_GUARD_V2`, lower its floors, or hide overflow to mask a layout defect.
- Do not include unrelated stock imagery, unverified assets, external fonts, scripts, or libraries.
- Never claim a validator or rendered check passed without running it.

## Delivery

Return the clickable absolute path to the HTML and state the structural and rendered validation result. If acquisition was partial or density is `expanded`, disclose that limitation or confirmation explicitly.
