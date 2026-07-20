# Ledger-to-HTML trace example

Load this example only when the ledger is complete but page selection, primary placement, or visual encoding remains unclear.

## 1. Ledger row

| Claim | Evidence/location | Type | Confidence | Must keep | Audience | Relationship | Primary home | Page action |
|---|---|---|---|---|---|---|---|---|
| The author argues that Harness Engineering makes an Agent controllable through explicit constraints and feedback | Section “Harness Engineering”; author’s CPU/OS analogy | `AUTHOR_VIEW` | High | yes | Developer, enterprise | cause/effect | `deep:harness-control` | keep |

The terminology registry records `Harness Engineering` as the canonical form and no approved abbreviation because this source defines none.

## 2. Page placement

Explain the row once in `data-deep-chapter="harness-control"`. Quick-read may foreshadow the conclusion in shorter language, but it must not repeat the mechanism. The deep chapter adds the source-supported mechanism and its engineering consequence.

```html
<article data-deep-chapter="harness-control">
  <h3 id="harness-heading">把约束变成可控执行</h3>
  <p><strong>作者观点：</strong>可靠性不只来自提示词，还来自明确约束与持续反馈形成的执行环境。</p>

  <figure
    data-viz="harness-causal-chain"
    data-inline-viz
    data-viz-renderer="html"
    data-viz-kind="causal-chain"
    aria-labelledby="harness-caption"
    aria-describedby="harness-guide"
  >
    <figcaption id="harness-caption">约束如何影响 Agent 执行</figcaption>
    <p id="harness-guide" data-reading-guide>从左到右看工程机制如何收窄行为边界。</p>
    <div class="viz-flow">
      <div data-viz-node>
        <strong data-viz-label>显式约束</strong>
        <span data-viz-detail>权限、停止条件与可验证结果</span>
      </div>
      <div data-viz-node>
        <strong data-viz-label data-canonical-term="Harness Engineering">Harness Engineering</strong>
        <span data-viz-detail>把约束落实到执行与反馈</span>
      </div>
      <div data-viz-node>
        <strong data-viz-label>可控执行</strong>
        <span data-viz-detail>越界时停下，失败后可回退</span>
      </div>
    </div>
  </figure>

  <p><strong>文章依据：</strong>原文以 CPU/OS 类比说明模型能力需要外部工程环境约束。</p>
  <p><strong>应用：</strong>开发团队应把权限、验证和反馈回路纳入可靠性设计。</p>
</article>
```

There is no visible “文字版” or `data-text-alternative`. The caption names the question, the guide explains scan direction, semantic nodes expose the mechanism, and adjacent prose carries evidence and application without repeating the node sequence as a full sentence.

## 3. Why this visual

The reader question is “what mechanism connects constraints to controllable execution?” The source presents a directional argument, so `causal-chain` with an `html` renderer fits. If the source reported association only, remove the directional causal encoding and use `comparison`. If the relationship required crossing feedback loops or several interacting subsystems, keep the same claim placement but switch the visual root to an accessible `svg` architecture or network graphic.

## 4. Selection check

- **Ledger complete:** source evidence, claim type, audience, and boundary remain traceable.
- **Page selective:** the chapter prints only the judgment, mechanism, one evidence note, and one application.
- **One primary home:** another module cannot reproduce this mechanism unless it adds a new boundary or case.
- **Visual earned:** the causal relationship is explicit in the source; the figure is not present merely to decorate the chapter.
- **Compact by default:** if this is the only difficult turn in a short source, stop at one deep chapter and two page-level visuals. Do not turn its evidence and application into separate chapters or redraw the same causal path in the conclusion.
