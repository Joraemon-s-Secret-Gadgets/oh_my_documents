# Agent Instructions for docs

이 폴더는 로브(Lovv) 문서의 Markdown 원본을 보관한다. HTML은 생성물이며, 문서 내용 변경은 먼저 이 폴더의 Markdown에 반영한다.
## Source of Truth

- `docs/01_requirements/01_requirements.md`는 기능·비기능 요구사항의 기준 문서다.
- `docs/02_service_flow/02_service_flow.md`부터 `docs/07_api_spec/07_api_spec.md`까지는 요구사항 명세서를 상세화한 설계 문서다.
- `docs/00_project_plan/00_project_plan.md`는 상위 기획 문서이며, 상세 문서들의 최신 내용을 반영해 갱신한다.
- `docs/08_data_preprocessing/data_preprocessing_plan.md`부터 `docs/11_deployment_ops/11_deployment_ops.md`까지는 수집 이후 전처리, UI/UX, 테스트, 운영 문서의 대표 문서다.
- `docs/92_B2C/`, `docs/93_B2B/`, `docs/94_kick/`, `docs/95_aha_moment/`, `docs/96_market_research/`는 시장·제품 검증 보조 영역이며 각 폴더의 대표 문서를 기준으로 관리한다.
- `docs/98_prd/98_prd.md`는 특정 구축 범위나 실행 단위별 PRD를 모아 관리하는 대표 문서다.
- `docs/99_pptx/99_pptx.md`는 발표 자료 원본과 발표 단계별 하위 문서의 대표 문서다.

## Project Plan Synchronization

`docs/00_project_plan/00_project_plan.md`를 수정할 때는 아래 문서를 함께 확인한다. 이 문서들은 프로젝트 기획서 동기화를 위한 읽기 전용 참조이며, 이 작업만으로 함께 수정하지 않는다.

- `docs/01_requirements/01_requirements.md`
- `docs/02_service_flow/02_service_flow.md`
- `docs/03_data_collect_plan/03_data_collect_plan.md`
- `docs/04_database_design/04_database_design.md`
- `docs/05_agent_spec/05_agent_spec.md`
- `docs/06_technical_spec/06_technical_spec.md`
- `docs/07_api_spec/07_api_spec.md`

상세 문서와 프로젝트 기획서가 충돌하면 상세 문서의 결정을 우선하고, 프로젝트 기획서를 그 결정에 맞게 요약·정리한다.

상세 문서는 사용자가 해당 문서 수정을 직접 요청했거나, 다른 문서의 변경을 해당 상세 문서에 반영해야 하는 작업일 때만 Agent가 수정한다. 단순히 프로젝트 기획서를 최신화하는 작업에서는 상세 문서를 변경하지 않는다.

## Editing Rules

- 문서 버전, 문서 상태, 기준 문서를 상단 메타데이터에 유지한다.
- 문서의 `변경 이력`, `파일 이력`, `History`, `Changelog` 표는 최신 항목이 위에 오도록 최신순으로 작성한다. 같은 날짜의 이력은 더 높은 버전 또는 더 늦게 작성된 항목을 위에 둔다.
- `docs/00_project_plan` 및 `docs/01_requirements`부터 `docs/11_deployment_ops`까지는 `sections/*.md`를 먼저 수정한 뒤 각 폴더의 대표 문서 통합본과 생성 HTML을 갱신한다.
- 위 구조 적용 대상 폴더의 보조 Markdown은 각 폴더 루트가 아니라 `supplemental/`에서 관리한다.
- 90번대 문서 폴더는 `sections/`·`supplemental/` 강제 구조 적용 대상에서 제외한다.
- Markdown 표의 열 의미를 바꾸면 관련 HTML 생성물과 연결 문서도 함께 확인한다.
- 같은 폴더 안에 보조 Markdown을 추가해 수정할 내용, 근거, 초안을 먼저 작성할 수 있다. Agent는 보조 Markdown을 검토해 대표 문서에 반영한다.
- 새 문서 폴더를 추가하면 해당 폴더에 `AGENT.md`를 추가하고 `index.html` 및 `pages/` 생성 문서를 갱신한다.
- 대표 문서 이외에 새 `index.md` 파일은 만들지 않는다.
- 백업 파일은 근거 확인용으로만 사용하고, 현재 원본은 `docs/` 아래 Markdown으로 본다.
