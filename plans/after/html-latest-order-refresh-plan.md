---
작성자: llm팀
상태: 진행후
---

# HTML 최신화 및 문서 순서 재정렬 계획

## 목적

생성된 HTML 문서를 현재 `docs/` 원본 기준으로 다시 최신화하고, 문서 허브와 이전/다음 링크의 순서를 실제 작업 흐름에 맞게 재정렬한다.

이번 계획에서는 `docs/` Markdown을 원본으로 보고, `pages/*.html`과 `index.html`은 재생성 또는 정리 대상 산출물로 본다. 문서 번호와 HTML 파일명은 필요하면 바꿀 수 있으나, 변경 시 리다이렉트 또는 호환 링크를 함께 처리한다.

## 현재 확인된 상태

| 구분 | 확인 내용 |
| --- | --- |
| 생성 기준 | `scripts/generate_pages.py`의 `DOCUMENTS` 배열이 현재 공개 HTML 순서를 결정한다. |
| 현재 공개 대상 | `00_project_plan`부터 `07_api_spec`까지 8개 대표 문서가 생성 대상이다. |
| 과거 HTML 잔존 | `pages/03_technical_spec.html`, `pages/04_data_collect_plan.html`, `pages/04_api_spec.html`, `pages/05_api_spec.html`, `pages/05_database_design.html`, `pages/06_database_design.html`, `pages/06_agent_spec.html` 같은 이전 번호 체계 파일은 리다이렉트로 유지한다. |
| 리다이렉트 기준 | `scripts/generate_pages.py`에는 이전 파일을 새 파일로 연결하는 `REDIRECTS`가 있다. |
| 현재 작업트리 주의 | `docs/05_agent_spec/agent_spec_revision_plan.md`에 별도 수정이 있으므로, HTML 최신화 작업 전 반영 여부를 결정해야 한다. |

## 목표 문서 순서

프로젝트 공개 흐름은 `프로젝트 기획서`를 가장 먼저 보여주는 순서로 둔다.
현재 작업 진행 축은 `00 프로젝트 기획서 → 01 요구사항 → 02 서비스 흐름 → 03 데이터 수집 → 04 데이터베이스 설계 → 05 Agent 명세서 → 06 기술 명세서 → 07 API 명세서` 순서로 진행되도록 문서 번호와 HTML 번호를 재정렬했다.

| 작업 순서 | 원본 문서 | 생성 HTML | 역할 |
| --- | --- | --- | --- |
| 1 | `docs/00_project_plan/00_project_plan.md` | `pages/00_project_plan.html` | 프로젝트 소개·목표·범위의 첫 진입 문서 |
| 2 | `docs/01_requirements/01_requirements.md` | `pages/01_requirements.html` | 요구사항 기준 확정 |
| 3 | `docs/02_service_flow/02_service_flow.md` | `pages/02_service_flow.html` | 사용자·서비스 흐름 정합화 |
| 4 | `docs/03_data_collect_plan/03_data_collect_plan.md` | `pages/03_data_collect_plan.html` | 데이터 수집·전처리 기준 정합화 |
| 5 | `docs/04_database_design/04_database_design.md` | `pages/04_database_design.html` | 저장소·데이터 모델 정합화 |
| 6 | `docs/05_agent_spec/05_agent_spec.md` | `pages/05_agent_spec.html` | Agent 파이프라인 후속 정합화 |
| 7 | `docs/06_technical_spec/06_technical_spec.md` | `pages/06_technical_spec.html` | 기술 경계와 인프라 후속 정합화 |
| 8 | `docs/07_api_spec/07_api_spec.md` | `pages/07_api_spec.html` | API 계약 후속 정합화 |
| 9 | `index.html` | `index.html` | 공개 허브 순서와 상태 표시 최종 반영 |

`docs/99_pptx`는 발표 준비 문서이므로 기본 공개 HTML 순서에는 넣지 않는다. 사용자가 발표 문서도 GitHub Pages에서 공개하길 원하면 별도 Phase로 추가한다.

## 변경 원칙

- 대표 Markdown 문서를 먼저 확인한 뒤 HTML을 생성한다.
- `00_project_plan.md`는 공개 순서상 첫 문서로 둔다.
- 단, `00_project_plan.md`의 내용이 상세 문서와 충돌하면 상세 문서를 확인한 뒤 기획서 요약을 조정한다.
- `index.html` 카드 순서와 `pages/*.html` 이전/다음 링크는 같은 순서를 따른다.
- 기존 URL 호환이 필요하면 과거 HTML 파일은 삭제하지 않고 리다이렉트 파일로 유지한다.
- 기존 URL 호환이 필요 없으면 과거 번호 HTML을 제거하고 `README.md`에 새 순서를 명시한다.
- 보조 Markdown은 대표 문서에 반영할 기준으로만 보고, 별도 HTML 생성 대상에 넣을지는 명시적으로 결정한다.

## 작업 체크리스트

- [x] 현재 `docs/`, `pages/`, `index.html`, `scripts/generate_pages.py`의 문서 목록을 재확인한다.
- [x] `pages/04_api_spec.html`, `pages/05_database_design.html`, `pages/06_agent_spec.html`을 리다이렉트로 유지할지 삭제할지 결정한다.
- [x] `docs/05_agent_spec/agent_spec_revision_plan.md`의 미커밋 변경을 대표 문서에 반영할지, 별도 초안으로 둘지 결정한다.
- [x] `scripts/generate_pages.py`의 `DOCUMENTS` 배열을 `00 → 01 → 02 → 03 → 04 → 05 → 06 → 07` 순서에 맞게 재정렬한다.
- [x] 필요 시 `Document.target` 파일명을 새 순서에 맞게 변경하고 `REDIRECTS`를 갱신한다.
- [x] `README.md`와 루트 `AGENT.md`의 문서 흐름 설명이 새 순서와 충돌하지 않는지 확인한다.
- [x] `python scripts\generate_pages.py`로 `pages/*.html`과 `index.html`을 재생성한다.
- [x] 생성된 `index.html` 카드 순서가 목표 문서 순서와 일치하는지 확인한다.
- [x] 각 `pages/*.html`의 이전/다음 링크가 목표 문서 순서와 일치하는지 확인한다.
- [x] 구버전 리다이렉트 HTML을 유지하는 경우, 각 리다이렉트가 새 HTML로 이동하는지 확인한다.
- [x] 더 이상 생성 대상이 아닌 HTML을 삭제하는 경우, 깨진 링크가 없는지 확인한다.
- [x] `python scripts\verify_pages_structure.py`를 실행한다.
- [x] `git diff --check`를 실행한다.
- [x] 변경된 파일 목록을 검토하고 HTML 최신화 커밋 범위를 확정한다.

## 검증 방법

| 검증 | 명령 또는 확인 기준 |
| --- | --- |
| HTML 재생성 | `python scripts\generate_pages.py` |
| 페이지 구조 검증 | `python scripts\verify_pages_structure.py` |
| 공백·마크업 diff 검사 | `git diff --check` |
| 공개 순서 확인 | `index.html`의 카드 순서와 `scripts/generate_pages.py`의 `DOCUMENTS` 순서 비교 |
| 이전/다음 링크 확인 | 각 `pages/*.html`의 pager 링크가 목표 순서와 일치하는지 확인 |
| 구버전 URL 확인 | `03_technical_spec.html`, `04_data_collect_plan.html`, `04_api_spec.html`, `05_api_spec.html`, `05_database_design.html`, `06_database_design.html`, `06_agent_spec.html` 리다이렉트 정책 확인 |

## 리스크 및 대응

| 리스크 | 영향 | 대응 |
| --- | --- | --- |
| 문서 번호 변경으로 기존 링크가 깨짐 | 공유된 GitHub Pages 링크가 404가 될 수 있음 | `REDIRECTS`를 유지하거나 리다이렉트 HTML을 새로 생성한다. |
| `00_project_plan`이 상세 문서와 어긋남 | 첫 진입 문서가 실제 설계 상태를 잘못 안내 | 공개 순서는 00을 먼저 두되, 내용 수정 시 상세 문서를 읽기 전용 기준으로 확인한다. |
| 보조 Markdown까지 무분별하게 공개됨 | 초안과 정본이 섞여 사용자 혼란 발생 | 대표 문서만 기본 공개하고 보조 문서 공개는 별도 결정으로 둔다. |
| 미커밋 Agent 초안 변경이 HTML에 누락됨 | Agent 관련 최신 결정이 공개 HTML과 다름 | 작업 초반에 `agent_spec_revision_plan.md` 변경 반영 여부를 결정한다. |

## 완료 기준

- [x] `index.html`의 문서 카드가 목표 작업 순서로 정렬되어 있다.
- [x] `pages/*.html`의 이전/다음 링크가 같은 순서를 따른다.
- [x] 대표 `docs/` 문서와 생성 HTML 목록이 대응한다.
- [x] 과거 HTML 파일의 유지/삭제/리다이렉트 정책이 명확하다.
- [x] `python scripts\verify_pages_structure.py`와 `git diff --check`가 통과한다.
