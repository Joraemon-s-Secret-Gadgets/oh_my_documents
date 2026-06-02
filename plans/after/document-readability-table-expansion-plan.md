---
작성자: Codex
상태: 진행후
---

# 기존 문서 가독성 및 표 확장 개선 계획

## 목적

기존 `docs/` Markdown 원본과 `pages/` HTML 산출물의 문서 가독성을 높인다. 본문은 읽기 쉬운 문단·목록·소제목 구조로 정리하고, 표는 셀 안의 긴 문장이 지나치게 눌리거나 불필요한 좌우 슬라이드바가 생기지 않도록 개선한다. 표가 본문 폭보다 넓어질 필요가 있으면 표 영역을 오른쪽으로 확장해 더 넓은 읽기 폭을 확보한다.

## 적용 원칙

- 내용 기준은 `docs/` 대표 Markdown 문서다. 문장과 표 구조 변경은 먼저 Markdown에 반영한다.
- `pages/*.html`은 `scripts/generate_pages.py`로 재생성한다.
- 문서 의미는 바꾸지 않고, 읽기 순서·표현 밀도·표 구조만 정리한다.
- 표의 열 의미를 바꾸는 경우에는 관련 문서와 HTML 생성 결과를 함께 확인한다.
- 데스크톱에서는 표를 오른쪽으로 확장해 가독성을 우선하고, 모바일에서는 필요한 경우에만 좌우 스크롤을 허용한다.

## 대상 파일

### 원본 문서

- `docs/00_project_plan/00_project_plan.md`
- `docs/01_requirements/01_requirements.md`
- `docs/02_service_flow/02_service_flow.md`
- `docs/03_technical_spec/03_technical_spec.md`
- `docs/04_data_collect_plan/04_data_collect_plan.md`
- `docs/05_api_spec/05_api_spec.md`
- `docs/06_database_design/06_database_design.md`
- `docs/07_agent_spec/07_agent_spec.md`

### 생성 및 스타일

- `scripts/generate_pages.py`
- `assets/css/requirements.css`
- `index.html`
- `pages/*.html`

## 개선 방향

### 1. 문서 본문 가독성 정리

- 긴 문단은 하나의 주장 또는 하나의 정책 단위로 나눈다.
- 표 안에 들어가 있는 긴 설명 중 표가 아니어도 되는 내용은 표 밖 설명 문단이나 목록으로 이동한다.
- 같은 표현이 반복되는 경우, 표 위 설명에서 한 번 정의하고 표에는 짧은 키워드와 결정만 남긴다.
- `PoC`, `Production`, `P1~P5`, `RAG`, `Agent` 같은 반복 용어는 문서 초반 또는 표 위에서 먼저 설명한다.

### 2. 표 구조 개선

- 2열 표는 `항목 / 설명` 또는 `항목 / 결정` 구조로 유지하되, 설명 열을 넓게 둔다.
- 4열 이상 표는 열마다 실제 역할을 점검해 병합 가능한 열을 줄인다.
- 긴 설명 열은 표 안에서 줄바꿈 가능한 문장으로 정리하고, 코드·URL·ID는 `overflow-wrap: anywhere`가 적용되도록 유지한다.
- 변경 이력처럼 긴 문장이 들어가는 표는 날짜·작성자 열을 좁게 고정하고 변경 내용 열을 넓게 둔다.

### 3. 표 오른쪽 확장 레이아웃

현재 `requirements.css`의 `.table-wrap`은 `width: 100%`와 `overflow-x: auto`를 사용한다. 이 구조는 넓은 표에서 본문 폭 안에 좌우 슬라이드바를 만들 수 있다.

개선 방향:

- 데스크톱 폭에서는 `.table-wrap`이 본문 기준 오른쪽으로 확장될 수 있는 `wide-table` 또는 `table-wrap wide` 계열 클래스를 제공한다.
- 왼쪽 본문 정렬은 유지하고, 표의 추가 폭은 오른쪽으로만 확장한다.
- 사이드바와 겹치지 않도록 확장 폭은 `viewport - sidebar - main padding` 범위 안에서 제한한다.
- 표가 확장 가능한 폭 안에 들어오면 좌우 슬라이드바가 생기지 않아야 한다.
- 확장 폭을 넘어서는 매우 큰 표만 예외적으로 `overflow-x: auto`를 유지한다.
- 모바일에서는 본문 폭을 넘어 확장하지 않고 `overflow-x: auto`를 유지한다.

예상 CSS 방향:

```css
@media (min-width: 1024px) {
  .table-wrap.wide {
    width: min(1180px, calc(100vw - var(--sidebar-w) - 72px));
    max-width: none;
  }
}
```

실제 구현 시에는 기존 `main`의 `max-width`, `--doc-max`, `--sidebar-w`, `padding` 값을 확인해 정확한 계산식으로 조정한다.

### 4. 생성 스크립트의 표 클래스 부여

`scripts/generate_pages.py`에서 Markdown 표를 HTML로 변환할 때 열 개수와 셀 길이를 기준으로 표 클래스를 자동 부여한다.

- 2열 이하: 기본 `.table-wrap`
- 3열 이상 또는 긴 셀이 있는 표: `.table-wrap wide`
- 변경 이력 표: `.table-wrap wide`와 변경 이력용 클래스
- API 표처럼 `Method`, `Path`, `Auth`, `설명` 헤더가 있는 표: API용 클래스

## 작업 체크리스트

- [x] 현재 `pages/*.html`에서 좌우 슬라이드바가 생기는 표와 긴 셀을 목록화한다.
- [x] `docs/` 대표 문서 8개에서 긴 문단과 과밀한 표를 식별한다.
- [x] 표 안에 있어야 할 정보와 표 밖 설명으로 옮길 정보를 구분한다.
- [x] `requirements.css`에 오른쪽 확장용 표 래퍼 스타일을 추가한다.
- [x] `scripts/generate_pages.py`에 표 열 개수·헤더 기반 클래스 자동 부여 로직을 추가한다.
- [x] 우선순위가 높은 문서부터 Markdown 원본의 문단과 표를 정리한다.
- [x] `python scripts/generate_pages.py`로 HTML을 재생성한다.
- [x] 데스크톱에서 넓은 표가 오른쪽으로 확장되고 불필요한 좌우 슬라이드바가 사라졌는지 확인한다.
- [x] 모바일에서 표가 화면을 깨지 않고 필요한 경우에만 좌우 스크롤되는지 확인한다.
- [x] `git diff --check`로 공백 오류를 확인한다.

## 우선순위

1. `docs/01_requirements/01_requirements.md`: 표가 가장 많고 문서 길이가 길어 가독성 개선 효과가 크다.
2. `docs/07_agent_spec/07_agent_spec.md`: Agent 파이프라인 표와 긴 셀 설명이 많다.
3. `docs/02_service_flow/02_service_flow.md`: 흐름 표가 많아 열 폭 조정 효과가 크다.
4. `docs/05_api_spec/05_api_spec.md`: API 표는 구조가 반복되므로 전용 클래스 적용에 적합하다.
5. 나머지 문서: 공통 CSS와 생성기 변경 후 표·문단을 필요한 만큼 정리한다.

## 검증 방법

```powershell
python scripts\generate_pages.py
```

```powershell
rg -n "table-wrap|wide|overflow-x|문서 버전|문서 상태" assets\css\requirements.css scripts\generate_pages.py pages
```

```powershell
git diff --check
```

수동 검증 항목:

- [x] 데스크톱에서 넓은 표가 본문 왼쪽 정렬을 유지한 채 오른쪽으로 확장된다.
- [x] 데스크톱에서 일반적인 3~5열 표에 불필요한 좌우 슬라이드바가 생기지 않는다.
- [x] 아주 넓은 표는 레이아웃을 깨지 않고 예외적으로 좌우 스크롤된다.
- [x] 모바일에서 표가 화면 밖으로 무제한 확장되지 않는다.
- [x] 표 셀의 긴 URL, 코드, 기능 ID가 부모 셀을 뚫고 나가지 않는다.
- [x] 문서의 의미, 버전, 상태, 기준 문서 표기가 유지된다.

## 리스크와 대응

| 리스크 | 영향 | 대응 |
| --- | --- | --- |
| 표를 오른쪽으로 확장하면서 화면 밖으로 잘림 | Medium | 확장 폭을 `min()`과 viewport 계산식으로 제한한다. |
| 모바일에서 넓은 표가 본문을 밀어냄 | High | 모바일 미디어쿼리에서는 확장 클래스를 비활성화하고 스크롤을 유지한다. |
| 표 구조 정리 중 문서 의미가 변함 | High | Markdown 원본과 변경 전후 핵심 키워드를 비교하고, 내용 삭제가 아니라 재배치인지 확인한다. |
| 생성기 자동 클래스가 잘못 붙음 | Medium | 열 개수와 헤더명 기준을 단순하게 두고, 문서별 예외는 명시 클래스로 처리한다. |

## 완료 기준

- [x] `docs/` 대표 문서의 긴 문단과 과밀한 표가 읽기 쉬운 구조로 정리되어 있다.
- [x] 생성된 `pages/*.html`에서 표 클래스가 일관되게 적용되어 있다.
- [x] 데스크톱에서 넓은 표는 오른쪽 확장으로 가독성이 개선된다.
- [x] 모바일에서는 표가 레이아웃을 깨지 않는다.
- [x] HTML 재생성, 검색 검증, `git diff --check`가 통과한다.
