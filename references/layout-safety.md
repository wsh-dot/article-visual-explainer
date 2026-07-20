# Cross-model layout safety contract

Read this reference before writing or modifying CSS. These are acceptance invariants, not suggestions. The purpose is to make output quality depend on executable gates rather than on the generating model's visual judgment.

## Readability floors

- No rendered text below 14px at any tested viewport.
- Body copy is at least 16px for paragraphs, list items, table cells, quotations, definitions, and figure captions.
- Secondary labels may use 14px only for metadata, navigation, tags, eyebrows, and short importance labels.
- Headings render at no less than 32px (`h1`), 24px (`h2`), 18px (`h3`), and 16px (`h4`).
- Chinese body copy uses a computed line height of at least 1.5 unless a heading or compact label requires a tighter value.

Use absolute floors inside responsive expressions, for example `clamp(2rem, 5vw, 4.5rem)` or `max(.875rem, 14px)`. Never use viewport-only font sizing such as `font-size: 1.2vw`; it collapses on narrow screens.

## Overflow invariants

- The document must have no page-level horizontal overflow at 1440 × 900, 768 × 1024, or 375 × 812 CSS pixels.
- Text containers must grow vertically. Never use fixed height plus hidden overflow on text containers.
- Do not use `white-space: nowrap` for titles, paragraphs, evidence, ordinary labels, or card content. The only text exception is `data-viz-label`: it may use `nowrap` because its semantic primary label must remain one line, but it must pass the rendered wrap and overflow checks at every required viewport.
- Every Grid/Flex child that contains text gets `min-width: 0`; fractional tracks use `minmax(0, 1fr)` so long tokens cannot force the track wider.
- Long URLs, English identifiers, and uninterrupted strings use `overflow-wrap: anywhere` or an equivalent safe wrap rule.
- Images, SVG, canvas, video, and iframe elements use `max-width: 100%` and preserve aspect ratio. Information SVGs also use a `viewBox` and responsive dimensions; never solve mobile fit by shrinking the entire graphic below its label floor.
- Wide tables and intentionally scrollable navigation live inside a bounded wrapper marked `data-overflow-ok`; the exception belongs on the scroll container, never on the whole page.
- A genuinely visual-only clipped region must be marked `data-visual-only` and must not contain meaningful text.
- At 375 × 812, every `[data-deep-layout]` renders as one column with the visual before its explanation. Any HTML semantic-node grid that remains—whether in core, deep, or concepts—collapses to one readable column when labels cannot fit.
- Every `data-viz-label` renders on exactly one line at 16px or larger, stays inside its node, and contains no forced `<br>`. Its sibling `data-viz-detail` may wrap naturally.
- Every information-bearing SVG `<text>` carries `data-viz-label`, renders at 16px or larger, remains inside the SVG viewBox, and is legible without zoom at all three required viewports. Remove decorative `<text>` or mark it `aria-hidden="true"`. Put long prose in adjacent HTML rather than compressing it into the SVG.

## Immutable template guard

Preserve both `<html data-layout-guard="v2">` and every line from the `LAYOUT_GUARD_V2` marker through the `END_LAYOUT_GUARD_V2` marker in `assets/explainer-shell.html`. Models may change palette, spacing, card style, and composition outside those markers, but must not delete, reorder, override with weaker values, or otherwise weaken the guarded rules.

The static validator rejects:

- missing guard markers;
- font declarations with an absolute floor below 14px;
- viewport-only font sizes without a 14px floor;
- fixed-height plus hidden/clip overflow patterns outside visual-only regions;
- missing responsive rules and structural contract violations.

The rendered checker opens the page through Chrome DevTools Protocol at exact CSS viewports and rejects:

- computed text below the relevant floor;
- undersized headings;
- page-level or element-level horizontal overflow;
- meaningful text clipped by hidden/clip overflow;
- information-bearing SVG `<text>` without `data-viz-label`, SVG labels below 16px, labels outside their viewBox, or labels overflowing their visual root;
- SVG renderers without a valid viewBox or accessible name/description;
- keyboard focus that skips or repeats controls, uses a positive tabindex, or lacks a visible focus indicator;
- a browser viewport that differs from the requested dimensions.

## Repair order

When a gate fails, repair in this order:

1. Remove fixed widths/heights and clipping from content containers.
2. Add `min-width: 0`, safe wrapping, and bounded media.
3. Collapse semantic node grids at an earlier breakpoint, reduce columns, or make the visual full-width until every HTML or SVG `data-viz-label` fits on one line at 16px or larger.
4. Put legitimately wide tables/navigation inside `data-overflow-ok` wrappers.
5. Shorten redundant labels without deleting source meaning.

Never reduce font size to make a failing layout pass. Never add page-level `overflow-x: hidden` or `clip`; that masks the defect and can hide content from the reader.

## Acceptance command

Run both commands on the final file, not only the template:

```bash
python scripts/validate_explainer.py /absolute/path/to/article_explainer.html
python scripts/check_layout.py /absolute/path/to/article_explainer.html
```

Accept only zero errors from both commands. If no Chromium-family browser is available, report the artifact gate as not run and do not claim cross-model layout safety.
