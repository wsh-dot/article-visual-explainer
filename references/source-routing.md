# Source acquisition routing

Use this reference only when the input is not already complete pasted Markdown or plain text.

## Routing table

| Source | Primary path | Completeness proof | Fallback |
|---|---|---|---|
| Public URL | Open the canonical page; extract rendered body and metadata | First heading, full body, and terminal paragraph/credits are present | Use an alternate readable rendering or ask for exported HTML/Markdown |
| WeChat article | Use the user's chosen browser on the exact `mp.weixin.qq.com/s/...` URL; capture rendered content, not search snippets | Account header, article title, body, and footer/ending are present | Ask for browser export, pasted body, PDF, or full-page capture |
| HTML file | Read the local file directly; isolate the main article from navigation and comments | Main body has a coherent start and end | Parse a saved-page folder only if its assets are required |
| Markdown/text | Treat the supplied content as authoritative | No truncation marker; ending is coherent | Ask whether omitted appendices or tables exist when the text signals them |
| Text PDF | Extract all pages in reading order, including tables/captions | Page count matches extraction; final page is present | Use a document extraction tool that preserves layout |
| Scanned PDF | OCR all relevant pages, then inspect low-confidence regions | Page count matches; headings and numeric tables survive OCR | Ask for a clearer scan when critical values remain ambiguous |

## Completeness checks

Verify all that apply:

1. Metadata and body refer to the same article.
2. The acquisition includes the conclusion, limitations, afterword, or references if present.
3. Lazy-loaded sections and collapsed blocks have been expanded.
4. Tables retain headers, units, notes, and row/column association.
5. Image-only evidence has a caption or a faithful textual observation; do not guess unreadable labels.
6. Duplicate mobile/desktop DOM copies are deduplicated without dropping unique content.

## Access failures

- Treat anti-bot pages, login prompts, empty app-browser tabs, and safety-policy blocks as acquisition failures, not empty articles.
- Do not disable local-file or browser safety protections merely to automate a preview.
- Do not replace an inaccessible original with third-party summaries unless the user explicitly accepts a secondary source.
- When only screenshots or videos are available, inventory their temporal/page coverage. Mark the source `PARTIAL` unless they visibly cover the full article.

## Metadata discipline

Preserve source spelling for names, product/model versions, organizations, and dates. If author, publisher, publication time, or URL is absent, emit `原文未提供`; do not estimate it from file timestamps or surrounding UI.
