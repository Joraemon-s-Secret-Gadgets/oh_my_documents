from __future__ import annotations

import argparse
import html
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path


HTML_MARKERS = ("```html", "<!DOCTYPE html", "<html", "<body")
SKIP_TAGS = {"head", "style", "script", "nav", "aside", "button", "svg", "footer"}
SKIP_CLASSES = {
    "dot",
    "icon",
    "section-num",
    "doc-tag",
    "nf-icon",
    "nf-label",
    "aside-logo",
    "aside-ver",
    "aside-status",
}
VOID_TAGS = {"br", "hr", "img", "input", "meta", "link"}


@dataclass
class Node:
    tag: str | None = None
    attrs: dict[str, str] = field(default_factory=dict)
    children: list["Node | str"] = field(default_factory=list)


class TreeBuilder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("document")
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        node = Node(tag, {key.lower(): value or "" for key, value in attrs})
        self.stack[-1].children.append(node)
        if tag not in VOID_TAGS:
            self.stack.append(node)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        if data:
            self.stack[-1].children.append(data)


def strip_html_fence(text: str) -> str:
    text = text.lstrip("\ufeff")
    if text.startswith("```html"):
        text = re.sub(r"^```html\s*", "", text, count=1)
        text = re.sub(r"\s*```\s*$", "", text, count=1)
    return text


def is_html_document(text: str) -> bool:
    head = text[:500]
    return any(marker in head for marker in HTML_MARKERS)


def squeeze_spaces(value: str) -> str:
    value = html.unescape(value)
    value = value.replace("\xa0", " ")
    value = re.sub(r"[ \t\r\f\v]+", " ", value)
    value = re.sub(r" *\n *", "\n", value)
    return value.strip()


def plain_text(node: Node | str) -> str:
    if isinstance(node, str):
        return squeeze_spaces(node)
    if should_skip(node):
        return ""
    if node.tag == "br":
        return "\n"
    parts = [plain_text(child) for child in node.children]
    return squeeze_spaces(" ".join(part for part in parts if part))


def children_markdown(node: Node) -> str:
    parts = [to_markdown(child) for child in node.children]
    return clean_blocks("\n\n".join(part for part in parts if part.strip()))


def inline_markdown(node: Node | str) -> str:
    if isinstance(node, str):
        return squeeze_spaces(node)
    if should_skip(node):
        return ""
    if node.tag == "br":
        return "\n"
    text = squeeze_spaces(" ".join(inline_markdown(child) for child in node.children))
    if not text:
        return ""
    if node.tag in {"strong", "b"}:
        return f"**{text}**"
    if node.tag in {"em", "i"}:
        return f"*{text}*"
    if node.tag == "code":
        return f"`{text}`"
    if node.tag == "a":
        href = node.attrs.get("href", "")
        if href and not href.startswith("#"):
            return f"[{text}]({href})"
    return text


def table_to_markdown(node: Node) -> str:
    rows: list[list[str]] = []

    def walk(current: Node) -> None:
        if current.tag == "tr":
            cells = [
                squeeze_spaces(inline_markdown(child)).replace("\n", " ").replace("|", "\\|")
                for child in current.children
                if isinstance(child, Node) and child.tag in {"th", "td"}
            ]
            if cells:
                rows.append(cells)
            return
        for child in current.children:
            if isinstance(child, Node):
                walk(child)

    walk(node)
    if not rows:
        return ""

    width = max(len(row) for row in rows)
    normalized = [row + [""] * (width - len(row)) for row in rows]
    header = normalized[0]
    separator = ["---"] * width
    body = normalized[1:]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(separator) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in body)
    return "\n".join(lines)


def list_to_markdown(node: Node, ordered: bool = False) -> str:
    lines: list[str] = []
    item_index = 1
    for child in node.children:
        if not isinstance(child, Node) or child.tag != "li":
            continue
        item = children_markdown(child).replace("\n", "\n  ").strip()
        prefix = f"{item_index}. " if ordered else "- "
        lines.append(prefix + item)
        item_index += 1
    return "\n".join(lines)


def heading(node: Node, level: int) -> str:
    text = squeeze_spaces(inline_markdown(node))
    return f"{'#' * level} {text}" if text else ""


def to_markdown(node: Node | str) -> str:
    if isinstance(node, str):
        return squeeze_spaces(node)
    if should_skip(node):
        return ""
    if node.tag in {"document", "html", "body", "main"}:
        return children_markdown(node)
    if node.tag == "br":
        return "\n"
    if node.tag == "hr":
        return "---"
    if node.tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        return heading(node, int(node.tag[1]))
    if node.tag == "p":
        return squeeze_spaces(inline_markdown(node))
    if node.tag == "table":
        return table_to_markdown(node)
    if node.tag == "ul":
        return list_to_markdown(node)
    if node.tag == "ol":
        return list_to_markdown(node, ordered=True)
    if node.tag in {"li", "td", "th"}:
        return children_markdown(node)
    if node.tag in {"code", "strong", "b", "em", "i", "a"}:
        return inline_markdown(node)
    return children_markdown(node)


def should_skip(node: Node) -> bool:
    if node.tag in SKIP_TAGS:
        return True
    classes = set(node.attrs.get("class", "").split())
    return bool(classes & SKIP_CLASSES)


def clean_blocks(markdown: str) -> str:
    lines = [line.rstrip() for line in markdown.splitlines()]
    cleaned: list[str] = []
    blank = 0
    for line in lines:
        if line.strip():
            blank = 0
            cleaned.append(line)
        else:
            blank += 1
            if blank <= 1:
                cleaned.append("")
    return "\n".join(cleaned).strip()


def convert_text(text: str) -> str:
    parser = TreeBuilder()
    parser.feed(strip_html_fence(text))
    markdown = to_markdown(parser.root)
    return clean_blocks(markdown) + "\n"


def target_files(root: Path) -> list[Path]:
    files = []
    for path in sorted(root.glob("docs/*/*.md")):
        text = path.read_text(encoding="utf-8")
        if is_html_document(text):
            files.append(path)
    return files


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write converted Markdown back to files")
    parser.add_argument("--path", type=Path, help="convert one file instead of all docs/*/*.md")
    args = parser.parse_args()

    root = Path.cwd()
    files = [args.path] if args.path else target_files(root)
    for path in files:
        text = path.read_text(encoding="utf-8")
        if not is_html_document(text):
            print(f"skip {path}")
            continue
        converted = convert_text(text)
        print(f"convert {path} ({len(text)} bytes -> {len(converted)} bytes)")
        if args.write:
            path.write_text(converted, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
