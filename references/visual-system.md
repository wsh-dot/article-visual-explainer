# Relationship-driven visual system

## Contents

1. [Select by relationship](#select-by-relationship)
2. [Choose a renderer](#choose-a-renderer)
3. [Control visual count and grammar](#control-visual-count-and-grammar)
4. [Compose the reading rhythm](#compose-the-reading-rhythm)
5. [Build accessible visual roots](#build-accessible-visual-roots)
6. [Use custom SVG only for information](#use-custom-svg-only-for-information)
7. [Protect label fit and responsive reading](#protect-label-fit-and-responsive-reading)
8. [Apply the default editorial direction](#apply-the-default-editorial-direction)

## Select by relationship

Name the reader question and source-supported relationship before choosing a form.

| Article relationship | Reader question | Preferred form | Avoid |
|---|---|---|---|
| Steps, operations, state change | What happens in what order or after which trigger? | Flow, state diagram, timeline | Unordered card grid |
| Cause and result | What mechanism connects cause to outcome? | Causal chain or branching causal diagram | Causal arrows for correlation |
| System, architecture, hierarchy | What contains, depends on, or controls what? | Layered diagram, architecture, tree | Timeline |
| Several objects with the same fields | How do alternatives differ on a common basis? | Comparison table, parallel structure, small multiples | Separate prose cards |
| Real values with one common basis | How large or how fast is the difference? | Bars, dots, line chart, compact data table | Invented values or mismatched denominators |
| Network, spatial, or crossing connections | How do non-linear parts connect? | Custom inline SVG information graphic | Dense HTML arrows or decorative map shapes |
| One concept with no relationship | What does this term mean here? | One-sentence definition or annotated example | A forced multi-node diagram |
| Decisive source figure or chart | What did the source itself show? | Preserve the source image with attribution | Redrawing it without a fidelity reason |

The source controls the strength of the arrows. If evidence shows association only, use adjacency or comparison instead of a causal chain.

## Choose a renderer

Choose the implementation after the relationship:

| Renderer | Use when | Minimum structure |
|---|---|---|
| `html` | A simple flow, timeline, state, hierarchy, causal chain, or parallel comparison can reflow cleanly | Semantic nodes, short labels, visible connectors or grouping, caption/heading, reading guide |
| `svg` | Topology, crossing connections, spatial layout, network, or architecture needs exact placement | Responsive inline SVG, accessible name and description, short labels, source-faithful connections |
| `table` | Several objects share fields or real values need exact lookup | Semantic table, descriptive caption, headers, common comparison basis, bounded horizontal scroll if needed |
| `source-image` | The source already supplies the decisive chart, figure, or annotated image | Inline data URI or equivalent embedded resource, meaningful `alt`, visible source attribution, intrinsic dimensions or a `data-aspect-ratio` wrapper |

Use topology as the tie-breaker. A simple one-axis stack, tree, or sequence may use HTML. A shared bus, cross-layer fan-out or fan-in, feedback path, peer-to-peer event flow, or any connection set that needs more than one axis must use responsive inline SVG. If an article describes both layers and crossing connections, the crossing connections win; do not flatten them into unrelated HTML cards.

Every counted visual root carries a stable `data-viz`, one `data-viz-renderer`, and one `data-viz-kind`. Allowed kinds are:

`flow`, `timeline`, `causal-chain`, `hierarchy`, `network`, `architecture`, `state`, `comparison`, `quantitative`, `spatial`.

Quantitative roots also carry `data-comparison-basis`; repeat that exact basis visibly beside the values so the unit, scope, time window, or comparator cannot disappear into implementation metadata.

The renderer describes how the visual is built; the kind describes what relationship it communicates. Do not use renderer changes to disguise duplicated content.

## Control visual count and grammar

- Use 2–5 major visual roots in the whole page. Count unique `[data-viz]` roots; never nest one counted root inside another.
- Mark a chapter visual with `data-inline-viz` in addition to `data-viz`, and a concept visual with `data-concept-viz` in addition to `data-viz`.
- The core thread normally supplies one major visual. A separate `visualizations` module is optional and contains at most one synthesis visual.
- A deep chapter or concept receives a visual only when the relationship adds comprehension. Text-only units are valid when a diagram would merely repeat prose.
- Select one dominant grammar for the article—for example ordered nodes and connectors, layered architecture, or quantitative comparison. Use at most one supporting grammar when the source requires another relationship.
- Reuse color, connector style, node shape, label hierarchy, and annotation logic across visuals. Vary composition to fit the relationship, not to make every section look different.
- Decorative icons, numbered prose boxes, duplicated figures, and colored statistics without encoding do not count.
- Prefer one decisive visual over several partial versions. Never add a chart only to reach the numeric limit; instead improve or count the source-supported core relationship.
- For a short, single-thesis source, start and normally stop at two major visuals: the core relationship and one deep mechanism, boundary, or comparison. A third visual is allowed only for an independent relationship and may not redraw the core-thread path.

## Compose the reading rhythm

Default path:

`editorial hero -> quick-read rail -> ordered core thread -> selective deep chapters -> optional concept or synthesis support -> concise takeaways`

- **Hero:** left-aligned title with a separate thesis/reading-route column on wide screens; stack title, thesis, guide, metadata, and source on mobile.
- **Quick read:** one bordered rail with internal dividers; 2–3 points that orient rather than pre-explain every chapter.
- **Core thread:** 3–5 ordered stages sharing one line, path, layer system, or state transition. It is the article's logic, not a second summary list.
- **Deep dive:** 1–3 chapters. Lead with one judgment; add only necessary explanation and optional evidence or limits. Give a visual enough width, but do not force a fixed three-node composition or a three-column evidence band.
- **Concepts:** 0–3 compact items. Place prerequisites before deep-dive. Place other definitions, disambiguations, or explanatory concepts after deep-dive only when they add genuine supplementary value. Omit the module when none of those values exists. A definition may remain text-only.
- **Synthesis:** 0–1 visual that reveals a real cross-chapter pattern. Do not duplicate chapter visuals at a larger size.
- **Takeaways:** 2–3 reusable principles, tradeoffs, or decision rules. Keep the established simple editorial form; do not reuse quick-read wording or turn the core thread back into prose.

For a short, single-thesis source, use the minimum rhythm first: 2 quick items, 3 core steps, 1 deep chapter, no concept or synthesis module, and 2 takeaways. Expand only when the evidence ledger contains genuinely separate material; low word count is not a missing section.

Real source tables and figures belong beside the claim they support. Do not create a generic engineering decision table or visible coverage checklist.

## Build accessible visual roots

Every major visual must answer one explicit question and provide:

- a descriptive heading or caption;
- one short `data-reading-guide` that explains scan direction or encoding;
- an accessible name through a caption, `aria-label`, or `aria-labelledby`;
- an accessible description through concise adjacent prose, `aria-describedby`, an SVG `<desc>`, a table caption, or image `alt` as appropriate;
- semantic labels that remain meaningful without color.

Do not create `data-text-alternative` or a visible “文字版” block. The surrounding chapter already carries the long explanation; repeating it under the figure breaks reading rhythm and creates duplicate content.

For simple HTML diagrams, each `data-viz-node` contains one primary label and may contain one supporting detail:

```html
<div data-viz-node>
  <strong data-viz-label data-canonical-term="Prompt Engineering">Prompt Engineering</strong>
  <span data-viz-detail>第一代 · 把任务说清楚</span>
</div>
```

Use `data-approved-abbreviation="MCP"` only when the source explicitly defines it. Never insert `<br>` in `data-viz-label`; wrapping explanation belongs in `data-viz-detail` or adjacent prose.

## Use custom SVG only for information

An SVG renderer is justified by non-linear information structure, not by a desire for illustration. It must:

- be inline and use a `viewBox` plus responsive `width`/`height` behavior;
- use `role="img"` and expose an accessible name and description through either non-empty `<title>` plus `<desc>`, or equivalent `aria-labelledby`/`aria-describedby` associations to concise HTML text;
- use existing CSS design tokens for color and stroke; do not introduce an unrelated palette;
- put `data-viz-label` on every information-bearing SVG `<text>` and keep each at 16px or larger at all required viewports; remove purely decorative `<text>` or mark it `aria-hidden="true"`;
- keep labels short and move paragraphs, evidence, caveats, and instructions outside the SVG;
- avoid external fonts, scripts, raster images, and network dependencies;
- preserve reading order in the DOM or provide an equivalent accessible description;
- distinguish connections by labels, shape, or pattern when color alone is insufficient.

Use HTML instead when the graphic is a simple linear sequence that needs to stack on mobile. Use a table instead when exact common-field lookup is the main task.

For a `source-image` renderer, embed the image in the single HTML file as a data URI or equivalent inline resource. Do not remote-hotlink it. Keep a visible caption or source note that attributes the original figure even when the binary asset is embedded.

## Protect label fit and responsive reading

- Use one primary message per visual.
- Keep prose near 28–42 CJK characters per line on wide screens; reserve full width for diagrams and structured comparisons.
- Keep exact values and their basis in visible text, table cells, or labeled marks. Encoding cannot be the only source of the number.
- Keep long evidence and caveats outside diagrams and attach them to the affected claim.
- Start HTML visuals with auto-fit or bounded grids. If a primary label wraps or overflows, repair in this order: reduce columns, use full width, then switch to a vertical sequence.
- At 375px, preserve logical top-to-bottom order. Tables and navigation may scroll only inside bounded `data-overflow-ok` wrappers.
- Do not truncate canonical terms, invent abbreviations, force word breaks, or reduce primary labels below 16px.

## Apply the default editorial direction

When the user supplies no visual reference, use the bundled shell's **editorial / precise / calm** direction. Treat the output as a long-form reading aid, not a marketing page or analytics dashboard.

- Use warm paper, dark mineral ink, and one deep-teal accent family. Keep 3–5 functional colors and avoid gradients.
- Use an offline-safe CJK system stack. Create display contrast through weight, width, alignment, and whitespace.
- Use a loose 8px rhythm, 4–8px radii, thin rules, and no routine card shadows. Pills are only for real tags or statuses.
- Reserve bordered surfaces for semantic visuals, source tables, or independent takeaways. Do not box every paragraph.
- Use one deliberate dark or high-contrast narrative break, normally the core thread. Optional synthesis should not introduce a second unrelated visual system.
- Keep focus visible, interaction quiet, and motion optional. Respect reduced-motion preferences.

At 1440px, 768px, and 375px, confirm title integrity, section order, visual legibility, SVG labels, bounded tables, sticky-anchor clearance, visible keyboard focus, and zero page-level horizontal overflow.
