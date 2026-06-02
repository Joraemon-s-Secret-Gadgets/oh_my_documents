# oh_my_documents

GitHub Pages로 공유할 개발 문서를 관리하는 저장소입니다. 문서 원본은 Markdown으로 작성하고, Codex 같은 에이전트가 원본을 읽어 공유용 HTML 문서를 생성하는 흐름을 기준으로 운영합니다.

## 문서 운영 방식

문서는 원본과 배포 산출물을 분리합니다.

```text
docs/00_project_plan/      상위 프로젝트 기획서
docs/01_requirements/      요구사항 명세서와 보조 자료
docs/02_service_flow/      서비스 흐름 명세서
docs/03_technical_spec/    기술 명세서
docs/04_data_collect_plan/ 데이터 수집 계획서
docs/05_api_spec/          API 명세서
docs/06_database_design/   데이터베이스 설계 명세서
docs/07_agent_spec/        Agent 명세서
index.html                 GitHub Pages 첫 화면
pages/*.html               원본 Markdown을 바탕으로 생성된 공유용 HTML 문서
assets/                    공통 CSS, JS, 이미지 등 정적 리소스
plans/                     문서 사이트 구축 및 운영 계획
```

수정은 항상 `docs/`의 Markdown 원본에서 먼저 진행합니다. `index.html`과 `pages/*.html`은 원본 Markdown을 반영해 다시 생성하는 산출물로 취급합니다.

`docs/**/*.md`에는 `<!DOCTYPE html>`, `<html>`, `<body>`를 포함한 전체 HTML 문서를 저장하지 않습니다. HTML 형태로 작성된 문서를 원본으로 되돌릴 때는 제목, 문단, 표, 목록, 링크 같은 본문 의미만 Markdown으로 추출하고, 사이드바·스크립트·스타일·레이아웃 마크업은 제거합니다.

## 개발 문서 작성 흐름

개발 문서는 아래 순서로 작성합니다.

1. **프로젝트 기획서**
   상세 문서들의 확정 내용을 반영하는 상위 기획 문서입니다.

2. **요구사항 명세서**
   프로젝트 목적, 범위, 기능 요구사항, 비기능 요구사항, 제외 범위, 우선순위를 정의합니다.

3. **서비스 흐름 명세서**
   온보딩, 지도 진입, 챗봇 추천, 결과 확인, 저장·피드백 흐름을 정리합니다.

4. **기술 명세서**
   프론트엔드, 백엔드, 데이터베이스, 외부 서비스, 인증 구조 등 전체 기술 구성을 설명합니다.

5. **데이터 수집 계획서**
   수집할 데이터 소스, 주기, 포맷, 그리고 보존 정책을 정의합니다.

6. **API 명세서**
   엔드포인트, 요청, 응답, 에러 코드, 인증 방식을 정의합니다.

7. **데이터베이스 설계 명세서**
   ERD, 테이블 또는 컬렉션, 필드, 관계, 인덱스, 제약 조건을 정의합니다.

8. **Agent 명세서**
   조건 분류, RAG 검색, 후보 선정, 일정 구성, 설명 생성 파이프라인을 정의합니다.

9. **UI/UX 가이드**
   화면 레이아웃, 컴포넌트 규칙, 입력/오류/빈 상태, 반응형 기준을 정리합니다.

10. **테스트 계획서**
    단위 테스트, 통합 테스트, E2E 테스트, 수동 검증 체크리스트를 정리합니다.

11. **배포 가이드**
    로컬 실행, 빌드, 환경 변수, 배포 절차, GitHub Pages 설정 방법을 정리합니다.

12. **운영 가이드**
    로그, 장애 대응, 백업, 모니터링, 정기 점검 기준을 정리합니다.

### Agent 문서 수정 규칙

이 저장소에는 루트 `AGENT.md`와 각 `docs/` 하위 폴더별 `AGENT.md`가 있습니다. Claude나 Codex 같은 Agent는 가장 가까운 `AGENT.md`의 규칙을 우선합니다.

- `docs/00_project_plan/00_project_plan.md`는 상세 문서의 내용을 반영하는 상위 기획 문서입니다.
- 프로젝트 기획서를 수정할 때 `docs/01_requirements`부터 `docs/07_agent_spec`까지의 대표 문서는 읽기 전용 참조로만 확인합니다.
- 프로젝트 기획서 동기화 작업만으로 상세 문서를 함께 수정하지 않습니다.
- 상세 문서는 사용자가 해당 문서 수정을 요청했거나, 그 문서 자체의 내용을 업데이트하는 작업일 때만 Agent가 수정합니다.
- `01_requirements`를 수정하는 경우 `docs/01_requirements/01_requirements.md`를 먼저 업데이트하고, 필요한 보조 Markdown을 만든 뒤, 마지막에 `pages/01_requirements.html`을 최신화합니다.

### 역할·권한 반영 기준

요구사항 명세서의 이해관계자 역할 모델은 후속 문서 작성 시 공통 기준으로 사용합니다.

- 서비스 흐름 명세서에는 `R-USER`, `R-LOCAL-OPERATOR`, `R-ADMIN`, `R-DATA-PROVIDER`별 대표 흐름과 권한 없는 상태를 포함합니다.
- 데이터베이스 설계 명세서에는 역할, 권한, 기관 소속, 담당 지역, 승인 이력, 감사 로그 후보를 검토합니다.
- API 명세서에는 인증 필요 엔드포인트, 역할별 인가 조건, 401/403/키 만료 응답을 정의합니다.
- Agent 명세서에는 역할별 입력 가능 범위와 운영 데이터 접근 제한을 반영합니다.

## 권장 문서 목록

```text
docs/
├── AGENT.md
├── 00_project_plan/
│   ├── AGENT.md
│   └── 00_project_plan.md
├── 01_requirements/
│   ├── AGENT.md
│   └── 01_requirements.md
├── 02_service_flow/
│   ├── AGENT.md
│   └── 02_service_flow.md
├── 03_technical_spec/
│   ├── AGENT.md
│   └── 03_technical_spec.md
├── 04_data_collect_plan/
│   ├── AGENT.md
│   └── 04_data_collect_plan.md
├── 05_api_spec/
│   ├── AGENT.md
│   └── 05_api_spec.md
├── 06_database_design/
│   ├── AGENT.md
│   └── 06_database_design.md
└── 07_agent_spec/
    ├── AGENT.md
    └── 07_agent_spec.md
```

문서 내용이 많아지면 같은 폴더 안에 보조 Markdown을 추가할 수 있습니다. 단, 각 폴더의 대표 문서는 위 경로를 유지합니다.

보조 Markdown에는 수정할 내용, 근거, 초안을 먼저 작성할 수 있습니다. 이후 Claude나 Codex 같은 LLM Agent가 보조 Markdown의 내용을 검토해 해당 폴더의 대표 문서에 반영하고, 필요한 경우 `pages/`의 HTML 생성물도 최신화합니다.

## GitHub Pages

GitHub Pages는 저장소 루트의 `index.html`을 첫 화면으로 사용합니다. `docs/`는 원본 Markdown 보관 위치로 사용하고, 공유용 HTML은 `pages/`에 생성합니다.

문서 복구 및 최신화 계획은 [plans/requirements-restore-reapply-plan.md](plans/requirements-restore-reapply-plan.md)와 [plans/requirements_update_plan.md](plans/requirements_update_plan.md)를 참고합니다.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
