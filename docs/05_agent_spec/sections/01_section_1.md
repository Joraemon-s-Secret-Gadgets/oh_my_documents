# 1. 문서 개요

## 1.1 목적

본 문서는 로브 추천 Agent의 공개 정본이다.
Agent는 단일 LLM 호출이 아니라 `Intent_Agent`가 사용자 의도와 조건을 정리하고, `Supervisor_Router`가 상태 기반으로 전문 Agent와 결정적 Skill을 호출하는 멀티스텝 파이프라인으로 동작한다.

정본의 범위는 다음과 같다.

- 사용자 자연어, 온보딩 선호, 지도 진입 조건을 추천 가능한 상태로 구조화한다.
- 한국/일본 소도시와 장소 evidence 후보를 검색·점수화하고 Planner가 사용할 후보 패키지를 구성한다.
- 축제 날짜, 일정 구성, 추천 근거, 최종 응답의 안전성을 검증한다.
- AgentCore Runtime, Memory, Gateway, Policy, Observability에 연결 가능한 상태·노드·도구 계약을 정의한다.

## 1.2 설계 원칙

| 원칙 | 설명 |
| --- | --- |
| Supervisor I/O 허브 | `Supervisor_Router`는 raw 대화·웹 원문·RAG 원문을 보유하지 않고 압축 상태와 참조 키만 라우팅한다. |
| Sub-Agent / Skill 분리 | 자연어 해석, 검색 결과 해석, 일정·설명 생성, 의미 검증은 Sub-Agent가 수행하고, 계산·검증·링크 생성·상태 전이는 결정적 Skill이 수행한다. |
| 멀티턴 상태 보존 | `messages`, `conversation_summary`, `fulfilled_matrix`, `target_region`, `selected_destination`은 세션 상태로 이어진다. |
| 단일 목적지 추천 | 최종 추천은 소도시 1곳 중심으로 구성한다. |
| 검증 우선 | 미검증 축제 날짜, 국가 혼합, DB 근거 없는 장소·설명은 최종 응답에 확정값으로 노출하지 않는다. |
