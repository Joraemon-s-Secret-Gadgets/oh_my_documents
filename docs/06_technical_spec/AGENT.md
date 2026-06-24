# Agent Instructions for technical spec

이 폴더는 로브 기술 명세서를 관리한다.

## Primary Document

대표 문서는 `06_technical_spec.md`다. 프론트엔드, 백엔드, 데이터, 외부 API, AI/RAG 계층의 책임과 경계를 정의한다.
## Representative Document Flow

- `06_technical_spec.md` is the integrated representative document for this folder.
- `sections/*.md` is the editing source for `06_technical_spec.md`.
- When changing representative document body content, edit the matching `sections/*.md` file first, then regenerate or update `06_technical_spec.md` in the same change.
- `supplemental/*.md` stores supporting notes, rationale, drafts, and detailed references for this folder.
- Do not keep supplemental Markdown documents at this folder root.
- Do not create an `index.md` file in this folder.

## Dependencies

- 요구사항 기준: `../01_requirements/01_requirements.md`
- 데이터 수집 계획: `../03_data_collect_plan/03_data_collect_plan.md`
- API 계약: `../07_api_spec/07_api_spec.md`
- 데이터 모델: `../04_database_design/04_database_design.md`
- Agent 구조: `../05_agent_spec/05_agent_spec.md`

## Editing Rules

- 기술 선택은 요구사항과 운영 제약을 만족하는 방향으로만 변경한다.
- 프론트엔드, 백엔드, 데이터, Agent 책임 경계를 흐리지 않는다.
- API Key, 외부 API 프록시, CORS, 인증·인가 같은 보안 경계는 구체적으로 적는다.
- PoC에서 정적 파일이나 로컬 스토리지로 대체하는 부분은 Production 전환 조건을 함께 적는다.
