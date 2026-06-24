# 12. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.14 | 2026-06-14 | llm | `needs_clarification=true`의 사용자 응답 대기 라우팅과 `fulfilled_matrix` 표준 전이 규칙을 명시 |
| v0.13 | 2026-06-13 | llm | 현재 단계에서 restaurant table/후보 조회를 Agent 검색 범위에서 제외하고, 미식 테마를 선택 도시 기반 외부 맛집 검색 링크로 처리하도록 대표 계약 반영 |
| v0.12 | 2026-06-13 | llm | API 입력 필드명을 `userLocation`으로 맞추고, 내부 `user_location` 정규화 경계를 명시. 일정 저장 대상을 현재 DB의 경량 저장 구조로 정리 |
| v0.11 | 2026-06-13 | llm | Candidate Evidence 관련 외부 평가 구현 경로 직접 참조를 제거하고 정본 내부 문서 연결 중심으로 정리 |
| v0.10 | 2026-06-12 | llm팀 | 정본에서 특정 LLM 모델 고정 문구를 제거하고 Bedrock Converse 추상화 원칙으로 정리 |
| v0.9 | 2026-06-12 | llm팀 | AgentCore 하네스/Memory/Gateway/Policy/Observability 책임 경계와 Memory 저장 금지 원칙을 대표 문서에 반영 |
| v0.8 | 2026-06-12 | llm팀 | `supplemental/intent_agent.md`를 Intent Agent 상세 정본으로 추가하고, 모델 호출 경계를 Bedrock Converse adapter로 분리 |
| v0.7 | 2026-06-12 | llm팀 | `supplemental/planner_agent.md`를 Planner Agent 상세 정본으로 추가하고, 일정 생성·설명·검증의 구현 기준을 대표 문서에 연결 |
| v0.6 | 2026-06-12 | llm팀 | Candidate Evidence Agent의 Baseline/Ours 비교 원칙과 테스트 계획·결과 문서 연결 추가 |
| v0.5 | 2026-06-10 | llm팀 | UnifiedAgentState를 `supplemental/langgraph_flow.md` 상세 정본과 정합화하고, `Candidate_Evidence_Agent` 검색 도구 명칭을 `Destination Search Tool`로 통일 |
| v0.4 | 2026-06-10 | llm팀 | Retriever/Ranker 분리 구간을 `Candidate_Evidence_Agent`로 통합하고 Planner가 일정·설명·검증을 구조 수준에서 통합 담당하도록 정리 |
| v0.4 | 2026-06-08 | llm팀 | DB v0.5 기준으로 Agent trace 저장 필드를 `lovv_agent_runs` 요약 필드와 Observability 메트릭으로 분리 |
| v0.4 | 2026-06-08 | llm팀 | Itinerary Planner와 Explanation Writer를 `Itinerary_Writer_Agent`로 통합하고 생성 matrix 키를 `generation`으로 정리 |
| v0.4 | 2026-06-08 | llm팀 | Top-K 축제 검증, 후보 0건 폴백, Validator 실패 카테고리, `fulfilled_matrix` 표준 키와 라우팅 우선순위 반영 |
| v0.4 | 2026-06-08 | llm팀 | 버전 상향 없이 API `themes`/`links` 매핑, Agent trace 식별자, DynamoDB/S3 vector 저장소 계약을 대표 문서에 보강 |
| v0.4 | 2026-06-07 | llm팀 | Agent 05 번호 체계 반영, Intent/Condition 통합, Supervisor I/O 허브, LangGraph 상태, Skill 분리, 추천 흐름, AgentCore/Bedrock 매핑, 검증 루프 가드 반영 |
| v0.3 | 2026-06-01 | 로브 기획팀 | Intent Agent 도입, Festival Verifier Agent 승격, Agent 구성도 및 전국구 RAG 조회 흐름 반영 |
| v0.2 | 2026-05-31 | 로브 기획팀 | LangGraph 기반 순환형 아키텍처 개편 및 Supervisor Router 도입, Polymorphic Retriever 노드 모드 분리, 하이브리드 데이터 조회 및 실시간 API 검증 반영 |
| v0.1 | 2026-05-29 | 로브 기획팀 | Agent 명세서 초안 작성 |
