---
작성자: 조동휘
상태: 진행후
---

# Agent 출력 생성 노드 통합 계획

## 목적

`agent_update.md` 6.5의 기존 통합 제안인 `Itinerary_Planner_Agent` + `Explanation_Writer_Agent` 통합을 정본 문서와 하위 문서에 반영한다. 목표는 일정 생성과 설명 생성을 하나의 구조화 출력 노드로 합쳐 LLM 호출 수와 중복 컨텍스트 전달을 줄이고, 일정과 추천 이유가 서로 어긋나는 문제를 줄이는 것이다.

## 기준 결정

- 통합 대상: `Itinerary_Planner_Agent` + `Explanation_Writer_Agent`
- 신규 정본 노드명: `Itinerary_Writer_Agent`
- 유지 대상: `Output_Validator_Agent`는 병합하지 않는다.
- 통합 출력: `itinerary`, `alternativeItinerary`, `recommendationReasons`, `itineraryFlowReason`, `externalLinks`, `confidence`, `user_notice`
- DB 기준: DB 문서는 수정하지 않는다. Agent 문서군만 토폴로지와 하네스를 맞춘다.

## 현재 근거 문서

| 문서 | 현재 역할 |
| --- | --- |
| `docs/05_agent_spec/agent_update.md` 6.5 | 출력 통합 제안 원문 |
| `docs/05_agent_spec/agent_update.md` 10장 | `Planner` + `Writer` 적용 완료 상태 반영 |
| `docs/05_agent_spec/agent_update.md` 11.4 | `05_agent_spec.md`, `langgraph_flow.md`, `agent_harness_design.md` 동시 갱신 결과 반영 |
| `docs/05_agent_spec/05_agent_spec.md` | 공개 정본을 `Itinerary_Writer_Agent` 단일 생성 노드 기준으로 갱신 |
| `docs/05_agent_spec/langgraph_flow.md` | 그래프 정본을 `Itinerary_Writer → Validation Skill → Output_Validator` 순차 호출로 갱신 |
| `docs/05_agent_spec/agent_harness_design.md` | 하네스와 trajectory를 `generation` 단일 생성 키 기준으로 갱신 |
| `docs/05_agent_spec/agent_build_target.md` | 구현 대상 목록을 `Itinerary_Writer_Agent` 기준으로 갱신 |

## 작업 체크리스트

- [x] `docs/05_agent_spec/agent_update.md`의 6.5, 10장, 11.4 내용을 기준으로 적용 범위를 확정한다.
- [x] `docs/05_agent_spec/05_agent_spec.md` 4장 출력, 5.2 파이프라인, 7.6/7.7 단계별 명세를 `Itinerary_Writer_Agent` 기준으로 통합한다.
- [x] `docs/05_agent_spec/05_agent_spec.md`의 Validator 실패 분기에서 `grounding_missing`, `explanation_weak` 재호출 대상을 `Itinerary_Writer_Agent` 또는 부분 재작성 정책으로 갱신한다.
- [x] `docs/05_agent_spec/05_agent_spec.md`의 `fulfilled_matrix` 표준 키를 검토해 `itinerary`와 `explanation`을 유지할지, `generation` 단일 키로 통합할지 결정한다.
- [x] `docs/05_agent_spec/langgraph_flow.md` 3.2 Agent-Tool 매핑, 5장 노드표, 6.3 순차 생성 구간, 6.4 실패 분기, 10장 불변식을 통합 노드 기준으로 갱신한다.
- [x] `docs/05_agent_spec/agent_harness_design.md`의 L1 노드 단위 테스트, TC-N01 정상 경로, TC-E04/TC-E05 실패 경로, fulfilled_matrix 전이 예시를 통합 노드 기준으로 갱신한다.
- [x] `docs/05_agent_spec/agent_build_target.md`의 역할표, 3.6/3.7 섹션, 구현 우선순위를 통합 노드 기준으로 갱신한다.
- [x] `docs/02_service_flow/02_service_flow.md`의 Agent 실행 순서가 분리 노드 기준으로 남아 있는지 확인하고, 필요 시 `Itinerary Writer` 표현으로 갱신한다.
- [x] `docs/99_pptx/01_midterm_presentation/*.md`에 발표용 Agent 단계가 분리 노드 기준으로 남아 있는지 확인한다. 발표자료는 정본 변경 후 별도 커밋으로 분리할지 결정한다.
- [x] `python scripts\generate_pages.py`로 `pages/05_agent_spec.html`, 필요한 경우 `pages/02_service_flow.html`, `index.html`을 재생성한다.
- [x] `python scripts\verify_pages_structure.py`로 HTML 구조를 검증한다.
- [x] `rg -n "Itinerary_Planner_Agent|Explanation_Writer_Agent|Itinerary Planner|Explanation Writer|Itinerary_Planner → Explanation_Writer" docs/05_agent_spec docs/02_service_flow pages/05_agent_spec.html pages/02_service_flow.html`로 잔여 분리 표현을 점검한다.
- [x] `git diff --cached --name-status`로 staged 변경 범위가 Agent 통합 작업과 무관한 변경을 포함하지 않는지 확인한다.

## 예상 변경 파일

- `docs/05_agent_spec/05_agent_spec.md`
- `docs/05_agent_spec/langgraph_flow.md`
- `docs/05_agent_spec/agent_harness_design.md`
- `docs/05_agent_spec/agent_build_target.md`
- `docs/02_service_flow/02_service_flow.md` (필요 시)
- `pages/05_agent_spec.html`
- `pages/02_service_flow.html` (필요 시)
- `index.html`
- `plans/before/agent-output-consolidation-plan.md`

## 검증 방법

- `python scripts\generate_pages.py`
- `python scripts\verify_pages_structure.py`
- `rg -n "Itinerary_Planner_Agent|Explanation_Writer_Agent|Itinerary Planner|Explanation Writer|Itinerary_Planner → Explanation_Writer" docs/05_agent_spec docs/02_service_flow pages/05_agent_spec.html pages/02_service_flow.html`
- `git diff --cached -- docs/05_agent_spec docs/02_service_flow pages/05_agent_spec.html pages/02_service_flow.html`

## 리스크 및 대응

| 리스크 | 영향 | 대응 |
| --- | --- | --- |
| `fulfilled_matrix` 키 변경이 하네스와 trace에 영향 | 라우팅 테스트가 깨질 수 있음 | 키 유지안과 `generation` 통합안을 비교하고 하네스 fixture를 동시에 갱신 |
| 생성 노드가 너무 많은 책임을 가짐 | 품질 저하 또는 프롬프트 비대화 | 출력 스키마는 통합하되 Validation Skill과 Output Validator는 분리 유지 |
| 설명 재작성만 필요한 실패에도 전체 일정 재생성 | 불필요한 비용 증가 | 실패 카테고리별로 부분 재작성 또는 동일 후보 재생성 정책을 명시 |
| 발표자료/서비스 흐름까지 한 번에 수정해 커밋이 커짐 | 커밋 범위 오염 | 정본 문서군을 우선 커밋하고 발표자료 반영은 별도 커밋 후보로 분리 |

## 완료 기준

- `05_agent_spec.md`, `langgraph_flow.md`, `agent_harness_design.md`, `agent_build_target.md`가 같은 통합 노드명을 사용한다.
- `Output_Validator_Agent`는 독립 노드로 유지된다.
- 생성 HTML이 Markdown 원본과 같은 통합 구조를 보여준다.
- 구조 검증이 통과한다.
