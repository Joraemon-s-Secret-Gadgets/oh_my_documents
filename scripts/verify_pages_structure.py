from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS_PAGE = ROOT / "pages" / "01_requirements.html"
INDEX_PAGE = ROOT / "index.html"
UI_UX_PAGE = ROOT / "pages" / "09_ui_ux_guide.html"


def run_generator() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_pages.py")],
        cwd=ROOT,
        check=True,
    )


def read_requirements_page() -> str:
    if not REQUIREMENTS_PAGE.exists():
        raise AssertionError(f"missing generated page: {REQUIREMENTS_PAGE}")
    return REQUIREMENTS_PAGE.read_text(encoding="utf-8")


def read_page(path: Path) -> str:
    if not path.exists():
        raise AssertionError(f"missing generated page: {path}")
    return path.read_text(encoding="utf-8")


def assert_contains(html: str, needle: str, label: str) -> None:
    if needle not in html:
        raise AssertionError(f"missing {label}: {needle}")


def assert_count(html: str, needle: str, expected: int, label: str) -> None:
    actual = html.count(needle)
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected}, got {actual}")


def assert_not_matches(html: str, pattern: str, label: str) -> None:
    match = re.search(pattern, html)
    if match:
        raise AssertionError(f"{label}: found broken fragment {match.group(0)!r}")


def verify_requirements_page(html: str) -> None:
    assert_contains(html, '<div class="card-grid">', "stakeholder card grid")
    assert_count(html, '<div class="mini-card">', 4, "stakeholder cards")

    assert_contains(html, '<div class="api-grid">', "API card grid")
    assert_count(html, '<div class="api-card">', 4, "API cards")
    for api_name in ("Google Maps Platform", "Kakao Maps", "OpenRouteService", "Yahoo Japan"):
        assert_contains(html, f'<div class="api-card-name">{api_name}</div>', f"API card {api_name}")

    for constraint in (
        "일본 데이터 수집 실패:",
        "Yahoo Japan Maps SDK 지원 중단 (일본 트랙 P5 재검토 시 적용):",
        "Yahoo Japan REST API CORS:",
        "Kakao REST API 도메인 제약:",
        "Google Places API 과금:",
    ):
        assert_contains(html, f"<strong>{constraint}</strong>", f"constraint box {constraint}")

    assert_contains(html, '<div class="note-box"><p><strong>역할 구분:', "role distinction note box")
    assert_contains(html, '<a href="#s2">2. 이해관계자</a>', "stakeholder internal link")

    forbidden_patterns = {
        "API summary rendered as plain paragraph": r'<p class="doc-p">Google Maps Platform</p>',
        "role distinction title rendered as plain paragraph": r'<p class="doc-p"><strong>역할 구분:</strong></p>',
        "role ID rendered as separate paragraph": r'<p class="doc-p"><code>R-(USER|LOCAL-OPERATOR|ADMIN)</code></p>',
        "standalone comma paragraph": r'<p class="doc-p">,</p>',
        "constraint title rendered as plain paragraph": r'<p class="doc-p"><strong>(Yahoo Japan Maps SDK 지원 중단|Kakao REST API 도메인 제약):</strong></p>',
    }
    for label, pattern in forbidden_patterns.items():
        assert_not_matches(html, pattern, label)


def verify_ui_ux_page(index_html: str, page_html: str) -> None:
    assert_contains(index_html, './pages/09_ui_ux_guide.html', "UI/UX guide index link")
    assert_contains(index_html, "로브 (Lovv) — UI/UX 가이드", "UI/UX guide index title")
    assert_contains(page_html, '<h1 id="cover-title" class="s-h1">로브(Lovv) UI/UX 가이드</h1>', "UI/UX guide page title")
    assert_contains(page_html, "저장 일정 상세 (PLAN DETAIL) 화면", "UI/UX guide body section")
    assert_contains(page_html, '<a class="doc-nav-home" href="../index.html">문서 홈</a>', "UI/UX guide home nav")


def main() -> int:
    try:
        run_generator()
        verify_requirements_page(read_requirements_page())
        verify_ui_ux_page(read_page(INDEX_PAGE), read_page(UI_UX_PAGE))
    except (AssertionError, subprocess.CalledProcessError) as exc:
        print(f"page structure verification failed: {exc}", file=sys.stderr)
        return 1

    print("page structure verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

