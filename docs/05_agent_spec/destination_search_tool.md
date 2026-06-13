# Destination Search Tool 실행 명세

> 문서 버전: v0.5
> 문서 상태: Draft / Destination Search Tool 세부
> 작성일: 2026-06-13
> 기준 문서: `candidate_evidence_agent.md`, `candidate_evidence_runtime_retrieval.md`

## 1. 문서 목적

본 문서는 Candidate Evidence 후보 검색을 담당하는 `DestinationSearchTool`의 실행 세부를 정리한다.

`DestinationSearchTool`은 Candidate Evidence Agent 관점에서 다음 네 가지 작업을 하나의 Tool처럼 묶는다.

1. 축제 포함 요청이면 DynamoDB에서 월·테마 조건을 만족하는 festival candidates를 조회한다.
2. S3 Vector index에서 theme/city 조건에 맞는 관광지 후보를 검색한다.
3. 검색 후보를 도시별로 묶고 searchable place theme AND gate를 적용한다.
4. 최종 primary 후보에 대해서만 DynamoDB 상세 데이터를 지연 조회한다.

이 Tool은 점수를 계산하지 않는다. 장소/도시 점수 계산은 [scoring_tool.md](./scoring_tool.md)의 `ScoringTool`이 담당한다.

## 2. 구성 책임

| 구성 요소 | 역할 |
| --- | --- |
| Destination Search Tool | Candidate Evidence 관점의 검색·필터·상세조회 facade |
| Vector query helper | S3 Vector `query_vectors` 호출과 응답 정규화 |
| Detail rehydrate helper | DynamoDB `GetItem` 호출과 AttributeValue deserialize |
| Execution orchestration | Baseline/Ours에서 Tool 호출 순서와 fallback 흐름 관리 |

`DestinationSearchTool`은 저수준 vector/detail helper를 감싸 Candidate Evidence가 사용할 후보 형태로 정규화하는 facade다.

## 3. 책임 범위

| 구분 | 내용 |
| --- | --- |
| 책임 | DynamoDB festival candidate 조회, S3 Vector 검색, 후보 정규화, 도시별 AND gate, primary detail rehydrate |
| 입력 | query vector, optional city anchor, active theme, travelMonth, includeFestivals, top_k, 후보 list |
| 출력 | festival seed city pool 또는 anchor city festival candidates, 정규화된 candidate list, survived city groups, hydrated primary places |
| 사용 AWS | S3 Vectors, DynamoDB |
| 사용하지 않음 | LLM, Bedrock generation, scoring formula, itinerary generation |

담당하지 않는 범위:

| 비범위 | 담당 |
| --- | --- |
| query embedding 생성/조회 | Embedding helper / 실행 orchestration |
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
| DynamoDB table | `TourKoreaDomainData` | Tool 초기화 설정 |
| 기본 region | `us-east-1` | 실행 환경 설정 |
| 기본 profile | `skn26_final` | 실행 환경 설정 |

주의:

1. 이 값들은 현재 로컬 평가 기본값이다.
2. 제품 배포 환경의 고정 계약은 아니다.
3. profile, credential, `.env` 값은 문서에 확정값으로 추가하지 않는다.

## 5. 초기화 계약

`DestinationSearchTool`은 생성 시 AWS client와 리소스 이름을 받는다.

```python
DestinationSearchTool(
    s3vectors_client=s3_client,
    dynamodb_client=ddb_client,
    vector_bucket="lovv-vector-dev",
    index_name="kr-tour-domain-v1",
    table_name="TourKoreaDomainData"
)
```

실행 orchestration은 시작 시 다음 흐름으로 tool을 만든다.

```text
get_s3vectors_client(profile, region)
get_dynamodb_client(profile, region)
→ DestinationSearchTool(...)
```

## 6. `search_festival_city_seeds`

### 6.1 역할

`search_festival_city_seeds(country, travel_month, theme_pool, city_id=None, max_candidates=100)`는 `includeFestivals=true` 요청에서 장소 S3 Vector 검색 전에 실행되는 DynamoDB 조회 helper다.

이 helper의 목표는 축제를 scoring 대상으로 만들기 위한 것이 아니다.

`city_id`가 없으면 해당 월과 travel theme에 맞는 축제가 존재하는 **도시 pool**을 먼저 확정한다. `city_id`가 있으면 이미 고정된 도시 내부에서만 축제 후보를 조회해 Festival Verifier handoff 후보를 만든다.

입력:

| 인자 | 설명 |
| --- | --- |
| `country` | `KR`, `JP` 등 국가 제한 조건 |
| `travel_month` | 여행 월. `festival.month == travel_month` 조건에 사용 |
| `theme_pool` | API `themes`에서 온 non-festival travel theme label 목록 |
| `city_id` | anchor city가 있을 때의 도시 제한 조건. 없으면 전체 festival 후보에서 city seed 생성, 있으면 해당 도시 내부 축제 후보만 조회 |
| `max_candidates` | verifier handoff 전에 유지할 축제 후보 상한 |

`theme_pool`에는 `festival_event`나 `축제·이벤트`가 들어오면 안 된다. 실행 orchestration은 이 값이 비어 있으면 DynamoDB를 조회하지 않고 `no_required_theme_for_festival_seed`를 반환한다.

### 6.2 DynamoDB 논리 조건

조회는 물리 index 구현과 분리해 다음 논리 조건을 만족해야 한다.

```text
entity_type == "festival"
AND month == travel_month
AND (
  theme in theme_pool
  OR assigned_theme in theme_pool
  OR any(theme_tags in theme_pool)
)
AND (city_id == anchor_city_id if city_id is not null)
```

현재 정규화 데이터는 축제 기간에서 `month`를 파생하고, 날짜 원문/정규화 필드는 `event_start_date` 또는 legacy `eventstartdate` 형태로 존재할 수 있다. Festival Candidate 단계는 연도 정확성을 검증하지 않고 `month`, `theme_tags`, `city_id`만 조건으로 사용한다. `event_start_date`/`eventstartdate`와 `event_end_date`/`eventenddate`는 이후 `Festival_Verifier_Agent`가 목표 연도 개최 여부를 판단할 수 있도록 후보 payload에 보존한다.

DynamoDB 물리 조회는 현재 데이터 규모에서는 `entity_type=festival` 조회 후 application filter를 적용할 수 있다. 운영 규모가 커지면 `country + month`, `city_id + entity_type`, `theme/month` 성격의 GSI 또는 관계 탐색 보조 Lambda로 승격한다. 이 문서는 논리 계약을 우선하며 특정 GSI 이름을 고정하지 않는다.

### 6.3 출력

출력:

| 필드 | 설명 |
| --- | --- |
| `festival_candidates` | 월·테마 조건을 만족한 축제 후보 목록 |
| `seed_city_ids` | `festival_candidates`에서 추출한 고유 city_id 목록 |
| `festival_seed_audit` | month filter, theme pool, 후보 수, seed city 수 또는 anchor city lookup 결과 |

축제 후보의 최소 필드:

| 필드 | 설명 |
| --- | --- |
| `festival_id` | `entity_id` 또는 `FEST-{contentid}` 기반 안정 ID |
| `name` / `title` | 축제명 |
| `country` | 국가 |
| `city_id` | 개최 도시 |
| `city_name` | 표시용 도시명 |
| `month` | 카탈로그 개최 월 |
| `theme_tags` | 추천 travel theme label 목록 |
| `event_start_date` / `eventstartdate` | Verifier로 넘길 시작일 후보 |
| `event_end_date` / `eventenddate` | Verifier로 넘길 종료일 후보 |
| `source` | DynamoDB item 또는 원천 출처 식별자 |

`city_id`가 없고 `seed_city_ids`가 비어 있으면 실행 orchestration은 일반 장소 검색으로 자동 완화하지 않고 `no_festival_city_seed`를 반환한다.

`city_id`가 있고 `festival_candidates`가 비어 있으면 도시를 자동 변경하지 않고 `no_festival_in_anchor_city`를 반환한다.

## 7. `search_candidates`

### 7.1 역할

`search_candidates(query_vector, city_id=None, theme=None, top_k=50)`는 S3 Vector index에서 후보를 검색하고 Candidate Evidence가 사용할 dict로 정규화한다.

입력:

| 인자 | 설명 |
| --- | --- |
| `query_vector` | 1024차원 query embedding |
| `city_id` | anchor city가 있을 때의 도시 제한 조건 |
| `theme` | active required theme |
| `top_k` | S3 Vector에서 가져올 후보 수. 현재 평가 기본값은 50 |

출력 candidate:

| 필드 | 설명 |
| --- | --- |
| `key` | S3 Vector chunk key |
| `place_id` | chunk 번호를 제거한 장소 ID |
| `entity_type` | 현재 장소 검색에서는 `attraction` |
| `distance` | S3 Vector distance |
| `metadata` | S3 Vector metadata |
| `details` | 이 단계에서는 항상 `None` |

`theme`은 API `themes`에서 온 non-festival travel theme만 허용한다. `festival_event`나 `축제·이벤트`는 장소 검색 theme으로 넘기지 않는다.

### 7.2 theme to entity type mapping

현행 규칙:

| theme | S3 Vector `entity_type` filter |
| --- | --- |
| `미식·노포` | S3 Vector 장소 검색에서 제외. 선택 도시 기준 외부 `foodSearch` 링크로 처리 |
| 그 외 theme | `attraction` |

이 mapping은 Destination Search Tool 내부의 결정 규칙이다. 일반 장소 검색에서 `entity_type=festival`과 `entity_type=restaurant`는 사용하지 않는다.
현재 단계에서 식당 정보는 DB table/DynamoDB detail/S3 Vector 후보로 조회하지 않고, Planner 또는 Backend Link Builder가 선택 도시 기준 외부 맛집 검색 링크를 제공한다.

### 7.3 S3 Vector filter

`search_candidates`는 다음 조건을 조합한다.

| 조건 | filter |
| --- | --- |
| `entity_type` | `{"entity_type": {"$eq": entity_type}}` |
| `city_id`가 있음 | `{"city_id": {"$eq": city_id}}` |
| `theme`이 있음 | `{"theme_tags": {"$eq": theme}}` |

조건이 둘 이상이면 `$and`로 결합한다.

예시:

```json
{
  "$and": [
    { "entity_type": { "$eq": "attraction" } },
    { "theme_tags": { "$eq": "바다·해안" } }
  ]
}
```

### 7.4 S3 Vector query payload

저수준 S3 Vector 호출은 다음 형태의 payload를 사용한다.

```python
params = {
    "vectorBucketName": vector_bucket,
    "indexName": index_name,
    "queryVector": {"float32": query_vector},
    "topK": top_k,
    "returnMetadata": True,
    "returnDistance": True
}
```

filter가 있으면 `params["filter"]`에 추가된다.

### 7.5 `place_id` 정규화

S3 Vector `key`는 chunk 단위다.

```text
{entity_type}#{source_id}#{chunk_no}
```

Candidate Evidence에서는 같은 장소의 여러 chunk를 하나의 장소 후보로 다뤄야 하므로 chunk 번호를 제거한다.

```text
attraction#67890#2 → attraction#67890
```

이렇게 만든 값이 `place_id`다.

## 8. `prune_cities`

### 8.1 역할

`prune_cities(candidates, searchable_place_themes, allowed_city_ids=None)`는 검색 후보를 도시별로 묶고, 검색 가능한 관광 테마를 모두 만족하지 못하는 도시를 제거한다.

`allowed_city_ids`는 Festival Candidate Channel이나 anchor city 흐름에서 내려오는 도시 제한 pool이다. 값이 있으면 해당 city_id에 속하지 않는 후보는 searchable place theme AND gate 전에 제거한다.

출력:

| 값 | 설명 |
| --- | --- |
| `survived_groups` | `city_id -> 후보 목록` |
| `eliminated_cities` | searchable place theme AND gate에서 탈락한 도시 ID 목록 |

### 8.2 도시 grouping

현행 규칙은 다음 순서로 도시 식별자를 찾는다.

```text
metadata.city_id
→ metadata.city_name_ko
```

도시 식별자가 없으면 city discovery 비교 대상에서 제외된다.

### 8.3 Searchable place theme AND gate

도시 후보 pool의 `theme_tags`를 모아 searchable place theme가 모두 존재하는지 확인한다.

중요한 의미:

1. 이 gate는 "도시 후보 pool에 모든 검색 가능 관광 테마가 존재하는가"를 본다.
2. 최종 primary 목록이 모든 테마를 균형 있게 포함하는지는 보장하지 않는다.
3. 최종 primary 테마 균형은 Candidate selection helper의 quota 단계가 담당한다.
4. `includeFestivals=true`의 축제 seed 조건은 이 gate와 별개로 이미 `allowed_city_ids`에 반영되어 있어야 한다.

## 9. `rehydrate_places`

### 9.1 역할

`rehydrate_places(places)`는 선택된 place 목록에 DynamoDB detail을 in-place로 붙인다.

현재 실행 정책:

| 대상 | 호출 여부 |
| --- | --- |
| 최종 primary 후보 | 호출 |
| reserve 후보 | 기본 미호출 |
| scoring 전 전체 후보 | 미호출 |

### 9.2 DynamoDB key

S3 Vector metadata 안의 다음 필드를 사용한다.

| metadata 필드 | DynamoDB key |
| --- | --- |
| `ddb_pk` | `PK` |
| `ddb_sk` | `SK` |

Detail rehydrate helper는 다음 형태로 `GetItem`을 수행한다.

```python
response = client.get_item(
    TableName=table_name,
    Key={
        "PK": {"S": pk},
        "SK": {"S": sk}
    }
)
```

### 9.3 detail 주입 정책

조회 성공 시 `place["details"]`에 DynamoDB item을 일반 Python dict로 변환해 넣는다.

조회 실패 또는 key 누락 시:

1. 예외를 전체 실행으로 전파하지 않는다.
2. warning을 출력한다.
3. 해당 후보의 `details`는 `None`일 수 있다.

Planner 통합 시에는 `details=None`인 후보를 확정 설명 근거로 과장하면 안 된다.

## 10. Baseline과 Ours에서의 호출 방식

### 10.1 Baseline

Baseline 흐름:

1. raw query embedding을 cache에서 읽는다.
2. `includeFestivals=true`이면 `destinationId` 유무를 확인한다. `destinationId == null`이면 `search_festival_city_seeds(..., city_id=None)`로 seed city pool을 만들고, `destinationId != null`이면 anchor city 내부 축제 후보만 조회한다.
3. searchable place theme별로 `search_candidates(..., top_k=50)`를 호출한다.
4. 같은 `place_id`를 병합한다.
5. `prune_cities(..., allowed_city_ids=seed_city_ids 또는 [anchor_city_id])`로 city pool 제한과 searchable place theme AND gate를 적용한다.
6. 평균 similarity 기반으로 도시를 고른다.
7. 최종 primary 후보만 `rehydrate_places`로 detail을 붙인다.

Baseline은 soft channel을 호출하지 않는다.

### 10.2 Ours

Ours 흐름:

1. raw query embedding을 cache에서 읽는다.
2. soft query가 있으면 soft query embedding도 cache에서 읽는다.
3. `includeFestivals=true`이면 `destinationId` 유무를 확인한다. `destinationId == null`이면 `search_festival_city_seeds(..., city_id=None)`로 seed city pool을 만들고, `destinationId != null`이면 anchor city 내부 축제 후보만 조회한다.
4. raw channel을 searchable place theme별로 `search_candidates` 호출한다.
5. soft channel도 searchable place theme별로 `search_candidates` 호출한다.
6. 같은 `place_id`를 병합하되 raw distance와 soft distance를 모두 보존한다.
7. `prune_cities(..., allowed_city_ids=seed_city_ids 또는 [anchor_city_id])`로 city pool 제한과 searchable place theme AND gate를 적용한다.
8. scoring, fallback, quota 이후 최종 primary 후보만 `rehydrate_places`로 detail을 붙인다.

## 11. Resource metric

Destination Search Tool과 직접 관련되는 metric:

| metric | 의미 |
| --- | --- |
| `festival_seed_query_count` | DynamoDB festival seed 조회 수 |
| `festival_candidate_count` | 월·테마 seed 조건을 통과한 축제 후보 수 |
| `festival_seed_city_count` | 축제 후보에서 생성된 seed city 수 |
| `s3_query_count` | S3 Vector `query_vectors` 호출 수 |
| `retrieved_candidates` | S3 Vector에서 반환된 전체 후보 수 |
| `surviving_cities` | `prune_cities`를 통과한 도시 수 |
| `ddb_get_item_count` | DynamoDB `GetItem` 추정 수 |

주의:

1. festival seed의 DynamoDB Query/Scan 성격 조회는 `festival_seed_query_count`로 별도 기록한다.
2. `ddb_get_item_count`에는 primary detail rehydrate와 방문자 통계 `GetItem` 조회가 함께 포함될 수 있다.
3. 이 metric들은 평가 목적의 resource metric이며 사용자 API에 노출하지 않는다.

## 12. Failure와 fallback

| 상황 | 현재 처리 |
| --- | --- |
| `includeFestivals=true`이나 `theme_pool` 없음 | `no_required_theme_for_festival_seed` |
| 월·테마 조건을 만족하는 festival seed 없음 | `no_festival_city_seed` |
| anchor city 내부에 월·테마 조건 festival 후보 없음 | `no_festival_in_anchor_city` |
| S3 Vector 호출 실패 | strategy result를 `error`로 격리 |
| 후보 없음 | `no_candidate` |
| AND gate 생존 도시 없음 | `no_candidate` |
| `ddb_pk`/`ddb_sk` 누락 | warning, detail 미주입 |
| DynamoDB detail 조회 실패 | warning, detail `None` |

Destination Search Tool은 후보 부족을 직접 해결하지 않는다.
후보 수 sufficiency fallback은 city ranking 이후 공통 후보 충분성 단계에서 수행된다.

축제 seed 실패도 Tool 내부에서 일반 추천으로 완화하지 않는다. 사용자에게 축제 조건 제거, 여행 테마 추가, 월 변경 중 하나를 묻는 clarification은 Candidate Evidence runtime orchestration이 구성한다.

## 13. Tool 경계

Destination Search Tool이 하지 않는 일:

| 하지 않는 일 | 담당 |
| --- | --- |
| query 문장 해석 | Intent Agent |
| query embedding cache miss 처리 정책 | Embedding helper / 실행 orchestration |
| raw/soft 후보 병합 | 실행 orchestration |
| place/city score 계산 | Scoring Tool |
| primary quota 선택 | Candidate selection helper |
| festival seed/lookup 실패 시 사용자 질문 문구 생성 | Candidate Evidence runtime orchestration |
| 축제 event date의 목표 연도 검증 | Festival Verifier Agent |
| 추천 이유 생성 | Planner Agent |

## 14. Change History

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.5 | 2026-06-13 | llm | 현재 단계에서 `restaurant` 후보/테이블 조회를 제거하고, `미식·노포`는 선택 도시 기반 외부 맛집 검색 링크로 처리하도록 검색 필터 계약 정리 |
| v0.4 | 2026-06-13 | llm | `includeFestivals=true`를 city discovery seed와 anchored fixed-city festival lookup으로 분기하고 `no_festival_in_anchor_city` failure 추가 |
| v0.3 | 2026-06-13 | llm | `includeFestivals=true` 흐름의 DynamoDB festival city seed helper, seed city pool 제한, 관련 failure/metric 계약 추가 |
| v0.2 | 2026-06-13 | llm | 외부 파일 경로 직접 참조를 제거하고 Destination Search Tool의 입력·출력·실행 규칙 중심으로 정리 |
| v0.1 | 2026-06-13 | llm | S3 Vector 검색, 도시 AND gate, DynamoDB primary detail rehydrate 실행 세부 분리 |
