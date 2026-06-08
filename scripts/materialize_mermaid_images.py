from __future__ import annotations

import re
import textwrap
from collections import defaultdict, deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUTPUT = ROOT / "assets" / "images" / "mermaid"
MERMAID_BLOCK = re.compile(r"```mermaid\s*\n(.*?)\n```", re.DOTALL)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "malgunbd.ttf" if bold else "malgun.ttf"
    return ImageFont.truetype(f"C:/Windows/Fonts/{name}", size=size)


def slug(path: Path) -> str:
    return "-".join(path.relative_to(DOCS).with_suffix("").parts).lower().replace("_", "-")


def text_size(draw: ImageDraw.ImageDraw, value: str, face: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), value, font=face)
    return box[2] - box[0], box[3] - box[1]


def wrap_label(value: str, width: int = 18) -> list[str]:
    value = re.sub(r"<br\s*/?>", "\n", value).replace("&quot;", '"')
    lines: list[str] = []
    for part in value.splitlines() or [""]:
        lines.extend(textwrap.wrap(part, width=width, break_long_words=False) or [""])
    return lines


def clean_label(raw: str) -> str:
    value = raw.strip()
    while value and value[0] in "[{(":
        value = value[1:].strip()
    while value and value[-1] in "]})":
        value = value[:-1].strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        value = value[1:-1]
    return value


def node_id(value: str) -> str:
    match = re.match(r"\s*([A-Za-z0-9_]+)", value)
    return match.group(1) if match else value.strip()


def extract_node_defs(line: str) -> dict[str, str]:
    defs: dict[str, str] = {}
    for match in re.finditer(r"\b([A-Za-z0-9_]+)\s*(\[\[.*?\]\]|\[.*?\]|\{.*?\}|\(.*?\))", line):
        defs[match.group(1)] = clean_label(match.group(2))
    return defs


def parse_graph(source: str) -> tuple[dict[str, str], list[tuple[str, str, str, str]]]:
    nodes: dict[str, str] = {}
    edges: list[tuple[str, str, str, str]] = []
    connector = re.compile(r"(-\.->|-->|---|--|==>)")

    for raw in source.splitlines():
        line = raw.strip()
        if not line or line.startswith("%%") or line in {"end"}:
            continue
        if line.startswith(("graph ", "flowchart ", "sequenceDiagram")):
            continue
        if line.startswith("subgraph "):
            match = re.match(r"subgraph\s+([A-Za-z0-9_]+)(?:\[(.*?)\])?", line)
            if match:
                nodes.setdefault(match.group(1), clean_label(match.group(2) or match.group(1)))
            continue

        nodes.update(extract_node_defs(line))
        parts = connector.split(line, maxsplit=1)
        if len(parts) < 3:
            ident = node_id(line)
            if ident:
                nodes.setdefault(ident, nodes.get(ident, ident))
            continue

        left, mark, right = parts[0].strip(), parts[1], parts[2].strip()
        label = ""
        label_match = re.match(r'\|([^|]+)\|\s*(.*)', right)
        if label_match:
            label = clean_label(label_match.group(1))
            right = label_match.group(2).strip()
        elif mark in {"--", "---"}:
            mid_label = re.match(r'["]?([^"-]+?)["]?\s*--\s*(.*)', right)
            if mid_label:
                label = clean_label(mid_label.group(1))
                right = mid_label.group(2).strip()

        src, dst = node_id(left), node_id(right)
        if src and dst:
            nodes.setdefault(src, nodes.get(src, src))
            nodes.setdefault(dst, nodes.get(dst, dst))
            edges.append((src, dst, label, mark))
    return nodes, edges


def layered_positions(nodes: dict[str, str], edges: list[tuple[str, str, str, str]], direction: str) -> tuple[dict[str, tuple[int, int]], tuple[int, int]]:
    outgoing: dict[str, list[str]] = defaultdict(list)
    indegree = {node: 0 for node in nodes}
    for src, dst, _, _ in edges:
        outgoing[src].append(dst)
        indegree[dst] = indegree.get(dst, 0) + 1
        indegree.setdefault(src, 0)

    queue = deque([node for node, degree in indegree.items() if degree == 0])
    rank = {node: 0 for node in nodes}
    while queue:
        current = queue.popleft()
        for nxt in outgoing[current]:
            rank[nxt] = max(rank.get(nxt, 0), rank[current] + 1)
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)

    buckets: dict[int, list[str]] = defaultdict(list)
    for node in nodes:
        buckets[rank.get(node, 0)].append(node)

    box_w, x_gap, box_h, y_gap = 220, 80, 88, 48
    max_rank = max(buckets) if buckets else 0
    positions: dict[str, tuple[int, int]] = {}
    if direction == "LR":
        max_per_col = 6
        width = 80 + (max_rank + 1) * (box_w + x_gap)
        height = 120 + max(
            ((len(v) + max_per_col - 1) // max_per_col) * max_per_col * (box_h + y_gap)
            for v in buckets.values()
        )
        for r, bucket in buckets.items():
            for idx, node in enumerate(bucket):
                col = idx // max_per_col
                row = idx % max_per_col
                positions[node] = (60 + r * (box_w + x_gap) + col * (box_w + 24), 70 + row * (box_h + y_gap))
    else:
        max_per_row = 5
        rank_rows = {r: (len(v) + max_per_row - 1) // max_per_row for r, v in buckets.items()}
        width = 120 + min(max((len(v) for v in buckets.values()), default=1), max_per_row) * (box_w + x_gap)
        height = 110 + sum(max(1, rank_rows.get(r, 1)) * (box_h + y_gap) for r in range(max_rank + 1))
        y_offsets: dict[int, int] = {}
        current_y = 70
        for r in range(max_rank + 1):
            y_offsets[r] = current_y
            current_y += max(1, rank_rows.get(r, 1)) * (box_h + y_gap)
        for r, bucket in buckets.items():
            for idx, node in enumerate(bucket):
                row = idx // max_per_row
                col = idx % max_per_row
                count_in_row = min(max_per_row, len(bucket) - row * max_per_row)
                row_w = count_in_row * box_w + max(0, count_in_row - 1) * x_gap
                start_x = max(60, (width - row_w) // 2)
                positions[node] = (start_x + col * (box_w + x_gap), y_offsets[r] + row * (box_h + y_gap))
    return positions, (max(width, 900), max(height, 520))


def draw_box(draw: ImageDraw.ImageDraw, xy: tuple[int, int], label: str, shape: str = "rect") -> None:
    x, y = xy
    w, h = 220, 88
    fill, stroke = "#f8fafc", "#334155"
    if shape == "decision":
        points = [(x + w // 2, y), (x + w, y + h // 2), (x + w // 2, y + h), (x, y + h // 2)]
        draw.polygon(points, fill="#fff7ed", outline=stroke)
    elif shape == "store":
        draw.rounded_rectangle((x, y, x + w, y + h), radius=24, fill="#eef2ff", outline=stroke, width=2)
    elif shape == "tool":
        draw.rounded_rectangle((x, y, x + w, y + h), radius=4, fill="#ecfeff", outline="#0891b2", width=2)
    else:
        draw.rounded_rectangle((x, y, x + w, y + h), radius=6, fill=fill, outline=stroke, width=2)
    lines = wrap_label(label, 20)
    total = len(lines) * 18
    for idx, line in enumerate(lines[:4]):
        tw, th = text_size(draw, line, font(13, idx == 0 and len(lines) == 1))
        draw.text((x + (w - tw) / 2, y + (h - total) / 2 + idx * 18), line, font=font(13), fill="#111827")


def render_graph(source: str, output: Path) -> None:
    first = next((line.strip() for line in source.splitlines() if line.strip()), "graph TD")
    direction = "LR" if " LR" in first else "TD"
    nodes, edges = parse_graph(source)
    positions, size = layered_positions(nodes, edges, direction)
    image = Image.new("RGB", size, "#ffffff")
    draw = ImageDraw.Draw(image)

    for src, dst, label, mark in edges:
        if src not in positions or dst not in positions:
            continue
        x1, y1 = positions[src]
        x2, y2 = positions[dst]
        start = (x1 + 110, y1 + 88) if direction != "LR" else (x1 + 220, y1 + 44)
        end = (x2 + 110, y2) if direction != "LR" else (x2, y2 + 44)
        color = "#64748b" if "." in mark else "#111827"
        draw.line((start, end), fill=color, width=2)
        if label:
            mx, my = (start[0] + end[0]) // 2, (start[1] + end[1]) // 2
            draw.rectangle((mx - 55, my - 12, mx + 55, my + 12), fill="#ffffff")
            tw, _ = text_size(draw, label, font(11))
            draw.text((mx - tw / 2, my - 9), label, font=font(11), fill="#111827")

    for node, label in nodes.items():
        raw = label
        shape = "rect"
        if "[[" in source and node in source:
            shape = "tool"
        if f"{node}{{" in source:
            shape = "decision"
        if f"{node}[(" in source:
            shape = "store"
        draw_box(draw, positions[node], raw, shape)
    image.save(output)


RELATION_RE = re.compile(r"^\s*([A-Za-z0-9_]+)\s+([|o}{\w.-]+)\s+([A-Za-z0-9_]+)\s*:\s*(.+)$")


def parse_er(source: str) -> tuple[dict[str, list[tuple[str, str, str]]], list[tuple[str, str, str]]]:
    entities: dict[str, list[tuple[str, str, str]]] = {}
    relations: list[tuple[str, str, str]] = []
    current: str | None = None
    for raw in source.splitlines():
        line = raw.strip()
        if not line or line.startswith(("erDiagram", "%%")):
            continue
        if line.endswith("{"):
            current = line.split()[0]
            entities[current] = []
            continue
        if line == "}":
            current = None
            continue
        if current:
            parts = line.split()
            if len(parts) >= 2:
                entities[current].append((parts[0], parts[1], parts[2] if len(parts) > 2 else ""))
            continue
        match = RELATION_RE.match(line)
        if match:
            relations.append((match.group(1), match.group(3), clean_label(match.group(4))))
            entities.setdefault(match.group(1), [])
            entities.setdefault(match.group(3), [])
    return entities, relations


def draw_table(draw: ImageDraw.ImageDraw, x: int, y: int, name: str, rows: list[tuple[str, str, str]]) -> tuple[int, int, int, int]:
    row_h = 34
    width = 300
    height = row_h * (max(len(rows), 1) + 1)
    draw.rectangle((x, y, x + width, y + height), fill="#fff7ed", outline="#f97316", width=2)
    draw.rectangle((x, y, x + width, y + row_h), fill="#ffedd5", outline="#f97316", width=2)
    tw, _ = text_size(draw, name, font(14, True))
    draw.text((x + (width - tw) / 2, y + 8), name, font=font(14, True), fill="#111827")
    if not rows:
        return x, y, x + width, y + height
    for idx, (typ, field, key) in enumerate(rows):
        yy = y + row_h * (idx + 1)
        draw.line((x, yy, x + width, yy), fill="#f97316", width=1)
        draw.text((x + 10, yy + 8), typ, font=font(11), fill="#111827")
        draw.text((x + 90, yy + 8), field, font=font(11), fill="#111827")
        if key:
            draw.text((x + 260, yy + 8), key, font=font(11, True), fill="#111827")
    return x, y, x + width, y + height


def render_er(source: str, output: Path) -> None:
    entities, relations = parse_er(source)
    names = list(entities)
    cols = 3 if len(names) > 5 else 2
    cell_w, cell_h = 370, 300
    width = max(900, 80 + cols * cell_w)
    height = max(520, 90 + ((len(names) + cols - 1) // cols) * cell_h)
    image = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(image)
    boxes: dict[str, tuple[int, int, int, int]] = {}
    for idx, name in enumerate(names):
        x = 50 + (idx % cols) * cell_w
        y = 50 + (idx // cols) * cell_h
        boxes[name] = draw_table(draw, x, y, name, entities[name])
    for src, dst, label in relations:
        if src not in boxes or dst not in boxes:
            continue
        sx1, sy1, sx2, sy2 = boxes[src]
        dx1, dy1, dx2, dy2 = boxes[dst]
        start = ((sx1 + sx2) // 2, sy2)
        end = ((dx1 + dx2) // 2, dy1)
        draw.line((start, end), fill="#111827", width=2)
        mx, my = (start[0] + end[0]) // 2, (start[1] + end[1]) // 2
        draw.rectangle((mx - 58, my - 12, mx + 58, my + 12), fill="#ffffff")
        tw, _ = text_size(draw, label, font(11))
        draw.text((mx - tw / 2, my - 9), label, font=font(11), fill="#111827")
    image.save(output)


def render_class(source: str, output: Path) -> None:
    classes: dict[str, list[str]] = {}
    relations: list[tuple[str, str, str]] = []
    current: str | None = None
    for raw in source.splitlines():
        line = raw.strip()
        if not line or line.startswith(("classDiagram", "%%")):
            continue
        if line.startswith("class ") and line.endswith("{"):
            current = line.split()[1]
            classes[current] = []
            continue
        if line == "}":
            current = None
            continue
        if current:
            classes[current].append(line)
        elif any(mark in line for mark in ["--", "<|", "*--", "o--"]):
            parts = re.split(r"\s+(?:<\|--|\*--|o--|--)\s+", line, maxsplit=1)
            if len(parts) == 2:
                relations.append((node_id(parts[0]), node_id(parts[1].split(":")[0]), line.split(":")[-1].strip() if ":" in line else ""))
    pseudo = "graph TD\n" + "\n".join(f"{src} -->|{label}| {dst}" if label else f"{src} --> {dst}" for src, dst, label in relations)
    nodes, edges = parse_graph(pseudo)
    for name in classes:
        nodes.setdefault(name, name)
    positions, size = layered_positions(nodes, edges, "TD")
    image = Image.new("RGB", (max(size[0], 1000), max(size[1], 700)), "#ffffff")
    draw = ImageDraw.Draw(image)
    for src, dst, label, mark in edges:
        if src in positions and dst in positions:
            x1, y1 = positions[src]
            x2, y2 = positions[dst]
            draw.line((x1 + 110, y1 + 120, x2 + 110, y2), fill="#475569", width=2)
    for name, attrs in classes.items():
        x, y = positions.get(name, (60, 60))
        h = 46 + min(len(attrs), 10) * 22
        draw.rectangle((x, y, x + 260, y + h), fill="#effcff", outline="#0891b2", width=2)
        draw.rectangle((x, y, x + 260, y + 36), fill="#cffafe", outline="#0891b2", width=2)
        tw, _ = text_size(draw, name, font(13, True))
        draw.text((x + (260 - tw) / 2, y + 9), name, font=font(13, True), fill="#111827")
        for idx, attr in enumerate(attrs[:10]):
            draw.text((x + 10, y + 42 + idx * 22), attr, font=font(10), fill="#111827")
    image.save(output)


def render_mermaid(source: str, output: Path) -> None:
    stripped = source.strip()
    if stripped.startswith("erDiagram") or "erDiagram" in stripped.splitlines()[0:3]:
        render_er(stripped, output)
    elif stripped.startswith("classDiagram"):
        render_class(stripped, output)
    else:
        render_graph(stripped, output)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    changed = 0
    for md in sorted(DOCS.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        matches = list(MERMAID_BLOCK.finditer(text))
        if not matches:
            continue

        file_slug = slug(md)
        pieces: list[str] = []
        last = 0
        for idx, match in enumerate(matches, start=1):
            source = match.group(1).strip()
            stem = f"{file_slug}-{idx:02d}"
            png = OUTPUT / f"{stem}.png"
            mmd = OUTPUT / f"{stem}.mmd"
            mmd.write_text(source + "\n", encoding="utf-8")
            render_mermaid(source, png)
            rel = Path("../../assets/images/mermaid") / png.name
            alt = f"{md.stem} diagram {idx}"
            pieces.append(text[last : match.start()])
            pieces.append(f"![{alt}]({rel.as_posix()})")
            last = match.end()
            changed += 1
        pieces.append(text[last:])
        md.write_text("".join(pieces), encoding="utf-8", newline="\n")
        print(f"updated {md.relative_to(ROOT)} ({len(matches)} diagram(s))")
    print(f"materialized {changed} Mermaid diagram(s)")


if __name__ == "__main__":
    main()
