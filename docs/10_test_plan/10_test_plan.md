# 로브 (Lovv) 테스트 계획서

> 문서 버전: v0.1
> 문서 상태: 초안 (Draft)
> 작성일: 2026-06-23
> 문서 성격: 대표 Markdown
> 기준 문서: `../01_requirements/01_requirements.md`, `../05_agent_spec/05_agent_spec.md`, `../06_technical_spec/06_technical_spec.md`, `../07_api_spec/07_api_spec.md`
# 1. 문서 목적

이 문서는 Lovv 전체 테스트 범위를 대표 문서에서 관리하기 위한 상위 계획서다. 현재 확정된 검증 산출물은 Candidate Evidence Agent 검색 평가이며, Planner 일정 생성, Festival Verifier, API E2E, 배포·운영 검증은 후속 계획 범위로 둔다.

`docs/10_test_plan/`의 보조 Markdown은 개별 평가 계획과 결과 보고서로 관리한다. 보조 문서의 범위가 전체 시스템 테스트 기준으로 승격되면 이 대표 문서에 요약 반영한다.
# 2. 테스트 범위

| 구분 | 현재 문서화 상태 | 대표 문서 반영 기준 |
| --- | --- | --- |
| Candidate Evidence 검색 | 계획·결과 문서화 완료 | 현재 문서의 3장에 요약 |
| Planner 일정 생성 | 후속 작성 필요 | `05_agent_spec.md`, `planner_agent.md`, `itinerary_flow.md` 기준으로 테스트 계획 작성 |
| Festival Verifier | 후속 작성 필요 | `festival_verifier_agent.md` 기준으로 날짜·출처 검증 테스트 작성 |
| API E2E | 후속 작성 필요 | `07_api_spec.md` 기준으로 인증, 추천, 저장, 피드백, 운영 API 시나리오 작성 |
| UI/UX 수용 테스트 | 후속 작성 필요 | `09_ui_ux_guide.md` 기준으로 주요 사용자 여정 검증 |
| 배포·운영 검증 | 후속 작성 필요 | `11_deployment_ops.md` 기준으로 배포, 롤백, 모니터링, 장애 대응 검증 |
# 3. 현재 반영된 평가 산출물

| 보조 문서 | 범위 | 상태 |
| --- | --- | --- |
| `supplemental/candidate_evidence_search_test_plan.md` | Candidate Evidence Agent의 도시 및 관광지 검색 테스트 계획 | Review |
| `supplemental/candidate_evidence_evaluation_results.md` | Baseline Simple RAG와 Candidate Evidence Agent Ours 비교 결과 | Review |

Candidate Evidence 평가는 도시 선정, 관광지·음식점 후보 검색, scoring, quota, fallback, audit 구조를 검증한다. Planner 일정 품질, Festival 검증, LangGraph 전체 trajectory, API E2E는 해당 평가의 범위 밖이다.
# 4. 공통 검증 원칙

- 테스트 범위는 요구사항 ID, Agent 입출력, API 계약, 데이터 모델과 연결한다.
- 부분 평가 문서는 전체 시스템 합격으로 해석하지 않는다.
- 실행 결과는 통과·실패 수치뿐 아니라 범위, 제외 항목, 해석 한계를 함께 기록한다.
- LLM judge나 합성 fixture를 사용하는 경우 실제 사용자 검증을 대체하지 않는다고 명시한다.
- 성능, 비용, observability 항목은 기술 명세서와 배포·운영 문서의 기준을 따른다.
# 5. 후속 작성 항목

| 우선순위 | 항목 | 기준 문서 |
| --- | --- | --- |
| P1 | Planner 일정 생성 테스트 계획 | `../05_agent_spec/supplemental/planner_agent.md`, `../05_agent_spec/supplemental/itinerary_flow.md` |
| P1 | API 추천·저장 E2E 테스트 계획 | `../07_api_spec/07_api_spec.md` |
| P2 | Festival Verifier 날짜·출처 검증 테스트 | `../05_agent_spec/supplemental/festival_verifier_agent.md` |
| P2 | UI 주요 여정 수용 테스트 | `../09_ui_ux_guide/09_ui_ux_guide.md` |
| P3 | 배포·운영 smoke 및 rollback 테스트 | `../11_deployment_ops/11_deployment_ops.md` |
# 6. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.1 | 2026-06-23 | 로브 기획팀 | 테스트 계획 대표 문서 생성, Candidate Evidence 평가 산출물과 후속 테스트 범위 정리 |
