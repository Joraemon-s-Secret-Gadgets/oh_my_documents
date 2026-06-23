# Candidate Evidence Agent 명세서

> 문서 성격: 보조 Markdown
> 대표 문서: `05_agent_spec.md`

> 문서 버전: v0.13
> 문서 상태: Review / Candidate Evidence Agent 상세 정본  
> 대체 대상: `retriever.md`, `ranker.md`, `retriever_code.md`, `ranker_code.md`  
> 기준 문서: `05_agent_spec.md`, `langgraph_flow.md`, `user_raw_query_flow.md`, `candidate_evidence_baseline_comparison.md`, `candidate_evidence_runtime_retrieval.md`, `destination_search_tool.md`, `dynamo_lookup_tool.md`, `scoring_tool.md`, `festival_verifier_agent.md`

> **[PRD 반영 v0.1 — 대화형 빌더]** Candidate Evidence를 **3층 분해**한다: ① 공유 검색·스코어 **코어**
> (stateless, 게이트 `city｜radius`, scoring 가중치 context별, query_vector 재사용) ② **도시 선정**
> (1회, city 게이트) ③ **반경 Provider**(루프, radius 게이트+스텝 필터). 산출물은 **루프 시드**
> `{도시, query_vector, anchor, budget}`. 후보는 **2티어**(DB 큐레이션 + 지도 API 보충). 상세: `../98_prd/interactive_builder_prd.md`.

# 1. 문서 목적

본 문서는 기존 `Polymorphic_Retriever_Agent`와 `Ranker_Agent`로 분리되어 있던 검색·점수화 책임을 `Candidate_Evidence_Agent`로 통합하기 위한 보조 명세다.

이 Agent는 최종 일정을 생성하지 않는다.
역할은 Planner Agent가 사용할 수 있는 도시/장소 후보와 구조화 evidence/audit를 하나의 내부 패키지로 구성하는 것이다. 사용자에게 보여줄 자연어 추천 근거 문장은 생성하지 않는다.

```text
Intent_Agent
→ Candidate_Evidence_Agent
  - Destination Search Tool
  - Scoring Tool
→ Festival_Verifier_Agent
→ Planner_Agent
```

현재 검증된 Ours는 `Destination Search Tool`과 결정적 `Scoring Tool`을 사용한다. `Weather Trends Skill`은 전체 제품 설계의 계절 적합성 보강 요소지만 현재 Baseline/Ours 검색 비교에는 포함하지 않는다. 따라서 본 문서에서는 **현재 검증된 Ours 계약**과 **향후 제품 통합 항목**을 구분한다.

# 2. 책임 경계

| 구분 | 내용 |
| --- | --- |
| 책임 | 장소 evidence 검색, 축제 포함 요청의 월 조건 기반 도시 seed 구성, 후보 도시 구성, 도시/장소 scoring, primary/reserve 후보 패키징 |
| 하지 않음 | 일정 생성, 추천 설명 생성, 최종 API 응답 생성, 숙소 추천 확정, 축제 목표 연도 개최 검증 |
| 입력 | Intent Agent가 구조화한 국가, 월, 일정 길이, active theme, raw/soft query, anchor 조건 |
| 현재 검증 도구 | `Destination Search Tool`, `Scoring Tool` |
| 향후 통합 | `Weather Trends Skill`, Planner-level 운영시간·동선 검증 |
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
- `active_required_themes`는 API `themes`에서 온 canonical travel theme만 Intent Agent가 label로 변환한 값이다. 축제 포함 여부는 `includeFestivals`로만 전달되며 `축제·이벤트` 같은 값은 여기에 들어오지 않는다.
- `cleaned_raw_query`는 사용자의 반영 가능한 자연어 맥락을 보존한 검색 query다.
- `soft_preference_query`는 분위기·감성·선호 표현을 별도 evidence channel로 검색하기 위한 query다.
- `unsupported_conditions`는 검색 조건으로 사용하지 않고 Planner의 `user_notice` 후보로 넘긴다.
- `destinationId`가 있으면 city discovery를 생략하고 `anchored_place_search`로 동작한다.
- `includeFestivals=true`는 `destinationId` 유무와 독립적으로 유지된다.
- `destinationId == null`이고 `includeFestivals=true`이면 장소 검색 전에 Festival City Seed Channel을 실행한다.
- `destinationId != null`이고 `includeFestivals=true`이면 고정 도시 내부에서만 Festival Fixed-City Lookup을 실행한다. 이 경우 축제 후보가 도시를 바꾸거나 anchor를 해제하지 않는다.
- Festival City Seed Channel은 `festival.month == travelMonth`와 사용자 travel theme OR 조건을 모두 만족하는 축제가 있는 도시만 city discovery 후보군으로 둔다.
- 이 단계에서는 축제의 목표 연도 개최 여부를 판단하지 않는다. 연도와 최종 일정 배치 가능 여부는 `Festival_Verifier_Agent`가 검증한다.

현재 24건 평가는 `city_discovery`만 검증했다. `anchored_place_search`는 목표 계약에는 포함하지만 동일 수준의 회귀 테스트를 추가하기 전까지 검증 완료로 간주하지 않는다.

# 4. 검색 모드

| mode | 조건 | 동작 |
| --- | --- | --- |
| `city_discovery` | `destinationId == null` | 여러 도시의 장소 evidence를 검색하고 scoring으로 `selected_city`를 선정 |
| `anchored_place_search` | `destinationId != null` | 지정 도시 내부에서 Planner가 사용할 장소 후보와 예비 후보 구성. `includeFestivals=true`이면 같은 도시 안에서 월·테마 조건 축제 후보를 함께 조회 |
| `festival_seeded_city_discovery` | `includeFestivals=true`, `destinationId == null` | `festival.month == travelMonth`와 travel theme OR 조건을 만족하는 축제가 있는 도시를 먼저 seed로 만들고, 그 도시들 안에서 장소 evidence를 검색·scoring |

각 모드의 출력 schema는 동일하다.
차이는 `selected_city.selection_reason_code`와 검색 filter뿐이다.

## 4.1 현재 Ours 검색 흐름

```text
raw query embedding
+ optional soft preference embedding
→ 각 searchable place theme별 raw S3 Vector search (top_k=50)
+ 각 searchable place theme별 soft S3 Vector search (top_k=50)
→ place_id 기준 raw/soft 후보 병합
→ 도시별 grouping
→ searchable place theme Strict AND gate
→ 월별 방문객 통계 조회 및 congestion index 계산
→ place score 계산
→ city score 계산 및 score ranking
→ candidate sufficiency fallback
→ title dedup + min quota + soft max quota primary 구성
→ reserve 구성
→ Candidate Evidence Package 반환
```

테마별 content type mapping은 현재 다음과 같다.

| theme | S3 Vector `entity_type` filter |
| --- | --- |
| `미식·노포` | Candidate Evidence 장소 검색에서 제외. 선택 도시 기준 `foodSearch` 링크로 Planner가 처리 |
| 그 외 active theme | `attraction` |

현재 단계에서 Candidate Evidence는 `restaurant` table 또는 restaurant S3 Vector 후보를 조회하지 않는다.
`미식·노포`는 도시 선택을 위한 장소 evidence가 아니라 Planner의 식사 슬롯/외부 맛집 검색 링크 생성 요구로 전달한다.
따라서 `active_required_themes`에 `미식·노포`만 있는 경우에도 도시 검색은 다른 관광 테마 evidence가 없을 수 있으며, 이때는 축제 seed, anchor city, 온보딩/인기 도시 보조 정책, 또는 사용자 재질문 정책 중 하나로 보강해야 한다.

Candidate Evidence 내부에서는 다음처럼 theme 집합을 분리한다.

| 집합 | 설명 |
| --- | --- |
| `active_required_themes` | 사용자가 요구한 전체 travel theme |
| `searchable_place_themes` | S3 Vector 관광지 검색과 city AND gate에 사용하는 theme. 현재 `미식·노포` 제외 |
| `external_link_themes` | 장소 후보가 아니라 외부 링크/CTA로 처리할 theme. 현재 `미식·노포` |

searchable place theme AND gate와 quota는 `searchable_place_themes`에만 적용한다. `external_link_themes`는 Candidate Evidence가 탈락 조건으로 쓰지 않고 Planner coverage 계약으로 넘긴다.

soft query가 없으면 soft channel 호출을 생략한다. 같은 `place_id`가 여러 테마 검색 또는 raw/soft channel에서 반복되면 채널별 최소 cosine distance를 유지하고 하나의 후보로 병합한다.

## 4.2 Festival Candidate Channel

`includeFestivals=true`인 요청에서는 축제 후보를 일반 장소 후보와 분리해 다룬다.

단, `destinationId` 유무에 따라 축제 후보의 역할이 달라진다.

| 조건 | 축제 후보 역할 |
| --- | --- |
| `destinationId == null` | 축제는 city discovery 후보군을 제한하는 seed 조건이다. |
| `destinationId != null` | 축제는 이미 고정된 도시 안에서만 조회하는 부가 조건이다. 도시를 재선택하거나 anchor를 해제하지 않는다. |

`destinationId == null`에서 축제 seed는 hard gate다.
`festival.month == travelMonth`와 사용자 travel theme OR 조건을 모두 만족하는 축제가 없는 도시는 attraction retrieval/scoring 전에 후보군에서 제외한다.
따라서 `includeFestivals=true`인 city discovery에서 축제가 열리지 않는 도시는 일반 관광지 점수가 높아도 `selected_city`가 될 수 없다.

### 4.2.1 City Discovery의 Festival City Seed

```text
includeFestivals=true
destinationId == null
→ active_required_themes(non-festival travel theme)와 travelMonth 확인
→ festival.month == travelMonth 축제 후보 조회
→ 사용자 travel theme pool과 축제 theme_tags/assigned_theme OR 매칭
→ 축제가 존재하는 city_id set 생성
→ 해당 city_id set 안에서만 attraction retrieval
→ place/city scoring
→ selected_city 결정
→ selected_city의 축제 후보만 selected_festival_candidates로 분리
→ Festival_Verifier_Agent handoff
```

### 4.2.2 Anchored Place Search의 Fixed-City Festival Lookup

```text
includeFestivals=true
destinationId != null
→ anchor city 확정
→ anchor city 안에서 festival.month == travelMonth 축제 후보 조회
→ 사용자 travel theme pool과 축제 theme_tags/assigned_theme OR 매칭
→ anchor city의 장소 evidence retrieval/scoring
→ selected_city는 anchor city로 유지
→ anchor city의 축제 후보만 selected_festival_candidates로 분리
→ Festival_Verifier_Agent handoff
```

seed 조건은 아래 규칙을 사용한다.

```text
theme_pool = active_required_themes excluding festival/include-only labels

festival.month == travelMonth
AND
(
  festival.assigned_theme in theme_pool
  OR any(festival.theme_tags in theme_pool)
)
```

여러 travel theme를 선택한 경우 theme 조건은 OR로 해석한다. 예를 들어 `["바다·해안", "미식·노포"]`를 선택했다면 축제 후보는 두 테마 중 하나 이상과 매칭되면 theme seed 조건을 통과한다. 단, 월 조건은 항상 만족해야 한다.

API 계약상 축제 포함 여부는 `includeFestivals`가 담당한다. 따라서 `festival_event`나 `축제·이벤트`는 seed theme pool에 넣지 않는다. `includeFestivals=true`인데 정규화 이후 `theme_pool`이 비어 있으면 월만으로 축제 도시를 찾지 않고 `status=no_candidate`, `failure_signals=["no_required_theme_for_festival_seed"]`, `needs_clarification=true`를 반환해 사용자에게 여행 테마를 추가로 묻는다.

Festival Candidate Channel의 책임:

| 책임 | 설명 |
| --- | --- |
| 월 조건 조회 | `festival.month == travelMonth`를 만족하는 축제만 후보로 사용 |
| theme OR 매칭 | 사용자의 non-festival `active_required_themes` 중 하나 이상이 축제 `theme_tags` 또는 `assigned_theme`와 일치해야 함 |
| city pool 제한 | `destinationId == null`에서는 월·테마 조건을 만족하는 축제가 있는 도시만 장소 retrieve/scoring 대상으로 유지 |
| anchor city 제한 | `destinationId != null`에서는 anchor city 내부 축제만 조회하고 다른 도시 축제는 후보에서 제외 |
| Verifier handoff 후보 구성 | 최종 `selected_city`에 속한 축제 후보를 `selected_festival_candidates`로 분리 |

Festival City Seed Channel이 하지 않는 일:

| 하지 않는 일 | 담당 |
| --- | --- |
| 축제 `event_start_date`의 목표 연도 검증 | `Festival_Verifier_Agent` |
| 축제 일정 직접 배치 가능 여부 판단 | `Festival_Verifier_Agent`, `Planner_Agent` |
| 축제를 place/city scoring 대상으로 포함 | 하지 않음 |
| 축제 후보가 없는 경우 일반 city discovery로 몰래 완화 | 향후 relaxation 정책이 승인되기 전까지 금지 |
| anchored mode에서 축제 후보가 없다고 다른 도시로 자동 변경 | 하지 않음 |

`destinationId == null`이고 `includeFestivals=true`인데 월·테마 조건을 모두 만족하는 축제 city seed가 없으면 일반 장소 검색으로 몰래 완화하지 않는다. 이 경우 `status=no_candidate`, `failure_signals=["no_festival_city_seed"]`, `needs_clarification=true`를 반환하고 사용자에게 축제 조건을 완화할지 묻는다.
Supervisor는 이 결과를 받으면 Festival Verifier나 Planner를 호출하지 않고 사용자 응답 대기로 종료한다.

`destinationId != null`이고 anchor city 안에 월·테마 조건을 모두 만족하는 축제 후보가 없으면 도시를 자동 변경하지 않는다. 이 경우 `failure_signals=["no_festival_in_anchor_city"]`, `needs_clarification=true`를 반환해 Supervisor가 "고정 도시는 유지하되 축제 없이 진행할지" 또는 "도시 고정을 풀고 축제 포함 추천을 다시 받을지"를 묻도록 한다.

질문 예:

```text
선택한 월과 테마에 맞는 축제 후보를 찾지 못했어요. 축제 조건을 빼고 추천을 이어갈까요, 아니면 테마나 월을 바꿔볼까요?
```

# 5. Candidate Evidence Package

```json
{
  "status": "ok",
  "failure_signals": [],
  "needs_clarification": false,
  "clarifying_question": null,
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
  "festival_candidates": [],
  "selected_festival_candidates": [],
  "coverage_audit": {},
  "festival_seed_audit": {},
  "retrieval_audit": {},
  "candidate_counts": {},
  "warnings": {},
  "fallback_audit": {},
  "candidate_reason_claims": [
    {
      "claim_id": "city_reason_1",
      "scope": "city_selection",
      "text_ko": "선택 도시는 바다·해안 테마 관광지 후보가 충분하고 후보 분포가 안정적입니다.",
      "evidence_refs": ["selected_city", "city_rankings[0]", "coverage_audit"],
      "required_place_ids": [],
      "public_eligible": true
    },
    {
      "claim_id": "place_pool_1",
      "scope": "place_pool",
      "text_ko": "대표 후보들은 사용자의 바다 산책 요청과 연결되는 관광지들입니다.",
      "evidence_refs": ["recommended_places:P_001", "recommended_places:P_002"],
      "required_place_ids": ["P_001", "P_002"],
      "public_eligible": true
    }
  ]
}
```

`status`는 `ok`, `no_candidate`, `insufficient_candidates`, `error` 중 하나다. 후보 부족과 AWS/runtime 오류는 예외를 외부로 전파해 전체 실행을 중단하지 않고 구조화된 결과로 기록한다. `needs_clarification`은 Candidate Evidence 단계에서 사용자 조건 보완이 필요할 때만 `true`로 둔다. 예를 들어 축제 포함 요청에서 travel theme pool이 비었거나 월·테마 seed 도시가 없거나, anchored mode의 고정 도시 안에 조건에 맞는 축제가 없으면 `clarifying_question`에 다음 사용자 턴에서 물어볼 짧은 질문을 담는다.
`needs_clarification=true`이면 downstream은 후보 패키지를 Planner 입력으로 소비하지 않는다. Supervisor가 질문을 사용자에게 전달하고 다음 턴 입력을 기다린다.

정상·부족 결과는 위 전체 package를 사용한다. `no_candidate`와 `error`에서는 `selected_city=null`, 빈 후보 목록과 원인 필드를 우선 반환하며 일부 audit는 빈 객체일 수 있다. 따라서 downstream은 `status`를 먼저 확인한 뒤 상태별 필수 필드를 검증한다.

Candidate Evidence는 선택 근거를 제공한다. 이 근거는 두 계층으로 나뉜다.

1. deterministic 선택 근거: score, reason code, coverage/fallback audit
2. LLM 압축 claim: deterministic 근거를 짧은 한국어 문장 후보로 압축한 `candidate_reason_claims`

`candidate_reason_claims`는 최종 사용자 응답이 아니다. Planner는 최종 일정에 실제 배치된 item, detail enrichment 결과, raw/soft query, 검증된 축제 결과와 대조해 claim을 채택·수정·폐기한다.

선택 근거의 계층:

| 계층 | 필드 | 의미 |
| --- | --- | --- |
| 도시 선택 근거 | `selected_city.selection_reason_code`, `city_rankings[].score_breakdown`, `city_rankings[].evidence_place_ids` | 왜 이 도시가 후보가 되었는지에 대한 내부 reason code와 score audit |
| 장소 선택 근거 | `recommended_places[].evidence_reason_code`, `assigned_theme`, `place_score`, `similarity_raw`, `similarity_soft` | 각 장소가 어떤 query/theme 근거로 primary/reserve가 되었는지 |
| 축제 조건 근거 | `festival_seed_audit`, `selected_festival_candidates` | 축제 포함 요청에서 월·테마 seed가 어떻게 작동했는지 |
| 부족/완화 근거 | `coverage_audit`, `fallback_audit`, `warnings` | 후보 부족, quota shortfall, sufficiency fallback, runtime warning |
| LLM 압축 claim | `candidate_reason_claims` | 구조화 근거를 짧은 claim 후보 문장으로 압축. `evidence_refs`와 `required_place_ids`로 검증 가능해야 함 |

Candidate Evidence LLM은 검색·스코어링 결정을 바꾸지 않는다. 역할은 이미 결정된 구조화 근거를 `candidate_reason_claims`로 압축하는 것이다. Claim은 다음 규칙을 지킨다.

| 필드 | 의미 |
| --- | --- |
| `claim_id` | claim 식별자 |
| `scope` | `city_selection`, `place_pool`, `festival_anchor`, `candidate_shortage`, `external_link_policy`, `fallback_notice` 중 하나 |
| `text_ko` | Planner가 참고할 짧은 한국어 claim 후보 |
| `evidence_refs` | claim이 참조한 내부 evidence/audit 경로 |
| `required_place_ids` | claim이 특정 장소를 전제로 할 때 필요한 place id 목록 |
| `public_eligible` | Planner가 검증 후 사용자 문장으로 채택할 수 있는 후보인지 여부 |

LLM claim 생성이 schema validation에 실패하면 bounded retry를 수행한다. retry 이후에도 실패하면 Candidate Evidence Package 자체를 실패로 만들지 않고, `candidate_reason_claims=[]` 또는 `public_eligible=false`인 템플릿 claim만 남기며 warning을 기록한다.

사용자에게 보일 최종 문장은 Planner가 최종 배치 item과 detail enrichment 결과를 확인한 뒤 생성한다.

## 5.1 `selected_city`

`selected_city`는 도시 이미지가 아니라 장소 evidence와 scoring 결과에서 파생한다.

anchor city가 주어진 경우에는 사용자가 지정한 도시를 유지한다.
anchor가 없는 경우 city score 1위는 `score_winner`가 된다. 그러나 Planner 후보 예산을 충족하지 못하면 다음 우선순위의 sufficiency fallback을 적용할 수 있으므로 최종 `selected_city`는 `city_rankings[0]`과 다를 수 있다.

```text
1. primary + reserve total budget을 충족하는 최고 점수 도시
2. primary budget을 충족하는 최고 점수 도시
3. 둘 다 없으면 score winner(best available)
```

이 차이는 `fallback_audit.score_winner_city`, `selected_city`, `applied`, `tier`에 기록한다.

현재 fallback의 충분성 판정은 `place_id` 병합 후, title dedup 전의 선택 도시 후보 수를 기준으로 한다. 따라서 충분한 도시로 fallback했더라도 title dedup 또는 테마 공급 부족 이후 최종 package가 `insufficient_candidates`가 될 수 있다.

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
    "scale_correction": 0.048,
    "candidate_sufficiency": 0.1,
    "distance_penalty": 0.04,
    "congestion_penalty": 0.0
  },
  "evidence_place_ids": ["P_001", "P_002", "P_003"]
}
```

## 5.3 `recommended_places` / `reserve_places`

`recommended_places`는 Planner가 우선 사용하는 primary 관광지 후보이고, `reserve_places`는 Planner fallback 지연을 줄이기 위한 예비 관광지 후보다.

두 필드는 `attraction` 기반 일정 후보만 담는다. `restaurant` 후보는 현재 단계에서 조회하지 않으며, 식사 슬롯은 Planner가 선택 도시 기준 외부 맛집 검색 링크와 placeholder로 처리한다. 축제 후보는 `festival_candidates`와 `selected_festival_candidates`에 분리한다.

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
  "evidence_reason_code": ["raw_match", "soft_match", "theme_match"],
  "ddb_pk": "CITY#Yeongdeok",
  "ddb_sk": "ATTRACTION#P_001"
}
```

Planner는 `recommended_places`를 우선 사용하고, 장소 수·동선·시간대 제약으로 부족하면 `reserve_places`를 사용한다.
primary와 reserve가 모두 부족한 경우에만 Candidate Evidence Agent 재호출을 요청한다.

Candidate Evidence Package의 장소 후보는 S3 Vector metadata와 `ddb_pk`/`ddb_sk`를 포함하는 lightweight 후보로 유지한다. DynamoDB detail 조회는 Planner가 최종 일정에 실제 배치한 attraction item에 대해서만 이후 detail enrichment 단계에서 수행한다.

## 5.4 `festival_candidates` / `selected_festival_candidates`

`festival_candidates`는 `includeFestivals=true`일 때 Festival Candidate Channel이 찾은 월·테마 조건 축제 후보 전체다. `selected_festival_candidates`는 최종 `selected_city`에 속해 Festival Verifier가 실제 검증할 후보 목록이다.

`festival_candidates`의 범위는 실행 모드에 따라 다르다.

| mode | `festival_candidates` 범위 |
| --- | --- |
| `festival_seeded_city_discovery` | city seed 후보군에 포함된 도시들의 월·테마 매칭 축제 |
| `anchored_place_search` + `includeFestivals=true` | anchor city 내부의 월·테마 매칭 축제 |
| `city_discovery` + `includeFestivals=false` | 빈 배열 |

```json
{
  "festival_id": "FEST-12345",
  "name": "강릉커피축제",
  "country": "KR",
  "city_id": "KR-Gangneung",
  "city_name": "강릉시",
  "month": 10,
  "assigned_theme": "미식·노포",
  "theme_tags": ["미식·노포"],
  "catalog_start_date": "2026-10-03",
  "catalog_end_date": "2026-10-06",
  "candidate_rank": 1,
  "candidate_score": 0.82,
  "candidate_reason": "여행 월과 미식 테마에 맞는 선택 도시의 축제 후보",
  "source": "dynamodb_domain_item"
}
```

축제 후보 정책:

- `month == travelMonth`이고 사용자 테마 OR 조건을 만족하는 축제만 Festival Candidate 후보가 된다.
- 사용자 테마 OR 조건은 `includeFestivals`가 아니라 API `themes`에서 온 non-festival travel theme pool만 사용한다.
- 축제 후보는 `ScoringTool.score_place`와 `ScoringTool.score_city`의 입력이 아니다.
- `candidate_score`는 도시/장소 ranking 점수가 아니라 Festival Verifier handoff 우선순위다.
- `selected_festival_candidates`는 기본 Top-K 2-3개를 권장한다.
- Planner는 이 목록을 직접 믿고 축제를 배치하지 않는다. 일정 직접 배치는 `Festival_Verifier_Agent`가 `date_status=confirmed`로 검증한 축제에만 가능하다.

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

1. title 기준 중복 후보를 먼저 제거한다.
2. `searchable_place_themes`별 minimum quota를 먼저 채운다.
3. 남은 slot은 place score 순으로 채우되 한 테마가 soft maximum quota를 넘지 않게 한다.
4. maximum quota 때문에 primary가 비는 경우에만 상한을 완화해 후보 수를 보존한다.
5. `coverage_audit`에 theme count, quota shortfall, 상한 완화 여부를 남긴다.

현재 Ours quota:

```text
theme_min_quota = floor(primary_budget / searchable_place_theme_count * 0.6)
theme_max_quota = ceil(primary_budget / 2)
```

`searchable_place_theme_count == 0`이면 장소 quota 계산을 수행하지 않는다. 이 경우 Candidate Evidence는 anchor city, 축제 seed, 또는 별도 도시 선택 fallback 없이는 도시 ranking 근거가 부족하므로 사용자 재질문 또는 인기/온보딩 기반 보조 정책 결정이 필요하다.

예시:

```text
searchable place themes = 2
primary budget = 10
theme_min_quota = floor(10 / 2 * 0.6) = 3
theme_max_quota = ceil(10 / 2) = 5
```

`theme_max_quota`는 hard cap이 아니다. 예를 들어 두 번째 테마 후보가 2개뿐이라면 먼저 상한 안에서 가능한 후보를 채운 후, 남은 primary slot은 첫 번째 테마 후보로 보충한다. 이 경우 `max_quota_relaxed=true`와 완화된 slot 수를 audit에 기록한다. 복수 theme tag를 가진 장소도 quota 계산에서는 하나의 `assigned_theme`에만 배정한다.

title 중복 제거는 `strip + casefold`로 정규화한 값에 적용한다. title이 비어 있는 후보는 title dedup 대상에서 제외한다. title dedup 후 primary slot이 비면 차순위 고유 후보로 다시 채우며, reserve도 같은 고유 후보 pool에서 구성한다.

# 8. Scoring 개요

점수 계산 자체는 `Scoring Tool`이 결정론적으로 수행한다.
Agent는 score breakdown과 후보 패키지를 해석해 downstream에 넘긴다.

축제 후보는 Scoring Tool의 place/city scoring 대상이 아니다. `includeFestivals=true`에서 축제는 `destinationId == null`이면 도시 후보군을 제한하는 seed 조건으로, `destinationId != null`이면 고정 도시 내부 Verifier handoff 후보로만 사용한다. 도시 ranking 점수는 현재 `attraction` evidence를 기준으로 계산한다.
즉 `festival_seeded_city_discovery`에서는 scoring 전에 seed city pool이 먼저 확정되므로 축제가 없는 도시는 ranking 후보에 들어오지 않는다.
향후 `festival_city_signal`을 추가하더라도 이는 seed city pool 내부의 재정렬이나 tie-break에만 사용할 수 있으며, seed 밖 도시를 새로 끌어올리는 점수로 사용하지 않는다.

`restaurant`도 현재 단계의 scoring 대상이 아니다. 식당 정보는 DB detail 조회나 S3 Vector 후보 검색으로 확보하지 않고, Planner/Backend가 선택 도시 기반 외부 맛집 검색 링크를 제공한다.

## 8.1 City Score

```text
city_score =
  semantic_evidence_score
+ theme_coverage_score
+ theme_balance_score
- scale_correction
+ candidate_sufficiency_bonus
- distance_penalty
- congestion_penalty
```

| 항목 | 의미 |
| --- | --- |
| `semantic_evidence_score` | top primary 후보의 place score 합을 `primary_budget`으로 나눈 값. 후보가 부족하면 자동 감점 |
| `theme_coverage_score` | top primary 후보가 커버한 active theme 수 / 전체 active theme 수 |
| `theme_balance_score` | top primary 후보의 필수 테마 분포에 대한 정규화 Shannon entropy |
| `scale_correction` | `0.02 * log(top_place_count + 1)` 감점 |
| `candidate_sufficiency_bonus` | top 후보가 5개 이상이면 `+0.1`, 아니면 `0.0` |
| `distance_penalty` | 사용자 위치와 top 후보 평균 좌표 간 거리 100km당 `0.05` 감점 |
| `congestion_penalty` | 생존 도시 내 월별 방문객 rank index와 query별 `w_cong`의 곱 |

복수 테마의 `theme_balance_score`는 다음과 같다.

```text
p_i = theme_i assignment count / total theme assignments
theme_balance = -Σ(p_i log p_i) / log(required_theme_count)
```

단일 테마는 `1.0`, 복수 테마인데 assignment가 없으면 `0.0`이다.

city entropy 계산에서는 multi-tag 후보가 둘 이상의 필수 테마 count에 기여할 수 있다. 반면 최종 primary quota에서는 후보 하나를 하나의 `assigned_theme`에만 배정한다. 즉 city ranking의 entropy와 package 구성의 quota count는 계산 목적과 assignment 규칙이 다르다.

현재 `scale_correction`은 전체 도시 후보 수가 아니라 `primary_budget`으로 잘린 top 후보 수에 적용된다. 따라서 예산을 충분히 채운 도시끼리의 데이터 규모 차이를 강하게 보정하지 못한다. `candidate_sufficiency_bonus`도 5개 이상 여부만 보는 coarse signal이므로, 실제 primary/reserve 충족 판단은 별도의 fallback과 `candidate_counts`가 담당한다.

방문객 통계가 있는 도시는 생존 도시 집합 내 rank를 `0.0~1.0`으로 정규화한다. 통계 누락 도시는 가장 한적한 도시로 오인하지 않도록 중립값 `0.5`를 사용한다.

현재 평가 구현은 `travelMonth`를 사용하지만 방문객 통계 key의 연도는 `2025`로 고정되어 있다. `travelYear`별 통계 선택은 제품 통합 전에 보완해야 한다.

| query 성향 | 현재 `w_cong` | 효과 |
| --- | ---: | --- |
| quiet keyword | `4.0` | 혼잡 도시 감점 |
| vibrant keyword | `-1.5` | 활기찬 도시를 상대적으로 가점 |
| 명시 성향 없음 | `2.5` | 기본 혼잡 감점 |

현재 keyword 기반 weight는 실험용 결정 규칙이며 sensitivity calibration 대상이다.

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
| `raw_similarity` | raw cosine distance가 있으면 `1 - distance`, 없으면 `0.0` |
| `soft_similarity` | soft cosine distance가 있으면 `1 - soft_distance`, 없으면 `0.0` |
| `theme_match_score` | active theme와 하나 이상 겹치면 `+0.2` |
| `source_quality_score` | 좌표, title, theme tags, city 정보별 `+0.05`, 최대 `0.2` |
| `local_distance_penalty` | 해당 도시의 전체 생존 후보 좌표 평균점에서 장소까지 1km당 `0.005` 감점 |

최종 `place_score`는 음수가 되지 않도록 `max(score, 0.0)`을 적용한다. 현재 source quality는 description 길이나 실제 영업 정보의 정확성을 평가하지 않으며, 핵심 metadata 존재 여부만 확인한다.

# 9. Vector Index와 Runtime Retrieval 계약

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

## 9.1 런타임 조회 계층

현행 검증 흐름에서 Candidate Evidence Agent의 후보 조회는 다음 두 계층으로 분리된다.

| 계층 | 역할 | 정본 계약 |
| --- | --- | --- |
| S3 Vector index | query embedding과 metadata filter로 후보 chunk를 검색 | 도시/장소 후보 pool을 만드는 1차 evidence 원천 |
| DynamoDB normalized item | S3 Vector metadata의 `ddb_pk`/`ddb_sk`로 상세 원본을 point lookup | Planner가 최종 일정에 배치한 attraction item의 canonical detail 보강 |

S3 Vector 검색 결과는 최종 사실 자체가 아니라 후보 evidence다.
DynamoDB detail은 Planner가 최종 배치한 일정 item과 사용자용 설명을 만들 때 필요한 canonical detail 보강값이다. Candidate Evidence는 이 detail 조회를 직접 수행하지 않는다.

검색과 상세 조회의 표준 흐름:

```text
cleaned_raw_query / soft_preference_query
→ query embedding
→ searchable place theme별 S3 Vector search
→ vector metadata 기반 후보 병합, 도시 grouping, scoring
→ selected city 결정
→ primary/reserve 분리
→ Candidate Evidence Package 반환
→ Planner 최종 일정 배치
→ 최종 배치 attraction item만 DynamoLookupTool로 DynamoDB detail enrichment
```

## 9.2 S3 Vector metadata 계약

S3 Vector metadata는 Candidate Evidence가 후보를 병합하고 필터링하고 점수화하는 데 필요한 최소 정보를 제공해야 한다.

| metadata 필드 | 용도 | 비고 |
| --- | --- | --- |
| `entity_type` | 관광지/축제 등 검색 대상 유형 구분 | 현재 Candidate Evidence 장소 검색은 `attraction` 중심이며 `restaurant`는 조회하지 않음 |
| `city_id` | 도시 grouping, anchor 검증, 단일 도시 원칙 | 없으면 city discovery 비교 대상에서 제외될 수 있음 |
| `city_name_ko` 또는 도시명 | 감사와 출력 보조 | `city_id` 대체값으로만 제한적으로 사용 |
| `theme_tags` | searchable place theme AND gate와 quota 판단 | 관광지 검색 filter와 coverage audit에 사용 |
| `title` | title dedup, Planner 표시 후보명 | 없으면 source quality 하향 |
| `latitude`, `longitude` | 도시 내부 거리 패널티, 동선 보조 | 없으면 source quality 하향 |
| `ddb_pk`, `ddb_sk` | DynamoDB detail enrichment key | 최종 배치 item detail 보강에 필요 |
| S3 Vector `key` | chunk 식별자 | `{entity_type}#{source_id}#{chunk_no}` 형태를 권장 |
| S3 Vector `distance` | raw/soft similarity 계산 | 값이 낮을수록 query와 가까움 |

Candidate Evidence는 S3 Vector `key`에서 chunk 번호를 제거해 `place_id`를 만든다.

```text
attraction#67890#2 → attraction#67890
```

같은 `place_id`가 여러 theme 검색 또는 raw/soft channel에서 반복되면 하나의 후보로 병합하고, channel별 최소 distance를 보존한다.

## 9.3 S3 Vector 검색 filter 계약

현재 검증 구현은 S3 Vector `query_vectors` 호출에서 metadata filter를 함께 사용한다.

| 조건 | filter |
| --- | --- |
| anchor city가 있음 | `city_id == destinationId 또는 anchor city_id` |
| `미식·노포` theme | 장소 검색 filter를 만들지 않고 Planner의 `foodSearch` 링크 요구로 전달 |
| 그 외 active theme | `entity_type == attraction` |
| active theme 지정 | `theme_tags == theme` |

복수 조건은 `$and`로 결합한다.

현재 검증값은 searchable place theme별 `top_k=50`이다.
`top_k=50`은 제품 API 계약이 아니라 현재 평가에서 사용한 운영 파라미터다. 운영 환경에서는 latency budget, 후보 충분성, 비용 지표를 보고 조정할 수 있다.

raw/soft 검색 호출 수의 기본 관계:

| 전략 | 검색 channel | S3 Vector query 수 |
| --- | --- | --- |
| Baseline | raw only | active theme 수만큼 |
| Ours | raw + soft | soft query가 있으면 active theme 수의 최대 2배 |

soft query가 없으면 soft channel은 호출하지 않는다.

## 9.4 DynamoDB detail enrichment handoff 계약

DynamoDB detail enrichment는 scoring 전 전체 후보에도, Candidate Evidence의 primary/reserve package 구성 직후에도 수행하지 않는다.
Candidate Evidence는 S3 Vector metadata와 score 계산만으로 도시와 primary/reserve 후보를 고르고, 최종 일정에 실제 배치된 attraction item에 대한 detail 조회는 Planner 단계 이후로 넘긴다.

| 대상 | detail 조회 정책 | 이유 |
| --- | --- | --- |
| `recommended_places` / primary | Candidate Evidence에서는 조회하지 않음. `ddb_pk`/`ddb_sk`와 선택 근거만 유지 | Planner가 실제 배치하지 않을 수 있으므로 조기 detail lookup을 피함 |
| `reserve_places` | Candidate Evidence에서는 조회하지 않음. `ddb_pk`/`ddb_sk`와 선택 근거만 유지 | reserve는 실제 사용 여부가 Planner에서 결정됨 |
| Planner 최종 배치 attraction item | `DynamoLookupTool`로 DynamoDB detail enrichment 수행 | 사용자용 일정 item과 추천 설명에 필요한 canonical detail 보강 |
| scoring 전 전체 후보 | 조회하지 않음 | 대량 DynamoDB GetItem 비용 방지 |

이 정책은 Planner 계약에 영향을 준다.

1. Planner는 먼저 primary/reserve 후보를 일정 슬롯에 배치한다.
2. 최종 배치된 attraction item만 `ddb_pk`/`ddb_sk`로 `DynamoLookupTool` detail enrichment 대상이 된다.
3. `ddb_pk`/`ddb_sk`가 없어 detail을 조회하지 못하면 enrichment warning을 남기고 `details=null`로 둔다.
4. `details=null`인 항목은 title, theme, reason code 같은 metadata 수준으로만 보수적으로 설명한다.
5. DynamoDB detail이 없다고 해서 새로운 장소 설명을 생성하면 안 된다.
6. Candidate Evidence가 제공한 선택 근거(`selection_reason_code`, `evidence_reason_code`, audit, `candidate_reason_claims`)는 Planner 설명의 방향을 잡는 내부 claim 후보이며, 사용자용 최종 문장 그 자체가 아니다.

## 9.5 구현 세부 분리

본 정본은 런타임 조회의 아키텍처 계약만 정의한다.

다음 항목은 실행 세부 문서에서 관리한다.

| 실행 세부 | 문서 |
| --- | --- |
| runtime 전체 도구 흐름과 실행 명령 | `candidate_evidence_runtime_retrieval.md` |
| S3 Vector 검색, 도시 AND gate | `destination_search_tool.md` |
| DynamoDB festival seed lookup, 최종 배치 item detail enrichment | `dynamo_lookup_tool.md` |
| place/city scoring 공식과 score breakdown | `scoring_tool.md` |
| boto3 client 생성, profile/region, bucket/index/table 이름 | `destination_search_tool.md`, `dynamo_lookup_tool.md` |

AWS 리소스명이나 테스트 harness 경로 변경은 Agent 입출력 계약 변경이 아닐 수 있다.
단, S3 Vector metadata 필드나 Candidate Evidence Package schema가 바뀌면 본 정본과 API/DB 영향도를 함께 확인한다.

# 10. Audit

## 10.1 `coverage_audit`

```json
{
  "required_themes": ["바다·해안", "미식·노포"],
  "searchable_place_themes": ["바다·해안"],
  "external_link_themes": ["미식·노포"],
  "primary_theme_counts": {
    "바다·해안": 5
  },
  "reserve_theme_counts": {
    "바다·해안": 7
  },
  "candidate_sufficiency": "sufficient",
  "theme_min_quota": 3,
  "theme_max_quota": 5,
  "min_quota_shortfalls": {},
  "max_quota_relaxed": false,
  "relaxed_slots": 0,
  "deduplicated_title_count": 0,
  "unfilled_primary_slots": 0
}
```

도시 ranking의 `theme_balance`는 `city_rankings[].score_breakdown`에 entropy 기반 값으로 기록한다. `coverage_audit`는 최종 primary 구성의 quota 실행 결과를 기록하며, 두 지표는 서로 다른 단계의 편중을 설명한다.

quota는 primary에만 적용한다. reserve는 title dedup된 나머지 후보를 place score 순으로 채우므로 테마 균형을 보장하지 않는다. `coverage_audit.candidate_sufficiency`는 현재 primary 5개 이상 여부만 나타내는 coarse field다. 실제 일정 예산 충족 여부는 `status`, `failure_signals`, `candidate_counts`를 기준으로 판단한다.

## 10.2 `retrieval_audit`

```json
{
  "cleaned_raw_query": "바다를 보고 지역 맛집도 가고 싶다",
  "soft_preference_query": "조용하고 한적한 분위기",
  "tools_used": ["vector_search_tool", "scoring_tool"],
  "index_text_mode": "rich",
  "vector_backend": "s3_vectors",
  "detail_store": "dynamodb",
  "top_k_per_theme": 50,
  "s3_query_count": 4,
  "detail_enrichment_policy": "after_planner_final_placement",
  "detail_lookup_stage": "final_placed_items_only"
}
```

## 10.3 `festival_seed_audit`

`includeFestivals=true`일 때만 Festival Candidate Channel 결과를 기록한다. 필드명은 하위 호환을 위해 `festival_seed_audit`로 유지하되, 값의 의미는 실행 모드에 따라 city seed audit 또는 fixed-city festival lookup audit이다.

```json
{
  "enabled": true,
  "mode": "festival_seeded_city_discovery",
  "month_filter": 10,
  "seed_rule": "festival.month == travelMonth AND festival theme OR non_festival_active_required_themes",
  "theme_pool": ["미식·노포", "바다·해안"],
  "theme_match_rule": "OR",
  "festival_candidate_count": 6,
  "seed_city_count": 3,
  "seed_city_ids": ["KR-Gangneung", "KR-Yeongdeok", "KR-Goseong"],
  "selected_city_festival_count": 2,
  "selected_festival_candidate_ids": ["FEST-12345", "FEST-67890"]
}
```

`anchored_place_search`에서 축제 포함이 선택된 경우 예시는 다음과 같다.

```json
{
  "enabled": true,
  "mode": "anchored_place_search",
  "month_filter": 10,
  "anchor_city_id": "KR-Gangneung",
  "lookup_rule": "anchor_city AND festival.month == travelMonth AND festival theme OR non_festival_active_required_themes",
  "theme_pool": ["미식·노포"],
  "festival_candidate_count": 1,
  "selected_city_festival_count": 1,
  "selected_festival_candidate_ids": ["FEST-12345"]
}
```

`includeFestivals=false`이면 `enabled=false` 또는 빈 객체로 둔다.

## 10.4 `candidate_counts`

```json
{
  "primary": 10,
  "reserve": 8,
  "total": 18,
  "primary_budget": 10,
  "reserve_budget": 8
}
```

## 10.5 `fallback_audit`

```json
{
  "score_winner_city": "KR-Cheongsong",
  "selected_city": "KR-Pyeongchang",
  "applied": true,
  "tier": "full_budget"
}
```

`tier`는 `full_budget`, `primary_budget`, `best_available`, `no_candidate` 중 하나다.

## 10.6 `warnings`와 운영 metric

```json
{
  "visitor_stats_missing_cities": [],
  "congestion_zero_cities": ["KR-Goseong"]
}
```

평가 harness는 package 외부 비교 metric으로 S3 query 수, 검색 반환 후보 수, 고유 후보 수, 생존 도시 수, 선택 도시 후보 수, DynamoDB GetItem 추정, latency와 peak RSS를 기록한다. 제품 trace에도 동일 개념을 연결하되 사용자 API에 직접 노출하지 않는다.

# 11. Failure Signals

| signal | 의미 | downstream 처리 |
| --- | --- | --- |
| `no_candidate` | 필수 theme를 충족할 도시/장소 후보가 없음 | 검증 실패가 아니라 조건 완화 또는 안전 폴백 |
| `insufficient_primary` | primary 후보 수 부족 | reserve 사용 |
| `insufficient_total_candidates` | primary+reserve 후보 모두 부족 | Candidate Evidence Agent fallback 재호출 후보 |
| `aws_or_runtime_error` | embedding, S3 Vector, DynamoDB 또는 runtime 오류 | 해당 실행을 `error`로 격리하고 안전 폴백 |
| `no_required_theme_for_festival_seed` | `includeFestivals=true`이나 API `themes` 정규화 후 축제 seed에 사용할 travel theme가 없음 | 월만으로 축제 도시를 찾지 않고 사용자에게 여행 테마 선택을 질문 |
| `no_festival_city_seed` | `includeFestivals=true`이나 월·테마 seed 조건을 모두 만족하는 축제 도시가 없음 | 일반 추천으로 자동 완화하지 않고 사용자에게 축제 조건을 뺄지, 테마/월을 바꿀지 질문 |
| `no_festival_in_anchor_city` | `anchored_place_search`에서 고정 도시 안에 월·테마 조건을 만족하는 축제 후보가 없음 | 도시를 자동 변경하지 않고 축제 없이 진행할지, anchor를 풀고 다시 추천할지 질문 |
| `min_quota_shortfall` | `coverage_audit.min_quota_shortfalls`가 비어 있지 않음 | confidence 하향과 희소 테마 안내 후보 |
| `theme_max_quota_relaxed` | 후보 수 보존을 위해 soft max를 완화 | 실패가 아닌 설명 가능한 구성 audit |
| `anchor_violation` | anchor city 외 장소가 섞임 | Candidate Evidence Agent 결과 폐기 후 재검색 |

현재 구현에서 `min_quota_shortfall`과 `theme_max_quota_relaxed`는 `failure_signals` 배열보다 quota audit와 reason code로 표현한다. Planner와 통합할 때 confidence·notice 정책으로 연결한다.

## 11.1 상태별 처리

| status | 조건 | 처리 |
| --- | --- | --- |
| `ok` | primary와 total budget 충족 | Planner에 정상 전달 |
| `insufficient_candidates` | primary 또는 total budget 미달 | 보유 후보 전달 + confidence 하향 또는 제한적 추가 retrieve |
| `no_candidate` | AND gate 생존 도시 없음, 축제 포함 요청에서 seed theme pool 없음, 월·테마 seed 도시 없음, 또는 anchored mode에서 축제 조건을 hard condition으로 만족할 수 없음 | 검증 retry와 분리. 축제 seed/lookup 실패인 경우 사용자에게 조건 보완 또는 완화 질문 |
| `error` | AWS/runtime 예외 | `error_type`, `error_message` 기록 후 해당 실행만 격리 |

# 12. 현재 검증 범위와 미검증 항목

| 항목 | 상태 |
| --- | --- |
| KR city discovery | 24건 AWS 통합 실행 완료 |
| raw/soft dual retrieval | component·outcome test 완료 |
| entropy + min/soft max quota | component·outcome·AWS audit 완료 |
| S3 Vector + final item detail enrichment | S3 Vector 후보 검색은 검증 완료. DynamoDB detail 조회는 `DynamoLookupTool`의 Planner 최종 배치 item 대상 정책으로 재정의되어 별도 회귀 테스트 필요 |
| 후보 부족과 AWS 오류 격리 | resilience test 완료 |
| Festival Candidate Channel | 목표 계약. `DynamoLookupTool`이 `destinationId == null`에서는 `festival.month == travelMonth` AND non-festival travel theme OR city seed를 만들고, `destinationId != null`에서는 anchor city 내부 festival lookup을 수행한다. seed/lookup 실패 시 clarification fallback, selected city 내 `selected_festival_candidates` 구성 회귀 테스트 필요 |
| anchored place search | 목표 계약, 동일 수준 회귀 미완료 |
| JP index | 현 검증 범위 밖 |
| Weather Trends scoring | 현재 Baseline/Ours 비교에서 제외 |
| Planner 일정 실행 가능성 | Candidate Package 이후 단계로 미검증 |
| 휴폐업·운영시간·실제 교통 | 미검증 |

# 13. Legacy 문서와의 관계

`retriever.md`, `ranker.md`, `retriever_code.md`, `ranker_code.md`는 기존 분리 설계의 세부 아이디어를 보관하는 legacy 문서다.
새로운 상세 정본은 본 문서이며, 기존 문서의 유효한 공식과 기준은 이 문서의 scoring 및 audit 절로 선별 반영한다.

# 14. Baseline 비교와 검증 근거

Baseline과 Ours의 공통 조건, 추가 요소, 현재 24건 평가 결과와 해석 경계는 `candidate_evidence_baseline_comparison.md`를 따른다. 도시·관광지 검색 테스트 계획과 상세 결과는 `../10_test_plan/candidate_evidence_search_test_plan.md`, `../10_test_plan/candidate_evidence_evaluation_results.md`를 정본으로 사용한다.

현재 검증은 Candidate Evidence Package 수준이다. 이 결과만으로 Planner가 생성한 최종 일정의 운영 가능성이나 사용자 만족도를 확정하지 않는다.

S3 Vector 검색 실행 세부는 `destination_search_tool.md`를 따른다.
최종 배치 item detail enrichment 실행 세부는 `dynamo_lookup_tool.md`를 따른다.
place/city scoring 공식과 score breakdown은 `scoring_tool.md`를 따른다.
전체 runtime tool 연결과 실행 명령, 리소스 metric 해석은 `candidate_evidence_runtime_retrieval.md`를 따른다.

# 15. 변경 이력

| 버전 | 날짜 | 변경 내용 |
| --- | --- | --- |
| v0.13 | 2026-06-14 | Candidate Evidence와 Planner 사이 계약을 정리해 Candidate Evidence는 구조화 선택 근거를 LLM으로 `candidate_reason_claims`로 압축하고, Planner가 최종 배치 item/detail/raw·soft query 검증 후 사용자용 설명을 생성하도록 변경 |
| v0.12 | 2026-06-14 | 축제 포함 city discovery에서 월·테마 축제 seed를 hard gate로 명시하고, `needs_clarification=true` 시 Planner 미호출 대기 흐름을 정리 |
| v0.11 | 2026-06-13 | `restaurant` 후보/테이블 조회를 현재 단계 Candidate Evidence 범위에서 제외하고, 미식 테마를 선택 도시 기반 외부 맛집 검색 링크 요구로 Planner에 넘기도록 정리 |
| v0.10 | 2026-06-13 | `anchored_place_search`에서도 `includeFestivals=true`가 가능함을 명시하고, 고정 도시 내부 Festival Fixed-City Lookup 및 축제 후보 없음 fallback을 추가 |
| v0.9 | 2026-06-13 | Festival Verifier handoff 이후 Planner의 축제 직접 배치 기준을 `date_status=confirmed`로 단순화 |
| v0.8 | 2026-06-13 | API 계약에 맞춰 축제 포함을 `includeFestivals` 전용 조건으로 정리하고, Festival City Seed Channel의 theme pool에서 `festival_event`/`축제·이벤트`를 제외 |
| v0.7 | 2026-06-13 | `includeFestivals=true`에서 `festival.month == travelMonth` AND theme OR 축제 도시 seed를 먼저 적용하고, seed 실패 시 사용자 질문 fallback을 명시. 장소 후보와 축제 후보를 `recommended_places`/`reserve_places`와 `festival_candidates`/`selected_festival_candidates`로 분리 |
| v0.6 | 2026-06-13 | 외부 평가 구현 경로 직접 참조를 제거하고 정본 계약·검증 범위 중심으로 정리 |
| v0.5 | 2026-06-13 | runtime 세부 문서를 Destination Search Tool과 Scoring Tool 기준으로 분리하고 정본 참조 갱신 |
| v0.4 | 2026-06-13 | S3 Vector runtime retrieval과 당시 detail 보강 정책을 Candidate Evidence 정본 계약으로 명시하고 실행 세부 문서 분리 |
| v0.3 | 2026-06-12 | Ours 검증 기준으로 dual retrieval, 정확한 scoring 공식, sufficiency fallback, quota·audit·상태 계약과 검증 범위 정합화 |
| v0.2 | 2026-06-12 | min quota + soft max quota 및 quota audit 반영 |
| v0.1 | 2026-06-10 | Candidate Evidence Agent 통합 상세 명세 초안 |
