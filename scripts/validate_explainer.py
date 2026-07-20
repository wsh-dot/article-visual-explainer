#!/usr/bin/env python3
"""Validate the adaptive article-visual-explainer HTML contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable, Iterator


REQUIRED_MODULES = {"hero", "quick-read", "core-thread", "deep-dive", "takeaways"}
OPTIONAL_MODULES = {"concepts", "visualizations"}
FORBIDDEN_MODULES = {"key-table", "coverage"}
ALLOWED_MODULES = REQUIRED_MODULES | OPTIONAL_MODULES
ALLOWED_RENDERERS = {"html", "svg", "table", "source-image"}
ALLOWED_VIZ_KINDS = {
    "flow",
    "timeline",
    "causal-chain",
    "hierarchy",
    "network",
    "architecture",
    "state",
    "comparison",
    "quantitative",
    "spatial",
}
ALLOWED_CLAIM_TYPES = {"FACT", "AUTHOR_VIEW", "INFERENCE", "UNCERTAINTY", "MISSING"}
LAYOUT_GUARD_MARKER = "LAYOUT_GUARD_V2"
LAYOUT_GUARD_END_MARKER = "END_LAYOUT_GUARD_V2"
MIN_TEXT_PX = 14.0
MIN_VIZ_LABEL_PX = 16.0
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z0-9_-]+\}\}")
CANONICAL_SHELL = Path(__file__).resolve().parent.parent / "assets" / "explainer-shell.html"
VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}
NON_VISIBLE_TAGS = {"script", "style", "template", "noscript", "title", "desc"}
BLOCK_TAGS = {"p", "li", "blockquote", "dd", "dt", "figcaption"}


@dataclass
class Node:
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    parent: "Node | None" = None
    parts: list["Node | str"] = field(default_factory=list)

    def has(self, name: str) -> bool:
        return name.lower() in self.attrs

    def get(self, name: str, default: str = "") -> str:
        return self.attrs.get(name.lower(), default)


class DOMParser(HTMLParser):
    """Small HTML tree builder; sufficient for deterministic contract checks."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("#document")
        self.stack = [self.root]
        self.has_doctype = False

    def handle_decl(self, decl: str) -> None:
        if decl.strip().lower() == "doctype html":
            self.has_doctype = True

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        node = Node(
            tag=tag,
            attrs={name.lower(): value or "" for name, value in attrs},
            parent=self.stack[-1],
        )
        self.stack[-1].parts.append(node)
        if tag not in VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        self.stack[-1].parts.append(data)


def walk(node: Node) -> Iterator[Node]:
    for part in node.parts:
        if isinstance(part, Node):
            yield part
            yield from walk(part)


def descendants(node: Node) -> list[Node]:
    return list(walk(node))


def is_descendant(node: Node, ancestor: Node) -> bool:
    current = node.parent
    while current is not None:
        if current is ancestor:
            return True
        current = current.parent
    return False


def hidden(node: Node) -> bool:
    current: Node | None = node
    while current is not None:
        inline_style = current.get("style")
        style_hidden = bool(re.search(r"(?:^|;)\s*(?:display\s*:\s*none|visibility\s*:\s*hidden)(?:;|$)", inline_style, re.I))
        if (
            current.tag in NON_VISIBLE_TAGS
            or current.has("hidden")
            or current.get("aria-hidden").lower() == "true"
            or style_hidden
        ):
            return True
        current = current.parent
    return False


def visible_text(node: Node) -> str:
    if hidden(node):
        return ""
    chunks: list[str] = []

    def collect(current: Node) -> None:
        if hidden(current):
            return
        for part in current.parts:
            if isinstance(part, str):
                chunks.append(part)
            else:
                collect(part)

    collect(node)
    return re.sub(r"\s+", " ", "".join(chunks)).strip()


def raw_text(node: Node) -> str:
    chunks: list[str] = []

    def collect(current: Node) -> None:
        for part in current.parts:
            if isinstance(part, str):
                chunks.append(part)
            elif part.tag not in {"script", "style", "template", "noscript"}:
                collect(part)

    collect(node)
    return re.sub(r"\s+", " ", "".join(chunks)).strip()


EDITORIAL_TOKEN_RE = re.compile(
    r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
    r"|[A-Za-z]+(?:['’\-][A-Za-z]+)*"
    r"|\d+(?:[.,:/\-]\d+)*(?:[%％])?"
)


def editorial_units(text: str) -> int:
    return len(EDITORIAL_TOKEN_RE.findall(text))


def normalized_block(text: str) -> str:
    return re.sub(r"[^0-9A-Za-z\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]+", "", text).lower()


def nodes_with_attr(nodes: Iterable[Node], name: str, value: str | None = None) -> list[Node]:
    result = []
    for node in nodes:
        if not node.has(name):
            continue
        if value is None or node.get(name) == value:
            result.append(node)
    return result


def nodes_by_tag(nodes: Iterable[Node], tag: str) -> list[Node]:
    return [node for node in nodes if node.tag == tag]


def unit_label(node: Node, attr: str) -> str:
    return f'{attr}="{node.get(attr) or "missing"}"'


def validate_stable_values(nodes: list[Node], attr: str, errors: list[str]) -> None:
    values = [node.get(attr).strip() for node in nodes]
    if any(not value for value in values):
        errors.append(f"{attr} values must be non-empty stable ids")
    duplicates = sorted({value for value in values if value and values.count(value) > 1})
    if duplicates:
        errors.append(f"duplicate {attr} values: " + ", ".join(duplicates))


def validate_count(name: str, nodes: list[Node], minimum: int, maximum: int, errors: list[str]) -> None:
    if not minimum <= len(nodes) <= maximum:
        errors.append(f"expected {minimum}–{maximum} {name} units, found {len(nodes)}")


def content_blocks(unit: Node) -> list[tuple[str, str]]:
    candidates: list[Node] = []
    for node in descendants(unit):
        if node.tag in BLOCK_TAGS or node.has("data-reading-guide") or node.has("data-viz-detail"):
            if node.tag == "figcaption" and any(
                child.tag in {"p", "h2", "h3", "h4", "h5", "h6"} for child in descendants(node)
            ):
                continue
            candidates.append(node)
    candidate_ids = {id(node) for node in candidates}
    candidates = [
        node
        for node in candidates
        if not any(id(ancestor) in candidate_ids for ancestor in ancestors(node))
    ]
    seen: set[int] = set()
    blocks: list[tuple[str, str]] = []
    for node in candidates:
        if id(node) in seen:
            continue
        seen.add(id(node))
        text = visible_text(node)
        if editorial_units(text) >= 24:
            blocks.append((f"<{node.tag}>", normalized_block(text)))
    return blocks


def validate_repetition(unit: Node, attr: str, errors: list[str]) -> None:
    blocks = content_blocks(unit)
    for left_index, (left_tag, left) in enumerate(blocks):
        for right_tag, right in blocks[left_index + 1:]:
            if not left or not right:
                continue
            if left == right or left in right or right in left:
                errors.append(
                    f"duplicate or containment repetition in {unit_label(unit, attr)}: {left_tag} and {right_tag}"
                )
                return


def validate_cross_unit_repetition(units: list[tuple[Node, str]], errors: list[str]) -> None:
    indexed: list[tuple[Node, str, str, str]] = []
    for unit, attr in units:
        for tag, block in content_blocks(unit):
            if block:
                indexed.append((unit, attr, tag, block))
    for left_index, (left_unit, left_attr, left_tag, left) in enumerate(indexed):
        for right_unit, right_attr, right_tag, right in indexed[left_index + 1:]:
            if left_unit is right_unit:
                continue
            if left == right or left in right or right in left:
                errors.append(
                    "cross-unit duplicate or containment repetition between "
                    f"{unit_label(left_unit, left_attr)} {left_tag} and "
                    f"{unit_label(right_unit, right_attr)} {right_tag}"
                )
                return


def parse_font_px(value: str) -> list[float]:
    values: list[float] = []
    for number, unit in re.findall(r"(-?(?:\d+(?:\.\d+)?|\.\d+))\s*(px|rem|em|pt)\b", value, re.I):
        amount = float(number)
        unit = unit.lower()
        if unit in {"rem", "em"}:
            amount *= 16.0
        elif unit == "pt":
            amount *= 96.0 / 72.0
        values.append(amount)
    return values


def extract_layout_guard(source: str) -> str | None:
    start_token = "/* LAYOUT_GUARD_V2"
    end_token = "/* END_LAYOUT_GUARD_V2 */"
    start = source.find(start_token)
    end = source.find(end_token, start + len(start_token)) if start >= 0 else -1
    if start < 0 or end < 0:
        return None
    return source[start:end + len(end_token)]


def valid_idrefs(value: str, ids: dict[str, list[Node]]) -> bool:
    refs = value.split()
    if not refs or not all(ref in ids for ref in refs):
        return False
    for ref in refs:
        targets = ids[ref]
        if not any((raw_text(node) if node.tag in {"title", "desc"} else visible_text(node)) for node in targets):
            return False
    return True


def visual_guides(root: Node, ids: dict[str, list[Node]]) -> list[Node]:
    guides = nodes_with_attr(descendants(root), "data-reading-guide")
    described = root.get("aria-describedby")
    if described:
        for ref in described.split():
            for node in ids.get(ref, []):
                if node.has("data-reading-guide") and node not in guides:
                    guides.append(node)
    return guides


def accessible_name(root: Node, ids: dict[str, list[Node]]) -> bool:
    if root.get("aria-label").strip():
        return True
    if valid_idrefs(root.get("aria-labelledby"), ids):
        return True
    inside = descendants(root)
    if root.tag == "figure" and any(node.tag == "figcaption" and visible_text(node) for node in inside):
        return True
    if root.tag == "table" and any(node.tag == "caption" and visible_text(node) for node in inside):
        return True
    return False


def validate_html_visual(root: Node, errors: list[str]) -> None:
    label = f'visual "{root.get("data-viz")}"'
    nodes = nodes_with_attr(descendants(root), "data-viz-node")
    if len(nodes) < 2:
        errors.append(f"{label} html renderer needs at least two data-viz-node elements")
    for index, node in enumerate(nodes, 1):
        labels = nodes_with_attr(descendants(node), "data-viz-label")
        if len(labels) != 1:
            errors.append(f"{label} node {index} must contain exactly one data-viz-label")
            continue
        if not visible_text(labels[0]):
            errors.append(f"{label} node {index} has an empty data-viz-label")
        if any(desc.tag == "br" for desc in descendants(labels[0])):
            errors.append(f"{label} node {index} data-viz-label must not contain <br>")


def validate_svg_visual(root: Node, ids: dict[str, list[Node]], errors: list[str]) -> None:
    label = f'visual "{root.get("data-viz")}"'
    svgs = nodes_by_tag(descendants(root), "svg")
    if len(svgs) != 1:
        errors.append(f"{label} svg renderer must contain exactly one inline <svg>")
        return
    svg = svgs[0]
    if not svg.get("viewbox").strip():
        errors.append(f"{label} svg is missing viewBox")
    if svg.get("role").lower() != "img":
        errors.append(f'{label} svg must use role="img"')
    svg_nodes = descendants(svg)
    titles = [node for node in svg_nodes if node.tag == "title" and raw_text(node)]
    descriptions = [node for node in svg_nodes if node.tag == "desc" and raw_text(node)]
    equivalent_name = valid_idrefs(svg.get("aria-labelledby"), ids)
    equivalent_desc = valid_idrefs(svg.get("aria-describedby"), ids)
    if not ((titles and descriptions) or (equivalent_name and equivalent_desc)):
        errors.append(f"{label} svg needs non-empty <title> and <desc> or equivalent aria associations")
    if any(node.tag in {"script", "image", "foreignobject"} for node in svg_nodes):
        errors.append(f"{label} svg must not embed scripts, images, or foreignObject content")
    for node in svg_nodes:
        for attr_name in ("href", "xlink:href", "src"):
            value = node.get(attr_name)
            if value and not value.startswith("#"):
                errors.append(f"{label} svg contains an external dependency in {attr_name}")
    for index, text_node in enumerate([node for node in svg_nodes if node.tag == "text" and not hidden(node)], 1):
        if not text_node.has("data-viz-label"):
            errors.append(f"{label} informative SVG <text> {index} must carry data-viz-label")
        size_value = text_node.get("font-size")
        style = text_node.get("style")
        style_match = re.search(r"font-size\s*:\s*([^;]+)", style, re.I)
        if style_match:
            size_value = style_match.group(1)
        sizes = parse_font_px(size_value)
        if sizes and min(sizes) < MIN_VIZ_LABEL_PX - 0.01:
            errors.append(f"{label} SVG label {index} declares a font below 16px")


def has_overflow_wrapper(table: Node, root: Node) -> bool:
    current: Node | None = table.parent
    while current is not None:
        if current.has("data-overflow-ok"):
            return True
        if current is root:
            return False
        current = current.parent
    return False


def validate_table_visual(root: Node, errors: list[str]) -> None:
    label = f'visual "{root.get("data-viz")}"'
    tables = nodes_by_tag(descendants(root), "table")
    if len(tables) != 1:
        errors.append(f"{label} table renderer must contain exactly one <table>")
        return
    table = tables[0]
    captions = [node for node in descendants(table) if node.tag == "caption" and visible_text(node)]
    if len(captions) != 1:
        errors.append(f"{label} table needs one non-empty <caption>")
    header_cells = nodes_by_tag(descendants(table), "th")
    if not header_cells:
        errors.append(f"{label} table needs semantic <th> headers")
    else:
        scopes = {cell.get("scope").lower() for cell in header_cells}
        has_headers_map = any(node.get("headers") for node in descendants(table) if node.tag in {"td", "th"})
        if not ({"col", "row"} <= scopes or has_headers_map):
            errors.append(f"{label} table needs both row/column scope headers or explicit headers associations")
    if not has_overflow_wrapper(table, root) and not root.has("data-overflow-ok"):
        errors.append(f"{label} table must be inside a bounded data-overflow-ok wrapper")
    if root.get("data-viz-kind") == "quantitative" and not re.search(r"\d", visible_text(table)):
        errors.append(f"{label} quantitative table contains no visible values")


def validate_source_image(root: Node, allow_placeholders: bool, errors: list[str]) -> None:
    label = f'visual "{root.get("data-viz")}"'
    images = nodes_by_tag(descendants(root), "img")
    if len(images) != 1:
        errors.append(f"{label} source-image renderer must contain exactly one <img>")
        return
    image = images[0]
    src = image.get("src").strip()
    if not src:
        errors.append(f"{label} source image has an empty src")
    elif not src.lower().startswith("data:image/") and not (allow_placeholders and PLACEHOLDER_RE.fullmatch(src)):
        errors.append(f"{label} source image must use an embedded data:image URI in the single-file artifact")
    if not image.get("alt").strip():
        errors.append(f"{label} source image needs meaningful alt text")
    sized = bool(image.get("width") and image.get("height"))
    current: Node | None = image
    while current is not None and current is not root.parent:
        if "aspect-ratio" in current.get("style") or current.get("data-aspect-ratio").strip():
            sized = True
            break
        current = current.parent
    if not sized:
        errors.append(f"{label} source image needs width/height or a data-aspect-ratio wrapper")
    captions = [node for node in descendants(root) if node.tag == "figcaption" and visible_text(node)]
    if not captions:
        errors.append(f"{label} source image needs a visible caption")
    if not re.search(r"(?:来源|原文|source|credit|图表)", visible_text(root), re.I):
        errors.append(f"{label} source image needs visible source attribution")


def validate_visual(
    root: Node,
    ids: dict[str, list[Node]],
    allow_placeholders: bool,
    errors: list[str],
) -> None:
    visual_id = root.get("data-viz").strip()
    label = f'visual "{visual_id or "missing"}"'
    renderer = root.get("data-viz-renderer")
    kind = root.get("data-viz-kind")
    if renderer not in ALLOWED_RENDERERS:
        errors.append(f'{label} has unsupported data-viz-renderer "{renderer or "missing"}"')
    if kind not in ALLOWED_VIZ_KINDS:
        errors.append(f'{label} has unsupported data-viz-kind "{kind or "missing"}"')
    if kind in {"network", "spatial"} and renderer not in {"svg", "source-image"}:
        errors.append(f"{label} {kind} topology requires svg or source-image renderer")
    if any(ancestor.has("data-viz") for ancestor in ancestors(root)):
        errors.append(f"{label} is nested inside another data-viz root")
    guides = visual_guides(root, ids)
    if len(guides) != 1 or not visible_text(guides[0]):
        errors.append(f"{label} needs exactly one non-empty data-reading-guide")
    if not accessible_name(root, ids):
        errors.append(f"{label} needs an accessible heading, caption, aria-label, or aria-labelledby")
    if root.tag not in {"figure", "table"}:
        if root.get("role") not in {"group", "img"}:
            errors.append(f"{label} non-native visual root needs role=group or role=img")
        if not root.get("aria-label").strip() and not valid_idrefs(root.get("aria-labelledby"), ids):
            errors.append(f"{label} non-native visual root needs a non-empty accessible name association")
        if not valid_idrefs(root.get("aria-describedby"), ids):
            errors.append(f"{label} non-native visual root needs aria-describedby to its reading guide")
    if kind == "quantitative":
        basis = root.get("data-comparison-basis").strip()
        if not basis:
            errors.append(f"{label} quantitative visual needs data-comparison-basis")
        elif not (allow_placeholders and PLACEHOLDER_RE.fullmatch(basis)) and basis not in visible_text(root):
            errors.append(f"{label} data-comparison-basis must also be visible to readers")
        if not re.search(r"\d", visible_text(root)):
            errors.append(f"{label} quantitative visual contains no visible values")
    if renderer == "html":
        validate_html_visual(root, errors)
    elif renderer == "svg":
        validate_svg_visual(root, ids, errors)
    elif renderer == "table":
        validate_table_visual(root, errors)
    elif renderer == "source-image":
        validate_source_image(root, allow_placeholders, errors)


def ancestors(node: Node) -> Iterator[Node]:
    current = node.parent
    while current is not None:
        yield current
        current = current.parent


def audit(path: Path, *, allow_placeholders: bool = False) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    text = path.read_text(encoding="utf-8")
    parser = DOMParser()
    parser.feed(text)
    nodes = list(walk(parser.root))

    placeholders = sorted(set(PLACEHOLDER_RE.findall(text)))
    if placeholders and not allow_placeholders:
        errors.append("unresolved template placeholders: " + ", ".join(placeholders))
    if not parser.has_doctype:
        errors.append("missing HTML5 doctype")

    by_tag = {tag: nodes_by_tag(nodes, tag) for tag in ("html", "head", "body", "main", "style", "footer", "h1")}
    for tag in ("html", "head", "body", "main", "style", "footer"):
        if len(by_tag[tag]) != 1:
            errors.append(f"expected exactly one <{tag}>, found {len(by_tag[tag])}")
    if len(by_tag["h1"]) != 1:
        errors.append(f"expected exactly one <h1>, found {len(by_tag['h1'])}")

    html_node = by_tag["html"][0] if by_tag["html"] else None
    body_node = by_tag["body"][0] if len(by_tag["body"]) == 1 else None
    main_node = by_tag["main"][0] if len(by_tag["main"]) == 1 else None
    if html_node is not None:
        if not html_node.get("lang").strip():
            errors.append("<html> must declare lang")
        if html_node.get("data-layout-guard") != "v2":
            errors.append('missing data-layout-guard="v2" on <html>')
    if not any(node.tag == "meta" and node.get("name").lower() == "viewport" for node in nodes):
        errors.append("missing viewport meta")
    document_guard = extract_layout_guard(text)
    try:
        canonical_guard = extract_layout_guard(CANONICAL_SHELL.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        canonical_guard = None
    if document_guard is None:
        errors.append("missing immutable LAYOUT_GUARD_V2 block")
    elif canonical_guard is None:
        errors.append("canonical LAYOUT_GUARD_V2 block is unavailable")
    elif document_guard != canonical_guard:
        errors.append("LAYOUT_GUARD_V2 block differs from the canonical shell")

    modules: dict[str, list[Node]] = defaultdict(list)
    for node in nodes_with_attr(nodes, "data-module"):
        modules[node.get("data-module")].append(node)
    missing_modules = sorted(name for name in REQUIRED_MODULES if len(modules[name]) != 1)
    if missing_modules:
        errors.append("missing or duplicate required data-module sections: " + ", ".join(missing_modules))
    duplicate_optional = sorted(name for name in OPTIONAL_MODULES if len(modules[name]) > 1)
    if duplicate_optional:
        errors.append("duplicate optional data-module sections: " + ", ".join(duplicate_optional))
    forbidden = sorted(name for name in FORBIDDEN_MODULES if modules[name])
    if forbidden:
        errors.append("forbidden data-module sections: " + ", ".join(forbidden))
    unknown = sorted(name for name in modules if name not in ALLOWED_MODULES | FORBIDDEN_MODULES)
    if unknown:
        errors.append("unsupported data-module sections: " + ", ".join(unknown))

    hero = modules["hero"][0] if len(modules["hero"]) == 1 else None
    if hero is not None:
        hero_index = nodes.index(hero)
        main_index = nodes.index(main_node) if main_node in nodes else -1
        if (
            hero.tag != "header"
            or body_node is None
            or hero.parent is not body_node
            or main_node is None
            or is_descendant(hero, main_node)
            or hero_index >= main_index
        ):
            errors.append("hero must be a top-level <header> before <main> and is excluded from density")
        hero_descendants = descendants(hero)
        if len(nodes_by_tag(hero_descendants, "h1")) != 1:
            errors.append("hero must contain exactly one <h1>")
        source_link_candidates = [
            node for node in nodes_by_tag(hero_descendants, "a")
            if "source-link" in node.get("class").split() or "原文" in visible_text(node)
        ]
        source_links = []
        for node in source_link_candidates:
            href = node.get("href").strip()
            valid_href = bool(re.match(r"^(?:https?://|file:/)", href, re.I)) or bool(
                allow_placeholders and PLACEHOLDER_RE.fullmatch(href)
            )
            if valid_href:
                source_links.append(node)
            elif href:
                errors.append("hero source link must use a real http(s) or file URL, not a fragment or placeholder target")
        if not source_links and "原文链接未提供" not in visible_text(hero):
            errors.append("hero needs a source URL or the visible label 原文链接未提供")
        meta_nodes = [
            node for node in hero_descendants
            if "meta" in node.get("class").split() and visible_text(node)
        ]
        if not meta_nodes:
            errors.append("hero needs visible source metadata")
    if main_node is not None:
        for module_name in (REQUIRED_MODULES - {"hero"}) | OPTIONAL_MODULES:
            for module_node in modules[module_name]:
                if module_node.parent is not main_node:
                    errors.append(f'data-module="{module_name}" must be a direct child of <main>')
                section_indexes = [
                    node for node in descendants(module_node)
                    if "section-index" in node.get("class").split() and node.get("aria-hidden").lower() == "true"
                ]
                if len(section_indexes) != 1:
                    errors.append(f'data-module="{module_name}" needs exactly one aria-hidden section-index')
        if all(len(modules[name]) == 1 for name in ("quick-read", "core-thread", "deep-dive", "takeaways")):
            positions = {name: nodes.index(modules[name][0]) for name in modules if len(modules[name]) == 1}
            if not positions["quick-read"] < positions["core-thread"] < positions["deep-dive"] < positions["takeaways"]:
                errors.append("required modules must follow quick-read -> core-thread -> deep-dive -> takeaways")
            if modules["concepts"]:
                concept_position = positions["concepts"]
                before_deep = positions["core-thread"] < concept_position < positions["deep-dive"]
                after_deep = positions["deep-dive"] < concept_position < positions["takeaways"]
                if not (before_deep or after_deep):
                    errors.append("concepts must sit between core-thread/deep-dive or deep-dive/takeaways")
            if modules["visualizations"] and not (
                positions["deep-dive"] < positions["visualizations"] < positions["takeaways"]
            ):
                errors.append("visualizations must sit after deep-dive and before takeaways")

    quick = nodes_with_attr(descendants(modules["quick-read"][0]), "data-quick-item") if len(modules["quick-read"]) == 1 else []
    core = nodes_with_attr(descendants(modules["core-thread"][0]), "data-core-step") if len(modules["core-thread"]) == 1 else []
    deep = nodes_with_attr(descendants(modules["deep-dive"][0]), "data-deep-chapter") if len(modules["deep-dive"]) == 1 else []
    concepts = nodes_with_attr(descendants(modules["concepts"][0]), "data-concept-card") if len(modules["concepts"]) == 1 else []
    takeaways = nodes_with_attr(descendants(modules["takeaways"][0]), "data-takeaway") if len(modules["takeaways"]) == 1 else []

    validate_count("quick-read", quick, 2, 3, errors)
    validate_count("core-thread", core, 3, 5, errors)
    validate_count("deep-dive", deep, 1, 3, errors)
    if modules["concepts"]:
        validate_count("concept", concepts, 1, 3, errors)
    validate_count("takeaway", takeaways, 2, 3, errors)
    for unit_nodes, attr in (
        (quick, "data-quick-item"),
        (core, "data-core-step"),
        (deep, "data-deep-chapter"),
        (concepts, "data-concept-card"),
        (takeaways, "data-takeaway"),
    ):
        validate_stable_values(unit_nodes, attr, errors)
    for attr, scoped in (
        ("data-quick-item", quick),
        ("data-core-step", core),
        ("data-deep-chapter", deep),
        ("data-concept-card", concepts),
        ("data-takeaway", takeaways),
    ):
        global_nodes = nodes_with_attr(nodes, attr)
        if len(global_nodes) != len(scoped):
            errors.append(f"{attr} units must live inside their matching data-module section")

    for unit in quick:
        if editorial_units(visible_text(unit)) > 120:
            errors.append(f"{unit_label(unit, 'data-quick-item')} exceeds 120 editorial units")
        validate_repetition(unit, "data-quick-item", errors)
    for unit in core:
        if editorial_units(visible_text(unit)) > 70:
            errors.append(f"{unit_label(unit, 'data-core-step')} exceeds 70 editorial units")
        validate_repetition(unit, "data-core-step", errors)
    for unit in deep:
        if editorial_units(visible_text(unit)) > 320:
            errors.append(f"{unit_label(unit, 'data-deep-chapter')} exceeds 320 editorial units")
        for paragraph in nodes_by_tag(descendants(unit), "p"):
            if editorial_units(visible_text(paragraph)) > 120:
                errors.append(f"{unit_label(unit, 'data-deep-chapter')} has a paragraph over 120 editorial units")
        inside = descendants(unit)
        unit_visuals = nodes_with_attr(inside, "data-viz")
        explanations = nodes_with_attr(inside, "data-role", "explanation")
        if unit_visuals and explanations and inside.index(unit_visuals[0]) > inside.index(explanations[0]):
            errors.append(f"{unit_label(unit, 'data-deep-chapter')} must place its visual before explanation in DOM order")
        validate_repetition(unit, "data-deep-chapter", errors)
    for unit in concepts:
        if editorial_units(visible_text(unit)) > 140:
            errors.append(f"{unit_label(unit, 'data-concept-card')} exceeds 140 editorial units")
        for paragraph in nodes_by_tag(descendants(unit), "p"):
            if editorial_units(visible_text(paragraph)) > 70:
                errors.append(f"{unit_label(unit, 'data-concept-card')} has a paragraph over 70 editorial units")
        validate_repetition(unit, "data-concept-card", errors)
    for unit in takeaways:
        if editorial_units(visible_text(unit)) > 80:
            errors.append(f"{unit_label(unit, 'data-takeaway')} exceeds 80 editorial units")
        validate_repetition(unit, "data-takeaway", errors)

    density = html_node.get("data-density") if html_node is not None else ""
    main_units = editorial_units(visible_text(main_node)) if main_node is not None else 0
    if density not in {"standard", "expanded"}:
        errors.append('data-density must be "standard" or "expanded" on <html>')
    elif density == "standard" and main_units > 2200:
        errors.append(f"standard density exceeds 2200 editorial units: {main_units}")
    elif density == "expanded":
        if main_units > 2600:
            errors.append(f"expanded density exceeds 2600 editorial units: {main_units}")
        else:
            warnings.append("expanded density requires manual confirmation before delivery")

    ids: dict[str, list[Node]] = defaultdict(list)
    for node in nodes:
        if node.get("id"):
            ids[node.get("id")].append(node)
    duplicate_ids = sorted(name for name, values in ids.items() if len(values) > 1)
    if duplicate_ids:
        errors.append("duplicate IDs: " + ", ".join(duplicate_ids))
    missing_targets = sorted({
        node.get("href")[1:]
        for node in nodes
        if node.get("href").startswith("#") and len(node.get("href")) > 1 and node.get("href")[1:] not in ids
    })
    if missing_targets:
        errors.append("unresolved internal anchors: " + ", ".join(missing_targets))
    nav_nodes = nodes_by_tag(nodes, "nav")
    if nav_nodes and main_node is not None:
        skip_links = [
            node for node in nodes_by_tag(nodes, "a")
            if "skip-link" in node.get("class").split()
        ]
        expected_href = f'#{main_node.get("id")}' if main_node.get("id") else ""
        if len(skip_links) != 1:
            errors.append("a page with navigation needs exactly one skip-link")
        elif not expected_href or skip_links[0].get("href") != expected_href:
            errors.append("skip-link must target the main content id")
        if main_node.get("tabindex") != "-1":
            errors.append('skip-link target <main> needs tabindex="-1" for keyboard focus')
    for node in nodes:
        for attr in ("aria-labelledby", "aria-describedby"):
            value = node.get(attr)
            if value and not valid_idrefs(value, ids):
                errors.append(f"unresolved {attr} reference on <{node.tag}>")

    visuals = nodes_with_attr(nodes, "data-viz")
    visible_visuals = [visual for visual in visuals if not hidden(visual)]
    hidden_visuals = [visual.get("data-viz") or "missing" for visual in visuals if hidden(visual)]
    if hidden_visuals:
        errors.append("major data-viz roots must not be hidden: " + ", ".join(hidden_visuals))
    if not 2 <= len(visible_visuals) <= 5:
        errors.append(f"expected 2–5 visible major data-viz roots, found {len(visible_visuals)}")
    validate_stable_values(visuals, "data-viz", errors)
    synthesis = modules["visualizations"]
    if synthesis:
        synthesis_visuals = [visual for visual in visible_visuals if is_descendant(visual, synthesis[0])]
        if len(synthesis_visuals) != 1:
            errors.append(f"visualizations module must contain exactly one data-viz root, found {len(synthesis_visuals)}")
        validate_repetition(synthesis[0], "data-module", errors)
    repetition_units: list[tuple[Node, str]] = []
    for scoped, attr in (
        (quick, "data-quick-item"),
        (core, "data-core-step"),
        (deep, "data-deep-chapter"),
        (concepts, "data-concept-card"),
        (takeaways, "data-takeaway"),
    ):
        repetition_units.extend((unit, attr) for unit in scoped)
    if synthesis:
        repetition_units.append((synthesis[0], "data-module"))
    validate_cross_unit_repetition(repetition_units, errors)
    for visual in visuals:
        if any(is_descendant(visual, chapter) for chapter in deep) and not visual.has("data-inline-viz"):
            errors.append(f'visual "{visual.get("data-viz")}" inside deep-dive is missing data-inline-viz')
        if any(is_descendant(visual, concept) for concept in concepts) and not visual.has("data-concept-viz"):
            errors.append(f'visual "{visual.get("data-viz")}" inside concepts is missing data-concept-viz')
        validate_visual(visual, ids, allow_placeholders, errors)
    renderers = {visual.get("data-viz-renderer") for visual in visuals if visual.get("data-viz-renderer")}
    if len(renderers) > 2:
        warnings.append("more than two renderers are used; confirm the article still has one dominant and one supporting grammar")

    if any(node.has("data-text-alternative") for node in nodes):
        errors.append("data-text-alternative is forbidden; use semantic structure and concise aria associations")
    if main_node is not None and not re.search(
        r"(?:文章依据|作者观点|解读|依据\s*[：:]|来源\s*[：:]|原文(?:指出|显示|建议|未提供))",
        visible_text(main_node),
    ):
        warnings.append("no explicit evidence or interpretation attribution found; confirm source-dependent claims are labeled")

    for node in nodes_with_attr(nodes, "data-canonical-term"):
        term = node.get("data-canonical-term").strip()
        if not term:
            errors.append("empty data-canonical-term")
        elif not (allow_placeholders and PLACEHOLDER_RE.fullmatch(term)) and term not in visible_text(node):
            errors.append(f'data-canonical-term "{term}" is not preserved in its visible label')
    for node in nodes_with_attr(nodes, "data-approved-abbreviation"):
        abbreviation = node.get("data-approved-abbreviation").strip()
        if not abbreviation:
            errors.append("empty data-approved-abbreviation")
        elif not (allow_placeholders and PLACEHOLDER_RE.fullmatch(abbreviation)) and abbreviation not in visible_text(html_node or parser.root):
            errors.append(f'data-approved-abbreviation "{abbreviation}" is not visible in the document')
    for node in nodes_with_attr(nodes, "data-claim-type"):
        if node.get("data-claim-type") not in ALLOWED_CLAIM_TYPES:
            errors.append(f'unsupported data-claim-type "{node.get("data-claim-type")}"')

    external_styles = [
        node for node in nodes
        if node.tag == "link" and "stylesheet" in node.get("rel").lower().split()
    ]
    external_scripts = [node for node in nodes if node.tag == "script" and node.get("src")]
    unpackaged_images = [
        node for node in nodes
        if node.tag == "img"
        and node.get("src").strip()
        and not node.get("src").lower().startswith("data:image/")
        and not (allow_placeholders and PLACEHOLDER_RE.fullmatch(node.get("src").strip()))
    ]
    if external_styles:
        errors.append("external stylesheet dependencies are not allowed")
    if external_scripts:
        errors.append("external script dependencies are not allowed")
    if unpackaged_images:
        errors.append("all image assets must be embedded in the single-file artifact")
    if any("chapter-copy" in node.get("class").split() for node in nodes):
        errors.append("fixed chapter-copy explanation/evidence/impact bands are forbidden")
    if main_node is not None and "文字版" in visible_text(main_node):
        errors.append("visible 文字版 repetition is forbidden")
    for node in nodes:
        inline_style = node.get("style")
        if not inline_style:
            continue
        if node.tag in {"html", "body", "main"} and re.search(
            r"(?:^|;)\s*overflow(?:-x)?\s*:\s*(?:hidden|clip)\b",
            inline_style,
            re.I,
        ):
            errors.append(f"page-level overflow hiding is forbidden on <{node.tag}>")
        fixed_height = re.search(r"(?:^|;)\s*(?:height|max-height)\s*:\s*(?!auto\b)[^;]+", inline_style, re.I)
        clipped = re.search(r"(?:^|;)\s*overflow(?:-[xy])?\s*:\s*(?:hidden|clip)\b", inline_style, re.I)
        intentional_hiding = (
            node.has("data-visual-only")
            or "visual-only" in node.get("class").split()
            or "visually-hidden" in node.get("class").split()
            or "sr-only" in node.get("class").split()
        )
        if fixed_height and clipped and not intentional_hiding:
            errors.append(f"inline fixed-height text clipping pattern on <{node.tag}>")

    headings = [node for node in nodes if re.fullmatch(r"h[1-6]", node.tag)]
    if any(not visible_text(node) for node in headings):
        errors.append("empty heading found")
    levels = [int(node.tag[1]) for node in headings]
    if any(current - previous > 1 for previous, current in zip(levels, levels[1:])):
        warnings.append("heading hierarchy skips a level")

    style_blocks = [visible_text(node) for node in by_tag["style"]]
    # visible_text intentionally skips style nodes; read their raw parts here.
    style_blocks = ["".join(part for part in node.parts if isinstance(part, str)) for node in by_tag["style"]]
    css = "\n".join(style_blocks)
    if "@media" not in css:
        errors.append("embedded CSS has no responsive @media rule")
    if css.count("{") != css.count("}"):
        errors.append("unbalanced CSS braces")
    css_urls = [match.strip().strip('"\'') for match in re.findall(r"url\(\s*([^\)]+?)\s*\)", css, re.I)]
    invalid_css_urls = [value for value in css_urls if not value.lower().startswith("data:") and not value.startswith("#")]
    if re.search(r"@import\b", css, re.I) or invalid_css_urls:
        errors.append("external CSS, font, or image dependencies are not allowed")
    for pattern, message in (
        (r"counter-reset\s*:\s*explainer-section", "missing automatic section counter reset"),
        (r"counter-increment\s*:\s*explainer-section", "missing automatic section counter increment"),
        (r"counter\(\s*explainer-section", "missing automatic section number output"),
    ):
        if not re.search(pattern, css, re.I):
            errors.append(message)
    for value in re.findall(r"font-size\s*:\s*([^;}]+)", css, re.I):
        sizes = parse_font_px(value)
        if sizes and min(sizes) < MIN_TEXT_PX - 0.01:
            errors.append(f"font-size below 14px: {value.strip()}")
        if not sizes and re.search(r"\b(?:vw|vh|vmin|vmax)\b", value, re.I):
            errors.append(f"viewport-only font-size has no 14px floor: {value.strip()}")
    for selector, declarations in re.findall(r"([^{}]+)\{([^{}]*)\}", css, re.S):
        selector_targets_page = bool(re.search(r"(?:^|[\s,>+~])(?:html|body)(?=$|[\s,.:#\[>+~])", selector, re.I))
        page_overflow_hidden = re.search(
            r"(?:^|;)\s*overflow(?:-x)?\s*:\s*(?:hidden|clip)\b",
            declarations,
            re.I,
        )
        if selector_targets_page and page_overflow_hidden:
            errors.append(f"page-level overflow hiding is forbidden: {selector.strip()}")
        fixed_height = re.search(r"(?:^|;)\s*(?:height|max-height)\s*:\s*(?!auto\b)[^;]+", declarations, re.I)
        clipped = re.search(r"(?:^|;)\s*overflow(?:-[xy])?\s*:\s*(?:hidden|clip)\b", declarations, re.I)
        intentional_hiding = any(
            token in selector
            for token in ("data-visual-only", ".visual-only", ".visually-hidden", ".sr-only")
        )
        if fixed_height and clipped and not intentional_hiding:
            errors.append(f"fixed-height text clipping pattern: {selector.strip()}")

    return {
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "stats": {
            "density": density or "missing",
            "editorial_units": main_units,
            "quick": len(quick),
            "core": len(core),
            "deep": len(deep),
            "concepts": len(concepts),
            "synthesis": 1 if synthesis else 0,
            "takeaways": len(takeaways),
            "visuals": len(visible_visuals),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    parser.add_argument("--template", action="store_true", help="allow {{PLACEHOLDER}} tokens")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.html.is_file():
        print(f"ERROR: file not found: {args.html}", file=sys.stderr)
        return 2
    try:
        result = audit(args.html, allow_placeholders=args.template)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for message in result["errors"]:
            print(f"ERROR: {message}")
        for message in result["warnings"]:
            print(f"WARN: {message}")
        stats = result["stats"]
        print(
            "STRUCTURE: "
            f"density={stats['density']} units={stats['editorial_units']} "
            f"quick={stats['quick']} core={stats['core']} deep={stats['deep']} "
            f"concepts={stats['concepts']} synthesis={stats['synthesis']} "
            f"takeaways={stats['takeaways']} visuals={stats['visuals']}"
        )
        print(f"SUMMARY: {len(result['errors'])} error(s), {len(result['warnings'])} warning(s)")
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
