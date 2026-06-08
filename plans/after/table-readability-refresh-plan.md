---
작성자: llm팀
상태: 진행후
---

# 표 가독성 개선 계획

## 목적

문서 원본의 표 의미와 열 구조는 유지하면서 HTML 공유 문서와 PDF 산출물에서 표를 더 쉽게 읽히도록 개선한다.

## 대상 파일

- 원본 문서: `docs/04_database_design/04_database_design.md`, `docs/05_agent_spec/05_agent_spec.md` 등 현재 표를 포함한 Markdown 문서
- HTML 생성기: `scripts/generate_pages.py`
- HTML 스타일: `assets/css/requirements.css`
- PDF 변환기: `scripts/markdown_to_tex.py`
- 생성물: `index.html`, `pages/*.html`, `pdf/database_design.tex`, `pdf/database_design.pdf`

## 유지할 항목

- Markdown 표의 데이터 의미, 행/열 구조, 용어
- `docs/` 원본 우선 원칙
- `pages/*.html`, `index.html`, `pdf/*.tex`, `pdf/*.pdf`는 생성물로 관리
- 기존 PDF 표 폭 규칙과 `Overfull \hbox` 검증

## 변경할 항목

- HTML 표의 헤더 고정감, 셀 여백, 행 구분, hover, 코드 토큰 줄바꿈 가독성
- 표 성격별 CSS 클래스 판별 보강
- PDF 표의 헤더 강조, 행 간격, 줄바꿈, 짧은 열/긴 설명 열 배분
- Mermaid 이미지 전환 이후 생성 HTML/PDF와의 정합성 검증

## 작업 체크리스트

- [x] 현재 HTML/PDF 표 렌더링 규칙 확인
- [x] HTML 표 공통 스타일 및 특화 테이블 스타일 개선
- [x] PDF 표 변환 규칙 개선
- [x] HTML 생성물 재생성
- [x] 데이터베이스 설계 PDF 재생성
- [x] Mermaid 제거 상태, HTML 구조, PDF 로그, 공백 오류 검증
- [x] 계획 문서를 `plans/after`로 이동하고 완료 상태 반영

## 검증 방법

- `python scripts\generate_pages.py`
- `python scripts\verify_pages_structure.py`
- `python scripts\markdown_to_tex.py docs\04_database_design\04_database_design.md pdf\database_design.tex ...`
- `xelatex -interaction=nonstopmode -halt-on-error database_design.tex` 2회
- `Select-String -Path pdf\database_design.log -Pattern 'Overfull \\hbox'`
- `rg -n -F '```mermaid' docs`
- `rg -n -F 'class="mermaid"' pages index.html`
- `git diff --check`
