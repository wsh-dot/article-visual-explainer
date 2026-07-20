# Analysis and evidence contract

## Contents

1. [Evidence ledger](#evidence-ledger)
2. [Canonical terminology registry](#canonical-terminology-registry)
3. [Must-keep test](#must-keep-test)
4. [Claim typing and number integrity](#claim-typing-rules)
5. [Explanation and page selection](#explanation-depth-and-concept-selection)
6. [Anti-repetition and final audit](#anti-repetition-audit)

## Evidence ledger

Build the ledger before deciding layout. It must remain complete even though the visible page is selective. Every must-keep row needs a traceable source location and one primary visible home.

| Field | Meaning |
|---|---|
| Claim | Minimal proposition that can be checked independently |
| Evidence/location | Section heading, page, paragraph cue, table, figure, or short quotation cue |
| Type | `FACT`, `AUTHOR_VIEW`, `INFERENCE`, `UNCERTAINTY`, or `MISSING` |
| Confidence | High only when explicit; medium for faithful synthesis; low requires a visible caveat |
| Must keep | `yes` when removal changes the answer, mechanism, evidence, boundary, case, or consequence |
| Audience | Ordinary user, developer, enterprise, policy maker, industry, or another source-named group |
| Relationship | Sequence, state change, cause/effect, hierarchy, comparison, quantity, network, spatial, or `none` |
| Primary home | `quick-read`, `core-thread`, a deep/concept stable id, `visualizations`, or `takeaways` |
| Page action | `keep`, `merge`, or `omit`; never omit a must-keep row |

One row may support several decisions, but only its primary home explains it. A secondary mention is allowed only when it adds a mechanism, evidence item, boundary, or application that the primary home does not contain.

## Canonical terminology registry

Build this registry before drafting diagrams or tables:

| Field | Meaning |
|---|---|
| Source term | Exact visible spelling in the article |
| Canonical form | Complete product, model, paper, company, policy, architecture, or technical name to preserve |
| Approved abbreviation | An abbreviation explicitly defined by the source, otherwise `none` |
| Evidence/location | Where the source establishes the name or abbreviation |

The registry, not available card width, controls visible wording. Preserve capitalization, punctuation, version suffixes, and meaningful qualifiers. An industry-familiar abbreviation is not approved unless the source defines it. When the source uses both forms, retain the full term as `data-canonical-term` and record the abbreviation separately as `data-approved-abbreviation`.

## Must-keep test

Mark a point `must keep: yes` if removing it changes at least one of these:

- the core question or answer;
- the mechanism explaining why the answer holds;
- the magnitude, date, version, comparison basis, or boundary of a result;
- a named case that demonstrates application or failure;
- the stated limitation, risk, dispute, or uncertainty;
- the consequence for a materially affected audience.

Supporting detail may be `merge` or `omit` when it merely repeats an existing claim without changing its mechanism, evidence, boundary, or consequence. Ledger completeness is not permission to print every row.

## Claim typing rules

- `FACT`: directly reported event, specification, measurement, named artifact, or attributable statement. A report can be factual while the reported claim remains an author's view.
- `AUTHOR_VIEW`: recommendation, interpretation, causal claim, prediction, or value judgment made by the source author.
- `INFERENCE`: a conclusion introduced by the explainer. Prefix with `解读` or equivalent and state the evidence chain.
- `UNCERTAINTY`: hedged, preliminary, disputed, conditional, or method-limited information. Preserve the hedge beside the affected claim.
- `MISSING`: information readers would reasonably expect but the source does not provide. Write `原文未提供`.

Any layer count, renamed framework, merged category system, or causal bridge introduced by the explainer is `INFERENCE`, even when every ingredient comes from the source. Label the grouping `解读` and describe it as a reading aid. Do not call it the source's official, required, complete, or minimum structure unless the source explicitly does.

Do not launder `AUTHOR_VIEW` through neutral prose. Do not turn correlation into causation. Do not describe an example as representative unless the source establishes representativeness.

## Number integrity

For every important number, retain as available:

`value + unit + population/scope + time window + baseline/comparator + source caveat`

If two values use different denominators, scopes, or time windows, do not place them in a direct visual comparison. If only endpoints are given, do not fabricate intermediate trend points. Record the missing basis as `MISSING` when readers might otherwise infer a false comparison.

## Explanation depth and concept selection

Use the smallest explanation that unblocks the article:

1. one-sentence plain definition when a term is unfamiliar;
2. its role in this article's mechanism when that role matters;
3. an analogy only when it adds understanding without creating a false equivalence.

Do not automatically print all three layers. If the definition alone is sufficient, stop there. Place a concept before deep-dive when later reasoning depends on it. Place it after deep-dive when it still adds necessary definition, disambiguation, or supplementary value without blocking the argument. Omit the concepts module only when no item provides one of those three forms of value. A concept with no meaningful relationship does not need a diagram.

## Page-selection pass

After the ledger is complete and before writing HTML:

1. Group rows that answer the same reader question.
2. Choose the one row or synthesis that leads each group.
3. Assign one primary home to every must-keep row.
4. Merge only details that add evidence, boundary, or application.
5. Omit rhetoric, duplicate examples, and secondary facts that do not change the conclusion.
6. Check the planned page against the standard density target; use `expanded` only for source-essential overflow.

### Compact composition for short sources

When the ledger contains one central thesis, one mechanism or procedure, and no separate evidence clusters, begin at the minimum valid composition: 2 quick items, 3 core steps, 1 deep chapter, no concepts, no synthesis, and 2 takeaways. The page may remain below 1500 editorial units.

Do not infer that every point deserves a deep chapter. Admit a second or third chapter only after writing one sentence that names what it adds beyond all upstream modules: a new mechanism, evidence item, boundary, or application. If that sentence only renames the claim, keep one chapter.

The default page should feel progressive: quick-read states what matters, core-thread shows how the argument moves, deep-dive explains only the difficult turns, and takeaways state reusable implications rather than retelling the route.

## Anti-repetition audit

For each planned module, ask whether its longest sentence already appears in the same unit or another primary home.

Also build a temporary novelty matrix with one row per visible paragraph, caption, and takeaway:

| Visible location | Ledger row | Role | New information relative to the primary home |
|---|---|---|---|
| stable id | claim / evidence id | `claim`, `mechanism`, `evidence`, `boundary`, or `application` | one short phrase |

Delete a row when another location already carries the same ledger row in the same role and the “new information” cell cannot be filled. Paraphrase, extra adjectives, and a second diagram of the same sequence do not count as new information.

- Exact or containment-style repetition over 24 editorial units inside one unit is an error.
- Reusing a short canonical label is allowed.
- A figure caption names the relationship; it does not restate the full paragraph.
- A reading guide tells the reader how to scan; it does not narrate every node.
- Conclusions compress implications; they do not replay evidence or reproduce the article outline.
- Each conclusion must add a reusable principle, tradeoff, or decision rule. If it can be replaced by a core-thread step without changing meaning, rewrite or delete it.

If two passages compete as the primary explanation, keep the clearer one and move only genuinely new evidence or limits beside it.

## Final ledger audit

Before delivery, compare visible page content back to the ledger for:

- core thesis and article logic;
- exact facts, numbers, baselines, and dates;
- important cases and mechanisms;
- audience impact;
- risks, limits, disputes, and uncertainty;
- final conclusion and deeper implication;
- expected but absent metadata labeled `原文未提供`.

This audit is internal evidence mapping, not a visible coverage checklist.
