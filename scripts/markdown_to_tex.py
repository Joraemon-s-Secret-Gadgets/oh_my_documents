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


def add_soft_breaks_to_escaped_token(text: str) -> str:
    token_breaks = {
        "contenttypeid": r"content\allowbreak{}type\allowbreak{}id",
        "contentid": r"content\allowbreak{}id",
        "sigungucode": r"sigungu\allowbreak{}code",
        "destinationId": r"destina\allowbreak{}tion\allowbreak{}Id",
        "recommendationId": r"recommen\allowbreak{}dation\allowbreak{}Id",
        "feedbackType": r"feedback\allowbreak{}Type",
        "lclsSystm1": r"lcls\allowbreak{}Systm1",
        "lclsSystm2": r"lcls\allowbreak{}Systm2",
        "lclsSystm3": r"lcls\allowbreak{}Systm3",
    }
    for source, target in token_breaks.items():
        text = text.replace(source, target)
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1\\allowbreak{}\2", text)
    return (
        text.replace(r"\_", r"\_\allowbreak{}")
        .replace(r"\#", r"\#\allowbreak{}")
        .replace(r"\{", r"\{\allowbreak{}")
        .replace(r"\}", r"\allowbreak{}\}")
        .replace("-", r"-\allowbreak{}")
        .replace("/", r"/\allowbreak{}")
        .replace(".", r".\allowbreak{}")
        .replace(":", r":\allowbreak{}")
        .replace("|", r"|\allowbreak{}")
        .replace(">", r">\allowbreak{}")
    )


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
    escaped = re.sub(
        r"`([^`]+)`",
        lambda match: r"\texttt{" + add_soft_breaks_to_escaped_token(match.group(1)) + "}",
        escaped,
    )
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\\url{\2})", escaped)
    escaped = re.sub(r"([一-龯ぁ-ゟ゠-ヿー]+)", r"{\\jpfont \1}", escaped)
    escaped = escaped.replace("✓", "O")
    escaped = escaped.replace("✗", "X")
    escaped = escaped.replace("🌐", "글로벌")
    escaped = escaped.replace("🟢", "O")
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
        2: 0.972,
        3: 0.959,
        4: 0.947,
        5: 0.934,
        6: 0.921,
    }
    return target_by_columns.get(column_count, 0.915)


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
    table_font = "footnotesize" if column_count >= 4 else "small"
    table_row_stretch = "1.48" if column_count >= 4 else "1.42"
    table_needspace = min(38, max(8, 6 + len(body) * 2)) if len(body) <= 15 else 8
    col_specs = []
    for index, width in enumerate(widths):
        alignment = r"\centering" if index in centered_columns else r"\RaggedRight"
        col_specs.append(rf">{{{alignment}\arraybackslash}}m{{{width:.3f}\linewidth}}")
    col_spec = "".join(col_specs)

    result = [
        rf"\DocNeedspace{{{table_needspace}\baselineskip}}",
        rf"\begin{{{table_font}}}",
        r"\setlength{\tabcolsep}{3pt}",
        r"\setlength{\extrarowheight}{1pt}",
        rf"\renewcommand{{\arraystretch}}{{{table_row_stretch}}}",
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
    result.extend([r"\bottomrule", r"\end{longtable}", rf"\end{{{table_font}}}", ""])
    return result


def latest_first_table_rows(rows: list[str]) -> list[str]:
    if len(rows) <= 3:
        return rows
    header = rows[:2]
    body = rows[2:]

    def version_key(row: str) -> tuple[int, ...]:
        version = split_table_row(row)[0] if split_table_row(row) else ""
        numbers = re.findall(r"\d+", version)
        return tuple(int(number) for number in numbers)

    return header + sorted(body, key=version_key, reverse=True)


def format_table_cell(cell: str, forced_line_breaks: dict[str, list[str]] | None = None) -> str:
    if forced_line_breaks and cell in forced_line_breaks:
        return r"\newline ".join(escape_latex(part) for part in forced_line_breaks[cell])
    if re.search(r"<br\s*/?>", cell, flags=re.IGNORECASE):
        return r"\newline ".join(escape_latex(part.strip()) for part in re.split(r"<br\s*/?>", cell, flags=re.IGNORECASE))
    if cell == "Production":
        return r"{\footnotesize Production}"
    if re.fullmatch(r"[A-Z]+(?:-[A-Z0-9]+)+-\d+", cell):
        return r"{\footnotesize " + escape_latex(cell).replace("-", r"-\allowbreak{}") + "}"
    if re.fullmatch(r"[A-Za-z]{8,}", cell):
        return r"{\scriptsize " + add_soft_breaks_to_escaped_token(escape_latex(cell)) + "}"
    if re.fullmatch(r"[A-Za-z0-9_./:-]{8,}", cell):
        return r"{\footnotesize " + add_soft_breaks_to_escaped_token(escape_latex(cell)) + "}"
    return escape_latex(cell)


def add_sentence_line_breaks(text: str) -> str:
    return re.sub(r"\.\s+(?=\S)", lambda _: r".\newline ", text)


def format_body_text(text: str, split_sentences: bool = False) -> str:
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
    formatted = escape_latex(text)
    if split_sentences:
        return add_sentence_line_breaks(formatted)
    return formatted


def clean_project_plan_pdf_text(text: str) -> str:
    text = re.sub(
        r"\s*비즈니스 모델 세부 내용은 보조 문서 `supplemental/[^`]+`에서 관리한다\.",
        "",
        text,
    )
    text = re.sub(
        r"상세 리스크는 보조 문서 `supplemental/[^`]+`(?:, `supplemental/[^`]+`)*에서 관리한다\.",
        "상세 리스크는 운영 검토 항목으로 별도 관리한다.",
        text,
    )
    text = text.replace(
        "성과 구간, CPA, 추천 모듈·API, 화이트라벨, 공동브랜드 같은 장기 확장 후보는 보조 문서에서 관리한다.",
        "성과 구간, CPA, 추천 모듈·API, 화이트라벨, 공동브랜드 같은 장기 확장 후보는 별도 검토 항목으로 관리한다.",
    )
    text = re.sub(r"`supplemental/[^`]+`로 분리했던\s*", "세부 문서로 분리했던 ", text)
    text = re.sub(r"`supplemental/[^`]+`", "세부 문서", text)
    text = text.replace("`supplemental/`", "별도 폴더")
    text = text.replace("보조 Markdown", "세부 문서")
    text = text.replace("보조 MD", "세부 문서")
    text = text.replace("하위 MD", "하위 문서")
    text = text.replace("보조 문서", "세부 문서")
    return re.sub(r"\s{2,}", " ", text).strip()


def clean_project_plan_pdf_table_lines(rows: list[str]) -> list[str]:
    cleaned_rows: list[str] = []
    for row in rows:
        if is_table_separator(row):
            cleaned_rows.append(row)
            continue
        cleaned_cells = [clean_project_plan_pdf_text(cell) for cell in split_table_row(row)]
        cleaned_rows.append("| " + " | ".join(cleaned_cells) + " |")
    return cleaned_rows


def image_to_latex(markdown_src: str, alt: str) -> list[str]:
    src = markdown_src.replace("\\", "/")
    if src.startswith("../../assets/"):
        src = "../assets/" + src.removeprefix("../../assets/")
    elif src.startswith("assets/"):
        src = "../" + src
    return [
        r"\DocNeedspace{18\baselineskip}",
        r"\begin{figure}[htbp]",
        r"\centering",
        rf"\includegraphics[width=0.96\linewidth,height=0.72\textheight,keepaspectratio]{{{src}}}",
        rf"\caption*{{{escape_latex(alt)}}}",
        r"\end{figure}",
        "",
    ]


def code_block_to_latex(lines: list[str], language: str | None = None) -> list[str]:
    result = [
        r"\DocNeedspace{7\baselineskip}",
        r"\begin{quote}",
        r"\begin{scriptsize}",
        r"\ttfamily",
        r"\RaggedRight",
        r"\setlength{\parskip}{1pt}",
    ]
    if language:
        result.append(r"\textcolor{LovvGreen}{\textbf{" + escape_latex(language) + r"}}\\[0.2em]")
    for line in lines:
        leading_spaces = len(line) - len(line.lstrip(" "))
        prefix = rf"\hspace*{{{leading_spaces * 0.55:.2f}em}}" if leading_spaces else ""
        content = line.lstrip(" ")
        if not content:
            result.append(r"\mbox{}\\")
            continue
        escaped = add_soft_breaks_to_escaped_token(escape_latex(content))
        escaped = re.sub(r"([가-힣]+)", r"{\\normalfont \1}", escaped)
        result.append(prefix + escaped + r"\\")
    result.extend([r"\end{scriptsize}", r"\end{quote}", ""])
    return result


def acquisition_pipeline_flow_to_latex(lines: list[str]) -> list[str]:
    stages = [line.strip() for line in lines if line.strip() and line.strip() != "↓"]
    descriptions = {
        "자동 수집": "Wikipedia, TourAPI, JNTO/JTA, 기상청/JMA 등 정의된 출처에서 City, Attraction, Festival 원본을 취득한다.",
        "JSON 직렬화": "엔티티 유형, 출처, 수집 시각, 신뢰도 메타데이터를 포함해 JSON 문서로 저장한다.",
        "S3 Raw Bucket 적재": "재사용과 재처리를 위해 원본 JSON을 Raw Prefix에 먼저 적재한다.",
        "Raw 보관 기간 경과": "일정 기간 누적 후 배치 기준이 충족되면 전처리 대상으로 전환한다.",
        "Lambda 배치 전처리": "Raw JSON을 읽어 필드 정규화, 누락 탐지, 출처 검증 메타데이터를 생성한다.",
        "취득 상태 분류": "collected, needs_review, missing, blocked 상태로 분류하고 후속 작업을 결정한다.",
        "공식 사이트 확인 / Web Search Worker": "모호하거나 누락된 값은 공식 사이트 확인 또는 검색 Worker로 보강한다.",
        "수동 검수": "운영시간, 입장료, 사진, 축제 기간처럼 자동 판정이 어려운 값을 검수한다.",
        "정규화 DB 적재": "검증된 데이터를 DynamoDB 정규화 테이블에 적재하고 서비스 조회 대상으로 전환한다.",
    }
    result = [
        r"\DocNeedspace{18\baselineskip}",
        r"\begin{center}",
        r"\setlength{\tabcolsep}{3pt}",
        r"\setlength{\extrarowheight}{1pt}",
        r"\renewcommand{\arraystretch}{1.52}",
        r"\begin{footnotesize}",
        r"\begin{tabular}{@{}>{\centering\arraybackslash}m{0.089\linewidth}>{\RaggedRight\arraybackslash}m{0.244\linewidth}>{\RaggedRight\arraybackslash}m{0.626\linewidth}@{}}",
        r"\toprule",
        r"\textbf{순서} & \textbf{단계} & \textbf{처리 내용} \\",
        r"\midrule",
    ]
    for index, stage in enumerate(stages, start=1):
        result.append(
            rf"\textcolor{{LovvGreen}}{{\textbf{{{index:02d}}}}} & "
            + r"\textbf{"
            + escape_latex(stage)
            + "} & "
            + escape_latex(descriptions.get(stage, "데이터 취득 파이프라인의 후속 처리 단계로 관리한다."))
            + r" \\"
        )
        if index < len(stages):
            result.append(r"\addlinespace[0.12em]")
    result.extend([r"\bottomrule", r"\end{tabular}", r"\end{footnotesize}", r"\end{center}", ""])
    return result


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

    forced_line_breaks = {
        "사용자가 국내 지역과 여행 시기, 여행 일정 길이, 자연어 취향 또는 지도 마커를 입력하면 조건에 맞는 소도시 1곳과 day-by-day 일정이 생성된다.": [
            "사용자가 국내 지역과 여행 시기, 여행 일정 길이,",
            "자연어 취향 또는 지도 마커를 입력하면",
            "조건에 맞는 소도시 1곳과 day-by-day 일정이 생성된다.",
        ],
        "추천 결과에는 추천 이유, 지도 링크, 월별 날씨 경향, 외부 탐색 링크, 출처·검증 상태 중 핵심 정보가 함께 제공된다.": [
            "추천 결과에는 추천 이유, 지도 링크, 월별 날씨 경향,",
            "외부 탐색 링크, 출처·검증 상태 중",
            "핵심 정보가 함께 제공된다.",
        ],
        "유사 취향 공개 일정이 노출되고 사용자가 1탭 복제 후 저장 또는 부분 수정으로 이어지는 흐름을 설계 산출물로 확보한다.": [
            "유사 취향 공개 일정이 노출되고",
            "사용자가 1탭 복제 후 저장 또는 부분 수정으로",
            "이어지는 흐름을 설계 산출물로 확보한다.",
        ],
        "PoC에서는 P1 한국 강원·경북 데이터 기반 추천을 구현하고, P2 한국 전국 확장과 KICK은 설계 중심으로 정리하며, 일본 데이터 기반 추천은 P5 재검토 범위로 관리한다.": [
            "PoC에서는 P1 한국 강원·경북 데이터 기반 추천을 구현하고,",
            "P2 한국 전국 확장과 KICK은 설계 중심으로 정리하며,",
            "일본 데이터 기반 추천은 P5 재검토 범위로 관리한다.",
        ],
        "신규 지역, 축제, 촬영지, 체험 정보, 외부 데이터 소스를 추가할 수 있는 공통 데이터 모델과 운영 구조를 유지한다.": [
            "신규 지역, 축제, 촬영지, 체험 정보,",
            "외부 데이터 소스를 추가할 수 있는",
            "공통 데이터 모델과 운영 구조를 유지한다.",
        ],
    }
    body = [split_table_row(row) for row in rows[2:]]
    result = [
        r"\DocNeedspace{8\baselineskip}",
        r"\begin{center}",
        r"\setlength{\tabcolsep}{3pt}",
        r"\setlength{\extrarowheight}{1pt}",
        r"\renewcommand{\arraystretch}{1.58}",
        r"\begin{tabular}{@{}>{\RaggedRight\arraybackslash}m{0.243\linewidth}>{\RaggedRight\arraybackslash}m{0.729\linewidth}@{}}",
        r"\toprule",
        r"\multicolumn{1}{c}{\textbf{구분}} & \multicolumn{1}{c}{\textbf{성공 기준}} \\",
        r"\midrule",
    ]
    for row in body:
        if len(row) < 2:
            continue
        label, criterion = row[0], row[1]
        result.append(
            r"\textbf{"
            + format_table_cell(label, forced_line_breaks)
            + r"} & "
            + format_table_cell(criterion, forced_line_breaks)
            + r" \\[0.35em]"
        )
    result.extend([r"\bottomrule", r"\end{tabular}", r"\end{center}", ""])
    return result


def database_design_table_to_latex(current_heading: str, rows: list[str]) -> list[str] | None:
    database_table_rules: dict[str, tuple[list[float], set[int]]] = {
        "1.2 설계 기준": ([0.14, 0.24, 0.60], {0}),
        "1.3 저장소 책임": ([0.16, 0.34, 0.48], {0}),
        "2.1 핵심 도메인": ([0.15, 0.48, 0.35], {0}),
        "2.2 사용자 데이터 개념 모델": ([0.13, 0.13, 0.39, 0.33], {0, 1}),
        "3.1 MySQL 논리 ERD": ([0.12, 0.25, 0.61], {0, 1}),
        "NoSQL 사용자 이벤트 저장 원칙": ([0.15, 0.79], {0}),
        "3.3 DynamoDB NoSQL 사용자 설계": ([0.15, 0.21, 0.19, 0.31, 0.08], {0, 4}),
        "3.4 S3 vector index 논리 모델": ([0.12, 0.40, 0.42], {0}),
        "3.5 AWS Neptune 그래프 논리 모델": ([0.11, 0.27, 0.36, 0.18], {0, 1}),
        "3.6 API 식별자 매핑": ([0.13, 0.29, 0.32, 0.16], {0}),
        "4.1 MySQL 물리 설계 기준": ([0.16, 0.78], {0}),
        "4.2 주요 인덱스": ([0.22, 0.72], {0}),
        "4.3 DynamoDB 물리 설계 기준": ([0.16, 0.78], {0}),
        "4.4 DynamoDB GSI 후보": ([0.26, 0.27, 0.14, 0.23], {0, 1, 2}),
        "4.5 S3 vector index 물리 설계 기준": ([0.20, 0.74], {0}),
        "4.6 AWS Neptune 물리 설계 기준": ([0.16, 0.78], {0}),
        "5. 보존 정책 및 권한": ([0.18, 0.51, 0.25], {0, 2}),
        "5.1 보존 기간 및 TTL (권고·잠정)": ([0.27, 0.27, 0.40], {0, 1}),
        "6. PoC 적용 범위와 Production 전환": ([0.18, 0.76], {0}),
        "9. 변경 이력": ([0.11, 0.18, 0.14, 0.57], {0, 1, 2}),
    }
    if current_heading in database_table_rules:
        widths, centered = database_table_rules[current_heading]
        return table_to_latex(rows, widths, centered)
    if re.fullmatch(r"3\.2\.\d+ `[^`]+`", current_heading):
        return table_to_latex(rows, [0.22, 0.18, 0.14, 0.44], {1, 2})
    return None


def data_collect_table_to_latex(current_heading: str, rows: list[str]) -> list[str] | None:
    data_collect_table_rules: dict[str, tuple[list[float], set[int]]] = {
        "1.2 취득 데이터 구조": ([0.24, 0.70], {0}),
        "2.1 데이터셋 관계": ([0.26, 0.68], {0}),
        "2.3 City 수집 항목": ([0.18, 0.35, 0.35, 0.08], {0, 3}),
        "2.4 Attraction 수집 항목": ([0.18, 0.35, 0.35, 0.08], {0, 3}),
        "2.5 Festival 수집 항목": ([0.18, 0.35, 0.35, 0.08], {0, 3}),
        "2.6.1 한국 데이터 출처": ([0.28, 0.32, 0.34], {0}),
        "2.6.2 일본 데이터 출처": ([0.28, 0.32, 0.34], {0}),
        "3.3 원본 및 정규화 저장": ([0.24, 0.70], {0}),
        "4. 데이터 품질 정합성 관리 방법": ([0.24, 0.70], {0}),
        "4.1.1 정규화 기준 (한·일 공통)": ([0.24, 0.70], {0}),
        "4.1.2 정합성 지표 및 판정": ([0.38, 0.20, 0.36], {1}),
        "5. 법적 요소 검토": ([0.20, 0.74], {0}),
        "7. 변경 이력": ([0.11, 0.18, 0.14, 0.57], {0, 1, 2}),
    }
    if current_heading in data_collect_table_rules:
        widths, centered = data_collect_table_rules[current_heading]
        forced_breaks = {
            "한국관광공사 관광 빅데이터 API(DataLabService)": [
                "한국관광공사 관광 빅데이터 API",
                "(DataLabService)",
            ],
            "Wikipedia API / 크롤링 / Wikidata": [
                "Wikipedia API / 크롤링",
                "/ Wikidata",
            ],
            "`MAE_T ≤ 1.5℃` 그리고 `MAPE_P ≤ 0.20`": [
                "`MAE_T ≤ 1.5℃`",
                "`MAPE_P ≤ 0.20`",
            ],
            "위 미달이나 `ConsistencyScore ≥ 60`": [
                "위 미달",
                "`ConsistencyScore ≥ 60`",
            ],
            "`ConsistencyScore < 60` 또는 표 취득 실패": [
                "`ConsistencyScore < 60`",
                "또는 표 취득 실패",
            ],
        }
        return table_to_latex(rows, widths, centered, forced_breaks)
    return None


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
    code_language: str | None = None
    code_lines: list[str] = []
    current_heading = ""
    last_block_was_level1_heading = False
    preface_skipped = not skip_preface
    is_project_plan_pdf = title == "프로젝트 기획서"

    def heading_has_level2_child(start_index: int) -> bool:
        for next_line in lines[start_index + 1 :]:
            next_heading = re.match(r"^(#{1,6})\s+(.+)$", next_line.strip())
            if not next_heading:
                continue
            next_level = len(next_heading.group(1))
            if next_level <= 1:
                return False
            if next_level == 2:
                return True
        return False

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
                in_code = True
                code_language = line.strip().removeprefix("```").strip() or None
                code_lines = []
            else:
                if current_heading == "3.1 처리 흐름":
                    output.extend(acquisition_pipeline_flow_to_latex(code_lines))
                else:
                    output.extend(code_block_to_latex(code_lines, code_language))
                last_block_was_level1_heading = False
                in_code = False
                code_language = None
                code_lines = []
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        if (
            is_project_plan_pdf
            and current_heading == "13. 후속 문서 및 분리 문서"
            and line.strip().startswith("대표 기획서와 같은 기준으로 관리하는 보조 Markdown은")
        ):
            in_list = close_list(output, in_list)
            while i < len(lines):
                next_line = lines[i].rstrip()
                if re.match(r"^#\s+\d+\.", next_line):
                    break
                i += 1
            output.append("")
            last_block_was_level1_heading = False
            continue

        if line.strip().startswith("|") and i + 1 < len(lines) and is_table_separator(lines[i + 1]):
            in_list = close_list(output, in_list)
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].rstrip())
                i += 1
            if is_project_plan_pdf:
                if current_heading == "13. 후속 문서 및 분리 문서" and split_table_row(table_lines[0]) == [
                    "보조 Markdown",
                    "분리 내용",
                ]:
                    last_block_was_level1_heading = False
                    continue
                table_lines = clean_project_plan_pdf_table_lines(table_lines)
            if current_heading in {"2.1 사용자 문제", "2.2 시장·운영 문제"}:
                output.extend(issue_table_to_paragraphs(table_lines))
            elif current_heading == "3.2 성공 기준":
                output.extend(success_criteria_table_to_latex(table_lines))
            elif (database_table := database_design_table_to_latex(current_heading, table_lines)) is not None:
                output.extend(database_table)
            elif (data_collect_table := data_collect_table_to_latex(current_heading, table_lines)) is not None:
                output.extend(data_collect_table)
            elif current_heading == "3.3 원본 및 정규화 저장":
                output.extend(
                    table_to_latex(
                        table_lines,
                        forced_line_breaks={
                            "Raw 데이터": ["Raw", "데이터"],
                            "정규화 데이터": ["정규화", "데이터"],
                            "검수 메타데이터": ["검수", "메타데이터"],
                            "출처 메타데이터": ["출처", "메타데이터"],
                        },
                    )
                )
            elif current_heading == "4. 데이터 품질 정합성 관리 방법":
                output.extend(
                    table_to_latex(
                        table_lines,
                        forced_line_breaks={
                            "City 매핑": ["City", "매핑"],
                            "행정구역 정합성": ["행정구역", "정합성"],
                            "출처 기록": ["출처", "기록"],
                            "전체 필드 상태": ["전체 필드", "상태"],
                            "기후 정합성": ["기후", "정합성"],
                            "링크 유효성": ["링크", "유효성"],
                            "다국어 매핑": ["다국어", "매핑"],
                        },
                    )
                )
            elif current_heading == "4.2 사용자 흐름":
                output.extend(
                    table_to_latex(
                        table_lines,
                        [0.10, 0.24, 0.40, 0.24],
                        {0},
                        {"자연어 취향 또는 지도 마커 선택": ["자연어 취향 또는", "지도 마커 선택"]},
                    )
                )
            elif current_heading == "1.4 시장 포지셔닝과 차별점":
                output.extend(
                    table_to_latex(
                        table_lines,
                        [0.16, 0.36, 0.44],
                        {0},
                        {
                            "사용자가 이미 선택한 도시 내부 일정 최적화": ["사용자가 이미 선택한 도시 내부", "일정 최적화"],
                            "국내 지역·시기 조건에서 대체 소도시 1곳 발견": ["국내 지역·시기 조건에서", "대체 소도시 1곳 발견"],
                            "RAG 기반 후보 검색, 추천 이유, 출처·검증 상태 제공": [
                                "RAG 기반 후보 검색",
                                "추천 이유",
                                "출처·검증 상태 제공",
                            ],
                            "로그인·온보딩 후 국내 지역·시기·일정 길이 선질문": [
                                "로그인·온보딩 후",
                                "국내 지역·시기·일정 길이",
                                "선질문",
                            ],
                            "공공·지자체·외부 API·제휴 링크를 함께 관리": [
                                "공공·지자체·외부 API",
                                "제휴 링크를 함께 관리",
                            ],
                            "블랙박스형 일정 생성에 가까움": ["블랙박스형 일정 생성에", "가까움"],
                            "Explainable RAG 기반 소도시 추천 엔진": ["Explainable RAG 기반", "소도시 추천 엔진"],
                        },
                    )
                )
            elif current_heading == "5. 주요 사용자 및 이해관계자":
                output.extend(table_to_latex(table_lines, [0.23, 0.20, 0.55]))
            elif current_heading in {"6.1 우선순위", "6.1 PoC 범위"}:
                output.extend(table_to_latex(table_lines, [0.12, 0.50, 0.10, 0.14, 0.12], {0, 2, 3, 4}))
            elif current_heading == "7.2 추천 기능":
                output.extend(table_to_latex(table_lines, [0.26, 0.72], {0}))
            elif current_heading == "7.4.3 B2G: 비과금 공익 협력 트랙":
                output.extend(table_to_latex(table_lines, [0.16, 0.52, 0.30], {0, 2}))
            elif current_heading == "8.1 필요 데이터":
                output.extend(table_to_latex(table_lines, [0.16, 0.36, 0.46], {0}))
            elif current_heading == "8.2 외부 연동":
                output.extend(table_to_latex(table_lines, [0.18, 0.38, 0.42], {0}))
            elif current_heading == "10. 추진 일정":
                output.extend(table_to_latex(table_lines, [0.20, 0.28, 0.50], {0, 1}))
            elif current_heading == "12. 리스크 및 대응":
                output.extend(table_to_latex(table_lines, [0.24, 0.34, 0.40], {0}))
            elif current_heading in {"13. 후속 문서", "13. 후속 문서 및 분리 문서"}:
                output.extend(table_to_latex(table_lines, [0.30, 0.68], {0}))
            elif current_heading == "14. 변경 이력":
                output.extend(table_to_latex(latest_first_table_rows(table_lines), [0.11, 0.18, 0.16, 0.53], {0, 1, 2}))
            else:
                output.extend(table_to_latex(table_lines))
            last_block_was_level1_heading = False
            continue

        image_match = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", line.strip())
        if image_match:
            in_list = close_list(output, in_list)
            output.extend(image_to_latex(image_match.group(2).strip(), image_match.group(1).strip()))
            last_block_was_level1_heading = False
            i += 1
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            in_list = close_list(output, in_list)
            level = len(heading.group(1))
            raw_text = heading.group(2).strip()
            current_heading = raw_text
            if (
                section_pagebreak
                and ((level == 2 and re.match(r"^4\.\d+\s", raw_text)) or raw_text == "우선순위 기능 요구사항")
                and output
                and not last_block_was_level1_heading
            ):
                output.append(r"\newpage")
            if section_pagebreak and level == 1 and not output and not re.match(r"^\d+\.", raw_text):
                i += 1
                continue
            if section_pagebreak and level == 1 and re.match(r"^\d+\.", raw_text) and output:
                output.append(r"\newpage")
                output.append("")
            if section_pagebreak and raw_text == "2.2 시장·운영 문제":
                output.append(r"\newpage")
                output.append("")
            if section_pagebreak and raw_text == "7.2 추천 기능":
                output.append(r"\newpage")
                output.append("")
            if section_pagebreak and raw_text == "7.4.2 B2B: 성과형 제휴 트랙":
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
                if not heading_has_level2_child(i):
                    output.append(r"\addtocontents{toc}{\protect\TocNoChildTight}")
                last_block_was_level1_heading = True
            elif level == 2:
                subsection_needspace = 8 if last_block_was_level1_heading else 24
                output.append(rf"\DocNeedspace{{{subsection_needspace}\baselineskip}}")
                output.append(r"\subsection*{" + text + "}")
                if toc_pagebreak_before and raw_text in toc_pagebreak_before:
                    output.append(r"\addtocontents{toc}{\protect\clearpage}")
                output.append(r"\addcontentsline{toc}{subsection}{" + text + "}")
                last_block_was_level1_heading = False
            elif level == 3:
                output.append(r"\DocNeedspace{5\baselineskip}")
                output.append(r"\subsubsection*{" + text + "}")
                last_block_was_level1_heading = False
            else:
                output.append(r"\DocNeedspace{4\baselineskip}")
                output.append(r"\paragraph{" + text + "}")
                last_block_was_level1_heading = False
            output.append("")
            i += 1
            continue

        if line.startswith(">"):
            in_list = close_list(output, in_list)
            quote_lines: list[str] = []
            while i < len(lines) and lines[i].startswith(">"):
                quote_line = lines[i].lstrip("> ").rstrip()
                if is_project_plan_pdf:
                    quote_line = clean_project_plan_pdf_text(quote_line)
                if quote_line:
                    quote_lines.append(quote_line)
                i += 1
            if quote_lines:
                output.append(r"\begin{quote}")
                for quote_line in quote_lines:
                    output.append(escape_latex(quote_line) + r"\\")
                output.append(r"\end{quote}")
                output.append("")
            last_block_was_level1_heading = False
            continue

        bullet = re.match(r"^\s*[-*]\s+(.+)$", line)
        ordered = re.match(r"^\s*\d+\.\s+(.+)$", line)
        if bullet or ordered:
            item_text = (bullet or ordered).group(1).strip()
            if is_project_plan_pdf:
                item_text = clean_project_plan_pdf_text(item_text)
            if not item_text:
                i += 1
                continue
            if not in_list:
                output.append(r"\begin{itemize}")
                in_list = True
            output.append(r"\item " + format_body_text(item_text))
            last_block_was_level1_heading = False
            i += 1
            continue

        if not line.strip():
            in_list = close_list(output, in_list)
            output.append("")
            i += 1
            continue

        in_list = close_list(output, in_list)
        paragraph_text = line.strip()
        if is_project_plan_pdf:
            paragraph_text = clean_project_plan_pdf_text(paragraph_text)
        if not paragraph_text:
            i += 1
            continue
        output.append(r"\DocNeedspace{3\baselineskip}")
        output.append(format_body_text(paragraph_text, split_sentences=True))
        output.append("")
        last_block_was_level1_heading = False
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
\newfontfamily\jpfont[Path=C:/Windows/Fonts/]{{NotoSansJP-VF.ttf}}
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
\definecolor{{DarkCharcoal}}{{HTML}}{{222222}}
\definecolor{{MainOrange}}{{HTML}}{{F26518}}
\definecolor{{MutedBrown}}{{HTML}}{{D44A14}}
\definecolor{{SoftBeige}}{{HTML}}{{FFF3E7}}
\definecolor{{CardPeach}}{{HTML}}{{FCE7DB}}
\definecolor{{SubTextGray}}{{HTML}}{{666666}}
\color{{DarkCharcoal}}
\colorlet{{LovvGreen}}{{MutedBrown}}
\colorlet{{LovvGreenDark}}{{DarkCharcoal}}
\colorlet{{LovvGold}}{{MainOrange}}
\colorlet{{LovvPaper}}{{SoftBeige}}
\renewcommand{{\arraystretch}}{{1.35}}
\setlength{{\tabcolsep}}{{2pt}}
\setlength{{\LTpre}}{{6pt}}
\setlength{{\LTpost}}{{10pt}}
\setlength{{\LTleft}}{{\fill}}
\setlength{{\LTright}}{{\fill}}
\setlist[itemize]{{leftmargin=*, itemsep=2pt, topsep=2pt}}
\setstretch{{1.08}}
\setlength{{\headheight}}{{30pt}}
\setcounter{{tocdepth}}{{2}}
\newcommand{{\TocNoChildTight}}{{\vspace{{-0.28em}}}}
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
