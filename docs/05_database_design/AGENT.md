# Agent Instructions for database design

이 폴더는 로브 데이터베이스 설계 명세서를 관리한다.

## Primary Document

대표 문서는 `05_database_design.md`다. 핵심 데이터 모델, 테이블 후보, 관계, 인덱스, 보존 정책을 정의한다.

## Dependencies

- 요구사항 기준: `../01_requirements/01_requirements.md`
- API 계약: `../04_api_spec/04_api_spec.md`
- Agent 검색·추천 데이터: `../06_agent_spec/06_agent_spec.md`

## Editing Rules

- 개인정보, 저장 일정, 피드백, 운영 검토 이력은 보존 기간과 접근 권한을 함께 고려한다.
- 테이블이나 컬렉션을 추가하면 주요 키, 관계, 인덱스 후보를 함께 적는다.
- PoC의 로컬 스토리지·정적 파일 대체와 Production DB 설계를 구분한다.
- 추천 스코어링에 쓰는 데이터와 화면 표시용 데이터를 혼동하지 않는다.
