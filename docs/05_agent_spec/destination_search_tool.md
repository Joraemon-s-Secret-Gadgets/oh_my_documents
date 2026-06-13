# Destination Search Tool 실행 명세

> 문서 버전: v0.2
> 문서 상태: Draft / Destination Search Tool 세부
> 작성일: 2026-06-13
> 기준 문서: `candidate_evidence_agent.md`, `candidate_evidence_runtime_retrieval.md`

## 1. 문서 목적

본 문서는 Candidate Evidence 후보 검색을 담당하는 `DestinationSearchTool`의 실행 세부를 정리한다.

`DestinationSearchTool`은 Candidate Evidence Agent 관점에서 다음 세 가지 작업을 하나의 Tool처럼 묶는다.

1. S3 Vector index에서 theme/city 조건에 맞는 후보를 검색한다.
2. 검색 후보를 도시별로 묶고 required theme AND gate를 적용한다.
3. 최종 primary 후보에 대해서만 DynamoDB 상세 데이터를 지연 조회한다.

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
| 책임 | S3 Vector 검색, 후보 정규화, 도시별 AND gate, primary detail rehydrate |
| 입력 | query vector, optional city anchor, active theme, top_k, 후보 list |
| 출력 | 정규화된 candidate list, survived city groups, hydrated primary places |
| 사용 AWS | S3 Vectors, DynamoDB |
| 사용하지 않음 | LLM, Bedrock generation, scoring formula, itinerary generation |

담당하지 않는 범위:

| 비범위 | 담당 |
| --- | --- |
| query embedding 생성/조회 | Embedding helper / 실행 orchestration |
| raw/soft 후보 병합 | 실행 orchestration |
| place/city scoring | `ScoringTool` |
| primary quota 선택 | Candidate selection helper |
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

## 6. `search_candidates`

### 6.1 역할

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
| `entity_type` | `restaurant`, `attraction` 등 |
| `distance` | S3 Vector distance |
| `metadata` | S3 Vector metadata |
| `details` | 이 단계에서는 항상 `None` |

### 6.2 theme to entity type mapping

현행 규칙:

| theme | S3 Vector `entity_type` filter |
| --- | --- |
| `미식·노포` | `restaurant` |
| 그 외 theme | `attraction` |

이 mapping은 Destination Search Tool 내부의 결정 규칙이다.

### 6.3 S3 Vector filter

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
    { "entity_type": { "$eq": "restaurant" } },
    { "theme_tags": { "$eq": "미식·노포" } }
  ]
}
```

### 6.4 S3 Vector query payload

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

### 6.5 `place_id` 정규화

S3 Vector `key`는 chunk 단위다.

```text
{entity_type}#{source_id}#{chunk_no}
```

Candidate Evidence에서는 같은 장소의 여러 chunk를 하나의 장소 후보로 다뤄야 하므로 chunk 번호를 제거한다.

```text
restaurant#12345#0 → restaurant#12345
attraction#67890#2 → attraction#67890
```

이렇게 만든 값이 `place_id`다.

## 7. `prune_cities`

### 7.1 역할

`prune_cities(candidates, required_themes)`는 검색 후보를 도시별로 묶고, 필수 테마를 모두 만족하지 못하는 도시를 제거한다.

출력:

| 값 | 설명 |
| --- | --- |
| `survived_groups` | `city_id -> 후보 목록` |
| `eliminated_cities` | required theme AND gate에서 탈락한 도시 ID 목록 |

### 7.2 도시 grouping

현행 규칙은 다음 순서로 도시 식별자를 찾는다.

```text
metadata.city_id
→ metadata.city_name_ko
```

도시 식별자가 없으면 city discovery 비교 대상에서 제외된다.

### 7.3 required theme AND gate

도시 후보 pool의 `theme_tags`를 모아 required theme가 모두 존재하는지 확인한다.

중요한 의미:

1. 이 gate는 "도시 후보 pool에 모든 필수 테마가 존재하는가"를 본다.
2. 최종 primary 목록이 모든 테마를 균형 있게 포함하는지는 보장하지 않는다.
3. 최종 primary 테마 균형은 Candidate selection helper의 quota 단계가 담당한다.

## 8. `rehydrate_places`

### 8.1 역할

`rehydrate_places(places)`는 선택된 place 목록에 DynamoDB detail을 in-place로 붙인다.

현재 실행 정책:

| 대상 | 호출 여부 |
| --- | --- |
| 최종 primary 후보 | 호출 |
| reserve 후보 | 기본 미호출 |
| scoring 전 전체 후보 | 미호출 |

### 8.2 DynamoDB key

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

### 8.3 detail 주입 정책

조회 성공 시 `place["details"]`에 DynamoDB item을 일반 Python dict로 변환해 넣는다.

조회 실패 또는 key 누락 시:

1. 예외를 전체 실행으로 전파하지 않는다.
2. warning을 출력한다.
3. 해당 후보의 `details`는 `None`일 수 있다.

Planner 통합 시에는 `details=None`인 후보를 확정 설명 근거로 과장하면 안 된다.

## 9. Baseline과 Ours에서의 호출 방식

### 9.1 Baseline

Baseline 흐름:

1. raw query embedding을 cache에서 읽는다.
2. active theme별로 `search_candidates(..., top_k=50)`를 호출한다.
3. 같은 `place_id`를 병합한다.
4. `prune_cities`로 AND gate를 적용한다.
5. 평균 similarity 기반으로 도시를 고른다.
6. 최종 primary 후보만 `rehydrate_places`로 detail을 붙인다.

Baseline은 soft channel을 호출하지 않는다.

### 9.2 Ours

Ours 흐름:

1. raw query embedding을 cache에서 읽는다.
2. soft query가 있으면 soft query embedding도 cache에서 읽는다.
3. raw channel을 active theme별로 `search_candidates` 호출한다.
4. soft channel도 active theme별로 `search_candidates` 호출한다.
5. 같은 `place_id`를 병합하되 raw distance와 soft distance를 모두 보존한다.
6. `prune_cities`로 AND gate를 적용한다.
7. scoring, fallback, quota 이후 최종 primary 후보만 `rehydrate_places`로 detail을 붙인다.

## 10. Resource metric

Destination Search Tool과 직접 관련되는 metric:

| metric | 의미 |
| --- | --- |
| `s3_query_count` | S3 Vector `query_vectors` 호출 수 |
| `retrieved_candidates` | S3 Vector에서 반환된 전체 후보 수 |
| `surviving_cities` | `prune_cities`를 통과한 도시 수 |
| `ddb_get_item_count` | DynamoDB `GetItem` 추정 수 |

주의:

1. Ours의 `ddb_get_item_count`에는 방문자 통계 조회가 함께 포함될 수 있다.
2. `ddb_get_item_count`는 평가 목적의 resource metric이며 사용자 API에 노출하지 않는다.

## 11. Failure와 fallback

| 상황 | 현재 처리 |
| --- | --- |
| S3 Vector 호출 실패 | strategy result를 `error`로 격리 |
| 후보 없음 | `no_candidate` |
| AND gate 생존 도시 없음 | `no_candidate` |
| `ddb_pk`/`ddb_sk` 누락 | warning, detail 미주입 |
| DynamoDB detail 조회 실패 | warning, detail `None` |

Destination Search Tool은 후보 부족을 직접 해결하지 않는다.
후보 수 sufficiency fallback은 city ranking 이후 공통 후보 충분성 단계에서 수행된다.

## 12. Tool 경계

Destination Search Tool이 하지 않는 일:

| 하지 않는 일 | 담당 |
| --- | --- |
| query 문장 해석 | Intent Agent |
| query embedding cache miss 처리 정책 | Embedding helper / 실행 orchestration |
| raw/soft 후보 병합 | 실행 orchestration |
| place/city score 계산 | Scoring Tool |
| primary quota 선택 | Candidate selection helper |
| 추천 이유 생성 | Planner Agent |

## 13. Change History

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.2 | 2026-06-13 | llm | 외부 파일 경로 직접 참조를 제거하고 Destination Search Tool의 입력·출력·실행 규칙 중심으로 정리 |
| v0.1 | 2026-06-13 | llm | S3 Vector 검색, 도시 AND gate, DynamoDB primary detail rehydrate 실행 세부 분리 |
