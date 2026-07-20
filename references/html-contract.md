# Adaptive single-file HTML contract

## Contents

1. [Document shell and modules](#required-document-shell)
2. [Density and repetition](#density-and-unit-limits)
3. [Major visual roots](#major-visual-roots)
4. [Renderer contracts](#renderer-contracts)
5. [Accessible naming](#accessible-naming-without-repetition)
6. [Evidence, resilience, and styling](#evidence-presentation)
7. [Final checks](#final-checks)

## Required document shell

Produce a UTF-8 HTML5 document containing `<!DOCTYPE html>`, `<html lang="zh-CN" data-layout-guard="v2" data-density="standard">`, viewport metadata, one embedded `<style>`, a top-level `<header data-module="hero">` before `<main>`, `<nav>` when useful, `<main>`, and `<footer>`. The hero is not nested in `<main>`. Use `data-density="expanded"` only under the density rules below. Preserve every line from `LAYOUT_GUARD_V2` through `END_LAYOUT_GUARD_V2` unchanged and do not link external stylesheets, fonts, scripts, icons, or libraries.

For a new page without a supplied reference, start from `assets/explainer-shell.html`. Replace all placeholders and duplicate, move, or remove optional units according to the source. Preserve the editorial rhythms; do not rebuild the page as a repeated rounded-card grid.

## Module interface

Use each required marker exactly once:

| Module | Required content and count |
|---|---|
| `data-module="hero"` | A top-level `<header>` before `<main>`; an optional page nav may sit between them; include one `h1`, source title, one-sentence thesis, plain-language reading guide, source URL or missing label, and available author/date/publisher |
| `data-module="quick-read"` | 2–3 units marked `data-quick-item`; each states one takeaway and only the context needed to understand it |
| `data-module="core-thread"` | 3–5 ordered units marked `data-core-step`; normally contains one relationship visual for the article's logic |
| `data-module="deep-dive"` | 1–3 chapters marked `data-deep-chapter`; each has one core judgment, necessary explanation, and optional evidence or limits |
| `data-module="takeaways"` | 2–3 conclusions marked `data-takeaway`; each adds a reusable principle, tradeoff, or decision rule rather than replaying quick-read wording or core-thread steps |

Optional markers may appear zero or one time:

| Module | Contract |
|---|---|
| `data-module="concepts"` | 1–3 units marked `data-concept-card`; put prerequisites before deep-dive, put definitions/disambiguations with genuine supplementary value after it, and omit the module only when it adds no necessary definition, disambiguation, or supplementary value |
| `data-module="visualizations"` | Exactly one cross-chapter synthesis visual; omit when the core thread and chapter visuals already explain the article |

The markers `data-module="key-table"` and `data-module="coverage"` are forbidden. Real comparison/data tables are allowed inside the chapter or synthesis where their evidence is interpreted. Internal ledger coverage remains an analysis step, not a visible module.

Use CSS counters for visible section numbers. Number module order as rendered so removing or moving an optional module never creates a gap.

## Density and unit limits

An editorial unit is one CJK character, one Latin word, or one numeric group in visible text. The document density count covers visible text inside `<main>` only; it excludes the preceding hero, plus `script`, `style`, hidden content, and `aria-hidden="true"` section indexes. Unit caps include headings, captions, guides, and prose inside the marked unit unless a narrower paragraph cap is listed.

| Unit | Count | Per-unit limit |
|---|---:|---:|
| `data-quick-item` | 2–3 | 120 editorial units |
| `data-core-step` | 3–5 | 70 |
| `data-deep-chapter` | 1–3 | 320; every prose paragraph at most 120 |
| `data-concept-card` | 0–3 | 140; every prose paragraph at most 70 |
| `data-module="visualizations"` | 0–1 | one synthesis visual |
| `data-takeaway` | 2–3 | 80 |

- `standard`: target 1500–2200 editorial units; 2200 is a hard ceiling. A faithful short source may remain below 1500 and must not be padded.
- `expanded`: hard ceiling 2600. Use it only for source-essential content that cannot fit standard density. The validator must emit a manual-confirmation warning and the handoff must disclose it.
- More words are not a substitute for progression. If a page exceeds a cap, merge duplicate evidence, remove secondary examples, or move a claim back to its primary home before switching density.

For a short source with one central thesis and no separate evidence clusters, begin with the minimum valid counts: quick 2, core 3, deep 1, concepts 0, synthesis 0, takeaways 2, and visuals 2. These are editorial defaults rather than validator heuristics: exceed one only when its unit adds a separately nameable mechanism, evidence item, boundary, or application.

## Claim placement and repetition

Every must-keep ledger claim has one primary visible home. A later unit may mention it only when it adds mechanism, evidence, boundary, or application.

Before composing HTML, complete the novelty matrix from `analysis-contract.md`. The page must not assign the same ledger row and role to two visible locations. Rewording a claim, turning it into nodes, or adding detail-free prose does not create a new role.

Inside the same marked quick, core, deep, concept, synthesis, or takeaway unit, normalized visible blocks of 24 or more editorial units may not be exactly repeated or wholly contain one another. This includes paragraphs, list items, captions, reading guides, and visible diagram descriptions. Short canonical labels may repeat; full explanatory sentences may not.

Do not add a visible “文字版”, a `data-text-alternative` attribute, a fixed explanation/evidence/impact triptych, or a second prose rendering of the diagram. Use surrounding prose to carry explanation once.

## Major visual roots

Use 2–5 major visual roots across the entire page. Every counted root:

- carries a unique non-empty `data-viz="stable-id"`;
- carries exactly one `data-viz-renderer="html|svg|table|source-image"`;
- carries exactly one `data-viz-kind="flow|timeline|causal-chain|hierarchy|network|architecture|state|comparison|quantitative|spatial"`;
- is not nested inside another `[data-viz]` root;
- answers one explicit reader question and uses a source-supported relationship.

A `data-viz-kind="quantitative"` root also carries a non-empty `data-comparison-basis`. The same basis text must be visible in its caption, guide, note, or table so readers can see the unit, scope, time window, or comparator rather than relying on metadata.

The core-thread visual is a normal `[data-viz]` root. Add `data-inline-viz` to a visual inside a deep chapter and `data-concept-viz` to a visual inside a concept card. These placement markers do not create additional counts. A chapter or concept may be text-only when no meaningful relationship exists; total visual count remains a page-level gate. A `visualizations` module, when present, contains exactly one `[data-viz]` root.

Use one dominant visual grammar and at most one supporting grammar. Different `data-viz-kind` values may share the same grammar; changing renderer or node style in every section is not acceptable variation.

Renderer boundary for architecture: HTML is valid only when layers or branches stay on one reflowable axis. Shared buses, cross-layer fan-out/fan-in, feedback routes, peer event links, or other multi-axis topology require inline SVG. The SVG should be the dominant architecture visual rather than a decorative supplement to an HTML card grid.

## Renderer contracts

### HTML visual

- Use semantic HTML and visible relationship structure, not bordered prose pretending to be a diagram.
- Provide at least two non-empty `data-viz-node` elements for multi-part relationships.
- Give each node exactly one non-empty `data-viz-label`; optional wrapping copy belongs in `data-viz-detail`.
- Keep `data-viz-label` on one rendered line, with no `<br>`, at 16px or larger.
- When a label contains a registered term, place the exact full form in `data-canonical-term`. Use `data-approved-abbreviation` only for a source-defined abbreviation.

### SVG visual

- Place one inline `<svg>` inside the root. It must use `viewBox`, responsive dimensions, `role="img"`, and an accessible name.
- Expose an accessible name and description through either non-empty `<title>` plus `<desc>`, or equivalent `aria-labelledby`/`aria-describedby` associations to concise HTML text.
- Use existing CSS custom properties for color and no external fonts, scripts, or images.
- Put `data-viz-label` on every information-bearing SVG `<text>`; each must render at 16px or larger and remain inside the viewBox on mobile. Remove purely decorative `<text>` or mark it `aria-hidden="true"`.
- Keep only short labels inside SVG. Put paragraphs, evidence, limitations, and long instructions in HTML outside it.
- SVG may encode information structure only; decorative illustration is not a valid major visual.

### Table visual

- Use one semantic `<table>` with a non-empty descriptive `<caption>` and correct row/column headers.
- State the shared comparison basis, unit, time window, and source caveat where applicable.
- For a quantitative table, mirror that visible basis exactly in `data-comparison-basis` on the visual root.
- Do not compare incompatible denominators or fabricate missing values.
- Put wide tables inside a bounded `data-overflow-ok` wrapper; never create page-level overflow.
- Do not use a generic table that merely restates every chapter.

### Source-image visual

- Use one meaningful `<img>` with non-empty `alt`; include width/height attributes or an aspect-ratio-safe wrapper marked `data-aspect-ratio`.
- Preserve the single-file contract by embedding the asset as a data URI or equivalent inline resource. Remote image URLs and hotlinks are forbidden.
- Add a visible caption that identifies what the reader should notice and attributes the original source.
- Do not strip source context or use an unrelated stock image.

## Accessible naming without repetition

Every visual root needs a descriptive caption or heading and one short `data-reading-guide`. Use `aria-label`, `aria-labelledby`, and `aria-describedby` to connect that content when native semantics do not already do so.

- HTML visuals: accessible name from a caption/heading; description from the reading guide and adjacent non-duplicative prose.
- SVG visuals: accessible name and description from either `<title>`/`<desc>` or equivalently associated HTML through `aria-labelledby`/`aria-describedby`.
- Tables: native caption and header associations.
- Source images: meaningful `alt`, caption, and attribution.

The reading guide explains direction or encoding, such as “从左到右看状态如何变化”; it must not narrate all node content. Do not hide a full duplicate paragraph for screen readers—semantic structure and concise associations are sufficient.

## Evidence presentation

- Label source-dependent support as `文章依据` or another explicit term only when attribution would otherwise be unclear.
- Mark author interpretation with `作者观点`, forecasts with `趋势判断/推测`, and explainer-added reasoning with `解读`.
- Place caveats beside the affected claim, not only in a final disclaimer.
- Use `原文未提供` for absent expected metadata or evidence.
- Use `<blockquote>` sparingly; paraphrase unless a short exact quotation is essential.

Evidence does not require a fixed three-column band. Use one compact note, caption, table note, or adjacent paragraph where it supports the primary explanation.

## Accessibility and resilience

- Use one `<h1>` and sequential heading levels.
- Keep the skip link and visible `:focus-visible` treatment when navigation is present.
- Give meaningful source images `alt`; decorative images should normally be omitted.
- Make interactive controls keyboard-accessible; omit interaction when static HTML communicates the same information.
- Resolve every internal anchor and add `scroll-margin-top` when navigation is sticky.
- If the source URL is absent, replace the hero link with visible text `原文链接未提供`; never leave an empty or placeholder `href`.
- If smooth scrolling or transitions remain, include a `prefers-reduced-motion` override.
- Preserve useful content when JavaScript is disabled; inline JavaScript must be minimal and network-independent.

## Styling boundaries

Use CSS custom properties for palette, type scale, spacing, borders, and radius. Prefer Grid/Flexbox, bounded content width, and `clamp()` for responsive headings.

Without a supplied reference, retain the shell's editorial / precise / calm system: warm paper, dark ink, one deep-teal accent, thin rules, small radii, no routine shadows, and one strategic high-contrast narrative break. Preserve distinct rhythms for quick-read, core-thread, deep-dive, optional concepts/synthesis, and takeaways without giving every module a separate visual language.

## Final checks

Run both deterministic validators from `SKILL.md`. Inspect the first screen, the densest deep chapter, every visual renderer, the widest source table, and the conclusion. At each required viewport, Tab through the skip link, source link, navigation, and controls; verify visible focus and logical order. A structurally valid file still fails rendered QA if it clips, overflows, mislabels evidence, repeats content, weakens hierarchy, invents visual relationships, or uses decorative SVG as information.
