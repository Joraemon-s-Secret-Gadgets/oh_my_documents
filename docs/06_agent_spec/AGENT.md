# Agent Instructions for Agent spec

이 폴더는 로브 추천 Agent 명세서를 관리한다.

## Primary Document

대표 문서는 `06_agent_spec.md`다. 조건 분류, RAG 검색, 후보 선정, 일정 구성, 설명 생성, 폴백, 검증 기준을 정의한다.

## Dependencies

- 요구사항 기준: `../01_requirements/01_requirements.md`
- 서비스 흐름: `../02_service_flow/02_service_flow.md`
- 기술 경계: `../03_technical_spec/03_technical_spec.md`
- API 계약: `../04_api_spec/04_api_spec.md`
- 데이터 모델: `../05_database_design/05_database_design.md`

## Editing Rules

- Agent는 단일 LLM 호출이 아니라 멀티스텝 파이프라인으로 정의한다.
- 추천 후보 스코어링에는 월별 기상 경향 데이터를 사용하고, 실시간 WeatherAPI는 표시용으로 구분한다.
- RAG 근거, 필터링 조건, 폴백 조건, 금지 동작을 명확히 적는다.
- Agent 입출력 스키마를 바꾸면 API 명세와 데이터베이스 설계 영향도 함께 확인한다.
