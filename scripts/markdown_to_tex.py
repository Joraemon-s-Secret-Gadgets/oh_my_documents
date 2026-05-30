import argparse
import re
from pathlib import Path


SPECIAL_CHARS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def escape_latex(text: str) -> str:
    japanese_terms = {
        "楽天トラベル": "Rakuten Travel",
        "食べログ": "Tabelog",
        "じゃらん": "Jalan",
        "一休": "Ikyu",
        "金沢": "Kanazawa",
        "観光": "tourism",
        "モデルコース": "model course",
        "カフェ": "cafe",
        "穴場": "hidden spot",
        "ひとり旅": "solo travel",
    }
    for source, target in japanese_terms.items():
        text = text.replace(source, target)
    text = text.replace("ー", "-")
    escaped = "".join(SPECIAL_CHARS.get(char, char) for char in text)
    escaped = re.sub(r"`([^`]+)`", r"\\texttt{\1}", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\\url{\2})", escaped)
    escaped = re.sub(r"([一-龯ぁ-ゟ゠-ヿー]+)", r"{\\jpfont \1}", escaped)
    escaped = escaped.replace("✓", "O")
    escaped = escaped.replace("✗", "X")
    escaped = escaped.replace("🌐", "글로벌")
    escaped = escaped.replace("🟡", "주의")
    escaped = escaped.replace("🔴", "위험")
    escaped = escaped.replace("☀", "맑음")
    escaped = escaped.replace("⚠", "주의:")
    escaped = escaped.replace("→", r"$\rightarrow$")
    escaped = escaped.replace("—", "---")
    return escaped


def is_table_separator(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells)


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def table_target_width(column_count: int) -> float:
    target_by_columns = {
        2: 0.980,
        3: 0.960,
        4: 0.940,
        5: 0.920,
        6: 0.880,
    }
    return target_by_columns.get(column_count, 0.860)


def normalize_column_widths(widths: list[float], column_count: int, min_widths: list[float] | None = None) -> list[float]:
    target = table_target_width(column_count)
    total = sum(widths)
    if total <= 0:
        return [target / column_count] * column_count
    normalized = [width / total * target for width in widths]
    if not min_widths:
        return normalized

    fixed = [max(width, minimum) for width, minimum in zip(normalized, min_widths)]
    overflow = sum(fixed) - target
    if overflow <= 0:
        return fixed

    adjustable = [max(0.0, width - minimum) for width, minimum in zip(fixed, min_widths)]
    adjustable_total = sum(adjustable)
    if adjustable_total <= 0:
        return normalize_column_widths(min_widths, column_count)
    return [
        width - overflow * (adjustable[index] / adjustable_total)
        for index, width in enumerate(fixed)
    ]


def infer_column_widths(header: list[str], body: list[list[str]]) -> list[float]:
    column_count = len(header)
    weights: list[float] = []
    min_widths: list[float] = []
    for index, title in enumerate(header):
        values = [row[index] for row in body if index < len(row)]
        max_length = max([len(title), *(len(value) for value in values)] or [1])
        average_length = sum(len(value) for value in values) / max(1, len(values))
        weight = max(len(title) * 1.2, min(max_length, 42) * 0.65 + min(average_length, 34) * 0.35)
        if re.search(r"(ID|버전|날짜|인증|상태|PoC|예산|기간|구분|단계|역할)$", title):
            weight *= 0.70
        if re.search(r"(내용|설명|기준|책임|니즈|산출물|의존성|변경 내용|요구사항)", title):
            weight *= 1.25
        weights.append(max(6.0, weight))

        minimum = 0.080
        if re.search(r"(ID|Role ID)", title):
            minimum = 0.160
        elif re.search(r"(버전|날짜|기간|예산)", title):
            minimum = 0.125
        elif re.search(r"(구분|단계|상태|인증|역할|PoC|Production)", title):
            minimum = 0.105
        if any(len(token) >= 12 for value in values for token in re.split(r"\s+", value)):
            minimum = max(minimum, 0.130)
        min_widths.append(minimum)
    return normalize_column_widths(weights, column_count, min_widths)


def table_to_latex(
    rows: list[str],
    column_widths: list[float] | None = None,
    centered_columns: set[int] | None = None,
    forced_line_breaks: dict[str, list[str]] | None = None,
) -> list[str]:
    if len(rows) < 2 or not is_table_separator(rows[1]):
        return [escape_latex(row) for row in rows]

    header = split_table_row(rows[0])
    body = [split_table_row(row) for row in rows[2:]]
    column_count = len(header)
    if column_widths and len(column_widths) == column_count:
        widths = normalize_column_widths(column_widths, column_count)
    else:
        widths = infer_column_widths(header, body)
    centered_columns = centered_columns or set()
    col_specs = []
    for index, width in enumerate(widths):
        alignment = r"\centering" if index in centered_columns else r"\RaggedRight"
        col_specs.append(rf">{{{alignment}\arraybackslash}}m{{{width:.3f}\linewidth}}")
    col_spec = "".join(col_specs)

    result = [
        r"\DocNeedspace{8\baselineskip}",
        r"\begin{small}",
        rf"\begin{{longtable}}{{@{{}}{col_spec}@{{}}}}",
        r"\toprule",
        " & ".join(
            rf"\multicolumn{{1}}{{>{{\centering\arraybackslash}}m{{{widths[index]:.3f}\linewidth}}}}{{\textbf{{"
            + format_table_cell(cell, forced_line_breaks)
            + "}}"
            for index, cell in enumerate(header)
        )
        + r" \\",
        r"\midrule",
        r"\endhead",
    ]
    for row in body:
        padded = row[:column_count] + [""] * max(0, column_count - len(row))
        result.append(" & ".join(format_table_cell(cell, forced_line_breaks) for cell in padded[:column_count]) + r" \\")
    result.extend([r"\bottomrule", r"\end{longtable}", r"\end{small}", ""])
    return result


def format_table_cell(cell: str, forced_line_breaks: dict[str, list[str]] | None = None) -> str:
    if forced_line_breaks and cell in forced_line_breaks:
        return r"\newline ".join(escape_latex(part) for part in forced_line_breaks[cell])
    if cell == "Production":
        return r"{\footnotesize Production}"
    if re.fullmatch(r"[A-Z]+(?:-[A-Z0-9]+)+-\d+", cell):
        return r"{\footnotesize " + escape_latex(cell).replace("-", r"-\allowbreak{}") + "}"
    return escape_latex(cell)


def format_body_text(text: str) -> str:
    forced_line_breaks = {
        "본 문서는 로브(Lovv) 서비스의 아이디어 기획 단계에서 제품의 핵심 기능, API 연동 요구사항, 비기능 요구사항을 정의한다.": [
            "본 문서는 로브(Lovv) 서비스의 아이디어 기획 단계에서 제품의 핵심 기능,",
            "API 연동 요구사항, 비기능 요구사항을 정의한다.",
        ],
        "국내 소도시 (강원·전남·경남 등) 및 일본 소도시 (호쿠리쿠·기후·산인 등) 추천 — 나라별 독립 트랙": [
            "국내 소도시 (강원·전남·경남 등) 및",
            "일본 소도시 (호쿠리쿠·기후·산인 등) 추천 — 나라별 독립 트랙",
        ],
    }
    if text in forced_line_breaks:
        return r"\newline ".join(escape_latex(part) for part in forced_line_breaks[text])
    if "제외하고 " in text:
        before, after = text.split("제외하고 ", 1)
        return escape_latex(before + "제외하고") + r"\newline " + escape_latex(after)
    return escape_latex(text)


def issue_table_to_paragraphs(rows: list[str]) -> list[str]:
    if len(rows) < 3 or not is_table_separator(rows[1]):
        return table_to_latex(rows)

    body = [split_table_row(row) for row in rows[2:]]
    result: list[str] = []
    for row in body:
        if len(row) < 2:
            continue
        label, description = row[0], row[1]
        if label == "유명 관광지 편중":
            description = (
                "여행자는 검색 결과, SNS 후기, 패키지 상품에서 반복적으로 노출되는 대도시와 유명 관광지 위주로 정보를 찾게 된다. "
                "이 과정에서 실제 취향이나 여행 시기에 더 잘 맞는 소도시 후보는 비교 대상에 오르기 어렵고, 성수기 혼잡이나 높은 비용을 감수한 채 익숙한 목적지를 선택하게 된다."
            )
        elif label == "소도시 정보 부족":
            description = (
                "방문객 수가 낮은 관광지와 주변 소도시는 공식 정보, 블로그 후기, 지도 정보, 축제 일정, 교통편이 여러 채널에 흩어져 있다. "
                "여행자는 목적지의 계절성, 이동 난이도, 주변 관광 자원, 비수기 매력을 한 번에 파악하기 어려워 계획 수립에 많은 시간을 쓰게 된다."
            )
        elif label == "여행 조건 비교 어려움":
            description = (
                "날씨, 교통, 혼잡도, 동행 유형, 체험 요소, 여행 기간을 동시에 고려해야 하지만 일반 여행 검색은 조건별 정보를 분리해서 제공하는 경우가 많다. "
                "특히 짧은 일정에서는 비가 올 때의 대체 코스, 이동 시간이 긴 목적지의 부담, 축제 포함 여부 같은 의사결정 기준을 사용자가 직접 조합해야 한다."
            )
        elif label == "추천 신뢰도 부족":
            description = (
                "일반 생성형 답변은 그럴듯한 일정은 제시할 수 있지만, 어떤 데이터와 출처를 근거로 추천했는지 확인하기 어려운 경우가 있다. "
                "축제 개최 여부, 날씨 정보, 장소 운영 상태처럼 변동성이 큰 정보가 검증되지 않으면 사용자는 추천 결과를 실제 여행 계획에 바로 적용하기 어렵다."
            )
        elif label == "지역 관광 수요 불균형":
            description = (
                "관광 수요가 일부 대도시와 대표 관광지에 집중되면 숙박·교통·상권 혼잡이 심해지고, 여행 만족도와 지역 수용력이 함께 낮아질 수 있다. "
                "반면 주변 소도시나 비수기 목적지는 충분한 매력을 갖고 있어도 노출 기회가 부족해 방문 수요를 만들기 어렵다. "
                "로브는 인기 지역의 대체 목적지와 비수기 방문 가치를 함께 제안해 관광 수요를 더 넓은 지역과 시기로 분산시키는 역할을 한다."
            )
        elif label == "데이터 분산":
            description = (
                "여행 추천에 필요한 관광지 정보, 축제 일정, 교통 접근성, 날씨, 지도, 숙박·맛집 탐색 링크는 서로 다른 기관과 플랫폼에 흩어져 있다. "
                "이 데이터들은 형식과 갱신 주기가 달라 한 번에 비교하기 어렵고, 사용자가 직접 취합하면 정보 누락이나 오래된 정보를 사용할 가능성이 높다. "
                "서비스는 목적지 단위로 필요한 데이터를 묶고 출처와 갱신 기준을 관리해 추천 결과의 일관성과 신뢰도를 높여야 한다."
            )
        elif label == "운영 검증 필요":
            description = (
                "지자체, 관광 운영자, 데이터 제공 기관이 제안하는 지역 정보는 실제 서비스에 반영되기 전에 정확성, 최신성, 공개 적합성을 검토해야 한다. "
                "검증 절차가 없으면 폐업한 장소, 종료된 축제, 과장된 홍보 정보가 추천 결과에 포함될 수 있고 서비스 신뢰도가 낮아진다. "
                "따라서 데이터 제안, 관리자 검토, 승인·반려 이력, 갱신 상태를 관리하는 운영 흐름이 필요하다."
            )
        escaped_label = escape_latex(label)
        result.append(r"\DocNeedspace{5\baselineskip}")
        result.append(r"\subsubsection*{" + escaped_label + "}")
        result.append(escape_latex(description))
        result.append("")
    return result


def success_criteria_table_to_latex(rows: list[str]) -> list[str]:
    if len(rows) < 3 or not is_table_separator(rows[1]):
        return table_to_latex(rows)

    body = [split_table_row(row) for row in rows[2:]]
    result = [
        r"\DocNeedspace{8\baselineskip}",
        r"\begin{center}",
        r"\renewcommand{\arraystretch}{1.55}",
        r"\begin{tabular}{@{}>{\RaggedRight\arraybackslash}m{0.250\linewidth}>{\RaggedRight\arraybackslash}m{0.730\linewidth}@{}}",
        r"\toprule",
        r"\rowcolor{LovvGreen!12}\multicolumn{1}{c}{\textbf{구분}} & \multicolumn{1}{c}{\textbf{성공 기준}} \\",
        r"\midrule",
    ]
    for row in body:
        if len(row) < 2:
            continue
        label, criterion = row[0], row[1]
        result.append(
            r"\textcolor{LovvGreen}{\textbf{"
            + escape_latex(label)
            + r"}} & "
            + escape_latex(criterion)
            + r" \\[0.35em]"
        )
    result.extend([r"\bottomrule", r"\end{tabular}", r"\end{center}", ""])
    return result


def close_list(output: list[str], in_list: bool) -> bool:
    if in_list:
        output.append(r"\end{itemize}")
        output.append("")
    return False


def extract_document_info(markdown: str) -> tuple[str, dict[str, str]]:
    lines = markdown.splitlines()
    info: dict[str, str] = {}
    output: list[str] = []
    in_initial_info = False
    before_content = True
    before_numbered_section = True

    for line in lines:
        stripped = line.strip()
        numbered_section = re.match(r"^#\s+\d+\.", stripped)
        if numbered_section:
            before_numbered_section = False
        if (before_content or before_numbered_section) and stripped.startswith(">"):
            item = stripped.lstrip("> ").strip()
            if ":" in item:
                key, value = item.split(":", 1)
                info[key.strip()] = value.strip()
            else:
                info[item] = ""
            in_initial_info = True
            continue
        if before_content and in_initial_info and not stripped:
            in_initial_info = False
            before_content = False
            continue
        if stripped and not stripped.startswith("#"):
            before_content = False
        output.append(line)

    return "\n".join(output), info


def markdown_to_latex(
    markdown: str,
    title: str,
    author: str,
    mentor: str | None,
    team: str | None,
    service_label: str | None,
    section_pagebreak: bool,
    ci_image: str | None,
    ci_variant: str | None,
    ci_images: list[str] | None,
    toc_pagebreak_before: list[str] | None,
    body_pagebreak_before: list[str] | None,
    skip_preface: bool,
) -> str:
    markdown, document_info = extract_document_info(markdown)
    output: list[str] = []
    lines = markdown.splitlines()
    i = 0
    in_list = False
    in_code = False
    current_heading = ""
    preface_skipped = not skip_preface

    while i < len(lines):
        line = lines[i].rstrip()

        if not preface_skipped:
            heading = re.match(r"^(#{1,6})\s+(.+)$", line)
            if heading and len(heading.group(1)) == 1 and re.match(r"^\d+\.", heading.group(2).strip()):
                preface_skipped = True
            else:
                i += 1
                continue

        if line.startswith("```"):
            in_list = close_list(output, in_list)
            if not in_code:
                output.append(r"\begin{verbatim}")
                in_code = True
            else:
                output.append(r"\end{verbatim}")
                output.append("")
                in_code = False
            i += 1
            continue

        if in_code:
            output.append(line)
            i += 1
            continue

        if line.strip().startswith("|") and i + 1 < len(lines) and is_table_separator(lines[i + 1]):
            in_list = close_list(output, in_list)
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].rstrip())
                i += 1
            if current_heading in {"2.1 사용자 문제", "2.2 시장·운영 문제"}:
                output.extend(issue_table_to_paragraphs(table_lines))
            elif current_heading == "3.2 성공 기준":
                output.extend(success_criteria_table_to_latex(table_lines))
            elif current_heading == "4.2 사용자 흐름":
                output.extend(
                    table_to_latex(
                        table_lines,
                        [0.10, 0.24, 0.40, 0.24],
                        {0},
                        {"자연어 취향 또는 지도 마커 선택": ["자연어 취향 또는", "지도 마커 선택"]},
                    )
                )
            elif current_heading == "5. 주요 사용자 및 이해관계자":
                output.extend(table_to_latex(table_lines, [0.23, 0.20, 0.55]))
            elif current_heading == "6.1 PoC 범위":
                output.extend(table_to_latex(table_lines, [0.12, 0.50, 0.10, 0.14, 0.12], {0, 2, 3, 4}))
            elif current_heading == "7.2 추천 기능":
                output.extend(table_to_latex(table_lines, [0.26, 0.72], {0}))
            elif current_heading == "8.1 필요 데이터":
                output.extend(table_to_latex(table_lines, [0.30, 0.68], {0}))
            elif current_heading == "8.2 외부 연동":
                output.extend(table_to_latex(table_lines, [0.34, 0.64], {0}))
            elif current_heading == "10. 추진 일정":
                output.extend(table_to_latex(table_lines, [0.20, 0.28, 0.50], {0, 1}))
            elif current_heading == "12. 리스크 및 대응":
                output.extend(table_to_latex(table_lines, [0.24, 0.34, 0.40], {0}))
            elif current_heading == "13. 후속 문서":
                output.extend(table_to_latex(table_lines, [0.30, 0.68], {0}))
            elif current_heading == "14. 변경 이력":
                output.extend(table_to_latex(table_lines, [0.11, 0.18, 0.16, 0.53], {0, 1, 2}))
            else:
                output.extend(table_to_latex(table_lines))
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            in_list = close_list(output, in_list)
            level = len(heading.group(1))
            raw_text = heading.group(2).strip()
            current_heading = raw_text
            if section_pagebreak and level == 1 and not output and not re.match(r"^\d+\.", raw_text):
                i += 1
                continue
            if section_pagebreak and level == 1 and re.match(r"^\d+\.", raw_text) and output:
                output.append(r"\newpage")
                output.append("")
            if section_pagebreak and raw_text == "2.2 시장·운영 문제":
                output.append(r"\newpage")
                output.append("")
            if body_pagebreak_before and raw_text in body_pagebreak_before:
                output.append(r"\newpage")
                output.append("")
            text = escape_latex(raw_text)
            if level == 1:
                output.append(r"\DocNeedspace{10\baselineskip}")
                output.append(r"\section*{" + text + "}")
                if toc_pagebreak_before and raw_text in toc_pagebreak_before:
                    output.append(r"\addtocontents{toc}{\protect\clearpage}")
                output.append(r"\addcontentsline{toc}{section}{" + text + "}")
            elif level == 2:
                output.append(r"\DocNeedspace{8\baselineskip}")
                output.append(r"\subsection*{" + text + "}")
                if toc_pagebreak_before and raw_text in toc_pagebreak_before:
                    output.append(r"\addtocontents{toc}{\protect\clearpage}")
                output.append(r"\addcontentsline{toc}{subsection}{" + text + "}")
            elif level == 3:
                output.append(r"\DocNeedspace{5\baselineskip}")
                output.append(r"\subsubsection*{" + text + "}")
            else:
                output.append(r"\DocNeedspace{4\baselineskip}")
                output.append(r"\paragraph{" + text + "}")
            output.append("")
            i += 1
            continue

        if line.startswith(">"):
            in_list = close_list(output, in_list)
            output.append(r"\begin{quote}")
            while i < len(lines) and lines[i].startswith(">"):
                output.append(escape_latex(lines[i].lstrip("> ").rstrip()) + r"\\")
                i += 1
            output.append(r"\end{quote}")
            output.append("")
            continue

        bullet = re.match(r"^\s*[-*]\s+(.+)$", line)
        ordered = re.match(r"^\s*\d+\.\s+(.+)$", line)
        if bullet or ordered:
            if not in_list:
                output.append(r"\begin{itemize}")
                in_list = True
            output.append(r"\item " + format_body_text((bullet or ordered).group(1).strip()))
            i += 1
            continue

        if not line.strip():
            in_list = close_list(output, in_list)
            output.append("")
            i += 1
            continue

        in_list = close_list(output, in_list)
        output.append(r"\DocNeedspace{3\baselineskip}")
        output.append(format_body_text(line.strip()))
        output.append("")
        i += 1

    close_list(output, in_list)

    body = "\n".join(output)
    mentor_line = ""
    if mentor:
        mentor_line = rf"\\[0.8em]{{\large {escape_latex(mentor)}}}"
    scope_line = service_label or document_info.get("적용 범위")
    scope_block = ""
    if scope_line:
        scope_block = rf"""
\vspace{{1.5em}}
{{\large {escape_latex(scope_line)}\par}}
"""
    document_version = document_info.get("문서 버전")
    if document_version and "—" in document_version:
        document_version = document_version.split("—", 1)[0].strip()
    header_status = " | ".join(
        value for value in [document_version, document_info.get("문서 상태"), document_info.get("적용 범위")] if value
    )
    if not header_status:
        header_status = "Lovv"
    team_line = ""
    if team:
        team_line = rf"{{\Large\bfseries {escape_latex(team)}\par}}\vspace{{0.8em}}"
    ci_paths = [path.replace("\\", "/") for path in (ci_images or [])]
    if not ci_paths and ci_image:
        ci_paths = [ci_image.replace("\\", "/")]
    title_logo = ""
    header_logo = escape_latex(title)
    if ci_paths:
        include_options = "width=0.36\\textwidth"
        header_include_options = "height=13pt"
        if ci_variant == "sk-networks":
            include_options = "width=0.30\\textwidth, trim=0 235 0 0, clip"
            header_include_options = "height=13pt, trim=0 235 0 0, clip"
        if len(ci_paths) > 1:
            title_logo_images = r"\hbox to\textwidth{" + r"\hfil ".join(
                rf"\makebox[0.28\textwidth][c]{{\includegraphics[width={'0.26' if 'en-core' in path.lower() else '0.22'}\textwidth,height={'0.98' if 'en-core' in path.lower() else '0.82'}cm,keepaspectratio]{{{path}}}}}"
                for path in ci_paths
            ) + r"}"
            header_logo = r"\hbox{" + r"\hspace{0.7em}".join(
                rf"\makebox[42pt][c]{{\includegraphics[width={'44' if 'en-core' in path.lower() else '38'}pt,height={'15' if 'en-core' in path.lower() else '13'}pt,keepaspectratio]{{{path}}}}}"
                for path in ci_paths
            ) + r"}"
        else:
            title_logo_images = rf"\includegraphics[{include_options}]{{{ci_paths[0]}}}"
            header_logo = rf"\includegraphics[{header_include_options}]{{{ci_paths[0]}}}"
        title_logo = rf"""
\noindent {title_logo_images}
\vspace{{1em}}
\par\noindent\color{{LovvGold}}\rule{{\textwidth}}{{1.2pt}}\color{{black}}
"""

    return rf"""\documentclass[12pt,a4paper]{{article}}
\usepackage[margin=22mm]{{geometry}}
\usepackage{{fontspec}}
\usepackage{{xeCJK}}
\usepackage{{kotex}}
\usepackage{{graphicx}}
\usepackage[table]{{xcolor}}
\usepackage{{longtable}}
\usepackage{{booktabs}}
\usepackage{{array}}
\usepackage{{ragged2e}}
\usepackage{{enumitem}}
\usepackage{{hyperref}}
\usepackage{{amssymb}}
\usepackage{{fancyhdr}}
\usepackage{{titlesec}}
\usepackage{{setspace}}
\setmainfont[Path=C:/Windows/Fonts/, BoldFont=malgunbd.ttf, ItalicFont=malgunsl.ttf]{{malgun.ttf}}
\setsansfont[Path=C:/Windows/Fonts/, BoldFont=malgunbd.ttf, ItalicFont=malgunsl.ttf]{{malgun.ttf}}
\setmonofont{{Consolas}}
\newCJKfontfamily\jpfont[Path=C:/Windows/Fonts/, BoldFont=malgunbd.ttf, ItalicFont=malgunsl.ttf]{{malgun.ttf}}
\setCJKmainfont[Path=C:/Windows/Fonts/, BoldFont=malgunbd.ttf, ItalicFont=malgunsl.ttf]{{malgun.ttf}}
\setCJKsansfont[Path=C:/Windows/Fonts/, BoldFont=malgunbd.ttf, ItalicFont=malgunsl.ttf]{{malgun.ttf}}
\setCJKmonofont[Path=C:/Windows/Fonts/]{{malgun.ttf}}
\XeTeXlinebreaklocale "ko"
\hyphenpenalty=10000
\exhyphenpenalty=10000
\binoppenalty=10000
\relpenalty=10000
\emergencystretch=2em
\sloppy
\newcommand{{\DocNeedspace}}[1]{{\par\ifdim\dimexpr\pagegoal-\pagetotal\relax<#1\newpage\fi}}
\hypersetup{{colorlinks=true, linkcolor=black, urlcolor=blue}}
\definecolor{{LovvGreen}}{{HTML}}{{1B3B32}}
\definecolor{{LovvGreenDark}}{{HTML}}{{10251F}}
\definecolor{{LovvGold}}{{HTML}}{{D4AF37}}
\definecolor{{LovvPaper}}{{HTML}}{{F7F3EA}}
\renewcommand{{\arraystretch}}{{1.35}}
\setlength{{\tabcolsep}}{{2pt}}
\setlength{{\LTleft}}{{0pt}}
\setlength{{\LTright}}{{0pt}}
\setlist[itemize]{{leftmargin=*, itemsep=2pt, topsep=2pt}}
\setstretch{{1.08}}
\setlength{{\headheight}}{{30pt}}
\setcounter{{tocdepth}}{{2}}
\pagestyle{{fancy}}
\fancyhf{{}}
\lhead{{{header_logo}}}
\rhead{{\scriptsize {escape_latex(header_status)}}}
\cfoot{{\thepage}}
\renewcommand{{\headrulewidth}}{{0.4pt}}
\renewcommand{{\headrule}}{{\hbox to\headwidth{{\color{{LovvGreen}}\leaders\hrule height \headrulewidth\hfill}}}}
\begin{{document}}
\begin{{titlepage}}
\thispagestyle{{empty}}
{title_logo}
\centering
\vspace*{{0.16\textheight}}
{{\Huge\bfseries {escape_latex(title)}\par}}
{scope_block}
\vfill
{team_line}
{{\Large {escape_latex(author)}{mentor_line}\par}}
\vspace{{2em}}
{{\large 2026-05-30\par}}
\end{{titlepage}}
\begingroup
\fontsize{{11.7pt}}{{12.5pt}}\selectfont
\setlength{{\parskip}}{{0pt}}
\tableofcontents
\endgroup
\newpage
{body}
\end{{document}}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--author", default="로브 기획팀")
    parser.add_argument("--mentor")
    parser.add_argument("--team")
    parser.add_argument("--service-label")
    parser.add_argument("--section-pagebreak", action="store_true")
    parser.add_argument("--ci-image")
    parser.add_argument("--ci-variant", choices=["full", "sk-networks"])
    parser.add_argument("--ci-images", nargs="+")
    parser.add_argument("--toc-pagebreak-before", nargs="+")
    parser.add_argument("--body-pagebreak-before", nargs="+")
    parser.add_argument("--skip-preface", action="store_true")
    args = parser.parse_args()

    markdown = args.source.read_text(encoding="utf-8")
    tex = markdown_to_latex(
        markdown,
        args.title,
        args.author,
        args.mentor,
        args.team,
        args.service_label,
        args.section_pagebreak,
        args.ci_image,
        args.ci_variant,
        args.ci_images,
        args.toc_pagebreak_before,
        args.body_pagebreak_before,
        args.skip_preface,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(tex, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
