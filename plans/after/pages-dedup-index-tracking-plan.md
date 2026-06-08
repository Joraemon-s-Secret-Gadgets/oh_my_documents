---
작성자: 조동휘
상태: 진행후
---

# Pages 중복 정리 및 Index 반영 계획

## 목적

현재 작업 트리의 미추적 문서 폴더와 발표자료 초안을 git tracking 대상으로 올리고, `pages/`에 남아 있는 구형 번호 체계 중복 HTML을 정리한다. 정리 후 `index.html`은 대표 문서만 노출하고, 생성 스크립트와 검증 스크립트가 같은 문서 목록을 기준으로 동작하도록 맞춘다.

## 현재 상태 요약

- 신규 미추적 대상:
  - `docs/09_ui_ux_guide/AGENT.md`
  - `docs/10_test_plan/AGENT.md`
  - `docs/11_deployment_ops/AGENT.md`
  - `docs/99_pptx/01_midterm_presentation/01_midterm_presentation.md`
- 현재 대표 HTML:
  - `pages/00_project_plan.html`
  - `pages/01_requirements.html`
  - `pages/02_service_flow.html`
  - `pages/03_data_collect_plan.html`
  - `pages/08_data_preprocessing.html`
  - `pages/04_database_design.html`
  - `pages/05_agent_spec.html`
  - `pages/06_technical_spec.html`
  - `pages/07_api_spec.html`
- 현재 중복/구형 redirect HTML:
  - `pages/03_technical_spec.html`
  - `pages/04_api_spec.html`
  - `pages/04_data_collect_plan.html`
  - `pages/05_database_design.html`
  - `pages/05_technical_spec.html`
  - `pages/05_api_spec.html`
  - `pages/06_agent_spec.html`
  - `pages/06_api_spec.html`
  - `pages/06_database_design.html`
  - `pages/07_agent_spec.html`

## 정리 원칙

- `docs/` Markdown 원본을 기준으로 한다.
- 대표 HTML은 `scripts/generate_pages.py`의 `DOCUMENTS` 목록에서만 생성한다.
- 구형 번호 HTML은 더 이상 index에서 노출하지 않는다.
- 중복 페이지를 제거하기로 하면 `scripts/generate_pages.py`의 `REDIRECTS`도 함께 제거한다.
- 구형 redirect HTML은 tracked 중복 파일에서 제거한다.
- `09_ui_ux_guide`, `10_test_plan`, `11_deployment_ops`는 현재 대표 Markdown이 없으므로, AGENT.md만 tracking하고 index 노출은 보류한다. 대표 Markdown이 생긴 뒤 `DOCUMENTS`와 index에 추가한다.

## 작업 체크리스트

- [x] `git status --short`로 변경 파일과 미추적 파일을 재확인한다.
- [x] `docs/09_ui_ux_guide`, `docs/10_test_plan`, `docs/11_deployment_ops`에 대표 Markdown이 없는지 확인한다.
- [x] 미추적 문서 운영 파일과 발표자료 대표 문서를 git tracking 대상으로 스테이징한다.
- [x] `scripts/generate_pages.py`의 `REDIRECTS` 항목을 제거한다.
- [x] `pages/`의 구형 redirect HTML 10개를 제거한다.
- [x] `index.html`이 대표 HTML 9개만 참조하는지 확인한다.
- [x] `scripts/verify_pages_structure.py`가 삭제된 redirect HTML을 요구하지 않는지 확인하고 필요 시 수정한다.
- [x] `python scripts\generate_pages.py`를 실행해 대표 HTML과 `index.html`을 재생성한다.
- [x] `python scripts\verify_pages_structure.py`를 실행해 구조 검증을 통과시킨다.
- [x] `rg -n "03_technical_spec|04_api_spec|04_data_collect_plan|05_database_design|05_technical_spec|05_api_spec|06_agent_spec|06_api_spec|06_database_design|07_agent_spec" index.html pages scripts`로 구형 링크가 남지 않았는지 확인한다.
- [x] `git diff --cached --name-status`로 staging 범위가 tracking 및 중복 페이지 정리에 맞는지 확인한다.
- [ ] Conventional Commit을 만든다면 `docs(site): prune duplicate generated pages` 형태로 커밋한다.

## 예상 변경 파일

- `scripts/generate_pages.py`
- `scripts/verify_pages_structure.py`
- `index.html`
- `pages/*.html`
- `docs/09_ui_ux_guide/AGENT.md`
- `docs/10_test_plan/AGENT.md`
- `docs/11_deployment_ops/AGENT.md`
- `docs/99_pptx/01_midterm_presentation/01_midterm_presentation.md`

## 검증 방법

- `python scripts\generate_pages.py`
- `python scripts\verify_pages_structure.py`
- `git status --short`
- `git diff --cached --name-status`
- 구형 링크 잔존 검색:
  - `rg -n "03_technical_spec|04_api_spec|04_data_collect_plan|05_database_design|05_technical_spec|05_api_spec|06_agent_spec|06_api_spec|06_database_design|07_agent_spec" index.html pages scripts`

## 리스크 및 대응

| 리스크 | 영향 | 대응 |
| --- | --- | --- |
| 기존 외부 공유 링크가 구형 HTML을 직접 참조 | 삭제 시 404 발생 | 이번 정리에서는 중복 제거를 우선하고, 필요 시 별도 legacy redirect 정책을 후속 작업으로 만든다 |
| 신규 09~11 폴더가 AGENT.md만 있어 index에 표시할 문서가 없음 | 빈 문서 카드 노출 위험 | 대표 Markdown 생성 전까지 index 노출 보류 |
| 전체 작업 트리에 unrelated 변경이 섞임 | 커밋 범위 오염 | staging 전후 `git diff --cached --name-status`로 범위 확인 |

## 결정 사항

- 구형 redirect HTML 10개는 중복 페이지로 보고 제거한다.
