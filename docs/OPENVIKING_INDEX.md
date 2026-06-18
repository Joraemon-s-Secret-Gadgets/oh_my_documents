# OpenViking 이관 인덱스

## 이관 목적

이 문서는 `Joraemon-s-Secret-Gadgets/oh_my_documents` 저장소의 문서 원본을 OpenViking의 Agent 검색 및 컨텍스트 저장소로 동기화하기 위한 기준을 정의한다.

GitHub repo는 문서 원본 저장소로 유지하고, OpenViking은 Agent가 문서를 검색하고 작업 컨텍스트로 활용하는 보조 저장소로 사용한다.

## 원본 문서 원칙

OpenViking 이관의 기본 원본은 다음 경로의 Markdown 문서다.

```text
docs/**/*.md
```

다만 Agent가 repo 운영 규칙과 문서 작성 규칙을 함께 이해해야 하므로 다음 파일도 함께 이관한다.

- `README.md`
- `AGENT.md`
- `docs/**/AGENT.md`

## OpenViking 대상 경로

OpenViking 대상 루트는 다음 URI를 기준으로 한다.

```text
viking://resources/oh_my_documents/
```

동기화 시 repo 상대 경로를 유지한다. 예를 들어 `docs/05_agent_spec/05_agent_spec.md`는 `viking://resources/oh_my_documents/docs/05_agent_spec/05_agent_spec.md`로 대응한다.

## 주요 문서 목록

- `README.md`: 저장소 소개와 문서 운영 방식
- `AGENT.md`: repo 전체 Agent 작업 규칙
- `docs/AGENT.md`: `docs/` 하위 문서 작성 규칙
- `docs/00_project_plan/00_project_plan.md`: 프로젝트 기획서
- `docs/01_requirements/01_requirements.md`: 요구사항 명세서
- `docs/02_service_flow/02_service_flow.md`: 서비스 흐름 명세서
- `docs/03_data_collect_plan/03_data_collect_plan.md`: 데이터 수집 계획서
- `docs/04_database_design/04_database_design.md`: 데이터베이스 설계 명세서
- `docs/05_agent_spec/05_agent_spec.md`: Agent 명세서
- `docs/06_technical_spec/06_technical_spec.md`: 기술 명세서
- `docs/07_api_spec/07_api_spec.md`: API 명세서
- `docs/08_data_preprocessing/data_preprocessing_plan.md`: 데이터 전처리 계획서
- `docs/09_ui_ux_guide/`: UI/UX 가이드 문서
- `docs/10_test_plan/`: 테스트 계획 문서
- `docs/11_deployment_ops/`: 배포 및 운영 문서
- `docs/96_market_research/`: 시장 조사 문서
- `docs/98_prd/`: 실행 단위별 PRD 문서
- `docs/99_pptx/`: 발표 자료 원본 및 발표 관련 Markdown 문서

## 함께 이관할 보조 원본

sync 스크립트는 Markdown 외에도 Agent 컨텍스트 유지에 필요한 구조화된 보조 파일을 함께 이관할 수 있다.

- `docs/**/*.txt`
- `docs/**/*.json`
- `docs/**/*.yml`
- `docs/**/*.yaml`

## 제외 대상

다음 파일과 디렉터리는 생성 산출물 또는 바이너리 리소스로 취급하며 OpenViking 문서 원본 동기화에서 제외한다.

- `index.html`
- `pages/`
- `pdf/`
- `assets/`
- `*.pdf`
- `*.pptx`
- `*.png`
- `*.jpg`
- `*.jpeg`
- `*.html`

sync 스크립트 실행 시 로컬 개발 및 의존성 디렉터리도 제외한다.

- `.git/`
- `.venv/`
- `node_modules/`

## 운영 방식

GitHub repo는 사람이 검토하고 수정하는 원본 저장소다. 문서 본문을 바꿀 때는 기존 repo 규칙에 따라 `docs/` Markdown 원본을 먼저 수정한다.

OpenViking은 Agent 검색, 질의응답, 작업 컨텍스트 주입을 위한 읽기 중심 저장소로 사용한다. OpenViking에서 발견한 수정 필요 사항은 GitHub repo의 원본 Markdown에 반영한 뒤 다시 동기화한다.

`index.html`, `pages/`, `pdf/`, `assets/`는 배포 및 공유 산출물이므로 OpenViking의 Agent 컨텍스트 원본으로 사용하지 않는다.
