# Candidate Evidence Runtime Tool Overview

> 문서 성격: 보조 Markdown
> 대표 문서: `05_agent_spec.md`

> 문서 버전: v0.10
> 문서 상태: Draft / 실행 도구 개요
> 작성일: 2026-06-13
> 기준 문서: `candidate_evidence_agent.md`, `05_agent_spec.md`

> **[PRD 반영 v0.1 — 대화형 빌더]** 반경 빌더에서는 코어를 **radius 게이트**로 재사용하고, **식당·카페는
> 지도 API로 반경 표시**해 직접 선택지로 제공한다(아래 §5 통제조건 9 갱신). 상세: `../98_prd/interactive_builder_prd.md`.

## 1. 문서 목적

본 문서는 `candidate_evidence_agent.md` 정본의 실행 세부를 도구 단위로 분리하기 위한 상위 안내 문서다.

이전 v0.1에서는 S3 Vector 검색, DynamoDB detail 조회, scoring, resource metric을 한 문서에 함께 설명했다. v0.9부터는 Candidate Evidence 런타임의 책임을 다음 세 Tool 문서로 나눈다.

| Tool 문서 | 핵심 책임 |
| --- | --- |
| [destination_search_tool.md](./destination_search_tool.md) | S3 Vector attraction 검색, 후보 정규화, 도시 AND gate |
| [dynamo_lookup_tool.md](./dynamo_lookup_tool.md) | DynamoDB festival seed/fixed-city lookup, Planner 최종 배치 item detail enrichment |
| [scoring_tool.md](./scoring_tool.md) | 장소 점수, 도시 점수, score breakdown 계산 |

정본과 세부 문서가 충돌할 경우 `candidate_evidence_agent.md`를 우선한다.

## 2. 전체 실행 흐름

Candidate Evidence runtime은 Intent Agent가 생성한 `candidate_evidence_input`을 직접 입력으로 받는 시점에서 시작한다. API 요청 해석, 자연어 파싱, 온보딩 병합, 추가 질문 판단은 Intent Agent 책임이며, 본 문서는 그 이후 Candidate Evidence 내부 실행만 다룬다.

현행 Candidate Evidence runtime 흐름은 다음 순서로 실행된다.

```text
Intent_Agent.candidate_evidence_input
→ Candidate Evidence runtime orchestration이 입력 schema와 clarification 필요 여부 확인
→ cleaned_raw_query / soft_preference_query 수신
→ query embedding cache 조회 또는 Embedding helper로 query vector 준비
→ includeFestivals=true이면 DynamoLookupTool.search_festival_city_seeds(city_id optional)
→ destinationId 유무에 따라 festival seed city pool 또는 anchor city festival candidates 확정
→ 축제 조건 clarification failure가 있으면 구조화 실패 반환
→ 검색 가능한 관광 테마별 DestinationSearchTool.search_candidates()
→ S3 Vector query_vectors()
→ place_id 기준 raw/soft 후보 병합
→ DestinationSearchTool.prune_cities(seed city pool 또는 anchor city pool optional)
→ ScoringTool.score_place()
→ ScoringTool.score_city()
→ 후보 수 sufficiency fallback
→ select_primary_with_theme_quotas()
→ Candidate Evidence Package를 UnifiedAgentState.candidate_evidence_package에 저장
```

핵심 분리:

| 단계 | 담당 |
| --- | --- |
| query embedding cache 조회 | Embedding helper / 실행 orchestration |
| festival candidate 조회 | DynamoLookupTool |
| S3 Vector 검색 | Destination Search Tool |
| 도시별 AND gate | Destination Search Tool |
| place/city scoring | Scoring Tool |
| primary quota와 title dedup | Candidate selection helper |
| 최종 package 구성 | Candidate Evidence runtime orchestration |
| 최종 배치 item detail enrichment | Planner 단계에서 DynamoLookupTool |

## 3. 구성 책임

| 구성 요소 | 역할 |
| --- | --- |
| Embedding helper | query vector 준비와 cache 조회 |
| Destination Search Tool | Candidate Evidence 관점의 S3 Vector attraction 검색, filter, city gate |
| DynamoLookupTool | DynamoDB festival seed/fixed-city lookup, Planner 최종 배치 item detail enrichment |
| Scoring Tool | AWS 호출 없는 deterministic place/city scoring engine |
| Candidate selection helper | score 이후 primary 후보의 title dedup, theme quota, soft max relaxation |
| Runtime orchestration | AgentCore/LangGraph 실행에서 입력 검증, 후보 병합, fallback, metric 산정, state 저장 |

## 4. Tool 경계 요약

| 구분 | Destination Search Tool | DynamoLookupTool | Scoring Tool |
| --- | --- | --- | --- |
| AWS 호출 | S3 Vector | DynamoDB | 없음 |
| 입력 | query vector, searchable place theme, city anchor, allowed city pool | country, travelMonth, theme pool, optional city anchor, final placed item keys | 검색된 관광지 후보, searchable place themes, 위치/혼잡도 신호 |
| 출력 | attraction candidate list, survived city groups | festival seed city pool 또는 anchor city festival candidates, final item details/warnings | place score, city score, score breakdown |
| 다루는 정보 | vector key, distance, metadata | festival month/theme/city metadata, DynamoDB details | distance, soft distance, metadata completeness, theme coverage |
| 하지 않는 일 | DynamoDB 조회, 점수 계산, primary quota 선택, 일정 생성 | S3 Vector 검색, 점수 계산, quota 선택, 일정 생성 | 검색, detail 조회, quota 선택, 일정 생성 |

## 5. Runtime 통제 조건

`includeFestivals=true`이면 Festival Candidate Channel을 먼저 실행한다. 축제 자체는 place/city scoring 입력으로 넣지 않는다.

단, `destinationId` 유무에 따라 효과가 다르다.

| 조건 | Runtime 효과 |
| --- | --- |
| `destinationId == null` | festival city seed pool을 만들고 이후 장소 후보를 seed city 안으로 제한한다. |
| `destinationId != null` | anchor city 내부 festival candidates만 조회한다. 장소 검색은 anchor city로 제한하고, 축제 후보가 도시를 바꾸지 않는다. |

Candidate Evidence runtime은 다음 통제 조건을 유지한다.

1. `includeFestivals=true`이면 non-festival travel theme pool과 `travelMonth`로 DynamoDB festival candidates를 먼저 조회한다.
2. `destinationId == null`에서 festival seed가 생성되면 이후 장소 후보는 seed city pool 안에서만 유지한다.
3. `destinationId != null`에서는 anchor city 내부 축제 후보만 유지하고 장소 후보도 anchor city로 제한한다.
4. `미식·노포`처럼 외부 링크로 처리하는 테마를 제외하고, 검색 가능한 관광 테마별 검색을 수행한다.
5. 같은 `place_id` 후보는 병합한다.
6. searchable place theme AND gate를 적용한다.
7. 후보 수 sufficiency fallback을 수행한다.
8. Candidate Evidence에서는 DynamoDB detail enrichment를 수행하지 않는다. Planner가 최종 일정에 배치한 attraction item만 이후 `DynamoLookupTool`로 보강한다.
9. `restaurant` 후보/테이블은 조회하지 않고, 미식 요청은 선택 도시 기준 `foodSearch` 링크 생성 요구로 Planner에 전달한다.
   - **(빌더 전환 반영, PRD v0.1)** 대화형 반경 빌더에서는 식당·카페를 **지도 API로 반경 표시**해 직접 선택지로 제공한다(외부 링크 대체). 큐레이션 관광지(DB)는 통찰 이유 포함, 지도 API 보충 후보는 통찰 이유를 생성하지 않는다(2티어 구분).

## 6. Resource Metric 위치

런타임 trace는 다음 metric을 기록할 수 있다. 사용자 API 응답에는 직접 노출하지 않는다.

| metric | 주로 관련된 Tool |
| --- | --- |
| `festival_seed_query_count` | DynamoLookupTool |
| `festival_candidate_count` | DynamoLookupTool |
| `festival_seed_city_count` | DynamoLookupTool |
| `s3_query_count` | Destination Search Tool |
| `retrieved_candidates` | Destination Search Tool |
| `unique_candidates` | 후보 병합 orchestration |
| `surviving_cities` | Destination Search Tool |
| `selected_city_candidates` | fallback 이후 선택 도시 후보 수 |
| `ddb_get_item_count` | DynamoLookupTool 및 방문자 통계 조회 |
| `score_breakdown` | Scoring Tool |
| latency / peak RSS | 전체 runtime 실행 |

## 7. Change History

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.9 | 2026-06-14 | llm | `DestinationSearchTool`을 S3 Vector attraction 검색으로 한정하고 DynamoDB festival seed/detail 조회를 `DynamoLookupTool`로 분리 |
| v0.8 | 2026-06-13 | llm | `restaurant` 조회를 runtime 범위에서 제거하고, 미식 테마는 검색 가능한 관광 테마가 아닌 선택 도시 기반 외부 맛집 링크 요구로 분리 |
| v0.7 | 2026-06-13 | llm | `includeFestivals=true`를 city discovery seed와 anchored fixed-city festival lookup으로 분기하도록 runtime 흐름 정리 |
| v0.6 | 2026-06-13 | llm | Candidate Evidence runtime의 시작점을 `Intent_Agent.candidate_evidence_input`으로 고정하고 비런타임 설명을 제거 |
| v0.5 | 2026-06-13 | llm | 전체 실행 흐름의 시작점을 LangGraph/AgentCore 사용자 턴과 Intent handoff로 정정 |
| v0.4 | 2026-06-13 | llm | 축제 포함 요청에서 DynamoDB festival city seed를 S3 Vector 장소 검색보다 먼저 수행하는 runtime branch와 resource metric을 추가 |
| v0.3 | 2026-06-13 | llm | 외부 파일 경로와 실행 명령 직접 참조를 제거하고 tool 책임 계약 중심으로 정리 |
| v0.2 | 2026-06-13 | llm | runtime retrieval 세부를 Destination Search Tool과 Scoring Tool 문서로 분리하고 본 문서는 도구 개요로 축소 |
| v0.1 | 2026-06-13 | llm | S3 Vector runtime search, 초기 DynamoDB detail 조회 논의, resource metric을 Candidate Evidence 정본 부록으로 분리 |
