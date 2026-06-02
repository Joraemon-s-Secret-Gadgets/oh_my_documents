from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "pages"


@dataclass(frozen=True)
class Document:
    source: str
    target: str
    short: str
    title: str
    description: str
    status_label: str
    section: str


DOCUMENTS = [
    Document(
        "docs/00_project_plan/00_project_plan.md",
        "00_project_plan.html",
        "Project Plan",
        "로브 (Lovv) — 프로젝트 기획서",
        "프로젝트 배경, 목표, 범위, 우선순위, 추진 일정을 정리한 기획 문서입니다.",
        "검토 중",
        "프로젝트 기획서",
    ),
    Document(
        "docs/01_requirements/01_requirements.md",
        "01_requirements.html",
        "Requirements Spec",
        "로브 (Lovv) — 요구사항 명세서",
        "요구사항 명세서와 세부 기능 요구사항을 하나로 통합한 공개 문서입니다.",
        "검토 중",
        "요구사항 명세서",
    ),
    Document(
        "docs/02_service_flow/02_service_flow.md",
        "02_service_flow.html",
        "Service Flow",
        "로브 (Lovv) — 서비스 흐름 명세서",
        "인증, 목적지 탐색, AI 일정 생성, 저장·외부 연동, 운영 데이터 검증 흐름을 정의한 문서입니다.",
        "검토 중",
        "설계·명세 문서",
    ),
    Document(
        "docs/03_technical_spec/03_technical_spec.md",
        "03_technical_spec.html",
        "Technical Spec",
        "로브 (Lovv) — 기술 명세서",
        "프론트엔드, 백엔드, 데이터, 외부 API, AI/RAG 계층의 기술 책임과 경계를 정의합니다.",
        "검토 중",
        "설계·명세 문서",
    ),
    Document(
        "docs/04_data_collect_plan/04_data_collect_plan.md",
        "04_data_collect_plan.html",
        "Data Collection",
        "로브 (Lovv) — 데이터 수집 계획서",
        "한국·일본 지역 추천 품질 확보를 위한 수집 범위, 출처, 전처리, 품질 관리 기준을 정의합니다.",
        "검토 중",
        "설계·명세 문서",
    ),
    Document(
        "docs/05_api_spec/05_api_spec.md",
        "05_api_spec.html",
        "API Spec",
        "로브 (Lovv) — API 명세서",
        "추천, 지도, 저장, 피드백, 운영 검토 API의 계약과 공통 오류 형식을 정의합니다.",
        "기획 단계",
        "설계·명세 문서",
    ),
    Document(
        "docs/06_database_design/06_database_design.md",
        "06_database_design.html",
        "Database Design",
        "로브 (Lovv) — 데이터베이스 설계 명세서",
        "목적지, 축제, 사용자, 저장 일정, 피드백, 운영 검토 데이터 모델을 정의합니다.",
        "기획 단계",
        "설계·명세 문서",
    ),
    Document(
        "docs/07_agent_spec/07_agent_spec.md",
        "07_agent_spec.html",
        "Agent Spec",
        "로브 (Lovv) — Agent 명세서",
        "조건 분류, 검색, 후보 선정, 일정 구성, 설명 생성 Agent 파이프라인을 정의합니다.",
        "검토 중",
        "설계·명세 문서",
    ),
]


REDIRECTS = {
    "04_api_spec.html": "05_api_spec.html",
    "05_database_design.html": "06_database_design.html",
    "06_agent_spec.html": "07_agent_spec.html",
}


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def meta_value(markdown: str, key: str) -> str:
    match = re.search(rf"^>\s*{re.escape(key)}:\s*(.+)$", markdown, re.MULTILINE)
    return match.group(1).strip() if match else ""


def title_value(markdown: str) -> str:
    match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
    return match.group(1).strip() if match else "로브 (Lovv) 문서"


def plain_version(version: str) -> str:
    match = re.search(r"v\d+(?:\.\d+)*", version)
    return match.group(0) if match else version


def heading_id(text: str, fallback: int) -> str:
    number = re.match(r"^(\d+(?:\.\d+)*)", text.strip())
    if number:
        return "s" + number.group(1).replace(".", "-")
    slug = re.sub(r"[^0-9A-Za-z가-힣]+", "-", text.strip()).strip("-").lower()
    return slug or f"section-{fallback}"


def inline(value: str) -> str:
    escaped = html.escape(value)
    escaped = re.sub(r"`([^`]+)`", lambda m: f"<code>{m.group(1)}</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    return escaped


def split_table_row(line: str) -> list[str]:
    stripped = line.strip().strip("|")
    return [cell.strip() for cell in stripped.split("|")]


def slug_class(value: str) -> str:
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"[^0-9A-Za-z가-힣]+", "-", value).strip("-").lower()
    return value


def table_classes(header: list[str], body: list[list[str]]) -> tuple[str, str]:
    normalized = {slug_class(cell) for cell in header}
    max_cell_length = max((len(re.sub(r"<br\s*/?>", " ", cell)) for row in body for cell in row), default=0)
    column_count = len(header)
    wrap_classes = ["table-wrap"]
    table_classes = ["info-tbl"]

    if column_count >= 3 or max_cell_length >= 90:
        wrap_classes.append("wide")
    if column_count >= 5 or max_cell_length >= 180:
        wrap_classes.append("extra-wide")
    if {"method", "path", "auth", "설명"}.issubset(normalized):
        wrap_classes.append("wide")
        table_classes.append("api-contract-tbl")
    if {"버전", "날짜", "작성자", "변경-내용"}.issubset(normalized):
        wrap_classes.append("wide")
        table_classes.append("change-log-tbl")
    if {"단계", "노드-모듈명", "중앙-통제-및-역할", "입력", "출력"}.issubset(normalized):
        wrap_classes.extend(["wide", "extra-wide"])
        table_classes.append("agent-pipeline-tbl")
    if {"항목", "내용"}.issubset(normalized) or {"항목", "결정"}.issubset(normalized):
        table_classes.append("decision-tbl")

    return " ".join(dict.fromkeys(wrap_classes)), " ".join(dict.fromkeys(table_classes))


def render_table(lines: list[str]) -> str:
    rows = [split_table_row(line) for line in lines if line.strip()]
    if len(rows) < 2:
        return ""
    header = rows[0]
    body = rows[2:]
    wrap_class, table_class = table_classes(header, body)
    thead = "<thead><tr>" + "".join(f"<th>{inline(cell)}</th>" for cell in header) + "</tr></thead>"
    tbody_rows = []
    for row in body:
        cells = row + [""] * (len(header) - len(row))
        tbody_rows.append("<tr>" + "".join(f"<td>{inline(cell)}</td>" for cell in cells[: len(header)]) + "</tr>")
    tbody = "<tbody>\n" + "\n".join(tbody_rows) + "\n</tbody>"
    return f'<div class="{wrap_class}"><table class="{table_class}">\n{thead}{tbody}</table></div>'


def collect_headings(lines: list[str]) -> list[tuple[int, str, str]]:
    headings: list[tuple[int, str, str]] = []
    fallback = 1
    title_seen = False
    for line in lines:
        match = re.match(r"^(#{1,3})\s+(.+)$", line)
        if not match:
            continue
        level = len(match.group(1))
        text = match.group(2).strip()
        if not title_seen:
            title_seen = True
            continue
        hid = heading_id(text, fallback)
        headings.append((level, text, hid))
        fallback += 1
    return headings


def render_blocks(markdown: str) -> tuple[str, list[tuple[int, str, str]]]:
    lines = markdown.splitlines()
    headings = collect_headings(lines)
    output: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    heading_seen = False
    fallback = 1
    i = 0

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            output.append(f'<p class="doc-p">{inline(" ".join(paragraph).strip())}</p>')
            paragraph = []

    def flush_list() -> None:
        nonlocal list_items
        if list_items:
            output.append('<ul class="bullet-list">')
            output.extend(f"<li>{inline(item)}</li>" for item in list_items)
            output.append("</ul>")
            list_items = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            flush_list()
            i += 1
            continue

        if stripped.startswith("```"):
            flush_paragraph()
            flush_list()
            lang = stripped[3:].strip()
            code_lines: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            code = "\n".join(code_lines)
            if lang == "mermaid":
                output.append(f'<div class="mermaid">{html.escape(code)}</div>')
            else:
                output.append(f"<pre><code>{html.escape(code)}</code></pre>")
            i += 1
            continue

        if re.match(r"^\|.+\|$", stripped) and i + 1 < len(lines) and re.match(r"^\|\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$", lines[i + 1].strip()):
            flush_paragraph()
            flush_list()
            table_lines = [line, lines[i + 1]]
            i += 2
            while i < len(lines) and re.match(r"^\|.+\|$", lines[i].strip()):
                table_lines.append(lines[i])
                i += 1
            output.append(render_table(table_lines))
            continue

        heading = re.match(r"^(#{1,3})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            flush_list()
            level = len(heading.group(1))
            text = heading.group(2).strip()
            if not heading_seen:
                heading_seen = True
                i += 1
                continue
            hid = heading_id(text, fallback)
            tag = "h1" if level == 1 else "h2"
            klass = "s-h1" if level == 1 else "s-h2"
            output.append(f'<{tag} id="{hid}" class="{klass}">{inline(text)}</{tag}>')
            fallback += 1
            i += 1
            continue

        if stripped.startswith(">"):
            flush_paragraph()
            flush_list()
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_lines.append(lines[i].strip()[1:].strip())
                i += 1
            output.append("<blockquote>")
            output.extend(f'<p class="doc-p">{inline(q)}</p>' for q in quote_lines if q)
            output.append("</blockquote>")
            continue

        bullet = re.match(r"^[-*]\s+(.+)$", stripped)
        ordered = re.match(r"^\d+\.\s+(.+)$", stripped)
        if bullet or ordered:
            flush_paragraph()
            list_items.append((bullet or ordered).group(1))
            i += 1
            continue

        flush_list()
        paragraph.append(stripped)
        i += 1

    flush_paragraph()
    flush_list()
    return "\n".join(output), headings


def render_toc(headings: list[tuple[int, str, str]]) -> str:
    lines = ['<div class="toc-section"><a class="toc-link active" href="#cover">표지 / 문서 정보</a></div>']
    current_open = False
    for level, text, hid in headings:
        if level == 1:
            if current_open:
                lines.append("</div>")
            lines.append('<div class="toc-section">')
            lines.append(f'<div class="toc-section-hd">{inline(text)}</div>')
            current_open = True
        lines.append(f'<a class="toc-link" href="#{hid}">{inline(text)}</a>')
    if current_open:
        lines.append("</div>")
    return "\n".join(lines)


def render_doc_nav(doc: Document) -> str:
    index = DOCUMENTS.index(doc)
    previous_doc = DOCUMENTS[index - 1] if index > 0 else None
    next_doc = DOCUMENTS[index + 1] if index < len(DOCUMENTS) - 1 else None
    previous_link = (
        f'<a class="doc-nav-link" href="./{html.escape(previous_doc.target)}">이전 문서<br><strong>{html.escape(previous_doc.title.replace("로브 (Lovv) — ", ""))}</strong></a>'
        if previous_doc
        else '<span class="doc-nav-link disabled">이전 문서<br><strong>없음</strong></span>'
    )
    next_link = (
        f'<a class="doc-nav-link" href="./{html.escape(next_doc.target)}">다음 문서<br><strong>{html.escape(next_doc.title.replace("로브 (Lovv) — ", ""))}</strong></a>'
        if next_doc
        else '<span class="doc-nav-link disabled">다음 문서<br><strong>없음</strong></span>'
    )
    return f"""        <nav class="doc-nav" aria-label="이전 다음 문서">
          <a class="doc-nav-home" href="../index.html">문서 홈</a>
          <div class="doc-nav-pager">
            {previous_link}
            {next_link}
          </div>
        </nav>"""


def render_page(doc: Document) -> str:
    markdown = read_text(doc.source)
    title = title_value(markdown)
    version = meta_value(markdown, "문서 버전")
    status = meta_value(markdown, "문서 상태")
    body, headings = render_blocks(markdown)
    toc = render_toc(headings)
    doc_nav = render_doc_nav(doc)
    version_short = plain_version(version)
    mermaid = (
        '\n    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js" defer></script>'
        if "```mermaid" in markdown
        else ""
    )
    full_title = f"{doc.title} {version_short}".strip()
    return f"""<!DOCTYPE html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{html.escape(full_title)}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link
      href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Noto+Serif+KR:wght@600;700&display=swap"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="../assets/css/requirements.css" />{mermaid}
  </head>
  <body>
    <div class="layout">
      <aside>
        <div class="aside-brand">
          <div class="aside-logo">로브</div>
          <div class="aside-ver">{html.escape(doc.short)} · {html.escape(version_short)}</div>
          <div class="aside-status"><div class="status-dot"></div><span>{html.escape(doc.status_label)}</span></div>
        </div>
        <nav class="toc">
{toc}
        </nav>
      </aside>
      <main id="cover">
        <h1 id="cover-title" class="s-h1">{html.escape(title)}</h1>
{body}
{doc_nav}
      </main>
    </div>
    <script src="../assets/js/requirements.js" defer></script>
  </body>
</html>
"""


def render_redirect(source: str, target: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta http-equiv="refresh" content="0; url=./{html.escape(target)}" />
    <title>문서 위치 변경</title>
    <link rel="stylesheet" href="../assets/css/site.css" />
  </head>
  <body>
    <main class="site-shell">
      <section>
        <h1 class="site-title">문서 위치가 변경되었습니다</h1>
        <p><code>{html.escape(source)}</code>는 최신 문서 번호 체계에 따라 <a href="./{html.escape(target)}"><code>{html.escape(target)}</code></a>로 이동했습니다.</p>
      </section>
    </main>
  </body>
</html>
"""


def render_index() -> str:
    grouped: dict[str, list[Document]] = {}
    for doc in DOCUMENTS:
        grouped.setdefault(doc.section, []).append(doc)

    sections = []
    for title, docs in grouped.items():
        cards = []
        for doc in docs:
            markdown = read_text(doc.source)
            version = plain_version(meta_value(markdown, "문서 버전"))
            cards.append(
                f"""          <a class="doc-card primary" href="./pages/{html.escape(doc.target)}">
            <span class="status">{html.escape(doc.status_label)}</span>
            <h3>{html.escape(doc.title)} {html.escape(version)}</h3>
            <p>{html.escape(doc.description)}</p>
          </a>"""
            )
        section_id = re.sub(r"[^0-9A-Za-z가-힣]+", "-", title).strip("-")
        sections.append(
            f"""      <section aria-labelledby="{section_id}">
        <h2 id="{section_id}" class="section-title">{html.escape(title)}</h2>
        <div class="doc-stack">
{chr(10).join(cards)}
        </div>
      </section>"""
        )

    workflow = "\n".join(f"          <li>{html.escape(doc.title.replace('로브 (Lovv) — ', ''))}</li>" for doc in DOCUMENTS)
    return f"""<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>로브 (Lovv) 문서 허브</title>
    <link rel="stylesheet" href="./assets/css/site.css">
  </head>
  <body>
    <main class="site-shell">
      <header class="site-header">
        <h1 class="site-title">로브 (Lovv)</h1>
        <p>
          Markdown 원본 문서를 GitHub Pages에서 공유할 수 있는 HTML 문서로 변환해 모아둔 문서 허브입니다.
          현재 생성된 로브 프로젝트 문서를 공개합니다.
        </p>
      </header>

{chr(10).join(sections)}

      <section aria-labelledby="workflow-title">
        <h2 id="workflow-title" class="section-title">문서 작성 흐름</h2>
        <ol class="workflow">
{workflow}
        </ol>
      </section>

      <footer class="site-footer">
        Source documents live in <code>docs/</code>. Generated HTML pages live in <code>pages/</code>.
      </footer>
    </main>
  </body>
</html>
"""


def main() -> None:
    PAGES.mkdir(exist_ok=True)
    for doc in DOCUMENTS:
        (PAGES / doc.target).write_text(render_page(doc), encoding="utf-8", newline="\n")
    for source, target in REDIRECTS.items():
        (PAGES / source).write_text(render_redirect(source, target), encoding="utf-8", newline="\n")
    (ROOT / "index.html").write_text(render_index(), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
