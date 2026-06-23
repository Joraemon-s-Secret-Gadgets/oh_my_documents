---
작성자: llm팀
상태: 진행후
작성일: 2026-06-07
---

# Agent 명세서 최신화 계획

## 목적

`docs/05_agent_spec/05_agent_spec.md`를 Agent 명세서의 공개 정본으로 최신화한다. 현재 `agent_spec_revision_plan.md`, `langgraph_flow.md`, `agent_harness_design.md`, `recommendation_flow.md`에 반영된 최신 설계가 대표 문서에 충분히 통합되지 않았으므로, 보조 문서의 결정 사항을 선별해 정본, 연결 문서, 생성 HTML을 같은 기준으로 맞춘다.

## 현재 기준

| 구분 | 현재 상태 | 처리 방향 |
| --- | --- | --- |
| 대표 문서 | `docs/05_agent_spec/05_agent_spec.md` v0.2 | 최신 결정 반영 후 v0.4 후보로 갱신 |
| 수정 방안 | `docs/05_agent_spec/agent_spec_revision_plan.md`가 v0.3/v0.4 반영 항목을 보유 | 반영할 항목과 보류할 항목을 구분 |
| 그래프 정본 | `docs/05_agent_spec/langgraph_flow.md` v1.0 | 상태 스키마, 노드, 엣지, 루프 가드를 대표 문서에 요약 반영 |
| 하네스 | `docs/05_agent_spec/agent_harness_design.md` v1.0 | 검증 기준, 평가 지표, CI 연계 내용을 품질 검증 장에 반영 |
| 추천 흐름 | `docs/05_agent_spec/recommendation_flow.md` | 추천 점수화, 근거 생성, 예외 흐름을 Ranker/Explanation에 반영 |
| 연결 문서 | `02_service_flow`, `04_database_design`, `06_technical_spec`, `07_api_spec` | Agent 입출력·저장·API 영향만 필요한 범위로 동기화 |

## 목표 산출물

- `docs/05_agent_spec/05_agent_spec.md`: 최신 Agent 정본
- `docs/05_agent_spec/agent_build_target.md`: 구현 대상 목록과 정본 명칭 동기화
- `docs/05_agent_spec/langgraph_flow.md`: 정본과 충돌하는 표현이 있으면 최소 정리
- `docs/05_agent_spec/agent_harness_design.md`: 정본 변경에 따른 검증 항목 보강
- `docs/02_service_flow/02_service_flow.md`: Agent 처리 단계와 사용자 흐름 영향 반영
- `docs/04_database_design/04_database_design.md`: Agent 실행 상태, 캐시, 검증 결과 저장 영향 반영
- `docs/06_technical_spec/06_technical_spec.md`: Bedrock, AgentCore, LangGraph 책임 경계 반영
- `docs/07_api_spec/07_api_spec.md`: 추천 요청·응답 필드와 오류 계약 반영
- `pages/05_agent_spec.html`, `index.html`: Markdown 기준 재생성

## 작업 순서

### Task 1: 최신 결정 범위 확정

**Description:** `agent_spec_revision_plan.md`의 적용 순서와 체크리스트를 기준으로 대표 문서에 반영할 항목을 확정한다.

**Acceptance criteria:**
- [x] Intent/Condition 병합, 루프 가드, Festival 검색 캐시, 명칭 통일 항목의 반영 여부가 정리된다.
- [x] Bedrock/AgentCore, 비용, 추천 흐름, 멀티턴 항목이 정본에 들어갈 수준으로 분류된다.
- [x] 보류 항목은 별도 후속 작업으로 남긴다.

**Verification:**
- [x] `agent_spec_revision_plan.md` 9장 체크리스트와 계획 항목이 1:1로 대응하는지 확인한다.

**Dependencies:** None

**Files likely touched:**
- `docs/05_agent_spec/agent_spec_revision_plan.md`
- `plans/before/agent-spec-latest-refresh-plan.md`

**Estimated scope:** S

### Task 2: Agent 정본 구조 재정렬

**Description:** `05_agent_spec.md`의 장 구성을 최신 그래프와 추천 흐름을 담을 수 있게 재정렬한다.

**Acceptance criteria:**
- [x] 문서 버전, 상태, 기준 문서가 최신 번호 체계와 맞는다.
- [x] Agent 목표, 입력, 출력, 파이프라인, 단계별 명세의 중복이 줄어든다.
- [x] `Ranker`, `Itinerary_Planner_Agent`, `Explanation_Writer_Agent`, `Output_Validator_Agent` 명칭이 통일된다.

**Verification:**
- [x] `rg -n "Itinerary Planner|Output Validator|Ranker \\(" docs/05_agent_spec/05_agent_spec.md`로 잔여 구표현을 확인한다.

**Dependencies:** Task 1

**Files likely touched:**
- `docs/05_agent_spec/05_agent_spec.md`

**Estimated scope:** M

### Task 3: LangGraph 상태와 노드 반영

**Description:** `langgraph_flow.md`의 UnifiedAgentState, 노드, 엣지, 재진입 루프 가드를 대표 문서에 반영한다.

**Acceptance criteria:**
- [x] `UnifiedAgentState` 핵심 필드가 대표 문서에 요약된다.
- [x] 검색·후보 선정 루프와 순차 생성 구간의 경계가 명확해진다.
- [x] 검증 실패 재진입 횟수와 종료 조건이 명시된다.

**Verification:**
- [x] `05_agent_spec.md`의 Mermaid와 `langgraph_flow.md`의 주요 노드 명칭이 충돌하지 않는다.

**Dependencies:** Task 2

**Files likely touched:**
- `docs/05_agent_spec/05_agent_spec.md`
- `docs/05_agent_spec/langgraph_flow.md`

**Estimated scope:** M

### Task 4: 추천 로직과 근거 생성 반영

**Description:** `recommendation_flow.md`와 `agent_spec_revision_plan.md` 7장의 추천 흐름을 Ranker, Retriever, Explanation 장에 반영한다.

**Acceptance criteria:**
- [x] 자연어 입력, 필수 조건, 선호 조건, unsupported 조건 분류가 반영된다.
- [x] 거리, 테마, 희소 테마, 콘텐츠 타입, 축제 포함 여부, 임베딩 유사도 점수 요소가 정리된다.
- [x] `recommendationReasons`, `confidence`, `user_notice`의 생성 책임이 명확해진다.

**Verification:**
- [x] `07_api_spec.md`의 추천 응답 필드와 Agent 출력 필드가 충돌하지 않는다.

**Dependencies:** Task 3

**Files likely touched:**
- `docs/05_agent_spec/05_agent_spec.md`
- `docs/07_api_spec/07_api_spec.md`

**Estimated scope:** M

### Checkpoint: 정본 반영

- [x] `05_agent_spec.md`가 단독으로 읽어도 최신 Agent 구조를 설명한다.
- [x] 보조 문서는 상세 근거 역할로 남고, 정본과 반대되는 결정을 담지 않는다.
- [x] 변경 이력에 최신화 항목이 추가된다.

### Task 5: Bedrock, AgentCore, 비용 경계 반영

**Description:** AWS Bedrock, AgentCore, Knowledge Bases, 모델 티어링, 예산 관련 내용을 대표 문서와 기술 명세에 필요한 수준으로 반영한다.

**Acceptance criteria:**
- [x] AgentCore 역할과 LangGraph/하네스 역할이 혼동되지 않는다.
- [x] 모델 티어링과 비용 절감 레버가 운영 제약으로 정리된다.
- [x] 기술 명세에는 구현 책임 경계만 반영하고 Agent 세부 로직은 중복하지 않는다.

**Verification:**
- [x] `docs/06_technical_spec/06_technical_spec.md`와 `docs/05_agent_spec/05_agent_spec.md`의 책임 설명이 중복 대신 상호 참조로 정리된다.

**Dependencies:** Task 3

**Files likely touched:**
- `docs/05_agent_spec/05_agent_spec.md`
- `docs/06_technical_spec/06_technical_spec.md`

**Estimated scope:** M

### Task 6: 데이터베이스와 API 영향 동기화

**Description:** Agent 실행 상태, 검색 캐시, 축제 검증 결과, 추천 응답 필드가 DB/API 문서와 맞는지 갱신한다.

**Acceptance criteria:**
- [x] `04_database_design.md`에 Agent 실행 상태, 검증 캐시, 벡터/테마/좌표 사용 영향이 필요한 범위로 반영된다.
- [x] `07_api_spec.md`에 `user_location`, `naturalLanguageQuery`, 추천 근거, 신뢰도, 사용자 안내 필드가 정리된다.
- [x] Agent 출력 스키마와 API 응답 스키마의 명칭이 충돌하지 않는다.

**Verification:**
- [x] `rg -n "user_location|naturalLanguageQuery|recommendationReasons|confidence|user_notice" docs/05_agent_spec docs/07_api_spec`로 필드 정합성을 확인한다.

**Dependencies:** Task 4

**Files likely touched:**
- `docs/04_database_design/04_database_design.md`
- `docs/07_api_spec/07_api_spec.md`
- `docs/05_agent_spec/05_agent_spec.md`

**Estimated scope:** M

### Task 7: 서비스 흐름과 구현 대상 문서 정리

**Description:** 서비스 흐름 문서의 Agent 처리 단계와 `agent_build_target.md`의 구현 대상 목록을 정본에 맞춘다.

**Acceptance criteria:**
- [x] `02_service_flow.md`의 Agent 처리 단계가 최신 파이프라인과 일치한다.
- [x] `agent_build_target.md`의 구현 우선순위와 노드명이 정본과 일치한다.
- [x] 하네스 문서의 테스트 시나리오가 최신 추천 흐름을 검증한다.

**Verification:**
- [x] `rg -n "Intent_Agent|Condition_Parser_Agent|Polymorphic_Retriever_Agent|Output_Validator_Agent" docs/02_service_flow docs/05_agent_spec`로 노드명 충돌을 확인한다.

**Dependencies:** Task 4, Task 6

**Files likely touched:**
- `docs/02_service_flow/02_service_flow.md`
- `docs/05_agent_spec/agent_build_target.md`
- `docs/05_agent_spec/agent_harness_design.md`

**Estimated scope:** M

### Task 8: HTML 재생성 및 검증

**Description:** Markdown 변경을 기준으로 GitHub Pages HTML을 재생성하고 링크·구조를 검증한다.

**Acceptance criteria:**
- [x] `pages/05_agent_spec.html`이 최신 `05_agent_spec.md` 내용을 반영한다.
- [x] `index.html`의 문서 순서는 `00 → 01 → 02 → 03 → 04 → 05 Agent → 06 기술 → 07 API`를 유지한다.
- [x] 이전 번호 HTML 리다이렉트가 깨지지 않는다.

**Verification:**
- [x] `python scripts\generate_pages.py`
- [x] `python scripts\verify_pages_structure.py`
- [x] `git diff --check`

**Dependencies:** Task 1-7

**Files likely touched:**
- `pages/05_agent_spec.html`
- `index.html`
- `pages/*.html`

**Estimated scope:** S

## 리스크 및 대응

| 리스크 | 영향 | 대응 |
| --- | --- | --- |
| 보조 문서의 세부 설계를 대표 문서에 과도하게 중복 | 정본이 길어지고 유지보수가 어려워짐 | 대표 문서는 핵심 계약과 결정만 담고, 상세 근거는 보조 문서 링크로 유지 |
| API/DB/기술 명세와 Agent 출력 스키마 불일치 | 구현 시 요청·응답 또는 저장 계약 충돌 | Task 6에서 필드명 검색 검증을 고정 절차로 둠 |
| LangGraph 정본과 대표 문서 다이어그램 불일치 | 구현자가 다른 그래프를 기준으로 개발 | Task 3에서 노드명과 엣지명 충돌 검사를 수행 |
| 비용·인프라 내용이 Agent 문서와 기술 문서에 중복 | 문서 간 업데이트 누락 가능 | Agent 문서는 추론 정책, 기술 문서는 운영 경계 중심으로 분리 |
| 기존 미커밋 변경과 번호 재정렬 변경이 섞임 | 커밋 범위가 불명확해짐 | 최신화 작업 전 `git status --short`를 확인하고 Agent 관련 변경만 별도 커밋 후보로 분리 |

## 완료 기준

- [x] 대표 문서 `05_agent_spec.md`가 최신 Agent 구조, 입출력, 상태, 파이프라인, 품질 기준을 설명한다.
- [x] 보조 문서와 정본 사이의 노드명, 필드명, 책임 경계가 충돌하지 않는다.
- [x] 서비스 흐름, 데이터베이스, 기술 명세, API 명세가 Agent 변경 영향만큼 동기화된다.
- [x] HTML 생성물과 허브가 최신 Markdown을 반영한다.
- [x] 검증 명령 3종이 통과한다.
