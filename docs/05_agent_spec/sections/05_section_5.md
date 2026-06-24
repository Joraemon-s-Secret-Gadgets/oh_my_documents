# 5. 파이프라인

`Intent_Agent`는 조건 파싱을 내장한 entry node다.
`Condition_Parser_Agent`는 별도 물리 노드로 두지 않고 `Intent_Agent`의 논리 책임으로 통합한다.
이후 `Supervisor_Router`가 `fulfilled_matrix`와 구조화 조건을 기준으로 `Candidate_Evidence_Agent`를 호출한다.
`Candidate_Evidence_Agent`는 기존 `Polymorphic_Retriever_Agent`와 `Ranker_Agent`의 책임을 통합해 장소 evidence 검색, 도시/장소 점수화, Planner 입력 후보 패키지 구성을 수행한다.
목적지와 후보 장소 패키지가 구성된 뒤에는 `Planner_Agent`가 일정 생성, 설명 생성, 최종 출력 검증을 통합 담당한다.

## 5.1 Agent 구성도

![Lovv Agent 구성도](../../assets/images/mermaid/05-agent-spec-05-agent-spec-01.png)

## 5.2 파이프라인 단계

| 단계 | 노드/모듈 | 역할 | 출력 |
| --- | --- | --- | --- |
| 1 | `Intent_Agent` | 멀티턴 컨텍스트 정리, 조건 파싱, 필수 조건 확인 | handoff payload, 초기 `fulfilled_matrix` |
| 2 | `Supervisor_Router` | 상태 기반 라우팅, 재시도·폴백 제어, Skill 호출 | `next_node`, 라우팅 결정 |
| 3 | `Candidate_Evidence_Agent` | 장소 evidence 검색, 도시/장소 scoring, primary/reserve 후보 패키징 | `selected_city`, `recommended_places`, `reserve_places`, `city_rankings`, audit |
| 4 | `Festival_Verifier_Agent` | 축제 후보의 해당 연도 개최일 검증 | 검증 JSON, 캐시 |
| 5 | `Planner_Agent` | 일정 생성, 추천 설명 생성, 최종 출력 검증을 통합 수행 | `itinerary`, `alternativeItinerary`, `recommendationReasons`, `itineraryFlowReason`, `user_notice` |
| 6 | `Backend_Serving / SAM` | 응답 패키징, 저장, UI 서빙 | 최종 추천 응답 |
