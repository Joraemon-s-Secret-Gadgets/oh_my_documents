# Dynamo Lookup Tool 실행 명세

> 문서 성격: 보조 Markdown
> 대표 문서: `../05_agent_spec.md`

> 문서 버전: v0.2
> 문서 상태: Draft / Dynamo Lookup Tool 세부
> 작성일: 2026-06-14
> 기준 문서: `candidate_evidence_agent.md`, `planner_agent.md`, `candidate_evidence_runtime_retrieval.md`
>
> **[PRD 반영 v0.1 — 대화형 빌더]** 장기 raw 이벤트는 DynamoDB **TTL→S3 콜드** 라인으로 관리(파생 프로필은 핫·TTL 없음). 최종 배치 enrich는 빌더에서 사용자 픽 시점에 수행. 상세: `../../98_prd/interactive_builder_prd.md`, TTL 라인: `../../04_database_design/supplemental/database_design_retention_neptune_update.md` §0.

## 1. 문서 목적

본 문서는 DynamoDB 조회를 담당하는 `DynamoLookupTool`의 실행 세부를 정리한다.

`DestinationSearchTool`은 S3 Vector attraction 검색으로 한정한다. 반면 `DynamoLookupTool`은 DynamoDB 기반 조회를 전담한다.

`DynamoLookupTool`의 책임은 두 가지다.

1. `includeFestivals=true` 요청에서 월·테마 조건을 만족하는 festival candidates를 조회한다.
2. Planner가 최종 일정에 배치한 attraction item에 대해서만 DynamoDB 상세 데이터를 지연 조회한다.

이 Tool은 S3 Vector 검색, scoring, quota selection, itinerary generation, public response packaging을 수행하지 않는다.

## 2. 책임 범위

| 구분 | 내용 |
| --- | --- |
| 책임 | DynamoDB festival candidate 조회, 최종 배치 attraction item detail enrichment |
| 입력 | country, travelMonth, theme_pool, optional city anchor, max_candidates, 최종 배치 item list |
| 출력 | festival seed city pool 또는 anchor city festival candidates, detail-enriched final places |
| 사용 AWS | DynamoDB |
| 사용하지 않음 | S3 Vectors, LLM, Bedrock generation, scoring formula, itinerary generation |

담당하지 않는 범위:

| 비범위 | 담당 |
| --- | --- |
| query embedding 생성/조회 | Embedding helper / 실행 orchestration |
| S3 Vector attraction 검색 | `DestinationSearchTool` |
| raw/soft 후보 병합 | 실행 orchestration |
| place/city scoring | `ScoringTool` |
| primary quota 선택 | Candidate selection helper |
| 축제 목표 연도 개최 여부 검증 | `Festival_Verifier_Agent` |
| 최종 일정 생성과 설명 확정 | `Planner_Agent` |

## 3. 초기화 계약

`DynamoLookupTool`은 생성 시 DynamoDB repository/client와 runtime search budget을 받는다.

```python
DynamoLookupTool(
    dynamodb=dynamodb_repository,
    search_budget=search_budget,
)
```

AWS resource 이름과 credential은 runtime config 또는 repository 설정으로 주입한다. profile, credential, `.env` 값은 문서에 확정값으로 추가하지 않는다.

## 4. `search_festival_city_seeds`

### 4.1 역할

`search_festival_city_seeds(country, travel_month, theme_pool, city_id=None, max_candidates=100)`는 `includeFestivals=true` 요청에서 장소 S3 Vector 검색 전에 실행되는 DynamoDB 조회 helper다.

이 helper의 목표는 축제를 scoring 대상으로 만들기 위한 것이 아니다.

`city_id`가 없으면 해당 월과 travel theme에 맞는 축제가 존재하는 도시 pool을 먼저 확정한다. `city_id`가 있으면 이미 고정된 도시 내부에서만 축제 후보를 조회해 Festival Verifier handoff 후보를 만든다.

### 4.2 DynamoDB 논리 조건

조회는 물리 index 구현과 분리해 다음 논리 조건을 만족해야 한다.

```text
entity_type == "festival"
AND country == request.country
AND month == request.travelMonth
AND (
  assigned_theme IN theme_pool
  OR any(theme_tags IN theme_pool)
)
AND optional city_id == anchor city
```

여러 travel theme를 선택한 경우 theme 조건은 OR로 해석한다.

`theme_pool`에는 `festival_event`나 `축제·이벤트`가 들어오면 안 된다. 실행 orchestration은 이 값이 비어 있으면 DynamoDB를 조회하지 않고 `no_required_theme_for_festival_seed`를 반환한다.

물리 조회는 현재 데이터 규모에서는 `entity_type=festival` 조회 후 application filter를 적용할 수 있다. 운영 규모가 커지면 `country + month`, `city_id + entity_type`, `theme/month` 성격의 GSI 또는 관계 탐색 보조 Lambda로 승격한다. 이 문서는 논리 계약을 우선하며 특정 GSI 이름을 고정하지 않는다.

### 4.3 반환 정책

| 상황 | 반환 |
| --- | --- |
| 월·테마 조건 축제 후보 있음 | `status=ok`, `candidates`, `seed_city_ids` |
| theme pool 비어 있음 | `status=no_candidate`, `failure_signals=["no_required_theme_for_festival_seed"]`, `needs_clarification=true` |
| city discovery에서 seed 도시 없음 | `status=no_candidate`, `failure_signals=["no_festival_city_seed"]`, `needs_clarification=true` |
| anchored city 내부 축제 없음 | `status=no_candidate`, `failure_signals=["no_festival_in_anchor_city"]`, `needs_clarification=true` |

축제 seed 실패는 Tool 내부에서 일반 추천으로 완화하지 않는다. 사용자에게 축제 조건 제거, 여행 테마 추가, 월 변경 중 하나를 묻는 clarification은 Candidate Evidence runtime orchestration이 구성한다.

## 5. `enrich_final_places`

### 5.1 역할

`enrich_final_places(places)`는 Planner가 최종 일정에 배치한 attraction place 목록에 DynamoDB detail을 붙인다.

현재 실행 정책:

| 대상 | 호출 여부 |
| --- | --- |
| Planner 최종 배치 attraction item | 호출 |
| Candidate Evidence `recommended_places` / primary | Candidate Evidence 단계에서는 미호출 |
| `reserve_places` | Candidate Evidence 단계에서는 미호출 |
| scoring 전 전체 후보 | 미호출 |

### 5.2 DynamoDB key

S3 Vector metadata 안의 다음 필드를 사용한다.

| metadata 필드 | DynamoDB key |
| --- | --- |
| `ddb_pk` | `PK` |
| `ddb_sk` | `SK` |

Final item detail enrichment helper는 다음 형태로 `GetItem`을 수행한다.

```python
response = client.get_item(
    TableName=table_name,
    Key={
        "PK": {"S": pk},
        "SK": {"S": sk}
    }
)
```

### 5.3 detail 주입 정책

조회 성공 시 `place["details"]`에 DynamoDB item을 일반 Python dict로 변환해 넣는다.

조회 실패 또는 key 누락 시:

1. 예외를 전체 실행으로 전파하지 않는다.
2. warning을 출력한다.
3. 해당 후보의 `details`는 `None`일 수 있다.

Planner 통합 시에는 `details=None`인 최종 배치 item을 확정 설명 근거로 과장하면 안 된다. 이 경우 title/theme/reason code 수준의 보수적 설명만 허용한다.

## 6. Resource metric

| metric | 의미 |
| --- | --- |
| `festival_seed_query_count` | DynamoDB festival seed 조회 수 |
| `festival_candidate_count` | 월·테마 seed 조건을 통과한 축제 후보 수 |
| `festival_seed_city_count` | 축제 후보에서 생성된 seed city 수 |
| `ddb_get_item_count` | 최종 배치 item detail enrichment와 기타 DynamoDB `GetItem` 추정 수 |

이 metric들은 평가 목적의 resource metric이며 사용자 API에 노출하지 않는다.

## 7. Failure와 fallback

| 상황 | 현재 처리 |
| --- | --- |
| `includeFestivals=true`이나 `theme_pool` 없음 | `no_required_theme_for_festival_seed` |
| 월·테마 조건을 만족하는 festival seed 없음 | `no_festival_city_seed` |
| anchor city 내부에 월·테마 조건 festival 후보 없음 | `no_festival_in_anchor_city` |
| 최종 배치 item의 `ddb_pk`/`ddb_sk` 누락 | warning, detail 미주입 |
| 최종 배치 item의 DynamoDB detail 조회 실패 | warning, detail `None` |

`DynamoLookupTool`은 후보 부족을 직접 해결하지 않는다. 후보 수 sufficiency fallback은 city ranking 이후 공통 후보 충분성 단계에서 수행된다.

## 8. Tool 경계

`DynamoLookupTool`이 하지 않는 일:

| 하지 않는 일 | 담당 |
| --- | --- |
| query 문장 해석 | Intent Agent |
| S3 Vector 검색 | `DestinationSearchTool` |
| raw/soft 후보 병합 | 실행 orchestration |
| place/city score 계산 | `ScoringTool` |
| primary quota 선택 | Candidate selection helper |
| festival seed/lookup 실패 시 사용자 질문 문구 생성 | Candidate Evidence runtime orchestration |
| 축제 event date의 목표 연도 검증 | Festival Verifier Agent |
| 추천 이유 확정 | Planner Agent |

## 9. Change History

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.1 | 2026-06-14 | llm | `DestinationSearchTool`에서 DynamoDB 조회 책임을 분리해 festival seed lookup과 final item detail enrichment를 담당하는 별도 Tool 계약 추가 |
