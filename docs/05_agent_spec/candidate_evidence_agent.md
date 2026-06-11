# Candidate Evidence Agent 명세서

> 문서 버전: v0.1  
> 문서 상태: Review / Candidate Evidence Agent 상세 정본  
> 대체 대상: `retriever.md`, `ranker.md`, `retriever_code.md`, `ranker_code.md`  
> 기준 문서: `05_agent_spec.md`, `langgraph_flow.md`, `user_raw_query_flow.md`

# 1. 문서 목적

본 문서는 기존 `Polymorphic_Retriever_Agent`와 `Ranker_Agent`로 분리되어 있던 검색·점수화 책임을 `Candidate_Evidence_Agent`로 통합하기 위한 보조 명세다.

이 Agent는 최종 일정을 생성하지 않는다.
역할은 Planner Agent가 사용할 수 있는 도시/장소 후보와 그 근거를 하나의 내부 패키지로 구성하는 것이다.

```text
Intent_Agent
→ Candidate_Evidence_Agent
  - Destination Search Tool
  - Scoring Tool
  - Weather Trends Skill
→ Festival_Verifier_Agent
→ Planner_Agent
```

# 2. 책임 경계

| 구분 | 내용 |
| --- | --- |
| 책임 | 장소 evidence 검색, 후보 도시 구성, 도시/장소 scoring, primary/reserve 후보 패키징 |
| 하지 않음 | 일정 생성, 추천 설명 생성, 최종 API 응답 생성, 숙소 추천 확정 |
| 입력 | Intent Agent가 구조화한 국가, 월, 일정 길이, active theme, raw/soft query, anchor 조건 |
| 도구 | `Destination Search Tool`, `Scoring Tool`, `Weather Trends Skill` |
| 출력 | Planner Agent 입력용 `Candidate Evidence Package` |

`Candidate_Evidence_Agent`의 출력은 외부 `/recommendations` API 응답이 아니다.
외부 API 응답은 Planner Agent와 Backend Serving 단계에서 사용자용 일정 결과로 변환한다.

# 3. 입력 계약

```json
{
  "country": "KR",
  "travelMonth": 6,
  "travelYear": 2026,
  "tripType": "2d1n",
  "destinationId": null,
  "active_required_themes": ["바다·해안", "미식·노포"],
  "cleaned_raw_query": "바다를 보고 지역 맛집도 가고 싶다",
  "soft_preference_query": "조용하고 한적한 분위기",
  "unsupported_conditions": [],
  "user_location": {
    "latitude": 37.5665,
    "longitude": 126.9780
  },
  "includeFestivals": false
}
```

입력 정책:

- `active_required_themes`는 후보 도시/장소의 필수 theme coverage 기준이다.
- `cleaned_raw_query`는 사용자의 반영 가능한 자연어 맥락을 보존한 검색 query다.
- `soft_preference_query`는 분위기·감성·선호 표현을 별도 evidence channel로 검색하기 위한 query다.
- `unsupported_conditions`는 검색 조건으로 사용하지 않고 Planner의 `user_notice` 후보로 넘긴다.
- `destinationId`가 있으면 city discovery를 생략하고 anchored place search로 동작한다.

# 4. 검색 모드

| mode | 조건 | 동작 |
| --- | --- | --- |
| `city_discovery` | `destinationId == null` | 여러 도시의 장소 evidence를 검색하고 scoring으로 `selected_city`를 선정 |
| `anchored_place_search` | `destinationId != null` | 지정 도시 내부에서 Planner가 사용할 장소 후보와 예비 후보 구성 |

두 모드 모두 출력 schema는 동일하다.
차이는 `selected_city.selection_reason_code`와 검색 filter뿐이다.

# 5. Candidate Evidence Package

```json
{
  "mode": "city_discovery",
  "selected_city": {
    "city_id": "Yeongdeok",
    "city_name_ko": "영덕군",
    "country": "KR",
    "selection_reason_code": [
      "theme_coverage",
      "balanced_evidence",
      "candidate_sufficiency"
    ]
  },
  "city_rankings": [],
  "recommended_places": [],
  "reserve_places": [],
  "coverage_audit": {},
  "retrieval_audit": {}
}
```

## 5.1 `selected_city`

`selected_city`는 도시 이미지가 아니라 장소 evidence와 scoring 결과에서 파생한다.

anchor city가 주어진 경우에는 사용자가 지정한 도시를 유지한다.
anchor가 없는 경우에는 `city_rankings[0]`을 사용한다.

## 5.2 `city_rankings`

도시별 scoring 결과와 evidence 근거를 담는다.

```json
{
  "city_id": "Yeongdeok",
  "city_name_ko": "영덕군",
  "final_score": 0.84,
  "score_breakdown": {
    "semantic_evidence": 0.78,
    "theme_coverage": 1.0,
    "theme_balance": 0.91,
    "scale_correction": 0.12,
    "distance_penalty": -0.04,
    "candidate_sufficiency": 0.9
  },
  "evidence_place_ids": ["P_001", "P_002", "P_003"]
}
```

## 5.3 `recommended_places` / `reserve_places`

`recommended_places`는 Planner가 우선 사용하는 primary 후보이고, `reserve_places`는 Planner fallback 지연을 줄이기 위한 예비 후보다.

```json
{
  "place_id": "P_001",
  "city_id": "Yeongdeok",
  "title": "장사해수욕장",
  "assigned_theme": "바다·해안",
  "content_type": "attraction",
  "similarity_raw": 0.82,
  "similarity_soft": 0.61,
  "place_score": 0.79,
  "slot_role": "primary",
  "evidence_reason_code": ["raw_match", "theme_match"]
}
```

Planner는 `recommended_places`를 우선 사용하고, 장소 수·동선·시간대 제약으로 부족하면 `reserve_places`를 사용한다.
primary와 reserve가 모두 부족한 경우에만 Candidate Evidence Agent 재호출을 요청한다.

# 6. 후보 수 예산

후보 수는 `tripType` 또는 일정 일수에 따라 산정한다.

| 일정 | primary | reserve | total |
| --- | ---: | ---: | ---: |
| `daytrip` | 6 | 4 | 10 |
| `2d1n` | 10 | 8 | 18 |
| `3d2n` | 14 | 10 | 24 |
| `4d3n` 이상 | 18 | 12 | 30 |

이 값은 Planner가 실제 일정 구성 중 장소를 제외할 수 있다는 전제를 반영한 후보 예산이다.
최종 사용자에게 이 수량이 그대로 노출되는 것은 아니다.

# 7. Theme Quota와 Balance

복수 테마 선택 시 단순 Top-K만 사용하면 특정 테마 후보로 쏠릴 수 있다.
따라서 후보 선택은 다음 순서를 따른다.

1. `active_required_themes`별 minimum quota를 먼저 채운다.
2. 도시/장소 점수순으로 남은 slot을 채운다.
3. 후보가 특정 테마에 과도하게 몰리면 낮은 점수의 중복 테마 후보보다 다른 필수 테마 후보를 우선한다.
4. `coverage_audit`에 theme count와 balance 지표를 남긴다.

권장 quota:

```text
theme_min_quota = floor(total_candidate_count / required_theme_count * 0.6)
```

예시:

```text
required themes = 2
total candidates = 18
theme_min_quota = floor(18 / 2 * 0.6) = 5
```

# 8. Scoring 개요

점수 계산 자체는 `Scoring Tool`이 결정론적으로 수행한다.
Agent는 score breakdown과 후보 패키지를 해석해 downstream에 넘긴다.

## 8.1 City Score

```text
city_score =
  semantic_evidence_score
+ theme_coverage_score
+ theme_balance_score
+ scale_correction
+ candidate_sufficiency_bonus
- distance_penalty
- congestion_penalty
```

| 항목 | 의미 |
| --- | --- |
| `semantic_evidence_score` | raw/soft query와 도시 내 장소 evidence의 유사도 집계 |
| `theme_coverage_score` | active theme 전체를 도시 내 place 후보가 커버하는 정도 |
| `theme_balance_score` | 후보가 특정 테마에 과도하게 쏠리지 않는 정도 |
| `scale_correction` | 데이터가 많은 도시가 과도하게 유리해지는 것을 완화 |
| `candidate_sufficiency_bonus` | Planner가 사용할 primary/reserve 후보가 충분한 경우 가점 |
| `distance_penalty` | 출발지와 일정 길이에 비해 이동 부담이 큰 경우 감점 |
| `congestion_penalty` | 사전 혼잡도 또는 과밀 신호가 높은 경우 감점 |

## 8.2 Place Score

```text
place_score =
  raw_similarity
+ soft_similarity
+ theme_match_score
+ source_quality_score
- local_distance_penalty
```

| 항목 | 의미 |
| --- | --- |
| `raw_similarity` | `cleaned_raw_query`와 장소 embedding text의 유사도 |
| `soft_similarity` | `soft_preference_query`와 장소 embedding text의 유사도 |
| `theme_match_score` | place의 theme가 active theme에 포함되는지 |
| `source_quality_score` | 원본 설명, 좌표, 메뉴/주소 등 근거 필드의 충분성 |
| `local_distance_penalty` | anchor 또는 도시 중심 대비 동선 부담 |

# 9. Vector Index 전제

Candidate Evidence Agent는 DynamoDB 원본을 런타임에 직접 임베딩하지 않는다.
S3 vector index는 사전에 구축된 검색 인덱스다.

```text
DynamoDB normalized place item
→ Index Document Builder
→ rich embedding_text
→ embedding model
→ S3 vector index
```

`soft_preference_query`는 query-side 개선이고, `rich embedding_text`는 document-side 개선이다.
둘은 서로 대체 관계가 아니라 보완 관계다.

`rich embedding_text`에는 다음 필드를 포함할 수 있다.

```text
장소명
도시명
테마
장소 유형
주소
대표메뉴/취급메뉴
원본 설명
파생 태그
```

# 10. Audit

## 10.1 `coverage_audit`

```json
{
  "required_themes": ["바다·해안", "미식·노포"],
  "primary_theme_counts": {
    "바다·해안": 5,
    "미식·노포": 5
  },
  "reserve_theme_counts": {
    "바다·해안": 4,
    "미식·노포": 4
  },
  "theme_entropy": 0.98,
  "candidate_sufficiency": "sufficient"
}
```

## 10.2 `retrieval_audit`

```json
{
  "cleaned_raw_query": "바다를 보고 지역 맛집도 가고 싶다",
  "soft_preference_query": "조용하고 한적한 분위기",
  "tools_used": ["vector_search_tool", "scoring_tool"],
  "index_text_mode": "rich",
  "fallback_required": false
}
```

# 11. Failure Signals

| signal | 의미 | downstream 처리 |
| --- | --- | --- |
| `no_candidate` | 필수 theme를 충족할 도시/장소 후보가 없음 | 검증 실패가 아니라 조건 완화 또는 안전 폴백 |
| `insufficient_primary` | primary 후보 수 부족 | reserve 사용 |
| `insufficient_total_candidates` | primary+reserve 후보 모두 부족 | Candidate Evidence Agent fallback 재호출 후보 |
| `theme_imbalance` | 복수 테마 후보가 한쪽으로 쏠림 | quota 재조정 또는 confidence 하향 |
| `anchor_violation` | anchor city 외 장소가 섞임 | Candidate Evidence Agent 결과 폐기 후 재검색 |

# 12. Legacy 문서와의 관계

`retriever.md`, `ranker.md`, `retriever_code.md`, `ranker_code.md`는 기존 분리 설계의 세부 아이디어를 보관하는 legacy 문서다.
새로운 상세 정본은 본 문서이며, 기존 문서의 유효한 공식과 기준은 이 문서의 scoring 및 audit 절로 선별 반영한다.
