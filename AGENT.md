# Agent Instructions

이 저장소는 GitHub Pages로 공유할 로브(Lovv) 개발 문서를 관리한다. 에이전트는 Markdown 원본 문서를 기준으로 HTML 공유 문서를 생성하거나 갱신한다.

## Core Rule

수정은 항상 `docs/`의 Markdown 원본에서 먼저 진행한다.

`index.html`과 `pages/*.html`은 공유용 생성물로 취급한다. HTML을 직접 수정해야 하는 경우에도, 같은 변경이 반드시 대응하는 Markdown 원본에 반영되어 있어야 한다.

`docs/00_project_plan/00_project_plan.md`는 다른 상세 문서의 내용을 반영하는 상위 기획 문서다. LLM이 이 파일을 수정할 때는 `docs/01_requirements`부터 `docs/07_agent_spec`까지의 최신 내용을 읽기 전용 기준으로 확인하고, 상세 문서와 모순되지 않게 요약·동기화한다.

프로젝트 기획서 동기화 작업만으로 상세 문서를 수정하지 않는다. 상세 문서는 사용자가 해당 문서 수정을 요청했거나, 그 문서 자체의 내용을 업데이트하는 작업일 때만 Agent가 수정한다.

## Repository Roles

```text
docs/00_project_plan/      상위 프로젝트 기획서. 다른 문서의 내용을 반영한다.
docs/01_requirements/      요구사항 명세서와 요구사항 보조 자료
docs/02_service_flow/      서비스 흐름 명세서
docs/03_technical_spec/    기술 명세서
docs/04_data_collect_plan/ 데이터 수집 계획서
docs/05_api_spec/          API 명세서
docs/06_database_design/   데이터베이스 설계 명세서
docs/07_agent_spec/        Agent 명세서
index.html                 GitHub Pages 첫 화면
pages/*.html               Markdown 원본을 바탕으로 생성된 공유용 HTML 문서
assets/                    공통 CSS, JS, 이미지 등 정적 리소스
plans/                     문서 사이트 구축 및 운영 계획
README.md                  저장소 소개와 운영 방식 요약
```

## Document Flow

개발 문서는 아래 순서를 기본으로 한다.

1. 프로젝트 기획서
2. 요구사항 명세서
3. 서비스 흐름 명세서
4. 기술 명세서
5. 데이터 수집 계획서
6. API 명세서
7. 데이터베이스 설계 명세서
8. Agent 명세서
9. UI/UX 가이드
10. 테스트 계획서
11. 배포·운영 가이드

## Source Document Naming

현재 문서 구조는 다음을 기준으로 한다.

```text
docs/
├── 00_project_plan/00_project_plan.md
├── 01_requirements/01_requirements.md
├── 02_service_flow/02_service_flow.md
├── 03_technical_spec/03_technical_spec.md
├── 04_data_collect_plan/04_data_collect_plan.md
├── 05_api_spec/05_api_spec.md
├── 06_database_design/06_database_design.md
└── 07_agent_spec/07_agent_spec.md
```

문서 내용이 많아지면 같은 폴더 안에 보조 Markdown 문서를 추가할 수 있다. 단, 각 폴더의 대표 문서는 위 경로를 유지한다.

보조 Markdown에는 수정할 내용, 근거, 초안을 먼저 작성할 수 있다. 이후 Agent는 보조 Markdown을 검토해 해당 폴더의 대표 문서에 반영하고, 필요한 경우 `pages/`의 HTML 생성물도 최신화한다.

## HTML Generation Rules

- `index.html`은 전체 문서 목차, 문서별 요약, 상태를 보여주는 GitHub Pages 첫 화면으로 생성한다.
- `pages/*.html`은 `docs/*.md` 또는 `docs/*/index.md`를 바탕으로 생성한다.
- 모든 HTML 문서는 `assets/css/requirements.css`를 공유한다.
- HTML 문서에는 공통 헤더, 본문, 이전/다음 문서 링크, 푸터를 포함한다.
- 생성된 HTML 링크는 모두 상대 경로를 사용한다.
- 문서 상태는 `Draft`, `Review`, `Complete` 중 하나를 사용한다.

## Verification Checklist

HTML 생성 또는 문서 구조 변경 후 다음을 확인한다.

- `docs/` 원본 문서와 `pages/` 생성 문서의 목록이 대응한다.
- `index.html`에서 모든 문서로 이동할 수 있다.
- `pages/*.html`의 이전/다음 링크가 깨지지 않는다.
- GitHub Pages 기준 상대 경로가 올바르다.
- README의 운영 방식과 실제 구조가 어긋나지 않는다.

## Reference

자세한 문서 복구 및 최신화 계획은 `plans/requirements-restore-reapply-plan.md`와 `plans/requirements_update_plan.md`를 참고한다.
