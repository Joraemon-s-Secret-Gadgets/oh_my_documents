# Agent Instructions for test plan

이 폴더는 로브(Lovv) 테스트 계획서를 관리한다.

## Primary Document

대표 문서는 `10_test_plan.md`다. 테스트 범위, 테스트 유형(단위·통합·E2E·Agent 평가), 테스트 데이터, 합격 기준, 회귀 전략을 정의한다.

## Dependencies

- 요구사항 기준: `../01_requirements/01_requirements.md`
- Agent 구조·평가: `../05_agent_spec/05_agent_spec.md`
- 기술 명세(품질·관측성): `../06_technical_spec/06_technical_spec.md`
- API 계약: `../07_api_spec/07_api_spec.md`

## Editing Rules

- 합격 기준은 기술 명세서의 품질·관측성 지표(추천 처리 시간, RAG 검색, 추적 항목)와 일치시킨다.
- Agent 회귀 평가는 Agent 명세서의 평가 하네스 정의를 기준으로 작성한다.
- 같은 폴더 안에 보조 Markdown을 추가해 초안·근거를 먼저 작성하고, Agent가 검토해 대표 문서에 반영한다.
- 문서 버전, 문서 상태(Draft/Review/Complete), 기준 문서를 상단 메타데이터에 유지한다.
