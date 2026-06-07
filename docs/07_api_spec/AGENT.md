# Agent Instructions for API spec

이 폴더는 로브 API 명세서를 관리한다.

## Primary Document

대표 문서는 `07_api_spec.md`다. 프론트엔드, 백엔드, 추천 Agent, 운영 화면이 사용하는 API 계약을 정의한다.

## Dependencies

- 요구사항 기준: `../01_requirements/01_requirements.md`
- 서비스 흐름: `../02_service_flow/02_service_flow.md`
- 데이터 수집 계획: `../03_data_collect_plan/03_data_collect_plan.md`
- 데이터 모델: `../04_database_design/04_database_design.md`
- Agent 입출력: `../05_agent_spec/05_agent_spec.md`

## Editing Rules

- 엔드포인트를 추가하면 목적, 인증, 요청, 응답, 오류 형식을 함께 정의한다.
- 공개 API와 인증 필요 API를 명확히 구분한다.
- 401, 403, 404, 409, 422, 429, 500 계열 오류 의미를 일관되게 유지한다.
- API 필드가 데이터베이스 필드나 Agent 입출력과 충돌하지 않는지 확인한다.
