# Agent Instructions for test plan

이 폴더는 로브(Lovv) 테스트 계획서를 관리한다.

## Document Structure

대표 문서는 `10_test_plan.md`다. Lovv 전체 시스템의 단위·통합·E2E·Agent 평가 범위를 상위에서 관리한다.

현재 대표 문서는 통합 계획 초안이며, Candidate Evidence 평가 산출물을 먼저 상위 범위 안에 배치한다. 아직 Planner, Festival Verifier, API E2E, 배포 검증이 완결되지 않은 항목은 명시적으로 미정 또는 후속 범위로 둔다.

현재 하위 문서는 다음과 같다.

- `candidate_evidence_search_test_plan.md`: Candidate Evidence Agent의 도시 및 관광지 검색 테스트 계획
- `candidate_evidence_evaluation_results.md`: 해당 검색 테스트와 블라인드 정성 평가의 실행 결과와 한계

## Dependencies

- 요구사항 기준: `../01_requirements/01_requirements.md`
- Agent 구조·평가: `../05_agent_spec/05_agent_spec.md`
- 기술 명세(품질·관측성): `../06_technical_spec/06_technical_spec.md`
- API 계약: `../07_api_spec/07_api_spec.md`

## Editing Rules

- 합격 기준은 기술 명세서의 품질·관측성 지표(추천 처리 시간, RAG 검색, 추적 항목)와 일치시킨다.
- Agent 회귀 평가는 Agent 명세서의 평가 하네스 정의를 기준으로 작성한다.
- 기능 일부만 검증한 경우 범위를 드러내는 하위 Markdown으로 작성하고, `10_test_plan.md`에는 현재 커버리지와 미완료 상위 범위를 함께 표시한다.
- 문서 버전, 문서 상태(Draft/Review/Complete), 기준 문서를 상단 메타데이터에 유지한다.
