# Destination Search Tool 실행 명세

> 문서 버전: v0.7
> 문서 상태: Draft / Destination Search Tool 세부
> 작성일: 2026-06-13
> 기준 문서: `candidate_evidence_agent.md`, `candidate_evidence_runtime_retrieval.md`, `dynamo_lookup_tool.md`

## 1. 문서 목적

본 문서는 S3 Vector attraction 후보 검색을 담당하는 `DestinationSearchTool`의 실행 세부를 정리한다.

`DestinationSearchTool`은 이제 S3 Vector 검색으로 책임을 한정한다. DynamoDB 기반 festival seed 조회와 최종 item detail enrichment는 [dynamo_lookup_tool.md](./dynamo_lookup_tool.md)의 `DynamoLookupTool`이 담당한다.

`DestinationSearchTool`의 책임은 세 가지다.

1. S3 Vector index에서 theme/city 조건에 맞는 관광지 후보를 검색한다.
2. S3 Vector 검색 결과를 Candidate Evidence가 사용할 `AttractionCandidate` 형태로 정규화한다.
3. 검색 후보를 도시별로 묶고 searchable place theme AND gate를 적용한다.

이 Tool은 DynamoDB 조회, 점수 계산, quota selection, 일정 생성, 추천 이유 생성을 수행하지 않는다.

## 2. 구성 책임

| 구성 요소 | 역할 |
| --- | --- |
| Destination Search Tool | S3 Vector attraction 검색·정규화·city gate facade |
| Vector query helper | S3 Vector `query_vectors` 호출과 응답 정규화 |
| Execution orchestration | raw/soft channel 호출 순서와 후보 병합 관리 |

## 3. 책임 범위

| 구분 | 내용 |
| --- | --- |
| 책임 | S3 Vector 검색, attraction 후보 정규화, 도시별 AND gate |
| 입력 | query vector, optional city anchor, active theme, top_k, 후보 list |
| 출력 | 정규화된 attraction candidate list, survived city groups |
| 사용 AWS | S3 Vectors |
| 사용하지 않음 | DynamoDB, LLM, Bedrock generation, scoring formula, itinerary generation |

담당하지 않는 범위:

| 비범위 | 담당 |
| --- | --- |
| query embedding 생성/조회 | Embedding helper / 실행 orchestration |
| DynamoDB festival candidate 조회 | `DynamoLookupTool` |
| DynamoDB detail enrichment | `DynamoLookupTool` |
| raw/soft 후보 병합 | 실행 orchestration |
| place/city scoring | `ScoringTool` |
| primary quota 선택 | Candidate selection helper |
| 축제 목표 연도 개최 여부 검증 | `Festival_Verifier_Agent` |
| 최종 일정 생성 | `Planner_Agent` |

## 4. AWS 리소스 기본값

현행 로컬 평가 기본값:

| 항목 | 값 | 관리 위치 |
| --- | --- | --- |
| vector bucket | `lovv-vector-dev` | Tool 초기화 설정 |
| vector index | `kr-tour-domain-v1` | Tool 초기화 설정 |
| 기본 region | `us-east-1` | 실행 환경 설정 |
| 기본 profile | `skn26_final` | 실행 환경 설정 |

주의:

1. 이 값들은 현재 로컬 평가 기본값이다.
2. 제품 배포 환경의 고정 계약은 아니다.
3. profile, credential, `.env` 값은 문서에 확정값으로 추가하지 않는다.

## 5. 초기화 계약

`DestinationSearchTool`은 생성 시 S3 Vector repository/client와 검색 budget을 받는다.

```python
DestinationSearchTool(
    s3_vectors=s3_vector_repository,
    search_budget=search_budget,
)
```

실행 orchestration은 시작 시 다음 흐름으로 tool을 만든다.

```text
get_s3vectors_client(profile, region)
→ S3VectorRepository(...)
→ DestinationSearchTool(...)
```

## 6. `search_candidates`

### 6.1 역할

`search_candidates(query_vector, city_id=None, theme=None, top_k=None)`는 S3 Vector index에서 관광지 후보를 검색한다.

입력:

| 인자 | 설명 |
| --- | --- |
| `query_vector` | raw query 또는 soft query embedding |
| `city_id` | anchor city가 있거나 seed city별 검색을 수행할 때의 도시 제한 |
| `theme` | 단일 searchable place theme |
| `top_k` | 호출 단위 후보 수. 없으면 runtime config의 `per_theme_attraction_top_k` 사용 |

출력은 정규화된 `AttractionCandidate` 목록이다.

### 6.2 S3 Vector filter 계약

현재 검증 구현은 S3 Vector `query_vectors` 호출에서 metadata filter를 함께 사용한다.

| 조건 | filter |
| --- | --- |
| 기본 attraction 검색 | `entity_type == attraction` |
| anchor city 또는 seed city 제한 | `city_id == destinationId 또는 seed/anchor city_id` |
| active theme 지정 | `theme_tags == theme` |
| `미식·노포` theme | 장소 검색 filter를 만들지 않고 Planner의 `foodSearch` 링크 요구로 전달 |
| 축제 관련 label | 장소 검색 filter를 만들지 않음. 축제 후보는 `DynamoLookupTool`이 조회 |

복수 조건은 `$and`로 결합한다.

## 7. 후보 정규화

S3 Vector raw result는 최소 아래 정보를 포함해야 한다.

| 필드 | 사용 |
| --- | --- |
| `key` | chunk 식별자. `{entity_type}#{source_id}#{chunk_no}` 형태 권장 |
| `distance` | query와의 vector distance |
| `metadata.entity_type` | 현재는 `attraction`만 허용 |
| `metadata.city_id` | 도시 grouping과 anchor/seed 제한 |
| `metadata.city_name_ko` | 감사와 출력 보조 |
| `metadata.theme_tags` | 검색 filter, AND gate, quota |
| `metadata.title` | title dedup과 Planner 후보명 |
| `metadata.latitude`, `metadata.longitude` | 동선/거리 보조 |
| `metadata.ddb_pk`, `metadata.ddb_sk` | Planner 최종 배치 후 `DynamoLookupTool` detail enrichment에 사용 |

`DestinationSearchTool`은 S3 Vector `key`에서 chunk 번호를 제거해 안정적인 `place_id`를 만든다.

```text
attraction#67890#2 → attraction#67890
```

metadata에 `place_id`가 있으면 이 값을 우선한다.

## 8. Searchable place theme AND gate

`prune_cities(candidates, searchable_place_themes, allowed_city_ids=None)`는 도시 후보 pool의 `theme_tags`를 모아 searchable place theme가 모두 존재하는지 확인한다.

중요한 의미:

1. 이 gate는 "도시 후보 pool에 모든 검색 가능 관광 테마가 존재하는가"를 본다.
2. 최종 primary 목록이 모든 테마를 균형 있게 포함하는지는 보장하지 않는다.
3. 최종 primary 테마 균형은 Candidate selection helper의 quota 단계가 담당한다.
4. `includeFestivals=true`의 축제 seed 조건은 이 gate와 별개로 `DynamoLookupTool` 결과의 `allowed_city_ids`에 반영되어야 한다.

## 9. Baseline과 Ours에서의 호출 방식

### 9.1 Baseline

Baseline 흐름:

1. raw query embedding을 cache에서 읽는다.
2. `includeFestivals=true`이면 먼저 `DynamoLookupTool.search_festival_city_seeds(...)`로 seed city pool 또는 anchor city festival candidates를 만든다.
3. searchable place theme별로 `DestinationSearchTool.search_candidates(..., top_k=...)`를 호출한다.
4. 같은 `place_id`를 병합한다.
5. `DestinationSearchTool.prune_cities(..., allowed_city_ids=seed_city_ids 또는 [anchor_city_id])`로 city pool 제한과 searchable place theme AND gate를 적용한다.
6. 평균 similarity 기반으로 도시를 고른다.
7. Candidate Evidence Package를 반환한다. 이 단계에서는 DynamoDB detail enrichment를 호출하지 않는다.

Baseline은 soft channel을 호출하지 않는다.

### 9.2 Ours

Ours 흐름:

1. raw query embedding을 cache에서 읽는다.
2. soft query가 있으면 soft query embedding도 cache에서 읽는다.
3. `includeFestivals=true`이면 먼저 `DynamoLookupTool.search_festival_city_seeds(...)`로 seed city pool 또는 anchor city festival candidates를 만든다.
4. raw channel을 searchable place theme별로 `DestinationSearchTool.search_candidates` 호출한다.
5. soft channel도 searchable place theme별로 `DestinationSearchTool.search_candidates` 호출한다.
6. 같은 `place_id`를 병합하되 raw distance와 soft distance를 모두 보존한다.
7. `DestinationSearchTool.prune_cities(..., allowed_city_ids=seed_city_ids 또는 [anchor_city_id])`로 city pool 제한과 searchable place theme AND gate를 적용한다.
8. scoring, fallback, quota 이후 Candidate Evidence Package를 반환한다. 이 단계에서는 DynamoDB detail enrichment를 호출하지 않는다.

## 10. Resource metric

Destination Search Tool과 직접 관련되는 metric:

| metric | 의미 |
| --- | --- |
| `s3_query_count` | S3 Vector `query_vectors` 호출 수 |
| `retrieved_candidates` | S3 Vector에서 반환된 전체 후보 수 |
| `surviving_cities` | `prune_cities`를 통과한 도시 수 |

DynamoDB 관련 metric은 `dynamo_lookup_tool.md`를 따른다.

## 11. Failure와 fallback

| 상황 | 현재 처리 |
| --- | --- |
| S3 Vector 호출 실패 | strategy result를 `error`로 격리 |
| 후보 없음 | `no_candidate` |
| AND gate 생존 도시 없음 | `no_candidate` |
| 검색 불가 theme | S3 Vector 호출 없이 외부 링크/CTA 정책으로 전달 |

Destination Search Tool은 후보 부족을 직접 해결하지 않는다. 후보 수 sufficiency fallback은 city ranking 이후 공통 후보 충분성 단계에서 수행된다.

## 12. Tool 경계

Destination Search Tool이 하지 않는 일:

| 하지 않는 일 | 담당 |
| --- | --- |
| query 문장 해석 | Intent Agent |
| query embedding cache miss 처리 정책 | Embedding helper / 실행 orchestration |
| DynamoDB festival seed 조회 | `DynamoLookupTool` |
| DynamoDB detail enrichment | `DynamoLookupTool` |
| raw/soft 후보 병합 | 실행 orchestration |
| place/city score 계산 | `ScoringTool` |
| primary quota 선택 | Candidate selection helper |
| festival seed/lookup 실패 시 사용자 질문 문구 생성 | Candidate Evidence runtime orchestration |
| 축제 event date의 목표 연도 검증 | Festival Verifier Agent |
| 추천 이유 확정 | Planner Agent |

## 13. Change History

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.7 | 2026-06-14 | llm | `DestinationSearchTool` 책임을 S3 Vector attraction 검색·정규화·city gate로 한정하고 DynamoDB 조회는 `DynamoLookupTool`로 분리 |
| v0.6 | 2026-06-14 | llm | DynamoDB detail 조회 위치를 Candidate Evidence primary detail 조회에서 Planner 최종 배치 item detail enrichment로 변경하고 `enrich_final_places` 계약을 명시 |
| v0.5 | 2026-06-13 | llm | 현재 단계에서 `restaurant` 후보/테이블 조회를 제거하고, `미식·노포`는 선택 도시 기반 외부 맛집 검색 링크로 처리하도록 검색 필터 계약 정리 |
| v0.4 | 2026-06-13 | llm | `includeFestivals=true`를 city discovery seed와 anchored fixed-city festival lookup으로 분기하고 `no_festival_in_anchor_city` failure 추가 |
| v0.3 | 2026-06-13 | llm | `includeFestivals=true` 흐름의 DynamoDB festival city seed helper, seed city pool 제한, 관련 failure/metric 계약 추가 |
| v0.2 | 2026-06-13 | llm | 외부 파일 경로 직접 참조를 제거하고 Destination Search Tool의 입력·출력·실행 규칙 중심으로 정리 |
| v0.1 | 2026-06-13 | llm | S3 Vector 검색, 도시 AND gate, DynamoDB detail 조회 실행 세부 분리 |
