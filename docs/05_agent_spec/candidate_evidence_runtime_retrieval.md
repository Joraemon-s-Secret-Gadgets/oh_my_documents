# Candidate Evidence Runtime Tool Overview

> 문서 버전: v0.3
> 문서 상태: Draft / 실행 도구 개요
> 작성일: 2026-06-13
> 기준 문서: `candidate_evidence_agent.md`, `05_agent_spec.md`

## 1. 문서 목적

본 문서는 `candidate_evidence_agent.md` 정본의 실행 세부를 도구 단위로 분리하기 위한 상위 안내 문서다.

이전 v0.1에서는 S3 Vector 검색, DynamoDB detail 조회, scoring, resource metric을 한 문서에 함께 설명했다. v0.2부터는 Candidate Evidence 런타임의 책임을 다음 두 Tool 문서로 나눈다.

| Tool 문서 | 핵심 책임 |
| --- | --- |
| [destination_search_tool.md](./destination_search_tool.md) | S3 Vector 검색, 도시 AND gate, DynamoDB primary detail rehydrate |
| [scoring_tool.md](./scoring_tool.md) | 장소 점수, 도시 점수, score breakdown 계산 |

정본과 세부 문서가 충돌할 경우 `candidate_evidence_agent.md`를 우선한다.

## 2. 전체 실행 흐름

현행 Candidate Evidence 검증 흐름은 다음 순서로 실행된다.

```text
평가 testset
→ cleaned_raw_query / soft_preference_query 추출
→ query embedding cache에서 query vector 조회
→ DestinationSearchTool.search_candidates()
→ S3 Vector query_vectors()
→ place_id 기준 raw/soft 후보 병합
→ DestinationSearchTool.prune_cities()
→ ScoringTool.score_place()
→ ScoringTool.score_city()
→ 후보 수 sufficiency fallback
→ select_primary_with_theme_quotas()
→ DestinationSearchTool.rehydrate_places(primary)
→ Candidate Evidence Package 형태 결과 반환
```

핵심 분리:

| 단계 | 담당 |
| --- | --- |
| query embedding cache 조회 | Embedding helper / 실행 orchestration |
| S3 Vector 검색 | Destination Search Tool |
| 도시별 AND gate | Destination Search Tool |
| place/city scoring | Scoring Tool |
| primary quota와 title dedup | Candidate selection helper |
| primary detail rehydrate | Destination Search Tool |
| 최종 package 구성 | Candidate Evidence runtime orchestration |

## 3. 구성 책임

| 구성 요소 | 역할 |
| --- | --- |
| Embedding helper | query vector 준비와 cache 조회 |
| Destination Search Tool | Candidate Evidence 관점의 검색, filter, 상세 조회 facade |
| Scoring Tool | AWS 호출 없는 deterministic place/city scoring engine |
| Candidate selection helper | score 이후 primary 후보의 title dedup, theme quota, soft max relaxation |
| Evaluation orchestration | Baseline/Ours 전략 실행, 후보 병합, fallback, metric 산정 |
| Raw output generator | 테스트 케이스별 raw output 생성 |
| Evaluation report | Baseline/Ours 비교 평가 결과 요약 |

## 4. Tool 경계 요약

| 구분 | Destination Search Tool | Scoring Tool |
| --- | --- | --- |
| AWS 호출 | S3 Vector, DynamoDB | 없음 |
| 입력 | query vector, theme, city anchor, 후보 list | 검색된 후보, active themes, 위치/혼잡도 신호 |
| 출력 | candidate list, survived city groups, hydrated primary details | place score, city score, score breakdown |
| 다루는 정보 | vector key, distance, metadata, DynamoDB details | distance, soft distance, metadata completeness, theme coverage |
| 하지 않는 일 | 점수 계산, primary quota 선택, 일정 생성 | 검색, detail 조회, quota 선택, 일정 생성 |

## 5. Baseline과 Ours에서의 사용

| 전략 | Destination Search Tool 사용 | Scoring Tool 사용 |
| --- | --- | --- |
| Baseline | raw query를 active theme별 S3 Vector 검색, AND gate, primary detail rehydrate | 다요소 score는 사용하지 않고 평균 similarity 중심 ranking |
| Ours | raw + soft query를 active theme별 S3 Vector 검색, AND gate, primary detail rehydrate | `score_place`, `score_city`로 장소/도시 다요소 점수 계산 |

공통으로 유지되는 통제 조건:

1. active theme별 검색을 수행한다.
2. 같은 `place_id` 후보는 병합한다.
3. required theme AND gate를 적용한다.
4. 후보 수 sufficiency fallback을 수행한다.
5. 최종 primary 후보만 DynamoDB detail을 rehydrate한다.

Ours에 추가되는 요소:

1. soft preference query channel
2. place score
3. city score breakdown
4. visitor congestion signal
5. primary theme quota

## 6. Resource Metric 위치

평가 리포트와 raw output은 다음 metric을 기록한다.

| metric | 주로 관련된 Tool |
| --- | --- |
| `s3_query_count` | Destination Search Tool |
| `retrieved_candidates` | Destination Search Tool |
| `unique_candidates` | 후보 병합 orchestration |
| `surviving_cities` | Destination Search Tool |
| `selected_city_candidates` | fallback 이후 선택 도시 후보 수 |
| `ddb_get_item_count` | Destination Search Tool 및 방문자 통계 조회 |
| `score_breakdown` | Scoring Tool |
| latency / peak RSS | 전체 strategy 실행 |

## 7. 검증 산출물 해석

평가 하네스는 Baseline과 Ours를 같은 testset·동일 후보 예산·동일 fallback 조건에서 실행하고 다음 산출물을 만든다. 문서 정본에서는 특정 저장 경로나 실행 명령을 고정하지 않는다.

| 산출물 유형 | 설명 |
| --- | --- |
| Baseline raw output | raw similarity 중심 전략의 케이스별 원본 결과 |
| Ours raw output | soft channel, scoring, quota가 적용된 케이스별 원본 결과 |
| Evaluation report | Baseline/Ours 비교 평가 리포트 |

## 8. Change History

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.3 | 2026-06-13 | llm | 외부 파일 경로와 실행 명령 직접 참조를 제거하고 tool 책임 계약 중심으로 정리 |
| v0.2 | 2026-06-13 | llm | runtime retrieval 세부를 Destination Search Tool과 Scoring Tool 문서로 분리하고 본 문서는 도구 개요로 축소 |
| v0.1 | 2026-06-13 | llm | S3 Vector runtime search, DynamoDB primary-only detail rehydration, 평가 metric을 Candidate Evidence 정본 부록으로 분리 |
