# Agent Spec Update Plan

> 작성일: 2026-06-08
> 대상 문서: `docs/05_agent_spec/05_agent_spec.md`
> 관련 보조 문서: `agent_build_target.md`, `agent_harness_design.md`, `agent_update.md`, `langgraph_flow.md`, `recommendation_flow.md`, `user_raw_query_flow.md`, `theme_analysis_report.md`
> 산출물: `pages/05_agent_spec.html`

## 1. 목표

`docs/05_agent_spec` 문서군을 최신 서비스/데이터/API 설계와 일치하도록 업데이트한다. 대표 문서인 `05_agent_spec.md`는 공개 정본으로 유지하고, 상세 설계는 보조 문서에 남기되 대표 문서와 충돌하지 않게 동기화한다.

## 2. 기준 문서

- `docs/01_requirements/01_requirements.md`
- `docs/02_service_flow/02_service_flow.md`
- `docs/03_data_collect_plan/03_data_collect_plan.md`
- `docs/04_database_design/04_database_design.md`
- `docs/06_technical_spec/06_technical_spec.md`
- `docs/07_api_spec/07_api_spec.md`
- `docs/05_agent_spec/AGENT.md`

## 3. 업데이트 범위

### 3.1 대표 문서 정합성

- `05_agent_spec.md`의 문서 버전, 상태, 기준 문서 버전을 최신 문서군과 맞춘다.
- Agent 목표, 입력, 출력, 파이프라인, 검증 기준이 요구사항/서비스 흐름/API 계약과 충돌하지 않는지 확인한다.
- `travelYear`, `festivalDateVerifications`, `target_region`, `fulfilled_matrix`, `selected_destination` 등 핵심 상태 필드가 보조 문서와 같은 의미로 쓰이는지 점검한다.

### 3.2 LangGraph 흐름 동기화

- `langgraph_flow.md`의 노드, 상태 전이, 폴백 루프를 대표 문서의 파이프라인과 맞춘다.
- `Intent_Agent`, `Supervisor_Router`, `Polymorphic_Retriever_Agent`, `Festival_Verifier_Agent`, `Ranker_Agent`, `Itinerary_Planner_Agent`, `Explanation_Writer_Agent`, `Output_Validator_Agent`의 책임 경계를 재확인한다.
- Mermaid 다이어그램이 있으면 노드명, 라벨, 흐름이 최신 본문과 같은지 확인한다.

### 3.3 AgentCore 실행/하네스 설계 반영

- `agent_harness_design.md`와 `agent_build_target.md`에서 Runtime, Memory, Gateway, Policy, Observability의 책임을 최신 기술 명세와 맞춘다.
- MySQL/DynamoDB/VectorDB 등 저장소 계약이 DB 설계 문서와 어긋나지 않는지 확인한다.
- Agent 실행 상태와 비동기 작업 상태가 API 명세의 요청/응답 흐름과 연결되는지 점검한다.

### 3.4 추천 흐름과 사용자 질의 흐름 정리

- `recommendation_flow.md`와 `user_raw_query_flow.md`의 단계가 대표 문서의 입력/출력 계약과 맞는지 확인한다.
- 자연어 질의, 온보딩 선호, 지도 진입, 피드백 이력이 서로 다른 우선순위로 반영되는지 명확히 적는다.
- 국가 혼합 금지, 단일 목적지 추천, 검증 실패 시 폴백 조건을 반복적으로 확인한다.

### 3.5 테마/스코어링 근거 정리

- `theme_analysis_report.md`의 테마 기준이 데이터 수집 계획과 DB 테마 필드에 맞는지 확인한다.
- 월별 기상 경향 데이터는 추천 스코어링 근거로, 실시간 WeatherAPI는 표시용/보조 판단으로 구분한다.
- 설명 생성 단계에서 사용자에게 노출 가능한 근거와 내부 계산 근거를 구분한다.

## 4. 작업 순서

### Task 1: 현재 문서 차이 점검

**Description:** 대표 문서와 보조 문서의 핵심 용어, 상태 필드, Agent/Skill 목록, 입력/출력 계약 차이를 표로 정리한다.

**Acceptance criteria:**
- [ ] 대표 문서와 보조 문서 간 충돌 항목이 목록화된다.
- [ ] API/DB/기술 명세와 연결되는 영향 항목이 표시된다.
- [ ] 수정 대상과 읽기 전용 참조 대상이 분리된다.

**Verification:**
- [ ] `rg -n "travelYear|festivalDateVerifications|fulfilled_matrix|target_region|selected_destination" docs/05_agent_spec`
- [ ] `rg -n "AgentCore|Runtime|Gateway|Memory|Policy|Observability" docs/05_agent_spec`

**Dependencies:** None

**Files likely touched:**
- `docs/05_agent_spec/05_agent_spec.md`
- `docs/05_agent_spec/*.md`

**Estimated scope:** Medium

### Task 2: 대표 문서 업데이트

**Description:** `05_agent_spec.md`를 공개 정본으로 정리하고, 보조 문서에 있는 최신 결정 중 대표 문서에 필요한 계약만 반영한다.

**Acceptance criteria:**
- [ ] 문서 메타데이터가 최신 기준 문서 버전과 맞는다.
- [ ] Agent 입력/출력 표가 API 명세와 같은 필드 의미를 갖는다.
- [ ] 파이프라인 설명이 보조 문서의 상세 흐름과 충돌하지 않는다.

**Verification:**
- [ ] `rg -n "문서 버전|기준 문서|Agent 입력|Agent 출력|파이프라인" docs/05_agent_spec/05_agent_spec.md`
- [ ] 대표 문서에서 미정/임시 표현이 남지 않는지 확인한다.

**Dependencies:** Task 1

**Files likely touched:**
- `docs/05_agent_spec/05_agent_spec.md`

**Estimated scope:** Small

### Task 3: 상세 흐름 문서 동기화

**Description:** `langgraph_flow.md`, `recommendation_flow.md`, `user_raw_query_flow.md`가 대표 문서와 같은 상태 전이 및 폴백 정책을 설명하도록 정리한다.

**Acceptance criteria:**
- [ ] LangGraph 노드 책임과 대표 문서 Agent 목록이 일치한다.
- [ ] 추천 흐름의 후보 검색, 랭킹, 일정 생성, 검증 단계가 대표 문서와 같은 순서로 설명된다.
- [ ] 사용자 자연어 질의 처리 흐름이 입력 계약과 연결된다.

**Verification:**
- [ ] `rg -n "Intent_Agent|Supervisor_Router|Polymorphic_Retriever_Agent|Festival_Verifier_Agent|Output_Validator_Agent" docs/05_agent_spec`
- [ ] Mermaid 블록이 있으면 HTML 생성 후 렌더링 깨짐 여부를 확인한다.

**Dependencies:** Task 2

**Files likely touched:**
- `docs/05_agent_spec/langgraph_flow.md`
- `docs/05_agent_spec/recommendation_flow.md`
- `docs/05_agent_spec/user_raw_query_flow.md`

**Estimated scope:** Medium

### Task 4: 실행/저장소/관측성 계약 점검

**Description:** AgentCore 실행 설계와 저장소 사용 방식을 기술 명세 및 DB 설계 문서와 맞춘다.

**Acceptance criteria:**
- [ ] Runtime, Memory, Gateway, Policy, Observability 책임이 중복 없이 정의된다.
- [ ] 실행 상태와 비동기 작업 상태 저장 위치가 DB 설계와 일치한다.
- [ ] API 명세의 추천 요청/결과 조회 흐름과 Agent 실행 흐름이 맞는다.

**Verification:**
- [ ] `rg -n "lovv_agent_runs|lovv_async_jobs|DynamoDB|MySQL|VectorDB" docs/04_database_design docs/05_agent_spec docs/06_technical_spec`
- [ ] `rg -n "recommendation|itinerary|agent" docs/07_api_spec/07_api_spec.md`

**Dependencies:** Task 2

**Files likely touched:**
- `docs/05_agent_spec/agent_build_target.md`
- `docs/05_agent_spec/agent_harness_design.md`
- `docs/05_agent_spec/agent_update.md`

**Estimated scope:** Medium

### Task 5: 생성물 갱신 및 검증

**Description:** Markdown 원본 업데이트 후 HTML 생성물을 갱신하고 문서 사이트 구조를 검증한다.

**Acceptance criteria:**
- [ ] `pages/05_agent_spec.html`이 최신 Markdown을 반영한다.
- [ ] `index.html`의 문서 요약/상태가 필요 시 최신화된다.
- [ ] 이전/다음 문서 링크가 깨지지 않는다.

**Verification:**
- [ ] `python scripts/generate_pages.py`
- [ ] `python scripts/verify_pages_structure.py`
- [ ] `git diff --check`

**Dependencies:** Tasks 2-4

**Files likely touched:**
- `pages/05_agent_spec.html`
- `index.html`

**Estimated scope:** Small

## 5. 체크포인트

### Checkpoint A: 분석 완료

- [ ] 대표 문서와 보조 문서 충돌 목록이 정리됐다.
- [ ] API/DB/기술 명세 영향 범위가 확인됐다.
- [ ] 수정 우선순위가 확정됐다.

### Checkpoint B: 문서 업데이트 완료

- [ ] 대표 문서와 보조 문서가 같은 Agent/Skill/상태 필드 용어를 사용한다.
- [ ] 폴백, 금지 동작, 검증 기준이 대표 문서에 명확히 남아 있다.
- [ ] 상세 문서가 대표 문서의 결정을 확장하며, 별도 정책을 만들지 않는다.

### Checkpoint C: 산출물 검증 완료

- [ ] HTML 생성과 구조 검증이 통과한다.
- [ ] `git diff --check`가 통과한다.
- [ ] 변경분이 `docs(agent-spec)` 스코프로 커밋 가능한 상태다.

## 6. 리스크와 대응

| Risk | Impact | Mitigation |
| --- | --- | --- |
| 대표 문서와 보조 문서의 정본 경계가 흐려짐 | High | 대표 문서는 공개 계약, 보조 문서는 상세 설계로 역할을 고정한다. |
| API/DB 필드 의미 불일치 | High | 입력/출력/상태 필드를 API 및 DB 문서와 함께 `rg`로 교차 확인한다. |
| Mermaid 또는 HTML 생성 깨짐 | Medium | `generate_pages.py` 실행 후 `verify_pages_structure.py`로 검증한다. |
| 오래된 `docs/06_agent_spec` 기억과 현재 `docs/05_agent_spec` 구조 혼동 | Medium | 현재 `AGENT.md`의 최신 문서 순서를 기준으로 작업한다. |

## 7. Open Questions

- 이번 작업에서는 Agent 명세 문서 버전을 `v0.4`로 유지한다. 버전 상향은 추후 별도 작업에서 결정한다.
- 이번 작업에서는 PDF 산출물을 제외하고 Markdown 원본과 HTML 생성물까지만 갱신한다. PDF 최신화는 추후 별도 작업으로 진행한다.
- 이번 작업에서는 `agent_update.md`의 변경 이력성 내용을 대표 문서에 요약 반영하지 않는다. 해당 반영 여부는 추후 별도 작업에서 결정한다.
